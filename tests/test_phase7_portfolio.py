"""Cross-artifact and isolation checks for the reviewable portfolio release."""
import json
import subprocess
import zipfile
import xml.etree.ElementTree as ET
from hashlib import sha256
import pandas as pd
import pytest
from src.common import ROOT

OUT=ROOT/'outputs/phase7/validation'

def read(name): return json.loads((OUT/name).read_text())

def test_independent_checks_all_pass_and_artifact_hash_matches():
    detail=OUT/'numerical_reconciliation.csv'; frame=pd.read_csv(detail); summary=read('numerical_summary.json')
    assert len(frame)==summary['checks']==1571 and frame.status.eq('PASS').all()
    assert sha256(detail.read_bytes()).hexdigest()==summary['sha256']
    assert {'expected','recomputed','difference','tolerance','source'}<=set(frame)

def test_original_analytical_artifacts_unchanged():
    protected=read('protected_manifest.json')
    assert len(protected)==497
    for rel,expected in protected.items(): assert sha256((ROOT/rel).read_bytes()).hexdigest()==expected,rel

def test_documentation_relative_links_resolve():
    from src.phase7_quality import links
    result=links(); assert result['checked']>30 and not result['broken'],result['broken']

def test_interview_bank_categories_depth_and_structure():
    from src.phase7_interview import QA,build
    result=build()
    assert result['questions']==65 and sorted(result['categories'].values())==[5,5,5,6,8,8,8,8,12]
    assert len({row[1] for row in QA})==65
    assert min(result['answer_word_counts'])>=105
    assert all(len(row[2])==4 and all(row[3:]) for row in QA)

def test_interval_defense_uses_development_not_holdout_calibration():
    text=(ROOT/'docs/PHASE7_INTERVIEW_QA.md').read_text(encoding='utf-8')
    assert 'Development calibration provides' in text and 'holdout is never used to calibrate' in text
    assert 'The holdout provides only six, five and four cells' not in text

def test_architecture_mermaid_and_svg_have_same_ten_stages():
    flow=read('architecture_flow.json'); mermaid=(ROOT/'docs/assets/architecture.mmd').read_text()
    svg=ET.parse(ROOT/'docs/assets/architecture.svg'); rendered=' '.join(svg.getroot().itertext())
    assert len(flow['nodes'])==10 and len(flow['edges'])==9
    for node,label,_ in flow['nodes']: assert f'{node}["{label}"]' in mermaid and label in rendered
    for a,b in flow['edges']: assert f'{a} --> {b}' in mermaid

def test_presentation_is_real_twelve_slide_file_with_notes_and_media():
    with zipfile.ZipFile(ROOT/'deliverables/Phase7_Axtria_Project_Presentation.pptx') as z:
        slides=[n for n in z.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml')]
        notes=[n for n in z.namelist() if n.startswith('ppt/notesSlides/notesSlide') and n.endswith('.xml')]
        assert len(slides)==len(notes)==12
        assert len([n for n in z.namelist() if n.startswith('ppt/media/')])>=6
        for n in slides+notes: ET.fromstring(z.read(n))
        content=' '.join(z.read(n).decode('utf-8') for n in slides+notes)
        assert 'Ridge' in content and 'retrospective' in content and 'AI-assisted' in content

def test_native_presentation_review_matches_current_deck_and_pdf():
    review=read('native_presentation_render.json')
    assert review['visually_reviewed'] and review['slides']==review['images']==12
    assert review['pptx_sha256']==sha256((ROOT/'deliverables/Phase7_Axtria_Project_Presentation.pptx').read_bytes()).hexdigest()
    assert (ROOT/'deliverables/Phase7_Axtria_Project_Presentation.pdf').read_bytes().startswith(b'%PDF-')

@pytest.mark.parametrize('name',['01_executive_overview','02_regional_intelligence','03_presentation_intelligence','04_forecasting','05_decision_intelligence','06_scenario_simulator'])
def test_primary_screenshots_are_real_browser_artifacts(name):
    from PIL import Image
    p=ROOT/f'docs/assets/screenshots/{name}.png'
    with Image.open(p) as image: assert image.size==(1440,1000) and image.format=='PNG'
    evidence=read('browser_qa.json')
    assert evidence['passed'] and len(evidence['page_viewport_checks'])==24
    assert evidence['downloads'][0]['item_sum_matches'] and all(evidence['interactions'].values())

def test_browser_download_matches_actual_filtered_year():
    export=pd.read_csv(OUT/'browser_regional_2024.csv')
    fact=pd.read_parquet(ROOT/'outputs/tables/cost_analytics.parquet')
    selected=fact[fact.month.dt.year.eq(2024)]
    assert len(export)==7 and export.prescription_items.sum()==selected.prescription_items.sum()
    assert abs(export.net_ingredient_cost_gbp.sum()-selected.net_ingredient_cost_gbp.sum())<.01

def test_clean_runtime_package_has_identical_current_sources_and_inputs():
    assert read('clean_environment.json')['passed']
    isolated=ROOT/'outputs/phase7/clean_environment/project'
    manifest=json.loads((ROOT/'config/dashboard_manifest.json').read_text())
    assert len(manifest['datasets'])==52
    for rel in ['app.py','dashboard/scenarios.py','dashboard/components.py',*[v['path'] for v in manifest['datasets'].values()]]:
        assert (isolated/rel).read_bytes()==(ROOT/rel).read_bytes(),rel
    assert 'include-system-site-packages = false' in (isolated.parent/'venv/pyvenv.cfg').read_text()

def test_release_archive_contains_exact_runtime_and_no_private_directories():
    release=read('release_manifest.json'); manifest=json.loads((ROOT/'config/dashboard_manifest.json').read_text())
    with zipfile.ZipFile(ROOT/release['archive']) as z:
        names=z.namelist(); assert all(not any(s in n for s in ['/.venv/','/data/raw/','/clean_environment/','/secrets.toml','/.env']) for n in names)
        for v in manifest['datasets'].values(): assert z.read('PharmaLens/'+v['path'])==(ROOT/v['path']).read_bytes()
        for entry in release['entries']: assert sha256(z.read('PharmaLens/'+entry['path'])).hexdigest()==entry['sha256']
    assert not release['unsafe_candidates'] and release['runtime_parquet_files']==52

def test_release_sanitizer_does_not_alter_original_notebook():
    from src.phase7_release import sanitized
    nb={'cells':[{'cell_type':'code','execution_count':9,'outputs':[{'text':'private local output'}],'source':['x=1']}],'metadata':{}}
    original=json.dumps(nb).encode(); result=json.loads(sanitized(original,'.ipynb'))
    assert result['cells'][0]['outputs']==[] and result['cells'][0]['execution_count'] is None
    assert json.loads(original)==nb and result['cells'][0]['source']==['x=1']

def test_gitignore_blocks_secrets_and_runtime_junk(tmp_path):
    (tmp_path/'.gitignore').write_bytes((ROOT/'.gitignore').read_bytes())
    subprocess.run(['git','init','--quiet',str(tmp_path)],check=True,capture_output=True)
    candidates=['.env','secrets.toml','.streamlit/secrets.toml','.aws/credentials','.venv/file','__pycache__/cache.pyc','data/raw/private.json','outputs/private.log']
    run=subprocess.run(['git','check-ignore','--',*candidates],cwd=tmp_path,text=True,capture_output=True)
    assert set(run.stdout.splitlines())==set(candidates)

def test_two_scenario_sessions_do_not_share_slider_state():
    from streamlit.testing.v1 import AppTest
    script='from dashboard.pages.scenario_simulator import render\nrender()'
    first=AppTest.from_string(script).run(timeout=45); second=AppTest.from_string(script).run(timeout=45)
    assert not first.exception and not second.exception
    original=second.metric[4].value
    first.slider[0].set_value(5).run(timeout=45)
    assert not first.exception and first.metric[4].value!=original
    second.run(timeout=45)
    assert second.slider[0].value==0 and second.metric[4].value==original

def test_security_and_fatal_static_evidence_are_clean():
    assert read('security_review.json')['credential_candidates']==0
    assert read('fatal_static.json')==[]

def test_ci_is_data_free_and_does_not_imply_remote_execution():
    text=(ROOT/'.github/workflows/tests.yml').read_text()
    assert 'tests/ci -q --confcutdir=tests/ci' in text and 'requirements-dashboard.txt' in text
    assert 'integration:' not in text
    assert 'no remote workflow run is claimed' in (ROOT/'README.md').read_text().lower()
