#!/usr/bin/env bash
# sprint-check-app — static front-end regressions for board interactions

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "$ROOT/tests/helpers.sh"

APP="$ROOT/tools/sprint-check-app/app.html"

assert_grep 'class="modal-resize-handle"' "$APP"
assert_grep 'function makePanelResizable\(panelId\)' "$APP"
assert_grep "makePanelResizable\\('modal'\\)" "$APP"
assert_grep 'resetPanelResize\(document.getElementById\('\''modal'\''\)\)' "$APP"
assert_grep 'max-height: calc\(100vh - 24px\)' "$APP"
assert_grep 'padding: 12px;' "$APP"
assert_grep 'min-height: 0;' "$APP"
assert_grep '<div class="kbd-hint" id="m-kbd">Esc</div>' "$APP"

if grep -qE "act-prev|act-next|ArrowLeft|ArrowRight|← → Esc" "$APP"; then
  fail "ticket modal should not expose arrow-key or Back/Done status movement"
fi

printf 'sprint-check-app: ok\n'
