import atexit
import os
import re
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Dict, Any, Optional, Literal

from mcp.server.fastmcp import FastMCP
from mcp_server.utils.project_context import find_project_root
from mcp_server.utils import commands as cmd
from mcp_server.utils import sprint as sp

app = FastMCP("canon-mcp-server")

PROJECT_ROOT = find_project_root(Path(__file__).parent.parent.resolve())

_dashboard_proc: Optional[subprocess.Popen] = None


def _ok(**data: Any) -> Dict[str, Any]:
    return {"status": "ok", "data": data}


def _err(message: str) -> Dict[str, Any]:
    return {"status": "error", "data": {}, "message": message}


def _wrap(result: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize internal function return to {status, data, message?}."""
    if "error" in result:
        return _err(result["error"])
    if result.get("status") == "error":
        return _err(result.get("message", "Unknown error"))
    data = {k: v for k, v in result.items() if k != "status"}
    return {"status": "ok", "data": data}


def _cleanup_dashboard() -> None:
    global _dashboard_proc
    if _dashboard_proc is not None and _dashboard_proc.poll() is None:
        _dashboard_proc.terminate()
        try:
            _dashboard_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _dashboard_proc.kill()


atexit.register(_cleanup_dashboard)


@app.tool()
def list_skills(skill_name: Optional[str] = None) -> Dict[str, Any]:
    """List all skills. Omit skill_name for catalog, provide one for full details."""
    return _wrap(cmd.list_skills(PROJECT_ROOT / "skills", skill_name))


@app.tool()
def ticket(
    action: Literal["get", "status", "doc", "add_criterion"],
    ticket_id: str,
    new_status: Optional[Literal["open", "in_progress", "closed", "cancelled", "archived"]] = None,
    doc_name: Optional[Literal["acceptance", "plan", "test_plan", "summary", "body"]] = None,
    content: str = "",
    criterion: str = "",
) -> Dict[str, Any]:
    """Manage tickets. Actions:
    - get: read ticket + all companion files (acceptance, plan, test_plan, summary)
    - status: change ticket status (requires new_status)
    - doc: read (omit content) or write (provide content) a document
    - add_criterion: append acceptance criterion to acceptance.md

    Hint: for doc action, doc_name=body reads/writes the ticket body.
    Leave content empty to read, provide text to write/overwrite.
    """
    if action == "get":
        return _wrap(cmd.get_ticket(PROJECT_ROOT / ".tickets", ticket_id))

    if action == "status":
        if not new_status:
            return _err("new_status required for status action")
        return _wrap(cmd.update_ticket_status(PROJECT_ROOT / ".tickets", ticket_id, new_status))

    if action == "doc":
        if not doc_name:
            return _err("doc_name required: acceptance, plan, test_plan, summary, or body")
        if not content:
            if doc_name == "body":
                return _wrap(cmd.get_ticket(PROJECT_ROOT / ".tickets", ticket_id))
            return _wrap(cmd.read_doc(PROJECT_ROOT / ".tickets", ticket_id, f"{doc_name}.md"))
        if doc_name == "body":
            return _wrap(cmd.update_ticket_body(PROJECT_ROOT / ".tickets", ticket_id, content))
        return _wrap(cmd.write_doc(PROJECT_ROOT / ".tickets", ticket_id, f"{doc_name}.md", content))

    if action == "add_criterion":
        if not criterion:
            return _err("criterion text required for add_criterion action")
        return _wrap(cmd.add_acceptance_criterion(PROJECT_ROOT / ".tickets", ticket_id, criterion))

    return _err(f"Unknown action: {action}")


@app.tool()
def sprint(
    action: Literal["start", "board", "close"],
    title: str = "",
    ticket_id: str = "",
    priority: Literal["low", "medium", "high"] = "medium",
) -> Dict[str, Any]:
    """Manage sprints. Actions:
    - start: create a new sprint ticket (provide title) or resume an existing one (provide ticket_id)
    - board: show current sprint tickets + handoff context
    - close: validate gates, log eval runs, generate receipt, update HANDOFF.md

    Hint: sprint(close) automatically logs all evaluator runs found in eval-report.md.
    No need to log them separately.
    """
    if action == "start":
        if not title and not ticket_id:
            return _err("Provide title (new ticket) or ticket_id (existing), not both.")
        if title and ticket_id:
            return _err("Provide title or ticket_id, not both.")
        return _wrap(sp.start_sprint(PROJECT_ROOT, title, ticket_id, priority))

    if action == "board":
        return _wrap(sp.get_sprint_board(PROJECT_ROOT))

    if action == "close":
        _auto_log_eval_runs()
        return _wrap(sp.close_sprint(PROJECT_ROOT))

    return _err(f"Unknown action: {action}")


@app.tool()
def git_info() -> Dict[str, Any]:
    """Show git branch, recent commits, modified file count."""
    return _wrap(cmd.git_info(PROJECT_ROOT))


def _auto_log_eval_runs() -> None:
    """Find all eval-report.md files and log their evaluator-run-ids."""
    if not (PROJECT_ROOT / ".tickets").exists():
        return
    for d in (PROJECT_ROOT / ".tickets").iterdir():
        if not d.is_dir():
            continue
        report = d / "eval-report.md"
        if not report.exists():
            continue
        content = report.read_text(encoding="utf-8")
        m = re.search(r"^evaluator-run-id:\s+(\S+)", content, re.MULTILINE)
        if m:
            sp.log_subagent_run(PROJECT_ROOT, m.group(1))


def _dashboard_port() -> Optional[int]:
    """Return the port of an already-running dashboard, or None."""
    for port in range(8423, 8431):
        try:
            resp = urllib.request.urlopen(f"http://127.0.0.1:{port}/api/tickets?all=1", timeout=0.5)
            if resp.status == 200:
                return port
        except OSError:
            continue
    return None


def _find_free_port(start: int = 8423, end: int = 8430) -> int:
    """Find a free TCP port in range [start, end]."""
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"No free port found in range {start}-{end}")


def _start_dashboard(port: int) -> bool:
    """Launch sprint-check server on the given port as a background process.
    Returns True once the dashboard is confirmed responding.
    """
    global _dashboard_proc
    env = {**os.environ, "SPRINT_CHECK_ROOT": str(PROJECT_ROOT)}

    if sys.platform == "win32":
        server_script = PROJECT_ROOT / "tools" / "sprint-check-app" / "server.py"
        dash_cmd = [sys.executable, str(server_script), str(port)]
        creationflags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        script_path = PROJECT_ROOT / "tools" / "sprint-check"
        dash_cmd = ["bash", str(script_path), str(port)]
        creationflags = 0

    _dashboard_proc = subprocess.Popen(
        dash_cmd,
        cwd=str(PROJECT_ROOT),
        env=env,
        creationflags=creationflags,
    )

    time.sleep(0.5)
    if _dashboard_proc.poll() is not None:
        _dashboard_proc = None
        return False

    for _ in range(10):
        try:
            resp = urllib.request.urlopen(
                f"http://127.0.0.1:{port}/api/tickets?all=1", timeout=0.5
            )
            ok = resp.status == 200
            resp.close()
            if ok:
                return True
        except Exception:
            pass
        time.sleep(0.3)
    _dashboard_proc.terminate()
    try:
        _dashboard_proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        _dashboard_proc.kill()
    _dashboard_proc = None
    return False


def _open_browser(url: str) -> None:
    """Open a URL in the default browser using platform-specific commands."""
    if sys.platform == "win32":
        try:
            subprocess.run(["cmd.exe", "/c", "start", url], check=True)
            return
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
    elif sys.platform == "darwin":
        try:
            subprocess.run(["open", url], check=True)
            return
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
    elif sys.platform == "linux":
        for c in ["xdg-open", "wslview"]:
            try:
                subprocess.run([c, url], check=True)
                return
            except (FileNotFoundError, subprocess.CalledProcessError):
                continue
    print(f"Open in your browser: {url}", file=sys.stderr)


if __name__ == "__main__":
    app.run()
