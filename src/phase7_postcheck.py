"""Verify final sanitized release copies and heading links after full regression."""
import ast
import json
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from hashlib import sha256
from .common import ROOT,write_json
from .phase7_audit import documents
from .phase7_review import enrich
from .phase7_quality import links,protection,security
from .phase7_release import build

def check(root=ROOT):
    out=root/'outputs/phase7/validation'; result=json.loads((out/'final_audit.json').read_text())
    assert result['tests']['exit_code']==0
    result['protection']=protection(root)
    authorized={'.gitignore','app.py','dashboard/chart_factory.py','dashboard/components.py','dashboard/pages/forecasting.py','dashboard/scenarios.py','README.md','src/phase3_pipeline.py','src/phase7_inventory.py'}
    unexpected=set(result['protection']['authorized_modified_files'])-authorized
    result['protection']['unexpected_modifications']=sorted(unexpected)
    assert result['protection']['passed'] and not unexpected
    static=subprocess.run([sys.executable,'-m','ruff','check','app.py','dashboard','src','tests','--select','E9,F63,F7,F82','--output-format','json'],cwd=root,capture_output=True,text=True)
    assert static.returncode==0,static.stdout
    (out/'fatal_static.json').write_text(static.stdout,encoding='utf-8')
    assert security(root)['credential_candidates']==0
    suites=ET.parse(out/'ci_tests.xml').getroot().findall('testsuite')
    ci={'tests':sum(int(s.get('tests',0)) for s in suites),'failed':sum(int(s.get('failures',0))+int(s.get('errors',0)) for s in suites),'environment':'fresh dashboard venv','remote_executed':False}
    assert ci['tests']==6 and ci['failed']==0; result['ci_local']=ci
    documents(result,root); enrich(root,result)
    result['document_links']=links(root); assert not result['document_links']['broken'],result['document_links']['broken']
    write_json(out/'final_audit.json',result)
    release=build(root); modules=0; notebooks=0
    with zipfile.ZipFile(root/release['archive']) as z:
        assert z.testzip() is None
        for entry in release['entries']:
            data=z.read('PharmaLens/'+entry['path']); assert sha256(data).hexdigest()==entry['sha256']
            if entry['path'].endswith('.py'): ast.parse(data.decode('utf-8')); modules+=1
            if entry['path'].endswith('.ipynb'):
                nb=json.loads(data); notebooks+=1
                assert all(not c.get('outputs') and c.get('execution_count') is None for c in nb['cells'] if c['cell_type']=='code')
    final={'passed':True,'archive_entries':len(release['entries']),'archive_bytes':release['bytes'],'sanitized_python_modules_parsed':modules,'notebook_copies_with_outputs_cleared':notebooks,
        'relative_links_and_heading_anchors_checked':result['document_links']['checked'],'unexpected_modifications':sorted(unexpected),'zip_integrity':True,'entry_hashes':True,'static_passed':True,'ci':ci}
    write_json(out/'postchecks.json',final); print(json.dumps(final),flush=True)
    return final

if __name__=='__main__': check()
