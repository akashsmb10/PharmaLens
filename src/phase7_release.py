"""Build a reviewed, relative-path portfolio bundle without changing source evidence."""
import json
import re
import zipfile
from .common import ROOT,write_json,sha256
from .phase7_inventory import files

def sanitized(data,suffix):
    if suffix=='.ipynb':
        nb=json.loads(data)
        for cell in nb.get('cells',[]):
            if cell.get('cell_type')=='code': cell['outputs']=[]; cell['execution_count']=None
        data=json.dumps(nb,ensure_ascii=False,indent=1).encode('utf-8')
    if suffix in {'.md','.json','.py','.txt','.yml','.yaml','.toml','.ipynb','.ini','.mmd','.svg'}:
        text=data.decode('utf-8')
        # Remove machine-specific quoted paths from release copies; analytical originals remain immutable.
        text=re.sub(r'[A-Za-z]:[\\/]+Users[\\/]+[^\s\"\'<>\n]+','<PROJECT_ROOT>',text)
        data=text.encode('utf-8')
    return data

def build(root=ROOT):
    manifest=json.loads((root/'config/dashboard_manifest.json').read_text())
    required={v['path'] for v in manifest['datasets'].values()}
    selected=[]
    roots={'src','dashboard','tests','config','sql','notebooks','docs','.github','.streamlit','scripts'}
    top={'app.py','run_pipeline.py','README.md','CODE_LICENSE_NOTICE.md','.gitignore','requirements.txt','requirements-dashboard.txt','requirements-dashboard-lock.txt','requirements-portfolio.txt'}
    paths,_=files(root)
    for p in paths:
        rel=p.relative_to(root).as_posix()
        if rel in required or rel in top or p.relative_to(root).parts[0] in roots or rel in {'deliverables/Phase7_Axtria_Project_Presentation.pptx','deliverables/Phase7_Axtria_Project_Presentation.pdf'}:
            if p.name in {'secrets.toml','.env'} or any(s in p.name.lower() for s in ['credentials','private_key']): continue
            selected.append((rel,p))
    archive=root/'deliverables/PharmaLens_Phase7_Portfolio.zip'; archive.parent.mkdir(exist_ok=True)
    from hashlib import sha256 as digest
    entries=[]; removed=[]; risky=[]
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for rel,p in selected:
            original=p.read_bytes(); data=sanitized(original,p.suffix)
            if data!=original: removed.append(rel)
            if p.suffix in {'.py','.md','.json','.txt','.yml','.yaml','.toml','.ipynb'}:
                txt=data.decode('utf-8')
                if re.search(r'[A-Za-z]:[\\/]+Users[\\/]+',txt): risky.append(rel)
                if rel!='src/phase7_quality.py' and re.search(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\bAKIA[A-Z0-9]{16}\b|\bgh[pousr]_[A-Za-z0-9]{30,}\b',txt): risky.append(rel)
            info=zipfile.ZipInfo('PharmaLens/'+rel,date_time=(2026,10,12,0,0,0)); info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,data); entries.append({'path':rel,'bytes':len(data),'sha256':digest(data).hexdigest()})
        public=root/'outputs/phase7/validation/public_validation.json'
        if public.exists():
            data=public.read_bytes(); z.writestr('PharmaLens/PORTFOLIO_VALIDATION.json',data)
            entries.append({'path':'PORTFOLIO_VALIDATION.json','bytes':len(data),'sha256':digest(data).hexdigest()})
    result={'archive':archive.relative_to(root).as_posix(),'entries':entries,'runtime_parquet_files':len(required),'sanitized_copies':removed,'unsafe_candidates':sorted(set(risky)),
        'raw_data_excluded':True,'virtualenvs_excluded':True,'private_local_audit_logs_excluded':True,'originals_modified':False,'archive_sha256':sha256(archive),'bytes':archive.stat().st_size}
    write_json(root/'outputs/phase7/validation/release_manifest.json',result)
    if risky: raise AssertionError('Release review found unsafe candidates; inspect redacted file list')
    print(f'Release bundle: {len(entries)} files, {archive.stat().st_size:,} bytes')
    return result

if __name__=='__main__': build()
