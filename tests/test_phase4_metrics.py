import numpy as np
import pandas as pd
import pytest
from src.forecast_metrics import metrics,mase_scale

def test_all_metrics_known_errors():
    f=pd.DataFrame({'actual':[10.,20.],'prediction':[12.,16.],'mase_scale':[2.,4.]})
    r=metrics(f)
    assert r['MAE']==3 and r['RMSE']==pytest.approx(np.sqrt(10))
    assert r['WAPE']==20 and r['Bias']==-1 and r['MASE']==1
    assert r['sMAPE']==pytest.approx((200*2/22+200*4/36)/2)

def test_training_mase_scale(): assert mase_scale([1,3,2,5])==2
def test_zero_scale_undefined(): assert np.isnan(mase_scale([5,5,5]))

def test_zero_actual_smape_wape():
    r=metrics(pd.DataFrame({'actual':[0.,0.],'prediction':[0.,0.],'mase_scale':[1.,1.]}))
    assert r['sMAPE']==0 and np.isnan(r['WAPE']) and r['MAE']==0

def test_rmse_from_individual_errors():
    r=metrics(pd.DataFrame({'actual':[0.,0.,0.],'prediction':[1.,2.,10.],'mase_scale':[1.]*3}))
    assert r['RMSE']==pytest.approx(np.sqrt(35))

def test_empty_predictions_undefined():
    r=metrics(pd.DataFrame({'actual':[1.],'prediction':[np.nan],'mase_scale':[1.]}))
    assert r['n']==0 and np.isnan(r['MASE'])
