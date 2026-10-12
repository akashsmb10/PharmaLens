"""Non-destructive source and monthly-grain audit; errors block the pipeline."""
import argparse
import json
import numpy as np
import pandas as pd
from .common import ROOT, CONFIG, utc_now, write_json
from .ingest import KEY, METRICS

MONTHLY_REQUIRED = KEY + ["product_name", "region_name", "chemical_code", "chemical_name", "items", "total_quantity", "nic_gbp", "data_origin"]

def audit(detailed, monthly, config=CONFIG):
    checks, samples = [], []
    def add(name, severity, count, explanation, frame=None):
        checks.append({"check": name, "severity": severity, "count": int(count),
                       "status": "not_applicable" if severity == "not_applicable" else ("finding" if count else "pass"),
                       "explanation": explanation})
        if frame is not None and count:
            for index, row in frame.head(100).iterrows():
                samples.append({"check": name, "row_index": str(index), "row": row.to_json(date_format="iso")})
    missing_columns = sorted(set(MONTHLY_REQUIRED) - set(monthly))
    add("required_columns", "error", len(missing_columns), str(missing_columns))
    if missing_columns:
        return {"checks": checks, "samples": samples, "raw_rows": len(detailed), "monthly_rows": len(monthly), "passed": False}
    invalid_types = [f'{label}.month' for label, frame in [('source', detailed), ('monthly', monthly)]
                     if 'month' not in frame or not pd.api.types.is_datetime64_any_dtype(frame['month'])]
    invalid_types += [f'{label}.{metric}' for label, frame in [('source', detailed), ('monthly', monthly)]
                      for metric in METRICS.values() if metric not in frame or not pd.api.types.is_numeric_dtype(frame[metric])]
    add('data_type_correctness', 'error', len(invalid_types), str(invalid_types))
    if invalid_types:
        return {'checks': checks, 'samples': samples, 'raw_rows': len(detailed), 'monthly_rows': len(monthly), 'passed': False}
    add("total_records", "info", 0, f"{len(detailed)} source rows, {len(monthly)} monthly rows")
    add("empty_data", "error", int(detailed.empty or monthly.empty), "A successful acquisition must be nonempty")
    required_details = [c for c in MONTHLY_REQUIRED if c in detailed]
    required_null = detailed[required_details].isna().any(axis=1)
    add("required_missing_values", "error", required_null.sum(), "Required keys, labels and metrics must be present", detailed[required_null])
    monthly_null = monthly[MONTHLY_REQUIRED].isna().any(axis=1)
    add('monthly_required_missing_values', 'error', monthly_null.sum(), 'Aggregated keys/labels/measures must be populated', monthly[monthly_null])
    optional = [c for c in detailed if c not in required_details and not c.startswith('invalid_')]
    optional_missing = detailed[optional].isna()
    structural_count = 0
    for field, introduced in config.get('schema_optional_fields_introduced', {}).items():
        if field in optional_missing:
            structural = detailed[field].isna() & detailed.month.lt(pd.Timestamp(introduced))
            structural_count += int(structural.sum())
            optional_missing.loc[structural, field] = False
    add('structural_schema_absence', 'info', structural_count, 'Optional field did not exist in earlier monthly resources; valid schema exception')
    add("optional_missing_values", "warning", int(optional_missing.sum().sum()),
        "Optional source fields may be absent; unknown suppliers are not imputed")
    # Candidate source key is every source dimension, excluding normalized measures and coercion flags.
    dimensions = [c for c in detailed if c not in METRICS.values() and not c.startswith("invalid_")]
    duplicates = detailed.duplicated(keep=False)
    add("duplicate_source_rows", "error", duplicates.sum(), "Count includes all members of duplicate groups", detailed[duplicates])
    business_duplicates = detailed.duplicated(dimensions, keep=False)
    add("duplicate_source_business_keys", "error", business_duplicates.sum(),
        "Candidate full-dimensional source key; validate before interpreting repeated simpler product/month keys", detailed[business_duplicates])
    duplicate_monthly = monthly.duplicated(KEY, keep=False)
    add("duplicate_monthly_business_keys", "error", duplicate_monthly.sum(), str(KEY), monthly[duplicate_monthly])
    date_invalid = detailed.month.isna() | (detailed.month.dt.day != 1)
    add("invalid_dates", "error", date_invalid.sum(), "YEAR_MONTH must parse to a calendar month start", detailed[date_invalid])
    monthly_bad_dates = monthly.month.isna() | monthly.month.dt.day.ne(1)
    add('invalid_monthly_dates', 'error', monthly_bad_dates.sum(), 'Aggregated dates must also be calendar month starts', monthly[monthly_bad_dates])
    outside = detailed.month.notna() & ~detailed.month.between(pd.Timestamp(config['start_month']), pd.Timestamp(config['end_month']))
    add("dates_outside_extract", "error", outside.sum(), "Fixed configured extraction window", detailed[outside])
    for metric in METRICS.values():
        numeric = pd.to_numeric(detailed[metric], errors="coerce")
        invalid = numeric.isna() | ~np.isfinite(numeric.to_numpy(dtype=float, na_value=np.nan))
        flag = f"invalid_{metric}"
        if flag in detailed:
            invalid |= detailed[flag]
        add(f"invalid_numeric_{metric}", "error", invalid.sum(), "Missing, unparseable or non-finite values", detailed[invalid])
        negative = numeric.lt(0)
        add(f"negative_{metric}", "warning" if metric == 'nic_gbp' else "error", negative.sum(),
            "Negative cost requires source review; negative volume violates the intended demand use case", detailed[negative])
        zero = numeric.eq(0)
        add(f"zero_{metric}", "info", zero.sum(), "Valid business exception retained; zero is not missing", detailed[zero])
    fractional = detailed["items"].notna() & detailed["items"].mod(1).ne(0)
    add("fractional_prescription_items", "error", fractional.sum(), "Prescription item counts must be integral", detailed[fractional])
    expected = set(pd.date_range(config['start_month'], config['end_month'], freq="MS"))
    actual = set(monthly.month.dropna())
    add("missing_global_months", "error", len(expected - actual), str(sorted(str(x.date()) for x in expected - actual)))
    absent = []
    for key, series in monthly.groupby(["product_code", "region_code", "unit_of_measure"], dropna=False):
        for month in sorted(expected - set(series.month.dropna())):
            absent.append({"product_code": key[0], "region_code": key[1], "unit_of_measure": key[2], "month": month.strftime('%Y-%m')})
    add("missing_series_months", "warning", len(absent),
        "May reflect launches, discontinuations or no dispensing; absence is not automatically zero")
    extremes = []
    for _, group in monthly.groupby(["product_code", "region_code", "unit_of_measure"], dropna=False):
        for metric in METRICS.values():
            q1, q3 = group[metric].quantile([.25, .75])
            iqr = q3 - q1
            if len(group) >= 12 and iqr > 0:
                hit = group[(group[metric] < q1 - 3 * iqr) | (group[metric] > q3 + 3 * iqr)]
                extremes.extend([{**r, "metric": metric} for r in hit.to_dict('records')])
    add("extreme_observations", "warning", len(extremes), "Three-IQR fences within each monthly series/metric; review, do not remove")
    origins = ~monthly.data_origin.isin(["observed_nhsbsa", "synthetic_demo"])
    add("unexpected_origin_categories", "error", origins.sum(), "Allowed observed_nhsbsa or synthetic_demo", monthly[origins])
    observed = monthly.data_origin.eq("observed_nhsbsa")
    chemical = observed & monthly.chemical_code.ne(config['filters']['BNF_CHEMICAL_SUBSTANCE_CODE'])
    add("unexpected_chemical_category", "error", chemical.sum(), "Must match configured acquisition filter", monthly[chemical])
    bad_codes = observed & ~monthly.product_code.astype('string').str.fullmatch(r'[0-9A-Z]{15}', na=False)
    add("inconsistent_product_identifiers", "error", bad_codes.sum(), "Expected 15-character alphanumeric BNF presentation code", monthly[bad_codes])
    conflicting_products = int(detailed.groupby('product_code')['product_name'].nunique().gt(1).sum())
    add("product_code_name_changes", "warning", conflicting_products, "Names can evolve; identifiers remain the analytical key")
    bad_geography = monthly.region_code.isna() | monthly.region_name.isna() | monthly.region_code.astype('string').str.strip().eq('')
    add("geographic_inconsistencies", "error", bad_geography.sum(), "Missing/blank region identifiers", monthly[bad_geography])
    unusual_regions = observed & ~monthly.region_code.isin(['Y56', 'Y58', 'Y59', 'Y60', 'Y61', 'Y62', 'Y63'])
    add('unexpected_geographic_categories', 'warning', unusual_regions.sum(), 'Special/unknown source codes require interpretation; retained', monthly[unusual_regions])
    region_conflicts = int(detailed.groupby('region_code')['region_name'].nunique().gt(1).sum())
    add("region_code_name_changes", "warning", region_conflicts, "Review administrative naming changes, including STP-to-ICB transitions")
    unit_changes = int(detailed.groupby('product_code')['unit_of_measure'].nunique().gt(1).sum())
    add("product_unit_changes", "warning", unit_changes, "Unit is included in the monthly key to avoid mixing quantities")
    for metric in METRICS.values():
        source_sum, monthly_sum = detailed[metric].sum(), monthly[metric].sum()
        difference = abs(source_sum - monthly_sum) if np.isfinite(source_sum) and np.isfinite(monthly_sum) else float('inf')
        add(f"aggregation_reconciliation_{metric}", "error", int(not np.isclose(difference, 0, atol=.01)),
            f"Absolute source-minus-processed total difference = {difference:.6f}")
    add("data_grain_violations", "error", duplicate_monthly.sum(), "Exactly one row per month/presentation/region/unit")
    add("revenue_arithmetic", "not_applicable", 0, "No revenue or transaction unit price exists. NIC is NHS ingredient cost, not company revenue.")
    return {"generated_at_utc": utc_now(), "raw_rows": len(detailed), "monthly_rows": len(monthly),
            "checks": checks, "samples": samples, "missing_series_periods": absent,
            "extremes": [{k: str(v) if isinstance(v, pd.Timestamp) else v for k, v in r.items()} for r in extremes],
            "passed": not any(c['severity'] == 'error' and c['count'] for c in checks)}

def validate(root=ROOT):
    detailed = pd.read_parquet(root / "data/processed/source_rows.parquet")
    monthly = pd.read_parquet(root / "data/processed/monthly_prescribing.parquet")
    result = audit(detailed, monthly)
    out = root / "outputs/validation"
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / "quality_report.json", result)
    pd.DataFrame(result['checks']).to_csv(out / "quality_checks.csv", index=False)
    pd.DataFrame(result['samples'], columns=['check', 'row_index', 'row']).to_csv(out / "finding_samples.csv", index=False)
    pd.DataFrame(result.get('missing_series_periods', [])).to_csv(out / "missing_series_periods.csv", index=False)
    pd.DataFrame(result.get('extremes', [])).to_csv(out / "extreme_observations.csv", index=False)
    pd.DataFrame({"dtype": detailed.dtypes.astype(str), "missing_count": detailed.isna().sum(),
                  "missing_percent": detailed.isna().mean() * 100, "unique_values": detailed.nunique(dropna=False)}).to_csv(out / "column_profile.csv")
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.parse_args()
    result = validate()
    print(json.dumps({k: result[k] for k in ['raw_rows', 'monthly_rows', 'passed']}))
    raise SystemExit(0 if result['passed'] else 1)
