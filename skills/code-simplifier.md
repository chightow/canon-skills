---
name: code-simplifier
description: Simplify and refine recently modified code for clarity, consistency, and maintainability without changing behavior
category: skills
tags: [refactoring, code-quality, cleanup]
---

# Code Simplifier

Simplify and refine code after writing or modifying it. Focus on recently modified code unless told otherwise.

## Rules

**Preserve functionality** — never change what the code does, only how it does it.

**Apply project standards** — follow conventions in CLAUDE.md / AGENTS.md:
- ES modules with sorted imports
- `function` keyword over arrow functions for top-level declarations
- Explicit return type annotations on top-level functions
- Consistent naming conventions

**Enhance clarity:**
- Reduce unnecessary nesting and complexity
- Eliminate redundant code and abstractions
- Improve variable and function names
- Consolidate related logic
- Remove comments that describe obvious code
- No nested ternaries — use `if/else` or `switch` instead
- Explicit over compact — a clear longer line beats a dense one-liner

**Maintain balance — do not:**
- Sacrifice readability for fewer lines
- Create clever solutions that are hard to follow
- Merge unrelated concerns into one function
- Remove abstractions that genuinely aid organization
- Make code harder to debug or extend

**Scope** — only refine code touched in the current session unless explicitly asked to do more.

## Process

1. Identify recently modified sections.
2. Analyze for clarity, consistency, and redundancy.
3. Apply project standards.
4. Verify behavior is unchanged.
5. Note only changes that meaningfully affect understanding.
