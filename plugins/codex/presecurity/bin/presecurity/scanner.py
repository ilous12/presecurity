from __future__ import annotations

from pathlib import Path
import fnmatch
import hashlib
import json
from typing import Any

from .false_positive import is_false_positive
from .intent import analyze_intent
from .i18n import t
from .progress import progress
from .rules import Rule, iter_rules
from .state import utc_now

EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".presecurity",
    "node_modules",
    "vendor",
    "dist",
    "build",
    ".next",
    ".venv",
    "venv",
    "__pycache__",
}

EXT_LANGUAGE = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "jsx",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".go": "go",
    ".java": "java",
    ".rb": "ruby",
    ".php": "php",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".tf": "hcl",
}

SPECIAL_FILES = {
    "Dockerfile": "dockerfile",
    "dockerfile": "dockerfile",
}


def scan(root: Path, diff_base: str = "HEAD") -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    files_scanned = 0
    files = list(iter_files(root))
    progress(t("progress.scan.collect"), 1, 4)
    total_files = max(len(files), 1)
    for file_index, path in enumerate(files, start=1):
        progress(t("progress.scan.filter"), file_index, total_files)
        rel = path.relative_to(root).as_posix()
        language = detect_language(path)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        files_scanned += 1
        for rule in iter_rules():
            if not rule_applies(rule, language, rel):
                continue
            absent = rule.absent_compile()
            if absent and absent.search(text):
                continue
            compiled = rule.compile()
            for line_no, line in enumerate(text.splitlines(), start=1):
                if compiled.search(line):
                    if is_false_positive(rule.id, rel, line, text):
                        continue
                    findings.append(format_finding(rule, rel, line_no, line))

    progress(t("progress.scan.plan"), 3, 4)
    ordered = sorted(findings, key=lambda item: severity_rank(item["severity"]), reverse=True)
    plan = build_plan(ordered)
    progress(t("progress.scan.done"), 4, 4)
    return {
        "schema": 1,
        "generatedAt": utc_now(),
        "root": str(root),
        "intent": analyze_intent(root, diff_base),
        "summary": {
            "filesScanned": files_scanned,
            "findings": len(ordered),
            "critical": sum(1 for f in ordered if f["severity"] == "critical"),
            "high": sum(1 for f in ordered if f["severity"] == "high"),
            "medium": sum(1 for f in ordered if f["severity"] == "medium"),
            "low": sum(1 for f in ordered if f["severity"] == "low"),
            "autofixable": len(plan),
            "issueLocations": [f"{f['file']}:{f['line']}" for f in ordered],
        },
        "findings": ordered,
        "plan": plan,
    }


def iter_files(root: Path):
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        parts = set(path.relative_to(root).parts[:-1])
        if parts & EXCLUDED_DIRS:
            continue
        if path.stat().st_size > 512_000:
            continue
        yield path


def detect_language(path: Path) -> str:
    if path.name in SPECIAL_FILES:
        return SPECIAL_FILES[path.name]
    return EXT_LANGUAGE.get(path.suffix.lower(), "text")


def rule_applies(rule: Rule, language: str, rel: str) -> bool:
    if "any" in rule.languages or language in rule.languages:
        return True
    if rule.id == "github-actions-unpinned" and fnmatch.fnmatch(rel, ".github/workflows/*.yml"):
        return True
    return False


def format_finding(rule: Rule, rel: str, line_no: int, line: str) -> dict[str, Any]:
    digest = hashlib.sha256(f"{rule.id}:{rel}:{line_no}:{line.strip()}".encode()).hexdigest()[:16]
    return {
        "id": digest,
        "ruleId": rule.id,
        "name": rule.name,
        "owasp": rule.owasp,
        "severity": rule.severity,
        "confidence": rule.confidence,
        "file": rel,
        "line": line_no,
        "evidence": line.strip()[:240],
        "message": rule.message,
        "impact": rule.impact,
        "recommendation": rule.recommendation,
        "platforms": list(rule.platforms),
        "autofix": effective_autofix(rule),
    }


def build_plan(findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for index, finding in enumerate(findings, start=1):
        items.append(
            {
                "order": index,
                "findingId": finding["id"],
                "ruleId": finding["ruleId"],
                "file": finding["file"],
                "line": finding["line"],
                "severity": finding["severity"],
                "impact": finding["impact"],
                "action": finding["recommendation"],
                "autofix": finding.get("autofix") or "agent_intent_fix",
                "status": "planned",
            }
        )
    return items


def severity_rank(severity: str) -> int:
    return {"low": 1, "medium": 2, "high": 3, "critical": 4}.get(severity, 0)


def print_plan(plan: dict[str, Any]) -> str:
    summary = plan["summary"]
    lines = [
        t("scan.title"),
        f"- {t('scan.files')}: {summary['filesScanned']}",
        f"- {t('scan.findings')}: {summary['findings']} ({t('scan.findings.counts', critical=summary['critical'], high=summary['high'], medium=summary['medium'], low=summary['low'])})",
        f"- {t('scan.autofixable')}: {summary['autofixable']}",
        f"- {t('scan.intent')}: {plan.get('intent', {}).get('summary', 'not available')}",
    ]
    for finding in plan["findings"][:50]:
        lines.append(
            f"- [{finding['severity']}] {finding['file']}:{finding['line']} {finding['ruleId']} - {finding['message']} | {t('scan.evidence')}: {finding['evidence']}"
        )
    if len(plan["findings"]) > 50:
        lines.append(f"- ... {t('scan.more', count=len(plan['findings']) - 50)}")
    return "\n".join(lines)


def plan_as_json(plan: dict[str, Any]) -> str:
    return json.dumps(plan, indent=2, sort_keys=True)


def effective_autofix(rule: Rule) -> str:
    if rule.autofix:
        return rule.autofix
    return {
        "sql-string-concat": "parameterize_sql_placeholder",
        "go-sql-format": "parameterize_sql_placeholder",
        "django-raw-sql": "parameterize_sql_placeholder",
        "php-laravel-raw-query": "parameterize_sql_placeholder",
    }.get(rule.id, "agent_intent_fix")
