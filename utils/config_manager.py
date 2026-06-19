import json
from pathlib import Path

CONFIG_FILE = Path("data/avatar_config.json")


def load_configs():
    if not CONFIG_FILE.exists():
        return {}

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
            
    except (json.JSONDecodeError, OSError):
        return {}

def save_configs(data: dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )