---
name: context-check
description: Audit the always-on context budget — import sizes, active skills, hooks, memory — plus content quality of key markdowns (redundancy, vague rules, dead references). Appends findings only on explicit confirmation.
category: agent-ops
tags: [context, tokens, efficiency, audit]
---

# Context Check

Audit what Claude loads on every session. Maintains `standards/context-findings.md` as a running evidence log — append only on explicit confirmation.

## Steps

1. **Known findings.** Read `standards/context-findings.md` from the canon repo root. Note which issues are already logged — skip re-flagging them in step 6.

2. **Imports.** Read `~/.claude/CLAUDE.md`. For each `@` import line, measure the imported file's line count. Produce a table:
   | File | Lines |
   |------|-------|

3. **Active skills.** Run `skills.sh status` from the repo root. List registered skills and their file sizes.

4. **Hooks.** Read `~/.claude/settings.json`. List all configured hooks, their matchers, and the scripts they invoke.

5. **Memory.** List files under `~/.claude/projects/*/memory/`. Report total file count and combined size.

6. **Flag size issues.** Flag any item where: line count > 30 and less than half is relevant to most sessions, or a section exists solely for a single rarely-needed purpose (e.g., install verification, one-time setup). Skip anything already in context-findings.md.

7. **Content audit.** Read the full text of every file imported via `@` in `~/.claude/CLAUDE.md`, plus `AGENTS.md` from the canon repo. Flag only high-confidence issues — skip anything borderline. Four checks:

   - **Cross-file redundancy** — the same rule or constraint appears in two or more files, verbatim or near-verbatim. Quote both occurrences.
   - **Obvious statements** — rules a capable model follows from training without being told (e.g., "don't write syntax errors", "be helpful"). Distinguishable from non-obvious rules like "never use git add -A" which are codebase-specific.
   - **Vague non-actionable rules** — instructions with no specific guidance on how to comply. An agent reading "be concise" with no further definition cannot act on it differently than without it.
   - **Dead references** — mentions of specific files, paths, tools, or commands that no longer exist in the repo or system. Verify by checking the path or grepping for the tool name.

   Report content findings separately from size findings.

8. **Report.** Present the size audit table, then content findings. If no new findings in either: say so and stop here.

9. **Confirm before writing.** If new findings exist, ask: "Append these to context-findings.md? (y to confirm)." Do not write without an explicit yes.

## context-findings.md entry format

```
### YYYY-MM-DD — Short title
**File:** path
**Issue:** what was found
**Action:** what was done (or "Open — no action yet")
```

Keep entries concise. When the file exceeds 60 lines, archive (delete) entries older than 6 months before appending.
