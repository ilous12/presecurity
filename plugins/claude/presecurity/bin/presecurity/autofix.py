from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from .false_positive import is_plan_item_false_positive
from .i18n import t
from .packages import collect_package_requirements, install_required_packages
from .progress import progress
from .scanner import scan
from .state import append_history, write_plan


def apply_autofix(root: Path, plan: dict[str, Any]) -> dict[str, Any]:
    applied: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    items = actionable_plan_items(root, plan)

    for index, item in enumerate(items, start=1):
        progress(f"{t('progress.autofix.apply')} {item.get('file', 'unknown')}:{item.get('line', '?')}", index, max(len(items), 1))
        fix = item.get("autofix") or "agent_intent_fix"
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


def actionable_plan_items(root: Path, plan: dict[str, Any]) -> list[dict[str, Any]]:
    findings = {finding.get("id"): finding for finding in plan.get("findings", [])}
    items: list[dict[str, Any]] = []
    for item in plan.get("plan", []):
        finding = findings.get(item.get("findingId"))
        candidate = {**(finding or {}), **item}
        if is_plan_item_false_positive(root, candidate):
            continue
        items.append(item)
    return items


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
    if fix == "parameterize_sql_placeholder":
        return parameterize_sql_line(text, item)
    if fix == "agent_intent_fix":
        return add_agent_fix_marker(text, item)
    return text


def sanitize_react_html(text: str) -> str:
    pattern = re.compile(r"dangerouslySetInnerHTML\s*=\s*\{\{\s*__html\s*:\s*([^}]+?)\s*\}\}")

    def replace(match: re.Match[str]) -> str:
        expression = match.group(1).strip()
        if expression.startswith("DOMPurify.sanitize("):
            return match.group(0)
        return f"dangerouslySetInnerHTML={{{{__html: DOMPurify.sanitize({expression})}}}}"

    return pattern.sub(replace, text)


def parameterize_sql_line(text: str, item: dict[str, Any] | None) -> str:
    def transform(line: str) -> str:
        params: list[str] = []

        def replace_template(match: re.Match[str]) -> str:
            params.append(match.group(1).strip())
            return "?"

        updated = re.sub(r"\$\{([^}]+)\}", replace_template, line)
        updated = updated.replace("%s", "?")
        updated = re.sub(r"\+\s*([A-Za-z_][A-Za-z0-9_.$]*)", lambda m: collect_concat_param(m, params), updated)
        updated = re.sub(r"([A-Za-z_][A-Za-z0-9_.$]*)\s*\+", lambda m: collect_concat_param(m, params), updated)
        if params and "presecurity params:" not in updated:
            updated = f"{updated} {line_comment(item)} presecurity params: {', '.join(params)}"
        return updated

    return replace_target_line(text, item, transform)


def collect_concat_param(match: re.Match[str], params: list[str]) -> str:
    value = match.group(1).strip()
    if value.lower() not in {"select", "insert", "update", "delete"}:
        params.append(value)
    return "?"


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


def add_agent_fix_marker(text: str, item: dict[str, Any] | None) -> str:
    def transform(line: str) -> str:
        if "presecurity agent-fix" in line:
            return line
        return f"{line} {line_comment(item)} presecurity agent-fix: apply intent-preserving secure rewrite"

    return replace_target_line(text, item, transform)


def replace_target_line(text: str, item: dict[str, Any] | None, transform) -> str:
    if not item:
        return text
    line_no = int(item.get("line") or 1)
    lines = text.splitlines()
    if not lines:
        return text
    index = max(0, min(line_no - 1, len(lines) - 1))
    lines[index] = transform(lines[index])
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def line_comment(item: dict[str, Any] | None) -> str:
    file_name = str((item or {}).get("file", ""))
    if file_name.endswith((".py", ".rb", ".sh", ".yaml", ".yml", ".tf")):
        return "#"
    return "//"
