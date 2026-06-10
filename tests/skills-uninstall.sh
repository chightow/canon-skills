#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/tests/helpers.sh"

home="$(mktemp -d)"
trap 'rm -rf "$home"' EXIT

mkdir -p "$home/.claude" "$home/.codex" "$home/.pi/agent/extensions" "$home/.config/canon"

cat > "$home/.claude/settings.json" <<EOF
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "$ROOT/scripts/auto-handoff.sh"
          },
          {
            "type": "command",
            "command": "/usr/local/bin/user-stop"
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
            "command": "$ROOT/scripts/handoff-inject.sh"
          },
          {
            "type": "command",
            "command": "$ROOT/scripts/sprint-inject.sh"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "$ROOT/scripts/pre-commit-check.sh"
          }
        ]
      }
    ]
  },
  "theme": "dark"
}
EOF

cat > "$home/.codex/AGENTS.md" <<EOF
# Codex

@$home/.codex/RTK.md

Keep this user content.
EOF

cat > "$home/.pi/agent/extensions/handoff.ts" <<'EOF'
const configPath = join(homedir(), ".config", "canon", "install_path");
const script = join(canonRoot, "scripts", "auto-handoff.sh");
EOF

printf '%s\n' "$ROOT" > "$home/.config/canon/install_path"

output="$(HOME="$home" "$SKILLS" uninstall)"
assert_contains "$output" "[removed]  4 Claude hook(s)"
assert_contains "$output" "[removed]  Codex RTK import"
assert_contains "$output" "[removed]  Pi handoff extension"
assert_contains "$output" "[removed]  install_path"

assert_count 0 "$ROOT/scripts/auto-handoff.sh" "$home/.claude/settings.json"
assert_count 0 "$ROOT/scripts/handoff-inject.sh" "$home/.claude/settings.json"
assert_count 0 "$ROOT/scripts/sprint-inject.sh" "$home/.claude/settings.json"
assert_count 0 "$ROOT/scripts/pre-commit-check.sh" "$home/.claude/settings.json"
assert_count 1 "/usr/local/bin/user-stop" "$home/.claude/settings.json"
assert_count 1 '"theme": "dark"' "$home/.claude/settings.json"
assert_count 0 "@$home/.codex/RTK.md" "$home/.codex/AGENTS.md"
assert_count 1 "Keep this user content." "$home/.codex/AGENTS.md"
[[ ! -f "$home/.pi/agent/extensions/handoff.ts" ]] || fail "expected Pi extension to be removed"
[[ ! -f "$home/.config/canon/install_path" ]] || fail "expected install_path to be removed"

again="$(HOME="$home" "$SKILLS" uninstall)"
assert_contains "$again" "[ok]     no canon Claude hooks found"
assert_contains "$again" "[ok]     no canon Codex import found"
assert_contains "$again" "[skip]  Pi handoff extension not found"
assert_contains "$again" "[skip]  ~/.config/canon/install_path not found"

printf 'skills-uninstall: ok\n'
