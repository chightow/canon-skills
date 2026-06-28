import json
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from mcp_server.server import (
    list_skills,
    ticket,
    sprint,
    git_info,
    _auto_log_eval_runs,
    _ok,
    _err,
    _wrap,
)
from mcp_server.utils.parsers import AGENT_RUN_LOG_PATHS


# ── Helper tests ──────────────────────────────────────────────────────────

class TestHelpers:
    def test_ok(self):
        assert _ok(foo="bar") == {"status": "ok", "data": {"foo": "bar"}}

    def test_ok_empty(self):
        assert _ok() == {"status": "ok", "data": {}}

    def test_err(self):
        assert _err("fail") == {"status": "error", "data": {}, "message": "fail"}

    def test_wrap_error_key(self):
        assert _wrap({"error": "not found"})["status"] == "error"

    def test_wrap_status_error(self):
        assert _wrap({"status": "error", "message": "nope"})["message"] == "nope"

    def test_wrap_ok_strips_status(self):
        r = _wrap({"ticket_id": "T-1", "status": "ok"})
        assert r["status"] == "ok"
        assert r["data"]["ticket_id"] == "T-1"
        assert "status" not in r["data"]

    def test_wrap_ok_no_status(self):
        r = _wrap({"branch": "main", "commits": []})
        assert r["status"] == "ok"
        assert r["data"] == {"branch": "main", "commits": []}


# ── Fixtures ──────────────────────────────────────────────────────────────

@pytest.fixture
def root(monkeypatch, tmp_path):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".tickets").mkdir()
    monkeypatch.setattr("mcp_server.server.PROJECT_ROOT", tmp_path)
    return tmp_path


@pytest.fixture
def ticket1(root):
    d = root / ".tickets" / "TKT-0001"
    d.mkdir()
    (d / "ticket.md").write_text(
        "---\nid: TKT-0001\ntitle: Test ticket\nstatus: open\npriority: high\n---\n\n"
        "## Description\nA test.\n",
        encoding="utf-8",
    )
    (d / "acceptance.md").write_text("## Acceptance Criteria\n- [ ] Item\n", encoding="utf-8")
    return "TKT-0001"


@pytest.fixture
def skills_dir(root):
    d = root / "skills"
    d.mkdir()
    sd = d / "sprint"
    sd.mkdir()
    (sd / "SKILL.md").write_text(
        "---\nname: sprint\ndescription: Sprint management\ntags: [agile]\nhidden: false\n---\n"
        "# Sprint skill\n",
        encoding="utf-8",
    )
    return d


# ── Standardized return shape ─────────────────────────────────────────────

SHAPE_KEYS = {"status", "data"}


def assert_ok(result):
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    missing = SHAPE_KEYS - result.keys()
    assert not missing, f"Missing keys: {missing}"
    assert result["status"] == "ok", f"Expected ok, got error: {result.get('message')}"
    assert isinstance(result["data"], dict)
    return result


def assert_err(result):
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    missing = SHAPE_KEYS - result.keys()
    assert not missing, f"Missing keys: {missing}"
    assert result["status"] == "error", "Expected error"
    assert "message" in result
    assert isinstance(result["data"], dict)
    return result


# ── list_skills ───────────────────────────────────────────────────────────

class TestListSkills:
    def test_list_all(self, root, skills_dir):
        r = assert_ok(list_skills())
        assert any(s["name"] == "sprint" for s in r["data"]["skills"])

    def test_get_by_name(self, root, skills_dir):
        r = assert_ok(list_skills(skill_name="sprint"))
        assert r["data"]["name"] == "sprint"

    def test_not_found(self, root, skills_dir):
        assert_err(list_skills(skill_name="nope"))


# ── ticket ────────────────────────────────────────────────────────────────

class TestTicket:
    def test_get(self, root, ticket1):
        r = assert_ok(ticket("get", ticket1))
        assert r["data"]["ticket_id"] == ticket1
        assert "ticket.md" in r["data"]["files"]

    def test_get_not_found(self, root):
        assert_err(ticket("get", "NONEXIST"))

    def test_status(self, root, ticket1):
        r = assert_ok(ticket("status", ticket1, new_status="closed"))
        assert r["data"]["new_status"] == "closed"

    def test_status_missing_param(self, root, ticket1):
        assert_err(ticket("status", ticket1))

    def test_doc_read_body(self, root, ticket1):
        r = assert_ok(ticket("doc", ticket1, doc_name="body"))
        assert "ticket.md" in r["data"]["files"]

    def test_doc_read_acceptance(self, root, ticket1):
        r = assert_ok(ticket("doc", ticket1, doc_name="acceptance"))
        assert "Item" in r["data"]["content"]

    def test_doc_write_body(self, root, ticket1):
        assert_ok(ticket("doc", ticket1, doc_name="body", content="# New body"))
        body = (root / ".tickets" / ticket1 / "ticket.md").read_text(encoding="utf-8")
        assert "New body" in body

    def test_doc_write_acceptance(self, root, ticket1):
        assert_ok(ticket("doc", ticket1, doc_name="acceptance", content="## AC\n- [ ] X"))
        content = (root / ".tickets" / ticket1 / "acceptance.md").read_text(encoding="utf-8")
        assert "X" in content

    def test_doc_missing_doc_name(self, root, ticket1):
        assert_err(ticket("doc", ticket1))

    def test_add_criterion(self, root, ticket1):
        r = assert_ok(ticket("add_criterion", ticket1, criterion="New item"))
        assert r["data"]["criterion"] == "New item"

    def test_add_criterion_missing_param(self, root, ticket1):
        assert_err(ticket("add_criterion", ticket1))

    def test_unknown_action(self, root, ticket1):
        assert_err(ticket("bogus", ticket1))


# ── sprint ────────────────────────────────────────────────────────────────

class TestSprint:
    def test_board(self, root):
        r = assert_ok(sprint("board"))
        assert "tickets" in r["data"]
        assert "handoff" in r["data"]

    def test_start_new(self, root):
        r = assert_ok(sprint("start", title="New task", priority="high"))
        tid = r["data"]["ticket_id"]
        assert (root / ".tickets" / tid).exists()

    def test_start_existing(self, root, ticket1):
        r = assert_ok(sprint("start", ticket_id=ticket1))
        assert r["data"]["ticket_id"] == ticket1

    def test_start_no_params(self, root):
        assert_err(sprint("start"))

    def test_start_both_params(self, root, ticket1):
        assert_err(sprint("start", title="X", ticket_id=ticket1))

    def test_close_no_tickets(self, root):
        assert_err(sprint("close"))

    def test_close_auto_logs_eval_run(self, root):
        now = int(time.time())
        tid = "TKT-CLOSE"
        tdir = root / ".tickets" / tid
        tdir.mkdir()
        (tdir / "ticket.md").write_text(
            f"---\nid: {tid}\ntitle: Closable\nstatus: closed\n---\n\nDone.\n",
            encoding="utf-8",
        )
        (tdir / "acceptance.md").write_text("## AC\n- [x] Done\n", encoding="utf-8")
        (tdir / "plan.md").write_text(
            "---\n---\n\n# Plan\n\n## Sign-off\n\n- [x] Approved\n\n## Decisions\n\n### Some\n\nReason: OK\n",
            encoding="utf-8",
        )
        (tdir / "eval-report.md").write_text(
            f"evaluator-run-id: {now}-0001\npass: all good\n",
            encoding="utf-8",
        )
        (root / "HANDOFF.md").write_text(
            "# Handoff\n\n## Active Tasks\n- Task\n", encoding="utf-8"
        )

        result = sprint("close")
        assert result["status"] == "ok", result.get("message")

        for rel in AGENT_RUN_LOG_PATHS:
            log_file = root / rel
            assert log_file.exists(), f"Missing {rel}"
            log_text = log_file.read_text(encoding="utf-8").strip()
            assert f"{now}-0001" in log_text, f"run_id not found in {rel}"

    def test_unknown_action(self, root):
        assert_err(sprint("bogus"))


# ── git_info ──────────────────────────────────────────────────────────────

class TestGitInfo:
    @patch("mcp_server.utils.commands.subprocess.check_output")
    def test_returns_info(self, mock_check_output, root):
        mock_check_output.side_effect = [
            "main\n",
            "abc|Alice|Initial\n",
            " M file.py\n",
        ]
        r = assert_ok(git_info())
        assert r["data"]["branch"] == "main"
        assert len(r["data"]["commits"]) == 1


# ── _auto_log_eval_runs ───────────────────────────────────────────────────

class TestAutoLogEvalRuns:
    def test_logs_runs_from_eval_reports(self, root):
        run_ids = {}
        for tid in ("TKT-A", "TKT-B"):
            run_id = f"{int(time.time())}-{tid}"
            run_ids[tid] = run_id
            tdir = root / ".tickets" / tid
            tdir.mkdir()
            (tdir / "eval-report.md").write_text(
                f"evaluator-run-id: {run_id}\npass: ok\n",
                encoding="utf-8",
            )

        _auto_log_eval_runs()

        for tid, expected_run_id in run_ids.items():
            found = False
            for rel in AGENT_RUN_LOG_PATHS:
                log_file = root / rel
                if log_file.exists() and expected_run_id in log_file.read_text(encoding="utf-8"):
                    found = True
                    break
            assert found, f"run_id {expected_run_id} not found in any log path"

    def test_writes_to_all_log_paths(self, root):
        tdir = root / ".tickets" / "TKT-X"
        tdir.mkdir()
        run_id = f"{int(time.time())}-xxx"
        (tdir / "eval-report.md").write_text(
            f"evaluator-run-id: {run_id}\npass: ok\n",
            encoding="utf-8",
        )

        _auto_log_eval_runs()

        for rel in AGENT_RUN_LOG_PATHS:
            log_file = root / rel
            assert log_file.exists(), f"Should have written to {rel}"

    def test_no_tickets_dir(self, root):
        # Remove .tickets dir
        import shutil
        shutil.rmtree(root / ".tickets")
        _auto_log_eval_runs()  # should not crash
