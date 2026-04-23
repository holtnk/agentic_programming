import os
from pathlib import Path

DEFAULT_CONFIG = {
    "api_key": None,
    "base_url": "http://localhost:1234/v1",
    "model": "local-model",
    "testing": {
        "max_iterations": 3,
    },
}


def get_workspace_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_config() -> dict:
    config_path = get_workspace_root() / "config.yaml"
    if config_path.exists():
        try:
            import yaml

            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if isinstance(data, dict):
                    merged = DEFAULT_CONFIG.copy()
                    merged.update(data)
                    if "testing" in data and isinstance(data["testing"], dict):
                        merged["testing"] = {**DEFAULT_CONFIG["testing"], **data["testing"]}
                    return merged
        except Exception:
            pass

    return DEFAULT_CONFIG.copy()
