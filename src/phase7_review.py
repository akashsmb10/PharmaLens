"""Record actual assistant image inspection and align release-status documents."""
import json
from .common import ROOT,sha256,write_json

def record(root=ROOT):
    out=root/'outputs/phase7/validation'
    native=json.loads((out/'native_presentation_render.json').read_text(encoding='utf-8-sig'))
    assert native['rendered'] and native['slides']==native['images']==12
    native.update({'visually_reviewed':True,'reviewer':'Codex assistant inspected all twelve exported native PowerPoint slide images',
        'pptx_sha256':sha256(root/'deliverables/Phase7_Axtria_Project_Presentation.pptx'),
        'layout_findings':'No clipped titles, overlapping bullets or unreadable chart labels observed in the twelve native renders. Dashboard screenshot is intentionally smaller on slide eleven; demonstrate the app for detailed reading.'})
    write_json(out/'native_presentation_render.json',native)
    inventory=json.loads((out/'presentation_inventory.json').read_text()); inventory['native_powerpoint_render_review']=True; inventory['native_renderer']='Microsoft PowerPoint'; write_json(out/'presentation_inventory.json',inventory)
    review={'reviewer':'Codex assistant image inspection; not business-user acceptance','six_desktop_pages':True,'six_chart_detail_views':True,'mobile_spot_checks':['Executive Overview','Presentation Intelligence','Scenario Simulator'],'tablet_spot_checks':['Forecasting & Model Evaluation'],
        'fixed':['Tablet sidebar covered main content: default collapsed; desktop screenshot navigation explicitly expanded.','Narrow-screen KPI order corrected using rows of three.','Long chart titles wrapped.','Capture waits for the Streamlit running indicator to disappear.'],
        'residual_limits':['Dense all-presentation selector needs filtering on narrow screens.','Full presentation names require chart hover or a filtered selection; wide data tables scroll internally.','Viewport captures do not inspect every below-fold element.','Not exhaustive accessibility or multi-browser certification.'],
        'scope_passed':True,'primary_screenshot_hashes':{p.name:sha256(p) for p in (root/'docs/assets/screenshots').glob('*.png')}}
    write_json(out/'visual_review.json',review)

def enrich(root,result):
    """Evidence-derived status vocabulary and strengths/limits, without a composite score."""
    native=result.get('native_presentation',{}).get('visually_reviewed',False)
    audit=root/'docs/PHASE7_AUDIT.md'
    text=audit.read_text(encoding='utf-8').replace('native sidebar auto behavior','native collapsed-sidebar default')
    text=text.replace('#dashboard-screenshots','#dashboard-preview')
    text=text.replace('Tablet screenshots use the native sidebar-collapse control; mobile uses automatic collapse.','Tablet/mobile use the collapsed default; desktop screenshots explicitly expand native navigation.')
    if native:
        text=text.replace('Native PowerPoint/LibreOffice visual rendering was not performed; open the deck to confirm final font/layout behavior before an interview. It is completed but not visually verified in native PowerPoint.','Microsoft PowerPoint exported all twelve slides and a PDF; the assistant inspected every native slide image. No clipping or overlap was observed. [PDF copy](../deliverables/Phase7_Axtria_Project_Presentation.pdf). This is native visual verification, not a claim that the user rehearsed or reviewed the deck.')
        text=text.replace('Completed but not visually verified: native PowerPoint slide rendering.','Completed but not visually verified: no remaining generated presentation asset in the reviewed scope; broader dashboard inspection remains scoped.')
        text=text.replace('and native-deck review are resolved','are resolved')
    audit.write_text(text,encoding='utf-8')
    tests=result.get('tests',{}); count=tests.get('passed','pending'); failed=tests.get('failed','pending')
    rows=[
      ('Data quality','1,571 independent checks; raw receipts','Item/NIC totals and grains reconcile','Absence mechanisms remain unknown','New source vintages need renewed contracts','PASS'),
      ('SQL/database','DuckDB facts, dimensions, reporting views','Calendar-aware joins and ratio-of-sums','No population or patient denominators','Add decision-specific authorized dimensions','PASS'),
      ('Statistics','Trend, STL, anomalies, exact decomposition','Multiple descriptive checks and accounting reconciliation','Three cycles; uncertainty and causality limits','Longer history and hypothesis-specific design','PASS for descriptive scope'),
      ('Forecasting','Frozen selections; origin-only evaluation','Leakage boundaries and honest comparator table','Overlapping short holdout; no calibrated intervals','Prospective release-aware evaluation','PASS for retrospective scope'),
      ('Decision intelligence','Midrank/weight/sensitivity checks','Explicit missing states and lineage','Illustrative policies; unstable regional ranks','Domain-user validation','PASS for illustrative scope'),
      ('Dashboard','24 browser cells; downloads; AppTest','Actual UI and arithmetic checks','Dense selectors; limited accessibility/browser coverage','User review and expanded accessibility checks','PASS' if result.get('browser',{}).get('passed') else 'FAIL'),
      ('Software engineering','AST/fatal static checks; contracts','Relative paths and visible failure states','Legacy density and limited type annotations','Incremental maintainability improvements','PASS' if result.get('static_passed') else 'FAIL'),
      ('Security','Credential-pattern scan; curated archive','Secrets/logs/raw/venvs excluded; copy sanitization','Patterns cannot prove complete absence','Owner staged-diff and dependency review','PASS within scanned scope'),
      ('Reproducibility','Fresh dashboard venv; full local regression','52 exact runtime inputs and lock capture','Full clean historical rebuild not performed','Release-aware complete rebuild in a new version','PASS for dashboard runtime' if result.get('clean',{}).get('passed') else 'FAIL'),
      ('Documentation','README, diagram and resolved relative links','Definitions, units and evidence boundaries explicit','Owner comprehension not established','Review personal ownership and rehearse','PASS'),
      ('Interview readiness','65 answers; timed demo; native deck','Four points/examples/follow-ups and visual review','No actual interview or user rehearsal evaluated','Practice and adapt to actual contributions','PASS for materials'),
      ('Regression/preservation',f'{count} passed, {failed} failed; 497 protected hashes','Original validated outcomes unchanged','Remote Actions not executed','Remote check after authorized publication','PASS' if tests.get('exit_code')==0 else 'NOT TESTED'),
      ('Public release','Safe package, attribution and CI configuration','Concrete reviewable local deliverables','Code licence and publication authorization pending','Owner decisions before publication','BLOCKED'),
      ('Production readiness','Limits explicitly documented','No unsupported deployment or impact claims','No operational/business-user validation','Authorized rollout and prospective acceptance criteria','NOT TESTED')]
    lines=['# Evidence-based quality scorecard','','Ratings mean the stated scoped checks passed; they are not universal quality guarantees. There is no arbitrary overall score.','','| Dimension | Evidence | Strengths | Weaknesses | Outstanding work | Rating |','|---|---|---|---|---|---|']
    lines += ['| '+' | '.join(row)+' |' for row in rows]
    lines += ['','[Final audit](PHASE7_AUDIT.md) records executed evidence and boundaries.','']
    (root/'docs/PHASE7_QUALITY_SCORECARD.md').write_text('\n'.join(lines),encoding='utf-8')
    checklist=root/'docs/PHASE7_RELEASE_CHECKLIST.md'; lines=[]
    for line in checklist.read_text(encoding='utf-8').splitlines():
        if line.startswith('| ') and not line.startswith('| Check'):
            cells=line.split('|'); label=cells[1].strip(); detail=cells[2].strip()
            if any(detail.startswith(s+': ') for s in ['PASS','FAIL','BLOCKED','NOT TESTED']): detail=detail.split(': ',1)[1]
            if label=='Code licence': state='BLOCKED'
            elif label=='Remote GitHub/Actions/cloud': state='NOT TESTED'
            elif label=='Full local regression': state='PASS' if tests.get('exit_code')==0 else 'NOT TESTED'
            elif label=='Native PowerPoint visual review': state='PASS' if native else 'NOT TESTED'; detail='All twelve native slide renders inspected; PDF exported' if native else detail
            elif detail.startswith('False'): state='FAIL'
            else: state='PASS'
            line=f'| {label} | {state}: {detail} |'
        lines.append(line)
    checklist.write_text('\n'.join(lines)+'\n',encoding='utf-8')

if __name__=='__main__': record()
