from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

STATE_DIR = ".presecurity"
CONFIG_FILE = "config.json"
HISTORY_FILE = "history.jsonl"
PLAN_FILE = "scan-plan.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def state_paths(root: Path) -> dict[str, Path]:
    base = root / STATE_DIR
    return {
        "dir": base,
        "config": base / CONFIG_FILE,
        "history": base / HISTORY_FILE,
        "plan": base / PLAN_FILE,
    }


def ensure_state(root: Path) -> dict[str, Path]:
    paths = state_paths(root)
    paths["dir"].mkdir(parents=True, exist_ok=True)
    if not paths["config"].exists():
        paths["config"].write_text(
            json.dumps(
                {
                    "schema": 1,
                    "createdAt": utc_now(),
                    "scanner": "presecurity",
                    "riskPolicy": {
                        "autofix": "safe-only",
                        "reviewRequiredFor": ["critical", "high"],
                    },
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    if not paths["history"].exists():
        paths["history"].write_text("", encoding="utf-8")
    if not paths["plan"].exists():
        paths["plan"].write_text(
            json.dumps({"schema": 1, "findings": [], "plan": []}, indent=2) + "\n",
            encoding="utf-8",
        )
    append_history(root, "init", {"status": "ready"})
    return paths


def append_history(root: Path, event: str, payload: dict[str, Any]) -> None:
    paths = state_paths(root)
    paths["dir"].mkdir(parents=True, exist_ok=True)
    with paths["history"].open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"at": utc_now(), "event": event, "payload": payload}, sort_keys=True) + "\n")


def write_plan(root: Path, plan: dict[str, Any]) -> Path:
    paths = ensure_state(root)
    paths["plan"].write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    append_history(
        root,
        "scan",
        {
            "findings": len(plan.get("findings", [])),
            "autofixable": sum(1 for item in plan.get("findings", []) if item.get("autofix")),
        },
    )
    return paths["plan"]


def read_plan(root: Path) -> dict[str, Any]:
    paths = ensure_state(root)
    return json.loads(paths["plan"].read_text(encoding="utf-8"))

