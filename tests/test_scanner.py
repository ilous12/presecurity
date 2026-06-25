from pathlib import Path
import json

from presecurity.intent import parse_changed_files
from presecurity.autofix import apply_autofix
from presecurity.cli import main
from presecurity.doctor import run_doctor
from presecurity.scanner import scan
from presecurity.state import ensure_state, write_plan


def test_scan_detects_yaml_and_eval(tmp_path: Path):
    (tmp_path / "app.py").write_text("import yaml\nvalue = yaml.load(body)\n", encoding="utf-8")  # presecurity: ignore
    (tmp_path / "app.js").write_text("eval(input)\n", encoding="utf-8")

    plan = scan(tmp_path)

    rule_ids = {finding["ruleId"] for finding in plan["findings"]}
    assert "python-yaml-unsafe-load" in rule_ids
    assert "javascript-eval" in rule_ids
    yaml_finding = next(finding for finding in plan["findings"] if finding["ruleId"] == "python-yaml-unsafe-load")
    assert yaml_finding["file"] == "app.py"
    assert yaml_finding["line"] == 2
    assert "yaml.load" in yaml_finding["evidence"]
    assert "app.py:2" in plan["summary"]["issueLocations"]


def test_autofix_applies_safe_yaml_fix(tmp_path: Path):
    target = tmp_path / "app.py"
    target.write_text("import yaml\nvalue = yaml.load(body)\n", encoding="utf-8")  # presecurity: ignore
    plan = scan(tmp_path)

    result = apply_autofix(tmp_path, plan)

    assert result["applied"]
    assert "yaml.safe_load" in target.read_text(encoding="utf-8")


def test_scan_excludes_common_false_positive_secrets(tmp_path: Path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "example.py").write_text('api_key = "fake-placeholder-secret"\n', encoding="utf-8")
    (tmp_path / "config.py").write_text('secret = "CHANGE-ME-PLACEHOLDER"\n', encoding="utf-8")

    plan = scan(tmp_path)

    assert "falsePositivesExcluded" not in plan["summary"]
    assert "hardcoded-secret" not in {finding["ruleId"] for finding in plan["findings"]}


def test_false_positives_are_not_written_to_plan_or_history(tmp_path: Path):
    (tmp_path / "template.ts").write_text("export const example = `SELECT * FROM users WHERE id = ${'demo'}`\n", encoding="utf-8")
    (tmp_path / "content.tsx").write_text("return <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(html) }} />\n", encoding="utf-8")

    plan = scan(tmp_path)
    write_plan(tmp_path, plan)
    state = json.loads((tmp_path / ".presecurity" / "scan-plan.json").read_text(encoding="utf-8"))
    history = (tmp_path / ".presecurity" / "history.jsonl").read_text(encoding="utf-8")

    assert state["findings"] == []
    assert state["plan"] == []
    assert "template.ts" not in history
    assert "content.tsx" not in history
    assert "falsePositive" not in json.dumps(state)


def test_autofix_handles_react_finding_and_packages(tmp_path: Path):
    target = tmp_path / "page.tsx"
    target.write_text("export function Page({html}) { return <div dangerouslySetInnerHTML={{__html: html}} /> }\n", encoding="utf-8")

    plan = scan(tmp_path)
    result = apply_autofix(tmp_path, plan)
    updated = target.read_text(encoding="utf-8")

    assert result["applied"]
    assert "DOMPurify.sanitize(html)" in updated
    assert "from 'dompurify'" in updated
    assert result["packages"] == [{"ecosystem": "npm", "ok": False, "reason": "package.json not found"}]


def test_all_findings_are_planned_for_autofix(tmp_path: Path):
    (tmp_path / "app.js").write_text("eval(input)\n", encoding="utf-8")

    plan = scan(tmp_path)

    assert plan["summary"]["autofixable"] == plan["summary"]["findings"]
    assert plan["plan"][0]["autofix"] == "agent_intent_fix"


def test_autofix_parameterizes_obvious_sql_template(tmp_path: Path):
    target = tmp_path / "repo.ts"
    target.write_text("const sql = `SELECT * FROM users WHERE id = ${userId}`\n", encoding="utf-8")

    plan = scan(tmp_path)
    result = apply_autofix(tmp_path, plan)
    updated = target.read_text(encoding="utf-8")

    assert result["applied"]
    assert "${userId}" not in updated
    assert "?" in updated
    assert "presecurity params: userId" in updated


def test_scan_omits_sanitized_react_html(tmp_path: Path):
    target = tmp_path / "content.tsx"
    target.write_text("return <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(html) }} />\n", encoding="utf-8")

    plan = scan(tmp_path)

    assert "react-dangerously-set-html" not in {finding["ruleId"] for finding in plan["findings"]}


def test_scan_omits_sanitized_react_html_variable(tmp_path: Path):
    target = tmp_path / "NotiPopupModal.tsx"
    target.write_text(
        "const safeHtml = DOMPurify.sanitize(content)\n"
        "return <div dangerouslySetInnerHTML={{ __html: safeHtml }} />\n",
        encoding="utf-8",
    )

    plan = scan(tmp_path)

    assert "react-dangerously-set-html" not in {finding["ruleId"] for finding in plan["findings"]}


def test_scan_omits_regexp_exec_false_positive(tmp_path: Path):
    target = tmp_path / "messageTextParser.ts"
    target.write_text(
        "MESSAGE_TEXT_PATTERN.exec(messageContent)\n"
        "SIMPLE_MESSAGE_TEXT_PATTERN.exec(messageContent)\n",
        encoding="utf-8",
    )

    plan = scan(tmp_path)

    assert "node-child-process-exec" not in {finding["ruleId"] for finding in plan["findings"]}


def test_scan_detects_real_child_process_exec(tmp_path: Path):
    (tmp_path / "runner.ts").write_text("child_process.exec(command)\nexec(command)\n", encoding="utf-8")

    plan = scan(tmp_path)

    rule_ids = [finding["ruleId"] for finding in plan["findings"]]
    assert rule_ids.count("node-child-process-exec") == 2


def test_scan_omits_env_backed_fetch_ssrf_false_positive(tmp_path: Path):
    target = tmp_path / "serverAction.ts"
    target.write_text(
        "const url = `${API_BASE_URL}/users`\n"
        "await fetch(url)\n"
        "await fetch(`${process.env.API_BASE_URL}/health`)\n",
        encoding="utf-8",
    )

    plan = scan(tmp_path)

    assert "ssrf-unvalidated-url" not in {finding["ruleId"] for finding in plan["findings"]}


def test_scan_omits_relative_fetch_ssrf_false_positive(tmp_path: Path):
    target = tmp_path / "client.ts"
    target.write_text(
        "await fetch(`/api/users/${id}`)\n"
        "const path = `/internal/jobs/${jobId}`\n"
        "await fetch(path)\n",
        encoding="utf-8",
    )

    plan = scan(tmp_path)

    assert "ssrf-unvalidated-url" not in {finding["ruleId"] for finding in plan["findings"]}


def test_autofix_drops_stale_false_positive_plan_items(tmp_path: Path):
    target = tmp_path / "messageTextParser.ts"
    target.write_text("MESSAGE_TEXT_PATTERN.exec(messageContent)\n", encoding="utf-8")
    stale_plan = {
        "findings": [
            {
                "id": "stale-fp",
                "ruleId": "node-child-process-exec",
                "file": "messageTextParser.ts",
                "line": 1,
                "evidence": "MESSAGE_TEXT_PATTERN.exec(messageContent)",
                "autofix": "agent_intent_fix",
            }
        ],
        "plan": [
            {
                "findingId": "stale-fp",
                "ruleId": "node-child-process-exec",
                "file": "messageTextParser.ts",
                "line": 1,
                "autofix": "agent_intent_fix",
            }
        ],
    }

    result = apply_autofix(tmp_path, stale_plan)

    assert result["applied"] == []
    assert result["skipped"] == []
    assert target.read_text(encoding="utf-8") == "MESSAGE_TEXT_PATTERN.exec(messageContent)\n"
    state = json.loads((tmp_path / ".presecurity" / "scan-plan.json").read_text(encoding="utf-8"))
    assert state["findings"] == []
    assert state["plan"] == []


def test_autofix_drops_stale_line_mismatch_items(tmp_path: Path):
    target = tmp_path / "app.js"
    target.write_text("const value = 1\n", encoding="utf-8")
    stale_plan = {
        "findings": [
            {
                "id": "stale-eval",
                "ruleId": "javascript-eval",
                "file": "app.js",
                "line": 1,
                "evidence": "eval(input)",
                "autofix": "agent_intent_fix",
            }
        ],
        "plan": [
            {
                "findingId": "stale-eval",
                "ruleId": "javascript-eval",
                "file": "app.js",
                "line": 1,
                "autofix": "agent_intent_fix",
            }
        ],
    }

    result = apply_autofix(tmp_path, stale_plan)

    assert result["applied"] == []
    assert result["skipped"] == []
    assert "presecurity agent-fix" not in target.read_text(encoding="utf-8")


def test_cli_autofix_rescans_before_applying_stale_plan(tmp_path: Path):
    target = tmp_path / "messageTextParser.ts"
    target.write_text("MESSAGE_TEXT_PATTERN.exec(messageContent)\n", encoding="utf-8")
    ensure_state(tmp_path)
    stale_plan = {
        "schema": 1,
        "findings": [
            {
                "id": "stale-fp",
                "ruleId": "node-child-process-exec",
                "file": "messageTextParser.ts",
                "line": 1,
                "evidence": "MESSAGE_TEXT_PATTERN.exec(messageContent)",
                "autofix": "agent_intent_fix",
            }
        ],
        "plan": [
            {
                "findingId": "stale-fp",
                "ruleId": "node-child-process-exec",
                "file": "messageTextParser.ts",
                "line": 1,
                "autofix": "agent_intent_fix",
            }
        ],
    }
    (tmp_path / ".presecurity" / "scan-plan.json").write_text(json.dumps(stale_plan), encoding="utf-8")

    exit_code = main(["--root", str(tmp_path), "autofix"])

    assert exit_code == 0
    assert target.read_text(encoding="utf-8") == "MESSAGE_TEXT_PATTERN.exec(messageContent)\n"
    refreshed = json.loads((tmp_path / ".presecurity" / "scan-plan.json").read_text(encoding="utf-8"))
    assert refreshed["findings"] == []
    assert refreshed["plan"] == []


def test_scan_omits_template_and_css_selector_sql_false_positives(tmp_path: Path):
    (tmp_path / "template.ts").write_text("export const example = `SELECT * FROM users WHERE id = ${'demo'}`\n", encoding="utf-8")
    (tmp_path / "useImageExport.ts").write_text("export const css = `user-select: none; color: ${color};`\n", encoding="utf-8")

    plan = scan(tmp_path)

    assert "sql-string-concat" not in {finding["ruleId"] for finding in plan["findings"]}


def test_scan_detects_popular_platform_rules(tmp_path: Path):
    (tmp_path / "page.tsx").write_text("const key = 'NEXT_PUBLIC_SECRET_TOKEN'\n", encoding="utf-8")
    (tmp_path / "UserController.java").write_text("Runtime.getRuntime().exec(cmd);\n", encoding="utf-8")
    (tmp_path / "query.go").write_text('fmt.Sprintf("SELECT * FROM users WHERE id=%s", id)\n', encoding="utf-8")  # presecurity: ignore
    (tmp_path / "view.rb").write_text("comment.body.html_safe\n", encoding="utf-8")
    (tmp_path / "repo.php").write_text("DB::raw($sql);\n", encoding="utf-8")
    (tmp_path / "main.tf").write_text('"Action" = "*"\n', encoding="utf-8")
    (tmp_path / "pod.yaml").write_text("hostPath:\n  path: /var/run/docker.sock\n", encoding="utf-8")

    plan = scan(tmp_path)

    rule_ids = {finding["ruleId"] for finding in plan["findings"]}
    assert "nextjs-public-secret" in rule_ids
    assert "java-runtime-exec" in rule_ids
    assert "go-sql-format" in rule_ids
    assert "rails-html-safe" in rule_ids
    assert "php-laravel-raw-query" in rule_ids
    assert "terraform-iam-wildcard" in rule_ids
    assert "kubernetes-hostpath" in rule_ids


def test_docker_root_rule_skips_non_root_user(tmp_path: Path):
    (tmp_path / "Dockerfile").write_text("FROM python:3.12\nUSER app\n", encoding="utf-8")

    plan = scan(tmp_path)

    assert "docker-root-user" not in {finding["ruleId"] for finding in plan["findings"]}


def test_parse_changed_files_summarizes_security_hints():
    diff = """diff --git a/api.ts b/api.ts
+++ b/api.ts
+router.post('/users/:id', async (req, res) => {
+  const user = await User.findById(req.params.id)
+  res.json(user)
+})
"""

    changed = parse_changed_files(diff)

    assert changed[0].path == "api.ts"
    assert changed[0].added == 4
    assert "api-entrypoint" in changed[0].hints
    assert "database-access" in changed[0].hints


def test_doctor_reports_initialized_state(tmp_path: Path):
    ensure_state(tmp_path)

    result = run_doctor(tmp_path)

    assert result["summary"] in {"ready", "environment issue"}
    assert any(item["name"] == ".presecurity" and item["ok"] for item in result["checks"])
    assert any(item["name"] == "rules" and item["ok"] for item in result["checks"])
