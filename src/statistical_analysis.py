"""Phase 3 calendar-aware descriptive statistics. Never aggregate native quantity."""
import numpy as np
import pandas as pd

METRICS = ['prescription_items', 'net_ingredient_cost_gbp', 'ingredient_cost_per_item_gbp']

def safe_ratio(numerator, denominator):
    n, d = np.broadcast_arrays(np.asarray(numerator, dtype=float), np.asarray(denominator, dtype=float))
    return np.divide(n, d, out=np.full(n.shape, np.nan), where=np.isfinite(d) & (d != 0))

def calendar_series(frame, metric, calendar=None):
    f = frame.copy()
    f['month'] = pd.to_datetime(f.month)
    if f.month.duplicated().any():
        raise ValueError('One observation per calendar month required')
    s = f.set_index('month')[metric].sort_index().astype(float)
    if calendar is None:
        calendar = pd.date_range(s.index.min(), s.index.max(), freq='MS')
    return s.reindex(calendar)

def growth(series, lag=1):
    baseline = series.shift(lag)
    return 100 * (series - baseline) / baseline.where(baseline != 0)

def describe_series(series):
    s = series.dropna().astype(float)
    if s.empty:
        return {**{k:np.nan for k in ['mean','median','standard_deviation','minimum','maximum','q1','q3','coefficient_of_variation']},
                'observed_months':0,'missing_months':len(series),'coverage_pct':0. if len(series) else np.nan}
    mean = s.mean()
    return {'mean': mean, 'median': s.median(), 'standard_deviation': s.std(ddof=1),
            'minimum': s.min(), 'maximum': s.max(), 'q1': s.quantile(.25), 'q3': s.quantile(.75),
            'coefficient_of_variation': s.std(ddof=1)/mean if mean > 0 else np.nan,
            'observed_months': len(s), 'missing_months': len(series)-len(s),
            'coverage_pct': 100*len(s)/len(series) if len(series) else np.nan}

def summaries(populations, calendar):
    rows, rates = [], []
    for level, (frame, keys) in populations.items():
        groups = frame.groupby(keys, sort=True, dropna=False) if keys else [('England', frame)]
        for key, f in groups:
            key = key if isinstance(key, tuple) else (key,)
            identity = dict(zip(keys, key)) if keys else {}
            for metric in METRICS:
                s = calendar_series(f, metric, calendar)
                rows.append({'level': level, **identity, 'metric': metric, **describe_series(s)})
                for lag, name in [(1, 'MoM'), (12, 'YoY')]:
                    g = growth(s, lag)
                    rates.append({'level': level, **identity, 'metric': metric, 'comparison': name,
                                  **describe_series(g)})
    return pd.DataFrame(rows), pd.DataFrame(rates)

def regional_comparisons(regional):
    """Matched calendar contrasts are descriptive, not independent regional samples."""
    import itertools
    rows=[]
    for metric in METRICS:
        matrix=regional.pivot(index='month',columns='region_name',values=metric).sort_index()
        if metric != 'ingredient_cost_per_item_gbp':
            matrix=matrix.div(matrix.iloc[0]).mul(100)
        for a,b in itertools.combinations(matrix.columns,2):
            paired=matrix[[a,b]].dropna()
            d=paired[a]-paired[b]
            rows.append({'region_a':a,'region_b':b,'metric':metric,'paired_months':len(d),
                         'mean_paired_difference':d.mean(),'median_paired_difference':d.median(),
                         'minimum_difference':d.min(),'maximum_difference':d.max(),
                         'unit':'GBP/item' if metric==METRICS[2] else 'January 2023=100 index points',
                         'interpretation':'Descriptive matched months; no population adjustment or sampling inference'})
    return pd.DataFrame(rows)
