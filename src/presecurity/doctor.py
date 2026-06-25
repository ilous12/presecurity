from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

from .i18n import localize_summary, t
from .rules import SUPPORTED_PLATFORMS, iter_rules
from .state import state_paths


def run_doctor(root: Path) -> dict[str, Any]:
    paths = state_paths(root)
    checks = [
        check("project_root", True, str(root)),
        check("python", sys.version_info >= (3, 9), sys.version.split()[0]),
        check("git", shutil.which("git") is not None, shutil.which("git") or "not found"),
        check("git_repository", is_git_repository(root), "git rev-parse --is-inside-work-tree"),
        check(".presecurity", paths["dir"].exists(), str(paths["dir"])),
        check("config.json", paths["config"].exists(), str(paths["config"])),
        check("history.jsonl", paths["history"].exists(), str(paths["history"])),
        check("scan-plan.json", paths["plan"].exists(), str(paths["plan"])),
        check("rules", len(list(iter_rules())) > 0, f"{len(list(iter_rules()))} rules"),
        check("platforms", len(SUPPORTED_PLATFORMS) >= 20, f"{len(SUPPORTED_PLATFORMS)} platforms"),
    ]
    ok = all(item["ok"] for item in checks if item["name"] not in {".presecurity", "config.json", "history.jsonl", "scan-plan.json"})
    ready = all(item["ok"] for item in checks)
    return {
        "ok": ok,
        "ready": ready,
        "summary": "ready" if ready else "init required" if ok else "environment issue",
        "checks": checks,
    }


def check(name: str, ok: bool, detail: str) -> dict[str, Any]:
    return {"name": name, "ok": ok, "detail": detail}


def is_git_repository(root: Path) -> bool:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return completed.returncode == 0 and completed.stdout.strip() == "true"


def print_doctor(result: dict[str, Any]) -> str:
    lines = [t("doctor.title"), f"- {t('doctor.summary')}: {localize_summary(result['summary'])}"]
    for item in result["checks"]:
        status = t("doctor.ok") if item["ok"] else t("doctor.missing")
        lines.append(f"- [{status}] {item['name']}: {item['detail']}")
    return "\n".join(lines)
