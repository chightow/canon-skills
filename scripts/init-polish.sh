#!/usr/bin/env bash
# init-polish.sh — Register all skills required by the polish quality pipeline.
# Run once per project. Safe to re-run — skips already-registered skills.
#
# Usage:
#   init-polish.sh                    # registers in current directory
#   init-polish.sh /path/to/project   # registers in specified project

SCRIPT="${BASH_SOURCE[0]}"
while [ -L "$SCRIPT" ]; do SCRIPT="$(readlink "$SCRIPT")"; done
SKILLS_ROOT="$(cd "$(dirname "$SCRIPT")/.." && pwd)"

PROJECT="${1:-$(pwd)}"

# Skills required by the polish pipeline — add new ones here as the pipeline grows
POLISH_SKILLS=(
  code-simplifier
  code-reviewer
  security-review
  polish
)

echo "Registering polish pipeline skills in: $PROJECT"
echo

for skill in "${POLISH_SKILLS[@]}"; do
  "$SKILLS_ROOT/skills.sh" add "$skill" "$PROJECT"
  echo
done

echo "Done. Run '/polish' in Claude or Codex to use the pipeline."
