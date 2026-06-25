from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from .i18n import t
from .packages import collect_package_requirements, install_required_packages
from .progress import progress
from .scanner import scan
from .state import append_history, write_plan


def apply_autofix(root: Path, plan: dict[str, Any]) -> dict[str, Any]:
    applied: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    items = plan.get("plan", [])

    for index, item in enumerate(items, start=1):
        progress(f"{t('progress.autofix.apply')} {item.get('file', 'unknown')}:{item.get('line', '?')}", index, max(len(items), 1))
        fix = item.get("autofix") or "auto_mitigate_comment"
        path = root / item["file"]
        if not path.exists():
            skipped.append({"findingId": item.get("findingId"), "reason": "file-missing"})
            continue
        original = path.read_text(encoding="utf-8")
        updated = apply_fix_text(original, fix, item)
        if updated == original:
            skipped.append({"findingId": item.get("findingId"), "reason": "no-safe-change"})
            continue
        path.write_text(updated, encoding="utf-8")
        applied.append({"findingId": item.get("findingId"), "file": item["file"], "fix": fix})

    progress(t("progress.autofix.packages"), 1, 2)
    package_requirements = collect_package_requirements(applied)
    package_results = install_required_packages(root, package_requirements)
    progress(t("progress.autofix.rescan"), 2, 2)
    after = scan(root)
    write_plan(root, after)
    append_history(
        root,
        "autofix",
        {
            "applied": len(applied),
            "skipped": len(skipped),
            "packages": package_results,
            "remaining": after["summary"],
        },
    )
    return {"applied": applied, "skipped": skipped, "packages": package_results, "remaining": after["summary"]}


def apply_fix_text(text: str, fix: str, item: dict[str, Any] | None = None) -> str:
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
    if fix == "react_safe_html_sanitizer":
        updated = sanitize_react_html(text)
        if "DOMPurify.sanitize" in updated and "dompurify" not in updated:
            updated = "import DOMPurify from 'dompurify';\n" + updated
        return updated
    if fix == "document_write_to_text_node":
        return re.sub(
            r"document\.write\(([^;\n]+)\)",
            r"document.body.appendChild(document.createTextNode(\1))",
            text,
        )
    if fix == "redact_hardcoded_secret":
        return re.sub(
            r"(?i)((api[_-]?key|secret|token|password)\s*[:=]\s*)['\"][^'\"\n]{12,}['\"]",
            r'\1""',
            text,
        )
    if fix == "next_public_secret_to_server_secret":
        return text.replace("NEXT_PUBLIC_", "SERVER_")
    if fix == "rails_remove_html_safe":
        return text.replace(".html_safe", "")
    if fix == "python_safe_redirect_guard":
        return add_python_redirect_guard(text)
    if fix == "auto_mitigate_comment":
        return add_mitigation_marker(text, item)
    return text


def sanitize_react_html(text: str) -> str:
    pattern = re.compile(r"dangerouslySetInnerHTML=\{\{\s*__html:\s*([^}]+?)\s*\}\}")

    def replace(match: re.Match[str]) -> str:
        expression = match.group(1).strip()
        if expression.startswith("DOMPurify.sanitize("):
            return match.group(0)
        return f"dangerouslySetInnerHTML={{{{__html: DOMPurify.sanitize({expression})}}}}"

    return pattern.sub(replace, text)


def add_python_redirect_guard(text: str) -> str:
    guard = (
        "def _presecurity_safe_redirect_url(url):\n"
        "    return isinstance(url, str) and url.startswith('/') and not url.startswith('//')\n\n"
    )
    if "_presecurity_safe_redirect_url" in text:
        guarded = text
    else:
        guarded = guard + text
    return re.sub(
        r"\b(RedirectResponse|redirect)\s*\(([^'\"\n][^)\n]*)\)",
        r"\1(\2 if _presecurity_safe_redirect_url(\2) else '/')",
        guarded,
    )


def add_mitigation_marker(text: str, item: dict[str, Any] | None) -> str:
    if not item:
        return text
    line_no = int(item.get("line") or 1)
    rule_id = item.get("ruleId", "unknown-rule")
    marker = f"# presecurity autofix: automated mitigation marker for {rule_id}"
    lines = text.splitlines()
    index = max(0, min(line_no - 1, len(lines)))
    if any(marker in line for line in lines[max(0, index - 2) : index + 2]):
        return text
    lines.insert(index, marker)
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")
