from __future__ import annotations

from pathlib import Path
from typing import Any

from .scanner import scan
from .state import append_history, write_plan


def apply_autofix(root: Path, plan: dict[str, Any]) -> dict[str, Any]:
    applied: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []

    for item in plan.get("plan", []):
        fix = item.get("autofix")
        if not fix:
            skipped.append({"findingId": item.get("findingId"), "reason": "manual-review-required"})
            continue
        path = root / item["file"]
        if not path.exists():
            skipped.append({"findingId": item.get("findingId"), "reason": "file-missing"})
            continue
        original = path.read_text(encoding="utf-8")
        updated = apply_fix_text(original, fix)
        if updated == original:
            skipped.append({"findingId": item.get("findingId"), "reason": "no-safe-change"})
            continue
        path.write_text(updated, encoding="utf-8")
        applied.append({"findingId": item.get("findingId"), "file": item["file"], "fix": fix})

    append_history(root, "autofix", {"applied": len(applied), "skipped": len(skipped)})
    after = scan(root)
    write_plan(root, after)
    return {"applied": applied, "skipped": skipped, "remaining": after["summary"]}


def apply_fix_text(text: str, fix: str) -> str:
    if fix == "yaml_safe_load":
        return text.replace("yaml.load(", "yaml.safe_load(")  # presecurity: ignore
    if fix == "python_debug_false":
        return text.replace("debug=True", "debug=False").replace("debug = True", "debug = False")  # presecurity: ignore
    if fix == "inner_html_to_text_content":
        return text.replace(".innerHTML =", ".textContent =")
    if fix == "tls_verify_true":
        return (
            text.replace("verify=False", "verify=True")  # presecurity: ignore
            .replace("verify = False", "verify = True")  # presecurity: ignore
            .replace("rejectUnauthorized: false", "rejectUnauthorized: true")  # presecurity: ignore
            .replace("InsecureSkipVerify: true", "InsecureSkipVerify: false")  # presecurity: ignore
        )
    if fix == "yaml_privileged_false":
        return text.replace("privileged: true", "privileged: false")
    return text
