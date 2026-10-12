"""Immutable cached Parquet loads, hash verification, no DuckDB or network at runtime."""
from pathlib import Path
import hashlib
import json
import logging
import pandas as pd
import streamlit as st
from .data_contracts import DataError,validate

ROOT=Path(__file__).resolve().parents[1]

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def manifest(root=ROOT):
    try:
        data=json.loads((Path(root)/'config/dashboard_manifest.json').read_text(encoding='utf-8'))
        if not data['validated'] or not data['datasets']: raise ValueError('No validated datasets')
        return data
    except (OSError,ValueError,KeyError) as exc:
        logging.exception('Dashboard manifest unavailable')
        raise DataError('The validated dashboard data manifest is unavailable. Restore the packaged runtime data.') from exc

def safe_path(root,relative):
    root=Path(root).resolve(); path=(root/relative).resolve()
    if not path.is_relative_to(root): raise DataError('Dataset path must remain inside the project')
    return path

@st.cache_data(show_spinner=False,max_entries=96)
def _read(path_string,expected_hash,contract_json,stat_token):
    path=Path(path_string); contract=json.loads(contract_json)
    try:
        if digest(path)!=expected_hash: raise DataError('Dataset differs from its validated version; restore the matching artifacts.')
        frame=pd.read_parquet(path)
    except DataError: raise
    except Exception as exc:
        logging.exception('Cannot read runtime data')
        raise DataError('A required dataset could not be read. Restore its validated Parquet file.') from exc
    return validate(frame,contract,path.name)

def load(name,root=ROOT,optional=False):
    m=manifest(root)
    if name not in m['datasets']:
        if optional: return None
        raise DataError(f'Required dataset is not registered: {name}')
    contract=m['datasets'][name]; path=safe_path(root,contract['path'])
    if not path.is_file():
        if optional: return None
        raise DataError(f'Required dataset unavailable: {name}. Restore the runtime Parquet package.')
    stat=path.stat()
    return _read(str(path),contract['sha256'],json.dumps(contract,sort_keys=True),(stat.st_size,stat.st_mtime_ns)).copy(deep=True)

def read_doc(name,root=ROOT):
    path=safe_path(root,'docs/'+name)
    return path.read_text(encoding='utf-8') if path.is_file() else None
