#!/usr/bin/env bash
# gen-starters.sh — sync starters/standards/efficiency.md from standards/efficiency.md
# Run after editing standards/efficiency.md to keep the starters copy in sync.
# To add more synced files: add a cp line below and a matching grep in pre-commit-check.sh.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

SRC="$REPO_ROOT/standards/efficiency.md"
DST="$REPO_ROOT/starters/standards/efficiency.md"

cp "$SRC" "$DST"
echo "starters/standards/efficiency.md updated from standards/efficiency.md"
