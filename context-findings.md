---
name: context-findings
description: Running evidence log of context efficiency findings — bloat identified, optimizations made, open items.
category: agent-ops
tags: [context, tokens, efficiency]
hidden: true
---

# Context Findings

Evidence log for context efficiency. Paired with `standards/efficiency.md` (rules) — this file is the observations.

Run `/context-check` to generate new findings. Append only on explicit confirmation.

---

### 2026-05-23 — CLAUDE.md Approach block duplicates AGENTS.md
**File:** `~/.claude/CLAUDE.md` ↔ `AGENTS.md`
**Issue:** Near-verbatim duplicate of the Approach section. CLAUDE.md imports AGENTS.md, so both loaded every session. ~8 redundant lines.
**Action:** Removed entire Approach block from CLAUDE.md; kept only the "User instructions override" note and @imports.

### 2026-05-23 — AGENTS.md Standards section duplicates efficiency.md
**File:** `AGENTS.md` ↔ `standards/efficiency.md`
**Issue:** Five rules duplicated exactly across both files. Both imported separately — all appeared twice in context.
**Action:** Collapsed AGENTS.md `## Standards` to the pointer line only; removed the Key rules block.

### 2026-05-23 — "No sycophantic openers" duplicated in CLAUDE.md and AGENTS.md
**File:** `~/.claude/CLAUDE.md` ↔ `AGENTS.md`
**Issue:** Identical rule in both files, both loaded every session.
**Action:** Removed from CLAUDE.md; AGENTS.md is the canonical home.

