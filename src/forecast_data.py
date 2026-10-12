"""Read-only provenance controls and training-window-only eligibility."""
import json
import pandas as pd
from .common import ROOT,sha256
from .phase3_pipeline import load_inputs,protected_snapshot as previous_snapshot

def protected_snapshot(root=ROOT):
    # The previous phase scans all newer Markdown files. Phase 4 reports are
    # current outputs, not prior artifacts; retain every existing prior hash.
    inventory={k:v for k,v in previous_snapshot(root).items()
               if not k.startswith('docs/PHASE4_')}
    paths=[]
    for directory,pattern in [('outputs/phase3/tables','*'),('outputs/phase3/charts','*'),('outputs/phase3/validation','*.json'),
                              ('docs','PHASE3*.md'),('notebooks','0[123]*.ipynb')]:
        paths += [p for p in (root/directory).glob(pattern) if p.is_file()]
    paths+=[root/'docs/FORECASTING_READINESS.md']
    inventory.update({str(p.relative_to(root)).replace('\\','/'):sha256(p) for p in paths})
    return dict(sorted(inventory.items()))

def prepare_series(populations, inventory, cfg):
    calendar=pd.DatetimeIndex(populations['national'][0].month.sort_values()).as_unit('ns')
    initial_cutoff=calendar[cfg['initial_training_months']-1]
    series={}; records=[]
    known=set(zip(inventory.region_code,inventory.presentation_key))
    for level in ['national','regional','region_presentation']:
        frame,keys=populations[level]
        groups=frame.groupby(keys,sort=True) if keys else [('England',frame)]
        for key,f in groups:
            key=key if isinstance(key,tuple) else (key,)
            identity=dict(zip(keys,key)) if keys else {}
            sid='England' if level=='national' else identity['region_code'] if level=='regional' else identity['region_code']+'::'+identity['presentation_key']
            s=f.set_index('month').prescription_items.sort_index().reindex(calendar).astype(float)
            training=s.loc[:initial_cutoff]
            count=int(training.notna().sum()); volume=float(training.sum(min_count=1)) if count else 0.
            complete=training.notna().all() and len(training)>=cfg['initial_training_months']
            eligible=bool(complete and (level!='region_presentation' or volume>=cfg['minimum_training_total_items']))
            row={'series_id':sid,'aggregation_level':level,**identity,'target':cfg['primary_target'],
                 'eligibility_cutoff':initial_cutoff,'initial_training_observations':count,'initial_training_items':volume,
                 'initial_training_coverage_pct':100*count/len(training),'eligible':eligible,
                 'phase2_full_history_candidate':level=='region_presentation' and (identity['region_code'],identity['presentation_key']) in known,
                 'reason':'Eligible: complete initial history and training-only volume screen' if eligible else 'Incomplete initial calendar history' if not complete else 'Training-only item volume below threshold',
                 'full_history_missing_months_descriptive_only':int(s.isna().sum())}
            records.append(row)
            if eligible:
                series[sid]={'values':s,'metadata':row}
    return series,pd.DataFrame(records),calendar

def load_forecasting_data(cfg,root=ROOT):
    loaded,populations,calendar,evidence=load_inputs(root)
    audit=json.loads((root/'outputs/phase3/validation/final_audit.json').read_text(encoding='utf-8'))
    if not audit['passed']: raise ValueError('Phase 3 prerequisites failed')
    for stem,item in audit['tables'].items():
        for suffix in ['csv','parquet']:
            if sha256(root/f'outputs/phase3/tables/{stem}.{suffix}')!=item[f'{suffix}_sha256']:
                raise AssertionError(f'Phase 3 table changed: {stem}.{suffix}')
    series,eligibility,calendar=prepare_series(populations,loaded['forecast_candidate_series'],cfg)
    return series,eligibility,populations,loaded,evidence
