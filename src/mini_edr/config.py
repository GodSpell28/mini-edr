"""Configuration helpers for mini-edr."""

import json
import os
from typing import Any, Dict


DEFAULT_CONFIG: Dict[str, Any] = {
    "watch_paths": ["."],
    "poll_interval": 2.0,
    "alert_processes": [],
    "output": "edr-events.jsonl",
}


def load_config(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return dict(DEFAULT_CONFIG)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return {**DEFAULT_CONFIG, **data}


def save_config(path: str, config: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
