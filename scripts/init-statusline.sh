#!/usr/bin/env bash
set -euo pipefail
# init-statusline.sh — Install the canon statusline for Claude Code.
#
# What it does:
#   1. Copies scripts/statusline.sh → ~/.claude/statusline.sh
#   2. Wires ~/.claude/settings.json with the statusLine command entry
#
# Usage:
#   ./scripts/init-statusline.sh

SCRIPT="${BASH_SOURCE[0]}"
while [ -L "$SCRIPT" ]; do SCRIPT="$(readlink "$SCRIPT")"; done
CANON_ROOT="$(cd "$(dirname "$SCRIPT")/.." && pwd)"

DEST="$HOME/.claude/statusline.sh"
SETTINGS="$HOME/.claude/settings.json"

# --- Install script ---
mkdir -p "$(dirname "$DEST")"
cp "$CANON_ROOT/scripts/statusline.sh" "$DEST"
chmod +x "$DEST"
echo "Installed: $DEST"

# --- Wire settings.json ---
if [ ! -f "$SETTINGS" ]; then
  printf '{\n  "statusLine": {\n    "type": "command",\n    "command": "bash ~/.claude/statusline.sh"\n  }\n}\n' > "$SETTINGS"
  echo "Created: $SETTINGS"
else
  # Inject or replace the statusLine key using Python (available on all macOS)
  python3 - "$SETTINGS" <<'EOF'
import json, sys

path = sys.argv[1]
with open(path) as f:
    data = json.load(f)

data["statusLine"] = {"type": "command", "command": "bash ~/.claude/statusline.sh"}

with open(path, "w") as f:
    json.dump(data, f, indent=2)
    f.write("\n")

print(f"Updated: {path}")
EOF
fi

echo "Done. Restart Claude Code to see the statusline."
