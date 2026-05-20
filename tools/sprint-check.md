---
name: sprint-check
description: Local kanban dashboard for the current project — reads .tickets/, HANDOFF.md, and git log. Zero install beyond the canon repo.
category: tools
tags: [project-management, kanban, dashboard, gui]
---

# sprint-check — Local Kanban Dashboard

A browser-based kanban board that reads the current project's tickets, HANDOFF.md, and git history. No cloud, no login, no install beyond canon.

## Getting Started

**Step 1 — Add `canon/tools` to your PATH** (one-time, if not already done):
```bash
export PATH="<path-to-canon>/tools:$PATH"
```

**Step 2 — Launch from any canon project:**
```bash
sprint-check.sh
# or, from the canon repo itself:
tools/sprint-check.sh
```

The board opens in your default browser at `http://127.0.0.1:<port>`. Press `Ctrl+C` to stop.

## What It Shows

**Board — 4 columns mapping to tkt statuses:**

| Column | tkt status |
|--------|-----------|
| Open | `open` |
| In Progress | `in_progress` |
| Done | `closed` |
| Discarded | `cancelled` |

**Sidebar:**
- Current git branch + modified file count
- `## Current Focus` section from HANDOFF.md
- Last 5 git commits
- Ticket count summary by status

**Card expand (click any card or press Enter):**
- Full ticket body (markdown rendered)
- Status, type, priority, age
- Move status buttons (`← Back`, `Forward →`)
- Discard button
- Keyboard: `←` / `→` to move, `Esc` to close

## Agent Workflow

- sprint-check is read-only for agents — status changes happen via `tkt` commands
- Use it to orient at session start: "open sprint-check and tell me what's in progress"
- The sidebar's Current Focus reflects what's in HANDOFF.md — keep HANDOFF.md current for accurate sprint context

## Notes

- Refreshes automatically every 8 seconds
- Dark/light mode toggle in the header — remembers your preference
- Runs on macOS, Linux, and WSL (Python 3 stdlib only, no pip)
- Port defaults to 8423, increments if busy
