import json
import pandas as pd
from src.common import ROOT
from src.decision_validation import validate

def test_independent_reconciliation_and_tamper_detection(phase5_tables,phase5_inputs,phase5_cfg):
    summary=json.loads((ROOT/'outputs/phase5/validation/pipeline_summary.json').read_text())
    contracts={name:item['business_key'] for name,item in summary['exports'].items()}
    checks,passed=validate(phase5_tables,phase5_inputs,phase5_cfg,contracts)
    assert passed and checks.status.eq('passed').all()
    altered={k:v.copy() for k,v in phase5_tables.items()}
    altered['scenario_results'].loc[0,'hypothetical_nic_gbp']+=1000
    checks,passed=validate(altered,phase5_inputs,phase5_cfg,contracts)
    assert not passed and checks.status.eq('failed').any()

def test_dashboard_keys_and_schema_dictionary(phase5_tables):
    d=phase5_tables['dashboard_data_dictionary']
    for name,f in phase5_tables.items():
        if name.endswith('_dashboard') or name=='executive_kpi_summary':
            entries=d[d.output_table.eq(name)]; assert set(entries.field)==set(f.columns)
            keys=entries.business_key.iloc[0].split(';'); assert not f.duplicated(keys).any()

def test_reconciliation_evidence_has_required_fields():
    f=pd.read_csv(ROOT/'outputs/phase5/validation/decision_reconciliation.csv')
    assert set(['check_name','expected','observed','difference','tolerance','status'])<=set(f.columns)
    assert f.status.eq('passed').all()
