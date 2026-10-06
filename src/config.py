from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"
CONFIG_DIR = ROOT / "config"

def load_policy():
    with open(CONFIG_DIR / "policy.json", encoding="utf-8") as f:
        return json.load(f)
