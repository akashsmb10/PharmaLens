"""One configuration source. JSON syntax is a valid YAML subset; no new parser required."""
import json
from .common import ROOT

def configuration(root=ROOT):
    cfg=json.loads((root/'config/forecasting.yaml').read_text(encoding='utf-8'))
    if cfg['forecast_horizons']!=[1,2,3] or cfg['initial_training_months']<24:
        raise ValueError('This short-history benchmark requires horizons 1/2/3 and >=24 training months')
    return cfg
