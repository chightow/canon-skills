# MCP Migration Plan

## Overview
Transition the `canon` project from a script-based workflow to a Model Context Protocol (MCP) architecture. This will provide a native, cross-platform way for AI agents to interact with the project state while maintaining the existing web-based dashboard and legacy scripts.

## Architecture Goals
- **Language:** .NET (C#) (leveraging user expertise for high performance and type safety).
- **State:** Shared file-system state (keep `.tickets/`, `HANDOFF.md`, etc.).
- **Compatibility:** MCP tools will operate on the same files as the legacy bash/powershell scripts.

## Phase 1: Foundation & Read Tools
- [x] **MCP Server Setup:** Initialize a Python MCP server using the `mcp` SDK.
- [x] **Project Context:** Implement a robust `find_project_root` utility (shared with `server.py`).
- [x] **Tool: `get_sprint_board`:** 
    - Parse `.tickets/` and `HANDOFF.md`.
    - Return structured JSON of all tickets, statuses, and acceptance criteria.
- [x] **Tool: `open_dashboard`:**
    - Trigger the existing `sprint-check` logic to open the web UI in the default browser.

## Phase 2: Write Tools (The "Action" Layer)
- [ ] **Tool: `create_sprint_ticket`:**
    - Input: `description`, `priority`.
    - Action: Create `ticket.md` in `.tickets/`, initialize `acceptance.md` and `test_plan.md`.
- [ ] **Tool: `update_ticket_status`:**
    - Input: `ticket_id`, `new_status`.
    - Action: Update the frontmatter of the corresponding ticket.
- [ ] **Tool: `add_acceptance_criterion`:**
    - Input: `ticket_id`, `criterion_text`.
    - Action: Append to the `acceptance.md` of the specified ticket.

## Phase 3: Advanced Workflow & Gates
- [ ] **Tool: `close_sprint`:**
    - Action: 
        - Validate "Mechanical close gates" (Checkboxes, Summary, Wrapup).
        - Generate the "Delivery Receipt" table.
        - Update `HANDOFF.md` with the final summary.
- [ ] **Skill Integration:** Map `skills.sh` registration to MCP tool calls.

## Legacy Support
- Keep all `.sh` and `.ps1` scripts in place.
- Ensure MCP tools use the same file paths and naming conventions to prevent state divergence.
