"""Acquire immutable, filtered NHSBSA API responses and normalize without deleting anomalies."""
import argparse
import hashlib
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
import pandas as pd
import numpy as np
from .common import CONFIG, ROOT, prepare_dirs, sha256, utc_now, write_json

REQUIRED = ["YEAR_MONTH", "REGION_CODE", "REGION_NAME", "BNF_PRESENTATION_CODE",
            "BNF_PRESENTATION_NAME", "BNF_CHEMICAL_SUBSTANCE_CODE", "BNF_CHEMICAL_SUBSTANCE",
            "UNIT_OF_MEASURE", "ITEMS", "TOTAL_QUANTITY", "NIC"]
METRICS = {"ITEMS": "items", "TOTAL_QUANTITY": "total_quantity", "NIC": "nic_gbp"}
KEY = ["month", "product_code", "region_code", "unit_of_measure"]

def check_columns(df):
    missing = sorted(set(REQUIRED) - set(df.columns))
    if missing:
        raise ValueError(f"Missing required source columns: {missing}")

def load_csv(path):
    # Keep leading-zero BNF codes and SNOMED identifiers intact.
    try:
        return pd.read_csv(path, dtype="string", encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(path, dtype="string", encoding="cp1252")

def fetch_json(url, path, refresh=False):
    path = Path(path)
    if path.exists() and not refresh:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        if not payload.get("success"):
            raise ValueError(f"Unsuccessful cached API response: {path}")
        return payload, False
    request = urllib.request.Request(url, headers={"User-Agent": "PharmaPortfolioPhase1/1.0", "Accept": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                body = response.read()
            payload = json.loads(body.decode("utf-8-sig"))
            if not payload.get("success"):
                raise ValueError(f"API returned success=false: {payload.get('error')}")
            path.parent.mkdir(parents=True, exist_ok=True)
            # Refresh is deliberately prohibited on existing evidence: use a new raw directory.
            if path.exists():
                raise ValueError("Refusing to overwrite original raw response")
            path.write_bytes(body)
            write_json(path.with_suffix(".receipt.json"), {"url": url, "downloaded_at_utc": utc_now(),
                       "sha256": sha256(path), "bytes": len(body)})
            return payload, True
        except (OSError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)

def acquire(root=ROOT):
    raw = root / "data/raw"
    url = CONFIG["api_base"] + "package_show?" + urllib.parse.urlencode({"id": CONFIG["dataset_id"]})
    # Metadata may have been saved during source research; receipt marks pre-pipeline acquisition honestly.
    metadata_path = raw / "source_metadata.json"
    meta, _ = fetch_json(url, metadata_path)
    resources = {r["name"]: r for r in meta["result"]["resources"]}
    all_records, evidence = [], []
    for month in pd.date_range(CONFIG["start_month"], CONFIG["end_month"], freq="MS"):
        label = month.strftime("%Y%m")
        resource = resources.get("PCA_" + label)
        if resource is None:
            raise ValueError(f"Requested monthly resource PCA_{label} unavailable")
        offset, expected_fields = 0, None
        while True:
            api_filters = {k: [v] for k, v in CONFIG['filters'].items()}
            params = {"resource_id": resource["id"], "filters": json.dumps(api_filters),
                      "limit": CONFIG["page_size"], "offset": offset}
            query = CONFIG["api_base"] + "datastore_search?" + urllib.parse.urlencode(params)
            filter_hash = hashlib.sha256(json.dumps(api_filters, sort_keys=True).encode()).hexdigest()[:10]
            path = raw / f"pca_{label}_{filter_hash}_{offset:06d}.json"
            result, downloaded = fetch_json(query, path)
            fields = [f["id"] for f in result["result"]["fields"]]
            if expected_fields and fields != expected_fields:
                raise ValueError("Schema changed between pages")
            expected_fields = fields
            rows = result["result"]["records"]
            if rows and any(str(r.get("YEAR_MONTH")) != label for r in rows):
                raise ValueError("API returned records outside the requested month")
            if rows and any(str(r.get(k)) != str(v) for r in rows for k, v in CONFIG["filters"].items()):
                raise ValueError("API did not honor filters")
            receipt_path = path.with_suffix(".receipt.json")
            receipt = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.exists() else {}
            if receipt and receipt["sha256"] != sha256(path):
                raise ValueError(f"Raw acquisition checksum mismatch: {path.name}")
            evidence.append({"file": str(path.relative_to(root)), "url": query, "resource_id": resource["id"],
                             "rows": len(rows), "offset": offset, "sha256": sha256(path),
                             "source_fields": fields,
                             "downloaded_at_utc": receipt.get("downloaded_at_utc"),
                             "api_total_unfiltered": result["result"].get("total")})
            all_records.extend(rows)
            if len(rows) < CONFIG["page_size"]:
                break
            offset += len(rows)
        if not any(str(r["YEAR_MONTH"]) == label for r in all_records):
            raise ValueError(f"No matching records for {label}; not treating a failed filter as zero demand")
        print(f"Acquired {label}: {sum(e['rows'] for e in evidence if label in e['file'])} rows", flush=True)
    return pd.DataFrame(all_records).astype("string"), evidence, metadata_path

def normalize(raw, observed=True):
    check_columns(raw)
    df = raw.copy().replace(r'^\s*$', pd.NA, regex=True)
    dates = df["YEAR_MONTH"].astype("string").str.replace(r"\.0$", "", regex=True)
    df["month"] = pd.to_datetime(dates, format="%Y%m", errors="coerce")
    rename = {"BNF_PRESENTATION_CODE": "product_code", "BNF_PRESENTATION_NAME": "product_name",
              "REGION_CODE": "region_code", "REGION_NAME": "region_name", "UNIT_OF_MEASURE": "unit_of_measure",
              "BNF_CHEMICAL_SUBSTANCE_CODE": "chemical_code", "BNF_CHEMICAL_SUBSTANCE": "chemical_name", **METRICS}
    df = df.rename(columns=rename)
    for source, target in METRICS.items():
        source_values = df[target].astype("string")
        df[target] = pd.to_numeric(source_values, errors="coerce").astype("float64")
        df[f"invalid_{target}"] = source_values.notna() & df[target].isna()
    df["data_origin"] = "observed_nhsbsa" if observed else "synthetic_demo"
    return df

def aggregate(df):
    # Mixed units must never be added together; name/code mappings are audited first.
    names = ["product_name", "region_name", "chemical_code", "chemical_name", "data_origin"]
    grouped = df.groupby(KEY, dropna=False, sort=True)
    metrics = grouped[list(METRICS.values())].agg(lambda s: s.sum(min_count=len(s)))
    labels = grouped[names].first()
    counts = grouped.size().rename("source_row_count")
    return metrics.join(labels).join(counts).reset_index()

def synthetic_source():
    # Explicit fallback only: no public-data claims; independent of real values.
    rng = np.random.default_rng(CONFIG["synthetic_seed"])
    rows = []
    for i, month in enumerate(pd.date_range(CONFIG["start_month"], CONFIG["end_month"], freq="MS")):
        for product in range(3):
            for region in range(3):
                items = int(rng.poisson(500 + 80 * product + 40 * region + i * 3))
                rows.append({"YEAR_MONTH": month.strftime("%Y%m"), "REGION_CODE": f"SYN_R{region}",
                    "REGION_NAME": f"Synthetic region {region}", "BNF_PRESENTATION_CODE": f"SYN_P{product}",
                    "BNF_PRESENTATION_NAME": f"Synthetic product {product}", "BNF_CHEMICAL_SUBSTANCE_CODE": "SYN_C",
                    "BNF_CHEMICAL_SUBSTANCE": "Synthetic chemical", "UNIT_OF_MEASURE": "tablet",
                    "ITEMS": items, "TOTAL_QUANTITY": items * 28, "NIC": round(items * (2 + product), 2)})
    return pd.DataFrame(rows).astype("string")

def ingest(root=ROOT, synthetic=False):
    prepare_dirs(root)
    if synthetic:
        raw = synthetic_source()
        path = root / "data/synthetic/fallback_source.csv"
        raw.to_csv(path, index=False)
        evidence, metadata_path = [{"file": str(path.relative_to(root)), "sha256": sha256(path), "rows": len(raw)}], None
    else:
        raw, evidence, metadata_path = acquire(root)
    detailed = normalize(raw, observed=not synthetic)
    monthly = aggregate(detailed)
    detailed.to_parquet(root / "data/processed/source_rows.parquet", index=False)
    monthly.to_parquet(root / "data/processed/monthly_prescribing.parquet", index=False)
    monthly.to_csv(root / "data/processed/monthly_prescribing.csv", index=False)
    manifest = {"pipeline_run_at_utc": utc_now(), "dataset": CONFIG, "mode": "synthetic" if synthetic else "observed",
                "raw_rows": len(raw), "processed_rows": len(monthly), "source_columns": list(raw.columns),
                "raw_candidate_key": [c for c in raw.columns if c not in METRICS],
                "processed_business_key": KEY, "files": evidence,
                "source_metadata_sha256": sha256(metadata_path) if metadata_path else None,
                "metadata_download_time": "Research stage; exact time not recorded" if metadata_path and not metadata_path.with_suffix('.receipt.json').exists() else "See receipt",
                "processed_sha256": sha256(root / "data/processed/monthly_prescribing.csv")}
    write_json(root / "data/processed/acquisition_manifest.json", manifest)
    return detailed, monthly, manifest

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--synthetic", action="store_true", help="Explicit synthetic fallback; never automatic")
    args = parser.parse_args()
    detailed, monthly, manifest = ingest(synthetic=args.synthetic)
    print(f"{manifest['mode']}: {len(detailed)} source rows -> {len(monthly)} monthly rows")
