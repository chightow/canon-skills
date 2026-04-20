---
name: handoff
description: Session context handoff protocol — keeps Claude and Codex in sync across repos and agents
category: tools
tags: [context, memory, handoff, multi-agent]
---

# Handoff — Session Context Protocol

Preserves working context across sessions and agents using a `HANDOFF.md` file in the repo root. Bridges the gap between Claude, Codex, Pi, and any future agent — so the next session picks up where the last one left off.

---

## The problem it solves

AI agents don't share memory. When you switch from Codex to Claude (or vice versa), or when a context window fills up mid-session, the new agent starts completely cold. Without handoff, you spend the first 10 minutes re-explaining where things stand.

`HANDOFF.md` is the shared state — a lightweight, git-tracked snapshot that any agent can read.

---

## Getting Started — Pick Your Level

Choose the level that matches your project's complexity. Each level builds on the previous.

---

### Level 1 — Manual (any agent, no hooks)

Best for: simple projects, occasional agent switching.

**Step 1 — Register the skill in your project:**
```bash
~/Developer/AI-Skills/skills.sh add handoff /path/to/your/project
```

**Step 2 — Verify:**
```bash
~/Developer/AI-Skills/skills.sh status /path/to/your/project
```

**Step 3 — Initialize `HANDOFF.md` in the repo root:**

Tell the agent: "Initialize the handoff file" — it creates it from the template. Or run:
```bash
curl -s https://raw.githubusercontent.com/<your-ai-skills-repo>/main/tools/handoff.md \
  | awk '/^```markdown$/,/^```$/{if(!/^```/)print}' > HANDOFF.md
```

Or just create it manually using the template at the bottom of this file.

**Step 4 — Use it:**
- **Session start**: Tell the agent "Read HANDOFF.md and summarize where we are."
- **During session**: The agent updates it when significant decisions are made.
- **Session end**: Tell the agent "wrap up" — it updates `HANDOFF.md` and commits it.
- **Next session / switching agents**: The next agent reads `HANDOFF.md` before starting work.

---

### Level 2 — Automated (Claude Code with hooks)

Best for: long sessions, frequent context limit hits, heavy Claude Code usage.

Adds two hooks to Claude Code's global settings:
- **`Stop` hook** — auto-saves a snapshot of git state to `HANDOFF.md` whenever Claude stops. Safety net for context window exhaustion.
- **`UserPromptSubmit` hook** — injects `HANDOFF.md` into the first prompt of each session. Claude wakes up knowing where things stand without you having to ask.

**Step 1 — Complete Level 1 first.**

**Step 2 — Copy the two hook scripts to your AI-Skills repo:**
```bash
# Already included in AI-Skills at:
ls ~/Developer/AI-Skills/scripts/
# auto-handoff.sh   — Stop hook
# handoff-inject.sh — UserPromptSubmit hook
```

**Step 3 — Add the hooks to `~/.claude/settings.json`:**

Open `~/.claude/settings.json` and add to the `"hooks"` object:
```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "~/Developer/AI-Skills/scripts/auto-handoff.sh"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "~/Developer/AI-Skills/scripts/handoff-inject.sh"
          }
        ]
      }
    ]
  }
}
```

**Step 4 — Verify hooks are active:**
```bash
cat ~/.claude/settings.json | grep -A5 "Stop\|UserPromptSubmit"
```

**What happens automatically from here:**
- Open a project → Claude reads `HANDOFF.md` silently on your first message (once per 4-hour window)
- Context window fills → Stop hook saves current git state to `HANDOFF.md` and commits it
- Next session → Claude picks up from the snapshot, no re-explaining needed

---

### Level 3 — Full multi-agent (Claude + Codex + Pi)

Best for: teams or workflows that switch between multiple agents on the same repo.

**The shared file is still `HANDOFF.md`** — all agents read and write the same file. What differs is how each agent's automation is wired.

#### Codex

Codex reads `AGENTS.md` natively. Since `skills.sh add handoff` already writes to `AGENTS.md`, Codex will follow the handoff instructions automatically.

For the Stop hook equivalent, add to `~/.codex/config.toml`:
```toml
[hooks]
on_session_end = "~/Developer/AI-Skills/scripts/auto-handoff.sh"
```
> Note: Codex hook support varies by version. Check `codex --help` or the Codex docs for your installed version.

#### Pi

Pi reads `~/.pi/agent/AGENTS.md` (or your project's `AGENTS.md`). Since handoff instructions are in `AGENTS.md` via `skills.sh add`, Pi follows them automatically.

For session-end automation, check Pi's config for a `on_exit` or `hooks` key — wire it to `auto-handoff.sh` the same way.

#### Manual fallback (any agent without hook support)

Before ending any session, say: **"wrap up"** — the agent updates `HANDOFF.md` and commits it. This works in every agent that has loaded the handoff skill.

---

## How the hooks behave

### `Stop` hook (`auto-handoff.sh`)

- Runs every time Claude stops responding
- **Skips silently** if the working tree is clean (nothing changed)
- If there are uncommitted changes: appends a timestamped auto-snapshot to `HANDOFF.md`
- Commits just `HANDOFF.md` — no other files touched
- Safe to run frequently — idempotent

### `UserPromptSubmit` hook (`handoff-inject.sh`)

- Runs before every user message is sent to Claude
- **Injects `HANDOFF.md` only once per 4-hour window** per project — not on every prompt
- If no `HANDOFF.md` exists in the project: exits silently, no injection
- Token cost: ~200-400 tokens on session start only, zero overhead after

---

## HANDOFF.md Template

```markdown
# Handoff

_Last updated: YYYY-MM-DD HH:MM by <agent> (<model>)_

## Current Focus
One sentence: what are we working on right now.

## In Progress
- file/path or ticket-id: what's started but not finished

## Recent Decisions
- Decision made and WHY (not what — the diff shows what)

## Dead Ends
- What was tried and didn't work, so the next agent doesn't repeat it

## Open Questions
- Unresolved things that need a decision before proceeding

## Next Steps
1. First concrete next action
2. Second
```

---

## Rules

- **Keep it short.** This is a handoff note, not a journal. Prune old entries freely.
- **Current Focus is one sentence max.**
- **Decisions capture WHY** — the git diff already shows what changed.
- **Always commit before ending a session.** An uncommitted handoff is useless.
- **No secrets, credentials, or env-specific values** in this file — it's committed to git.
- **The auto-snapshot section** (added by the Stop hook) is mechanical. Fill in Current Focus and Decisions manually for full context.
