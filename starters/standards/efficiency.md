---
name: efficiency
description: Coding standards, git conventions, and agent design rules
category: agent-ops
tags: [coding, security, git, efficiency, tokens]
inject: true
version: 1.0.0
---

# Agent Standards

## Code

- Prefer editing existing files over creating new ones.
- Delete dead code your changes made unused.
- No feature flags or backwards-compat shims when you can change the code directly.
- No comments unless the WHY is non-obvious.
- Don't reformat or rename adjacent code — fix only what was asked.
- Out-of-scope issues noticed while working: surface as `NOTICED: <what>`, don't fix silently.
- Never introduce OWASP top 10 vulnerabilities. Never commit secrets or `.env` files.
- Don't add dependencies for problems solvable with existing tools.
- Write tests at system boundaries. Don't mock what you can integration-test cheaply.
- A passing test suite verifies code correctness — not feature correctness. Test both.

## Code Review Feedback

Format: `L<line>: <problem>. <fix>.` — no hedging, no preamble.
Include reasoning only when the fix isn't self-evident.
- Ground review in base code, not the PR diff. The diff biases toward the PR's framing; the base code is what exists.
- Scope review to areas relevant to the change. No frontend comments on backend-only features.

## Git

- Commits: imperative mood, 50-char target / 72-char hard limit, no trailing period.
- Type prefix: `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `chore`.
- Focus on WHY. No "This commit..." or first-person pronouns.
- Branches: `feat/short-description`, `fix/short-description`. Never force-push main/master.
- PRs: one concern per PR, title under 70 chars.
- Never stage with `git add -A`.

## Agent Design

- One skill, one job. A skill that does two things is two skills waiting to be separated.
- Compose agents from tools + context + prompts — not inheritance hierarchies.
- Request only the tools the current task needs. Bloated tool schemas degrade reasoning.
- Prefer reversible actions. Confirm before irreversible ones (send, delete, publish, deploy).
- Fail loudly — surface ambiguity rather than guessing silently.
- Solve with one agent before building a multi-agent pipeline. Complexity compounds failure.
- Requirements define intent; code defines reality. The gap between them is where hallucination lives.

## Triggers

Act on these when you see them — don't wait to be told.

- Same fact in multiple files → pick one owner, derive the rest.
- One change requires edits in many unrelated places → fix the missing boundary first.
- Unclear behavior before touching it → characterize what it does now before changing anything.
- A third copy of the same logic appears → remove the duplication; don't copy again.
- Spec conflicts with existing code → surface it: what each says, the options, and ask — don't silently pick one.
