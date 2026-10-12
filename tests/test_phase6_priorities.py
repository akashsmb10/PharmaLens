from dashboard.data_loader import load

def test_missing_forecast_preserved_unscored():
    f=load('p5/priority_dashboard'); p=f[f.aggregation_level.eq('presentation')]
    unscored=p[~p.rank_eligible]
    assert len(unscored)==13 and unscored.composite_score.isna().all() and unscored['rank'].isna().all()

def test_recommendation_source_traceability():
    recommendations=load('p5/recommendations_dashboard')
    for r in recommendations.itertuples():
        source=load('p5/'+r.source_output)
        assert source[r.source_key].astype(str).eq(r.source_key_value).any(),r.recommendation_id
