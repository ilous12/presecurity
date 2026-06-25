from __future__ import annotations

from pathlib import Path
import re


TEST_PATH_PARTS = {"test", "tests", "__tests__", "spec", "fixtures", "fixture", "examples", "demo"}
NON_RUNTIME_PATH_PARTS = {
    "docs",
    "documentation",
    "templates",
    "template",
    "stories",
    "storybook",
    "mock",
    "mocks",
    "samples",
}
PLACEHOLDER_WORDS = {
    "changeme",
    "change-me",
    "dummy",
    "example",
    "fake",
    "placeholder",
    "sample",
    "test",
    "todo",
    "xxx",
}
SANITIZER_TOKENS = ("dompurify.sanitize", "sanitizehtml", "sanitize-html", "sanitize_html")
SAFE_HTML_NAMES = ("sanitized", "safehtml", "safe_html", "cleanhtml", "clean_html", "trustedhtml", "trusted_html")
ENV_URL_TOKENS = (
    "api_base_url",
    "base_url",
    "baseurl",
    "backend_url",
    "service_url",
    "internal_api",
    "internalapi",
    "process.env",
    "import.meta.env",
    "env.",
    "config.",
)
USER_INPUT_TOKENS = ("req.", "request.", "params", "searchparams", "query", "body", "formdata", "headers.get")


def is_false_positive(rule_id: str, rel: str, line: str, full_text: str) -> bool:
    lowered = line.lower()
    path = Path(rel)
    path_parts = {part.lower() for part in path.parts}
    path_names = path_parts | {path.stem.lower()}
    if "presecurity: ignore" in lowered:
        return True
    if rule_id == "hardcoded-secret":
        return is_test_path(path_parts) or any(word in lowered for word in PLACEHOLDER_WORDS)
    if rule_id == "nextjs-public-secret":
        return any(word in lowered for word in PLACEHOLDER_WORDS)
    if rule_id == "node-child-process-exec":
        return bool(re.search(r"\.\s*exec\s*\(", line)) and "child_process.exec" not in lowered
    if rule_id == "react-dangerously-set-html":
        return is_sanitized_react_html(line, full_text)
    if rule_id == "docker-root-user":
        return bool(re.search(r"(?im)^USER\s+\S+", full_text))
    if rule_id == "express-state-changing-route":
        return any(token in lowered for token in ("requireauth", "authenticate", "authorize", "csrf"))
    if rule_id == "ssrf-unvalidated-url":
        return any(token in lowered for token in ("allowed", "allowlist", "trusted", "internal_only")) or is_env_backed_url(
            line, full_text
        )
    if rule_id == "sql-string-concat":
        return (
            is_non_runtime_path(path_names)
            or any(word in lowered for word in PLACEHOLDER_WORDS)
            or "presecurity: fixture" in lowered
            or looks_like_selector_or_css(lowered)
        )
    return False


def is_test_path(path_parts: set[str]) -> bool:
    return bool(path_parts & TEST_PATH_PARTS)


def is_non_runtime_path(path_parts: set[str]) -> bool:
    return is_test_path(path_parts) or bool(path_parts & NON_RUNTIME_PATH_PARTS)


def looks_like_selector_or_css(line: str) -> bool:
    return any(
        token in line
        for token in (
            "queryselector",
            "queryselectorall",
            "user-select",
            "select-none",
            "select:",
            "selected",
            "selection",
        )
    )


def is_sanitized_react_html(line: str, full_text: str) -> bool:
    lowered = line.lower()
    if any(token in lowered for token in SANITIZER_TOKENS):
        return True

    expression = react_html_expression(line)
    if not expression:
        return False
    expression_lowered = expression.lower()
    if any(token in expression_lowered for token in SAFE_HTML_NAMES):
        return True
    if not re.match(r"^[A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)?$", expression):
        return False

    assignment_pattern = (
        rf"(?is)\b(?:const|let|var)\s+{re.escape(expression_lowered)}\s*=\s*"
        rf"[^;\n]*(?:{'|'.join(re.escape(token) for token in SANITIZER_TOKENS)})"
    )
    return bool(re.search(assignment_pattern, full_text.lower()))


def react_html_expression(line: str) -> str:
    match = re.search(r"dangerouslySetInnerHTML\s*=\s*\{\{\s*__html\s*:\s*([^}]+?)\s*\}\}", line)
    return match.group(1).strip() if match else ""


def is_env_backed_url(line: str, full_text: str) -> bool:
    lowered = line.lower()
    if any(token in lowered for token in USER_INPUT_TOKENS):
        return False
    if any(token in lowered for token in ENV_URL_TOKENS):
        return True

    argument = ssrf_first_argument(line)
    if not argument:
        return False
    if is_relative_url_argument(argument, full_text):
        return True
    if any(token in argument.lower() for token in USER_INPUT_TOKENS):
        return False
    if any(token in argument.lower() for token in ENV_URL_TOKENS):
        return True
    if not re.match(r"^[A-Za-z_$][\w$]*$", argument):
        return False

    assignment_pattern = (
        rf"(?is)\b(?:const|let|var)\s+{re.escape(argument)}\s*=\s*"
        rf"[^;\n]*(?:{'|'.join(re.escape(token) for token in ENV_URL_TOKENS)})"
    )
    return bool(re.search(assignment_pattern, full_text.lower()))


def ssrf_first_argument(line: str) -> str:
    match = re.search(r"\b(?:fetch|axios|requests|http\.(?:Get|Post))\s*\(\s*([^,\)\n]+)", line)
    return match.group(1).strip() if match else ""


def is_relative_url_argument(argument: str, full_text: str) -> bool:
    stripped = argument.strip()
    if re.match(r"^[`'\"]/(?!/)", stripped):
        return True
    if not re.match(r"^[A-Za-z_$][\w$]*$", stripped):
        return False
    assignment_pattern = rf"(?is)\b(?:const|let|var)\s+{re.escape(stripped)}\s*=\s*[`'\"]/(?!/)"
    return bool(re.search(assignment_pattern, full_text))


def is_plan_item_false_positive(root: Path, item: dict) -> bool:
    rel = str(item.get("file") or "")
    rule_id = str(item.get("ruleId") or "")
    if not rel or not rule_id:
        return False
    path = root / rel
    if not path.exists():
        return False
    try:
        full_text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    lines = full_text.splitlines()
    line_no = int(item.get("line") or 0)
    if line_no < 1 or line_no > len(lines):
        return True
    line = lines[line_no - 1]
    evidence = str(item.get("evidence") or "").strip()
    if evidence and evidence not in line.strip():
        return True
    return is_false_positive(rule_id, rel, line, full_text)
