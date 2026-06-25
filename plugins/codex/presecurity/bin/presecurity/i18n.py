from __future__ import annotations

import os
from typing import Any


MESSAGES: dict[str, dict[str, str]] = {
    "ko": {
        "init.done": "presecurity 초기화 완료: {path}",
        "cleanup.done": "presecurity 상태 파일 삭제 완료: {path}",
        "autofix.title": "presecurity 자동 수정 결과",
        "autofix.applied": "적용된 수정",
        "autofix.skipped": "건너뛴 항목",
        "autofix.packages": "패키지 처리",
        "autofix.remaining": "남은 이슈",
        "progress.autofix.apply": "자동 수정 적용",
        "progress.autofix.packages": "필요 패키지 묶음 처리",
        "progress.autofix.rescan": "수정 후 재스캔",
        "progress.scan.collect": "스캔 대상 수집",
        "progress.scan.filter": "오탐 후보 제외 및 규칙 검사",
        "progress.scan.plan": "수정 계획 생성",
        "progress.scan.done": "스캔 완료",
        "scan.title": "presecurity 스캔 요약",
        "scan.files": "스캔한 파일",
        "scan.findings": "이슈",
        "scan.findings.counts": "치명 {critical}, 높음 {high}, 중간 {medium}, 낮음 {low}",
        "scan.autofixable": "자동 수정 가능",
        "scan.false_positives": "사전 제외된 오탐 후보",
        "scan.evidence": "근거 코드",
        "scan.intent": "변경 의도",
        "intent.none": "git diff가 없거나 변경된 라인이 없습니다.",
        "intent.no_changed": "변경된 파일이 없습니다.",
        "intent.with_hints": "변경 파일 {file_count}개, +{added}/-{removed} 라인. 보안상 민감한 영역: {hints}.",
        "intent.without_hints": "변경 파일 {file_count}개, +{added}/-{removed} 라인. 뚜렷한 보안 민감 영역은 감지되지 않았습니다.",
        "scan.more": ".presecurity/scan-plan.json에 {count}개 이슈가 더 있습니다",
        "doctor.title": "presecurity 진단",
        "doctor.summary": "요약",
        "doctor.ok": "정상",
        "doctor.missing": "확인 필요",
        "doctor.ready": "준비 완료",
        "doctor.init_required": "초기화 필요",
        "doctor.environment_issue": "환경 확인 필요",
    },
    "en": {
        "init.done": "presecurity initialized: {path}",
        "cleanup.done": "presecurity state removed: {path}",
        "autofix.title": "presecurity autofix summary",
        "autofix.applied": "applied",
        "autofix.skipped": "skipped",
        "autofix.packages": "package actions",
        "autofix.remaining": "remaining findings",
        "progress.autofix.apply": "applying autofix",
        "progress.autofix.packages": "installing required packages together",
        "progress.autofix.rescan": "rescanning after fixes",
        "progress.scan.collect": "collecting scan targets",
        "progress.scan.filter": "filtering false positives and checking rules",
        "progress.scan.plan": "building fix plan",
        "progress.scan.done": "scan complete",
        "scan.title": "presecurity scan summary",
        "scan.files": "files scanned",
        "scan.findings": "findings",
        "scan.findings.counts": "critical {critical}, high {high}, medium {medium}, low {low}",
        "scan.autofixable": "autofixable",
        "scan.false_positives": "false positives excluded",
        "scan.evidence": "evidence",
        "scan.intent": "intent",
        "intent.none": "No git diff available or no changed lines.",
        "intent.no_changed": "No changed files detected.",
        "intent.with_hints": "Detected {file_count} changed file(s), +{added}/-{removed} lines. Security-relevant areas: {hints}.",
        "intent.without_hints": "Detected {file_count} changed file(s), +{added}/-{removed} lines. No high-signal security areas detected.",
        "scan.more": "{count} more findings in .presecurity/scan-plan.json",
        "doctor.title": "presecurity doctor",
        "doctor.summary": "summary",
        "doctor.ok": "ok",
        "doctor.missing": "missing",
        "doctor.ready": "ready",
        "doctor.init_required": "init required",
        "doctor.environment_issue": "environment issue",
    },
}


SUMMARY_KEYS = {
    "ready": "doctor.ready",
    "init required": "doctor.init_required",
    "environment issue": "doctor.environment_issue",
}


def language() -> str:
    for key in ("PRESECURITY_LANG", "LC_ALL", "LC_MESSAGES", "LANG"):
        value = os.environ.get(key, "").lower()
        if value.startswith("ko"):
            return "ko"
        if value.startswith("en") or value in {"c", "posix"}:
            return "en"
    return "en"


def t(key: str, **kwargs: Any) -> str:
    lang = language()
    template = MESSAGES.get(lang, MESSAGES["en"]).get(key, MESSAGES["en"].get(key, key))
    return template.format(**kwargs)


def localize_summary(summary: str) -> str:
    return t(SUMMARY_KEYS.get(summary, summary))
