from pathlib import Path

from presecurity.intent import parse_changed_files
from presecurity.autofix import apply_autofix
from presecurity.doctor import run_doctor
from presecurity.scanner import scan
from presecurity.state import ensure_state


def test_scan_detects_yaml_and_eval(tmp_path: Path):
    (tmp_path / "app.py").write_text("import yaml\nvalue = yaml.load(body)\n", encoding="utf-8")  # presecurity: ignore
    (tmp_path / "app.js").write_text("eval(input)\n", encoding="utf-8")

    plan = scan(tmp_path)

    rule_ids = {finding["ruleId"] for finding in plan["findings"]}
    assert "python-yaml-unsafe-load" in rule_ids
    assert "javascript-eval" in rule_ids


def test_autofix_applies_safe_yaml_fix(tmp_path: Path):
    target = tmp_path / "app.py"
    target.write_text("import yaml\nvalue = yaml.load(body)\n", encoding="utf-8")  # presecurity: ignore
    plan = scan(tmp_path)

    result = apply_autofix(tmp_path, plan)

    assert result["applied"]
    assert "yaml.safe_load" in target.read_text(encoding="utf-8")


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
