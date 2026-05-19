---
name: security-review
description: Identify high-confidence, exploitable security vulnerabilities in code — not theoretical issues
category: skills
tags: [security, vulnerabilities, code-review]
hidden: true
---

# Security Review

Systematically identify exploitable security vulnerabilities. Report only high-confidence findings — skip theoretical issues and framework-mitigated patterns.

## Getting Started

**Step 1 — Register this skill in your project:**
```bash
<path-to-canon>/skills.sh add security-review /path/to/your/project
```

**Step 2 — Verify:**
```bash
<path-to-canon>/skills.sh status /path/to/your/project
```

**Step 3 — Use it:**
- **Claude**: "Run a security review" or "Security review my changes."
- **Codex**: "Run a security review."

The agent traces data flow before flagging anything — no noisy pattern-match reports. Findings come back with location, evidence, and a concrete fix.

> Tip: Use `wrapup` instead if you want simplify + review + security in one go after finishing a task.

## Confidence Threshold

Only report what meets HIGH or MEDIUM confidence:

| Level | Criteria | Action |
|---|---|---|
| HIGH | Vulnerable pattern + attacker-controlled input confirmed | Report with severity |
| MEDIUM | Vulnerable pattern, input source unclear | Note as "Needs verification" |
| LOW | Theoretical or best-practice only | Do not report |

## Do Not Flag

- Test files (unless explicitly asked)
- Dead, commented-out, or documentation code
- Patterns using constants or server-controlled config
- Code paths requiring prior authentication
- Django settings, env vars (`os.environ.get()`), framework constants — these are safe by design

## Pre-scan (ast-grep)

Before manual review, check whether `ast-grep` is available:

```bash
command -v ast-grep >/dev/null 2>&1 && echo "available" || echo "not installed"
```

**If available**, run a structural pattern scan over the changed files to surface confirmed hits before reading code. Use `--json` for structured output:

```bash
# Injection / unsafe exec
ast-grep -p '$F($$$ARGS, shell=True)' -l python --json
ast-grep -p 'exec.Command($CMD, $$$)' -l go --json

# Unvalidated input in queries
ast-grep -p 'f"$$$SELECT$$$WHERE$$$"' -l python --json
ast-grep -p '`$$$SELECT$$$${$VAR}$$$`' -l javascript --json

# Unsafe eval / innerHTML
ast-grep -p 'eval($INPUT)' -l javascript --json
ast-grep -p '$EL.innerHTML = $VAL' -l javascript --json

# Unsafe deserialization
ast-grep -p 'pickle.loads($DATA)' -l python --json
ast-grep -p 'yaml.load($DATA)' -l python --json
```

Adapt patterns to the languages in the changed files. No project setup needed — these run automatically.

If the project has a `scan-rules/` directory at the repo root (optional, project-specific custom rules), run those too:

```bash
ast-grep scan --rule scan-rules/ --json 2>/dev/null
```

Use ast-grep hits as **starting points for data flow tracing** — a pattern match is not a confirmed vulnerability. Proceed to manual review either way.

**If not available**, skip the pre-scan silently and proceed directly to manual review. Note in the report: `ast-grep not installed — structural pre-scan skipped`.

## Process

1. **Pre-scan** — run ast-grep if available (see above); note any pattern hits.
2. Trace data flow end-to-end before flagging anything.
3. Confirm attacker-controlled input reaches the vulnerable pattern.
4. Check for validation, sanitization, or framework mitigations along the path.
5. Only then report — with exploitability evidence, not pattern matches alone.

## Vulnerability Categories

Injection, XSS, authorization bypass, weak cryptography, unsafe deserialization, SSRF, CSRF, file security, broken authentication, business logic flaws, API security, misconfiguration, error handling leaks, sensitive data in logs.

## Language-Specific Patterns

- **Python** — Django, Flask, FastAPI: SQL via raw queries, template injection, unsafe deserialization formats, open redirects
- **JavaScript** — Express, React, Vue: prototype pollution, `eval`, dangerously set innerHTML, JWT misuse
- **Go** — `exec.Command` with user input, unsafe pointer use, goroutine races
- **Rust** — `unsafe` blocks, FFI boundaries, panics in production paths
- **Java** — Spring: deserialization, XXE, reflected input in responses
- **ASP.NET Razor Pages** — for every handler that performs a destructive or irreversible action (send email, delete, bulk-update, cache refresh):
  1. **UI-only access control**: hiding a button or `<form>` in Razor is not authorization — a POST to `?handler=X` works regardless of whether the element is rendered. Verify the handler has an explicit server-side `Forbid()` / `Unauthorized()` check that does not depend on UI state.
  2. **Duplicate triggers**: grep the `.cshtml` for every `asp-page-handler="X"` and `action="?handler=X"` binding to a destructive handler. More than one form targeting the same handler is a red flag — the secondary form often bypasses the JS confirmation dialog, admin-visibility guard, or access check that the primary form enforces.

## Severity Classification

- **Critical** — direct exploit, severe impact, no auth required
- **High** — exploitable with some conditions, significant impact
- **Medium** — requires specific conditions, moderate impact
- **Low** — defense-in-depth gap, minimal direct impact

## Report Format

```
## Findings

### [SEVERITY] Title
- **Location**: file:line
- **Pattern**: what the vulnerable code does
- **Evidence**: why attacker input reaches it
- **Impact**: what an attacker can do
- **Fix**: concrete remediation

## Needs Verification
Issues where input source is unclear — flag for human review.

## Out of Scope
Patterns reviewed and ruled out (briefly, to show coverage).
```
