from dashboard.chart_factory import forecast_points,heatmap
from dashboard.data_loader import load
from dashboard.metrics import monthly
import pandas as pd

def test_origin_points_have_no_false_lines_or_bands():
    f=load('p4/backtest_predictions'); f=f[f.series_id.eq('England')&f.split_type.eq('holdout')]
    fig=forecast_points(monthly(load('p2/cost_analytics')),f,'test')
    assert all(t.mode=='markers' and t.fill is None for t in fig.data[1:])
    assert all('Origin' in t.hovertemplate and len(t.customdata)==len(t.x) for t in fig.data[1:])

def test_heatmap_retains_unknown_cells():
    fig=heatmap(pd.DataFrame([[1.,float('nan')]]),'coverage','%')
    assert pd.isna(fig.data[0].z[0][1])
