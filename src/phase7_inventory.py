"""Capture an immutable analytical baseline before portfolio edits."""
import importlib.util
import json
import os
import platform
import subprocess
from pathlib import Path
from .common import ROOT,sha256,write_json
from .phase6_audit import protected_snapshot as phase6_protected

SKIP={'.venv','.git','__pycache__','.pytest_cache','node_modules','.ipynb_checkpoints'}

def files(root=ROOT):
    errors=[]; found=[]
    for directory,dirs,names in os.walk(root,onerror=lambda exc:errors.append(str(exc.filename))):
        dirs[:]=[d for d in dirs if d not in SKIP and 'tmp' not in d.lower() and not d.startswith('pytest-cache-files') and d!='clean_environment']
        for name in names:
            p=Path(directory)/name
            if p.is_file(): found.append(p)
    return sorted(found),errors

def snapshot(root=ROOT):
    protected=phase6_protected(root)
    for folder in ['data','outputs','notebooks','config','sql','docs']:
        paths,_=files(root/folder)
        for p in paths:
            rel=p.relative_to(root).as_posix()
            if rel.startswith('outputs/phase7/') or p.name.startswith('PHASE7_'): continue
            if folder=='docs' and not (p.name.startswith('PHASE') and not p.name.startswith('PHASE7_')): continue
            protected[rel]=sha256(p)
    return dict(sorted(protected.items()))

def baseline(root=ROOT):
    out=root/'outputs/phase7/validation'; out.mkdir(parents=True,exist_ok=True)
    guard=out/'protected_manifest.json'
    if guard.exists():
        old=json.loads(guard.read_text()); current={p:sha256(root/p) if (root/p).is_file() else None for p in old}
        if old!=current: raise AssertionError('Phase 7 protected baseline differs; do not overwrite it')
        return old
    protected=snapshot(root); write_json(guard,protected)
    paths,errors=files(root)
    inventory=[{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':sha256(p)} for p in paths]
    write_json(out/'baseline_inventory.json',{'files':inventory,'excluded_unreadable_paths_count':len(errors),
        'bytes_excluding_environment_and_caches':sum(p['bytes'] for p in inventory),
        'data_bytes':sum(p['bytes'] for p in inventory if p['path'].startswith('data/')),
        'generated_artifact_count':sum(p['path'].startswith('outputs/') for p in inventory)})
    git={}
    for label,arguments in [('status',['status','--porcelain']),('branch',['branch','--show-current']),('remotes',['remote','-v']),('tracked',['ls-files'])]:
        run=subprocess.run(['git',*arguments],cwd=root,capture_output=True,text=True)
        git[label]={'exit_code':run.returncode,'output':run.stdout.strip(),'reason':'Not a Git repository' if run.returncode else ''}
    write_json(out/'baseline_git.json',git)
    write_json(out/'environment.json',{'python':platform.python_version(),'platform':platform.system(),
        'packages':{name:importlib.util.find_spec(name) is not None for name in ['pptx','ruff','playwright','selenium','yaml']},
        'browser_tool_available':False,'remote_workflow_executed':False})
    (out/'README_before_phase7.md').write_bytes((root/'README.md').read_bytes())
    inspected=[]; notebooks=[]
    for p in paths:
        rel=p.relative_to(root).as_posix()
        if p.suffix in {'.py','.sql','.md','.yaml','.toml','.ini'} or p.name in {'requirements.txt','.gitignore'}:
            content=p.read_text(encoding='utf-8',errors='replace')
            inspected.append({'path':rel,'lines':len(content.splitlines()),'sha256':sha256(p)})
        if p.suffix=='.ipynb':
            n=json.loads(p.read_text(encoding='utf-8')); cells=[c for c in n['cells'] if c['cell_type']=='code']
            notebooks.append({'path':rel,'code_cells':len(cells),'unexecuted':sum(c.get('execution_count') is None for c in cells),
                'error_outputs':sum(o.get('output_type')=='error' for c in cells for o in c.get('outputs',[]))})
    write_json(out/'discovery.json',{'read_text_inventory':inspected,'notebooks':notebooks,
        'pyproject_present':(root/'pyproject.toml').is_file(),'protected_count':len(protected)})
    print(json.dumps({'protected':len(protected),'files':len(inventory),'bytes':sum(p['bytes'] for p in inventory),'git_repository':git['status']['exit_code']==0}),flush=True)
    return protected

if __name__=='__main__': baseline()
