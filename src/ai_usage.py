import os
import json
from datetime import datetime, timedelta, timezone
from typing import Tuple, Dict

BASE_DIR = os.path.dirname(__file__)
USAGE_FILE = os.path.join(BASE_DIR, "..", "data", "ai_usage.json")


def _ensure_dir():
    os.makedirs(os.path.dirname(USAGE_FILE), exist_ok=True)


def _today_str() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def load_usage() -> Dict:
    _ensure_dir()
    if not os.path.exists(USAGE_FILE):
        return {"date": _today_str(), "count": 0, "last_ts": None}
    try:
        with open(USAGE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # basic shape guard
        if not isinstance(data, dict):
            return {"date": _today_str(), "count": 0, "last_ts": None}
        return data
    except Exception:
        return {"date": _today_str(), "count": 0, "last_ts": None}


def save_usage(data: Dict) -> None:
    _ensure_dir()
    with open(USAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)


def can_call(max_calls_per_day: int = 20, cooldown_sec: int = 300) -> Tuple[bool, str, int]:
    """Return (allowed, reason, wait_seconds). reason in {"ok","daily_cap","cooldown"}.
    wait_seconds > 0 when not allowed.
    """
    now = datetime.now(timezone.utc)
    usage = load_usage()

    # reset if new day
    if usage.get("date") != _today_str():
        usage = {"date": _today_str(), "count": 0, "last_ts": None}
        save_usage(usage)

    # daily cap
    if usage.get("count", 0) >= max_calls_per_day:
        # seconds until next UTC day
        tomorrow = now.date() + timedelta(days=1)
        midnight = datetime.combine(tomorrow, datetime.min.time(), tzinfo=timezone.utc)
        wait = int((midnight - now).total_seconds())
        return False, "daily_cap", max(wait, 0)

    # cooldown
    last_ts = usage.get("last_ts")
    if last_ts:
        try:
            last_dt = datetime.fromisoformat(last_ts)
            if last_dt.tzinfo is None:
                last_dt = last_dt.replace(tzinfo=timezone.utc)
            elapsed = (now - last_dt).total_seconds()
            if elapsed < cooldown_sec:
                return False, "cooldown", int(cooldown_sec - elapsed)
        except Exception:
            pass

    return True, "ok", 0


def record_call() -> None:
    now = datetime.now(timezone.utc)
    usage = load_usage()
    if usage.get("date") != _today_str():
        usage = {"date": _today_str(), "count": 0, "last_ts": None}
    usage["count"] = int(usage.get("count", 0)) + 1
    usage["last_ts"] = now.isoformat()
    save_usage(usage)
