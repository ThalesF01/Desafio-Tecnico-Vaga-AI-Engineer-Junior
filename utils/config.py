# utils/config.py
import json
from pathlib import Path
from typing import Any, Dict

_DEFAULTS: Dict[str, Any] = {
    "llm": {
        "model": "compound-beta-mini",
        "temperature": 0.0,
        "max_tokens": 512,
    },
    "ui": {
        "math_message": "Math expression detected, using calculator...",
        "llm_message": "Fetching information via LLM...",
        "weather_message": "Fetching weather via API..."
    },
    "weather": {
        "provider": "open-meteo",
        "geocoding_url": "https://geocoding-api.open-meteo.com/v1/search",
        "forecast_url": "https://api.open-meteo.com/v1/forecast",
        "timeout_seconds": 30
    }
}

def _deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out

def load_config(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return dict(_DEFAULTS)
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return _deep_merge(_DEFAULTS, data or {})
