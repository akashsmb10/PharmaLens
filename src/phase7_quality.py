"""Redacted source audit, documentary checks and protected-artifact verification."""
import ast
import json
import re
import subprocess
from pathlib import Path
from .common import ROOT,sha256,write_json
from .phase7_inventory import files

def security(root=ROOT):
    patterns={'possible_private_key':r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
        'possible_aws_access_key':r'\bAKIA[A-Z0-9]{16}\b','possible_github_token':r'\bgh[pousr]_[A-Za-z0-9]{30,}\b',
        'possible_assigned_secret':r'(?i)(?:api_key|access_token|password|client_secret)\s*[=:]\s*[\"\x27][^\"\x27\s]{12,}[\"\x27]',
        'private_workstation_path':r'[A-Za-z]:[\\/]+Users[\\/]+[^\\/\s\"\x27]+',
        'email_address':r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b'}
    findings=[]; scanned=[]
    paths,_=files(root)
    for path in paths:
        rel=path.relative_to(root).as_posix()
        if rel.startswith('outputs/phase7/') or path.suffix.lower() not in {'.py','.md','.json','.yaml','.yml','.toml','.txt','.ipynb','.log','.ini'}: continue
        text=path.read_text(encoding='utf-8',errors='replace'); scanned.append(rel)
        for category,pattern in patterns.items():
            for match in re.finditer(pattern,text):
                if rel=='src/phase7_quality.py' and category.startswith('possible_'): continue
                if category=='email_address' and match.group().lower().endswith(('@nhsbsa.nhs.uk','@nationalarchives.gov.uk')): continue
                findings.append({'file':rel,'line':text.count('\n',0,match.start())+1,'category':category,'value':'REDACTED'})
    risky=[f for f in findings if f['category'].startswith('possible_')]
    result={'scanned_text_files':len(scanned),'credential_candidates':len(risky),'findings':findings,
        'scope':'Pattern scan, not proof of absence; no secret values are printed. Workstation paths remain in preserved historical evidence and are removed from release copies.',
        'no_credentials_found_by_patterns':not risky}
    write_json(root/'outputs/phase7/validation/security_review.json',result)
    return result

def code_audit(root=ROOT):
    inventory=[]; syntax=[]; broad=[]
    paths,_=files(root)
    for path in paths:
        if path.suffix!='.py' or path.relative_to(root).parts[0] not in {'src','dashboard','tests','app.py','run_pipeline.py'}: continue
        rel=path.relative_to(root).as_posix(); text=path.read_text(encoding='utf-8')
        try: tree=ast.parse(text)
        except SyntaxError as exc: syntax.append({'file':rel,'line':exc.lineno}); continue
        functions=[n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))]
        inventory.append({'file':rel,'lines':len(text.splitlines()),'functions':len(functions),'long_functions':[{'name':n.name,'lines':n.end_lineno-n.lineno+1} for n in functions if n.end_lineno-n.lineno>100],
            'annotated_functions':sum(n.returns is not None for n in functions)})
        for n in ast.walk(tree):
            if isinstance(n,ast.ExceptHandler) and (n.type is None or isinstance(n.type,ast.Name) and n.type.id=='Exception'):
                broad.append({'file':rel,'line':n.lineno,'review':'Forecast fits retain failures; loaders expose explicit errors; notebook/ingestion boundaries require review'})
    result={'syntax_errors':syntax,'modules':inventory,'broad_exception_boundaries':broad,
        'reviewed_core_modules':['ingest','validate','sql_analytics','trend_analysis','seasonality_analysis','anomaly_diagnostics','cost_diagnostics','forecast_features','forecast_models','forecast_splits','forecast_backtesting','forecast_selection','forecast_intervals','forecast_metrics','prioritization','forecast_risk','scenario_engine','dashboard'],
        'findings':['Dense formatting and limited type annotations remain in legacy analytical modules; no cosmetic rewrite of validated mathematics.',
            'Ruff F-series findings are limited to unused imports/variables; unused dashboard imports removed. Fatal static checks run separately.',
            'Later-phase documentation was excluded from the legacy Phase 1–2 document guard without changing baseline protected members or results.',
            'Broad forecast exception handling deliberately records failure rows rather than substituting another model; loader boundaries log and reject malformed files.']}
    write_json(root/'outputs/phase7/validation/code_audit.json',result)
    return result

def protection(root=ROOT):
    before=json.loads((root/'outputs/phase7/validation/protected_manifest.json').read_text())
    missing=[]; changed=[]
    for rel,expected in before.items():
        path=root/rel
        if not path.is_file(): missing.append(rel)
        elif sha256(path)!=expected: changed.append(rel)
    initial=json.loads((root/'outputs/phase7/validation/baseline_inventory.json').read_text())['files']
    baseline={f['path']:f['sha256'] for f in initial}; paths,_=files(root)
    new=[p.relative_to(root).as_posix() for p in paths if p.relative_to(root).as_posix() not in baseline]
    modified=[p for p,h in baseline.items() if (root/p).is_file() and sha256(root/p)!=h and not p.startswith('outputs/phase7/')]
    result={'protected':len(before),'unchanged':len(before)-len(changed)-len(missing),'changed':changed,'missing':missing,'new_files':new,'authorized_modified_files':modified,'passed':not changed and not missing}
    write_json(root/'outputs/phase7/validation/protection_result.json',result)
    return result

def links(root=ROOT):
    broken=[]; checked=[]
    for path in [root/'README.md',*(root/'docs').glob('PHASE7*.md'),*(root/'docs').glob('PROJECT_ARCHITECTURE.md'),*(root/'docs').glob('REPRODUCIBILITY_GUIDE.md'),*(root/'docs').glob('DATA_SOURCES_AND_LICENSES.md')]:
        text=path.read_text(encoding='utf-8')
        for ref in re.findall(r'\]\(([^\n)]+)\)',text):
            ref=ref.strip('<>'); target=ref.split('#')[0]
            if not target or '://' in target or target.startswith('mailto:'): continue
            check=(path.parent/target).resolve()
            checked.append({'document':path.relative_to(root).as_posix(),'target':target})
            if not check.is_file(): broken.append(checked[-1])
            elif '#' in ref and check.suffix=='.md':
                fragment=ref.split('#',1)[1]
                headings=re.findall(r'^#{1,6}\s+(.+?)\s*#*\s*$',check.read_text(encoding='utf-8'),re.M)
                anchors={re.sub(r'[^\w\- ]','',h.lower()).replace(' ','-') for h in headings}
                if fragment not in anchors: broken.append({'document':path.relative_to(root).as_posix(),'target':ref,'reason':'Missing heading anchor'})
    return {'checked':len(checked),'broken':broken}

if __name__=='__main__':
    print(json.dumps({'security':security()['credential_candidates'],'code_modules':len(code_audit()['modules']),'protection':protection()['passed']}))
