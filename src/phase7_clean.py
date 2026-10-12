"""Create a separate venv and minimal read-only dashboard checkout."""
import json
import shutil
import subprocess
import sys
import venv
from .common import ROOT,write_json,sha256

def prepare(root=ROOT):
    base=root/'outputs/phase7/clean_environment'; project=base/'project'; project.mkdir(parents=True,exist_ok=True)
    m=json.loads((root/'config/dashboard_manifest.json').read_text())
    paths=['app.py','requirements-dashboard.txt','config/dashboard_manifest.json','config/dataset.json','src/__init__.py','src/common.py','src/forecast_metrics.py','src/scenario_engine.py','src/phase6_startup.py']
    paths += [p.relative_to(root).as_posix() for p in (root/'dashboard').rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    paths += [p.relative_to(root).as_posix() for p in (root/'.streamlit').glob('config.toml')]
    paths += [v['path'] for v in m['datasets'].values()]
    paths += [p.relative_to(root).as_posix() for p in (root/'docs').glob('*.md')]
    hashes={}
    for rel in paths:
        dst=project/rel; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(root/rel,dst); hashes[rel]=sha256(dst)
    env=base/'venv'; venv.EnvBuilder(with_pip=True,clear=False,system_site_packages=False).create(env)
    python=env/('Scripts/python.exe' if sys.platform=='win32' else 'bin/python')
    (project/'test_clean_runtime.py').write_text('''import importlib
import sys
from streamlit.testing.v1 import AppTest
from dashboard.navigation import PAGES
from dashboard.data_loader import load,manifest
from src.phase6_startup import startup

def test_contracts_and_dashboard_pages():
    for name in manifest()['datasets']:
        assert len(load(name))==manifest()['datasets'][name]['rows']
    for name,title in PAGES:
        a=AppTest.from_string('from dashboard.pages.'+name+' import render\\nrender()',default_timeout=60).run()
        assert not a.exception and not a.error and a.header[0].value==title
    a=AppTest.from_file('app.py',default_timeout=60).run()
    assert not a.exception and not a.error and len(a.metric)==7

def test_actual_startup_and_cleanup():
    result=startup()
    assert result['passed'] and result['listener_closed']
''',encoding='utf-8')
    write_json(root/'outputs/phase7/validation/clean_package.json',{'files':hashes,'system_site_packages':False,'dataset_count':len(m['datasets'])})
    print(str(python),flush=True)
    return python,project

def verify(root=ROOT):
    base=root/'outputs/phase7/clean_environment'; project=base/'project'; python=base/'venv'/('Scripts/python.exe' if sys.platform=='win32' else 'bin/python')
    command=[str(python),'-m','pytest','test_clean_runtime.py','-q','-p','no:cacheprovider','--junitxml=../clean_tests.xml','--basetemp=../pytest_tmp']
    run=subprocess.run(command,cwd=project,capture_output=True,text=True,timeout=180)
    out=root/'outputs/phase7/validation'; (out/'clean_execution.log').write_text(run.stdout+run.stderr,encoding='utf-8')
    check=subprocess.run([str(python),'-m','pip','check'],capture_output=True,text=True)
    freeze=subprocess.run([str(python),'-m','pip','freeze'],capture_output=True,text=True)
    (out/'clean_requirements_lock.txt').write_text(freeze.stdout,encoding='utf-8')
    result={'passed':run.returncode==check.returncode==0,'dashboard_only':True,'fresh_venv':True,'system_site_packages':False,
        'separate_checkout':True,'tests_exit_code':run.returncode,'dependency_check':check.stdout.strip(),'full_pipeline_rebuilt':False}
    write_json(out/'clean_environment.json',result); print(run.stdout,flush=True)
    if not result['passed']: raise AssertionError('Clean dashboard environment failed')
    return result

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument('--verify',action='store_true'); args=parser.parse_args()
    verify() if args.verify else prepare()
