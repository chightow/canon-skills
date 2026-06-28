import atexit
import os
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
    """List all skills or get a specific skill by name."""
    return cmd.list_skills(PROJECT_ROOT / "skills", skill_name)


@app.tool()
def ticket(
    action: Literal["get", "status", "doc", "add_criterion"],
    ticket_id: str,
    new_status: Optional[Literal["open", "in_progress", "closed", "cancelled", "archived"]] = None,
    doc_name: Optional[Literal["acceptance", "plan", "test_plan", "summary", "body"]] = None,
    content: str = "",
    criterion: str = "",
) -> Dict[str, Any]:
    """Manage tickets: get info, update status, read/write docs, add acceptance criteria.

    Actions:
    - get: read ticket and all companion files
    - status: change ticket status (requires new_status)
    - doc: read (no content) or write (with content) a document
    - add_criterion: append acceptance criterion (requires criterion)
    """
    tickets_dir = PROJECT_ROOT / ".tickets"

    if action == "get":
        return cmd.get_ticket(tickets_dir, ticket_id)

    if action == "status":
        if not new_status:
            return {"status": "error", "message": "new_status required for status action"}
        return cmd.update_ticket_status(tickets_dir, ticket_id, new_status)

    if action == "doc":
        if not doc_name:
            return {"status": "error", "message": "doc_name required for doc action"}
        if content:
            if doc_name == "body":
                return cmd.update_ticket_body(tickets_dir, ticket_id, content)
            return cmd.write_doc(tickets_dir, ticket_id, f"{doc_name}.md", content)
        if doc_name == "body":
            ticket_file = tickets_dir / ticket_id / "ticket.md"
            if not ticket_file.exists():
                return {"status": "error", "message": f"Ticket '{ticket_id}' not found"}
            return {"ticket_id": ticket_id, "body": ticket_file.read_text(encoding='utf-8')}
        return cmd.read_doc(tickets_dir, ticket_id, f"{doc_name}.md")

    if action == "add_criterion":
        if not criterion:
            return {"status": "error", "message": "criterion required for add_criterion action"}
        return cmd.add_acceptance_criterion(tickets_dir, ticket_id, criterion)

    return {"status": "error", "message": f"Unknown action: {action}"}


@app.tool()
def sprint(
    action: Literal["start", "board", "close"],
    title: str = "",
    ticket_id: str = "",
    priority: Literal["low", "medium", "high"] = "medium",
) -> Dict[str, Any]:
    """Manage sprints: start a new one, view board, close.

    Actions:
    - start: create new ticket (provide title) or resume existing (provide ticket_id)
    - board: show sprint tickets + handoff context
    - close: validate gates, generate receipt, update HANDOFF.md
    """
    if action == "start":
        if not title and not ticket_id:
            return {"status": "error", "message": "Provide title (new ticket) or ticket_id (existing)."}
        if title and ticket_id:
            return {"status": "error", "message": "Provide title or ticket_id, not both."}
        return sp.start_sprint(PROJECT_ROOT, title, ticket_id, priority)

    if action == "board":
        return sp.get_sprint_board(PROJECT_ROOT)

    if action == "close":
        return sp.close_sprint(PROJECT_ROOT)

    return {"status": "error", "message": f"Unknown action: {action}"}


@app.tool()
def git_info() -> Dict[str, Any]:
    """Show branch, recent commits, modified file count."""
    return cmd.git_info(PROJECT_ROOT)


@app.tool()
def log_subagent_run(
    agent_id: str,
    agent_type: str = "agent",
    session_id: str = "",
) -> Dict[str, Any]:
    """Log evaluator run to audit trail (internal)."""
    return sp.log_subagent_run(PROJECT_ROOT, agent_id, agent_type, session_id)


@app.tool()
def open_dashboard() -> Dict[str, Any]:
    """Launch local kanban dashboard in browser (human use only)."""
    try:
        port = _dashboard_port()
        if port is None:
            port = _find_free_port()
            if not _start_dashboard(port):
                return {"status": "error", "message": f"Dashboard failed to start on port {port}"}
        url = f"http://127.0.0.1:{port}"
        _open_browser(url)
        return {"status": "ok", "url": url}
    except Exception as e:
        print(f"Failed to launch dashboard: {e}", file=sys.stderr)
        return {"status": "error", "message": f"Failed to launch dashboard: {e}"}


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
