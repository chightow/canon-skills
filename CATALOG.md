# canon Catalog

> Static snapshot — run `skills.sh list` for live output.

## Standalone Skills

Register these directly into a project with `skills.sh add <name>`.

| Skill | Category | Description |
|---|---|---|
| `capture` | dev | Proactively record non-obvious discoveries to HANDOFF.md and memory — fires automatically mid-session, also invocable explicitly |
| `context-check` | agent-ops | Audit the always-on context budget — import sizes, active skills, hooks, memory — plus content quality of key markdowns |
| `doc-audit` | agent-ops | Audit user-facing docs for overstated claims, missing prerequisites, and scope inflation. Appends findings to standards/doc-findings.md |
| `sprint` | dev | Full dev workflow — plan, build, and ship focused units of work with acceptance-criteria-gated delivery |
| `wrapup` | dev | Quality pipeline after any unit of work — runs code-simplifier, code-reviewer, and security-review in sequence |

## Sub-skills

Imported automatically by the skills above. Do not register directly.

| Skill | Imported by |
|---|---|
| `code-reviewer` | wrapup, sprint |
| `code-simplifier` | wrapup, sprint |
| `impact-analysis` | sprint |
| `orient` | sprint |
| `security-review` | wrapup, sprint |
