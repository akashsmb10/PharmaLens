from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config/dataset.json").read_text(encoding="utf-8"))

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")

def prepare_dirs(root=ROOT):
    for folder in ["config", "data/raw", "data/synthetic", "data/processed", "sql", "src",
                   "notebooks", "dashboard", "outputs/charts", "outputs/tables",
                   "outputs/forecasts", "outputs/validation", "tests", "docs"]:
        (root / folder).mkdir(parents=True, exist_ok=True)
