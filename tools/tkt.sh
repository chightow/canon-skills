#!/usr/bin/env bash
# tkt — minimal ticket system bundled with canon
# Tickets stored as markdown files in .tickets/

set -euo pipefail

VERSION="1.0.0"

# Walk up directory tree to find .tickets/, fallback to $PWD/.tickets
tickets_dir() {
  local dir="$PWD"
  while [[ "$dir" != "/" ]]; do
    [[ -d "$dir/.tickets" ]] && echo "$dir/.tickets" && return 0
    dir="$(dirname "$dir")"
  done
  echo "$PWD/.tickets"
}

ensure_tickets_dir() {
  local dir
  dir="$(tickets_dir)"
  mkdir -p "$dir"
  echo "$dir"
}

gen_id() {
  local suffix
  suffix=$(LC_ALL=C tr -dc 'a-z0-9' < /dev/urandom | head -c 4)
  echo "t-$suffix"
}

# Find ticket file by partial or full ID match
find_ticket() {
  local query="$1"
  local dir
  dir="$(tickets_dir)"
  [[ ! -d "$dir" ]] && { echo "Error: no .tickets directory found" >&2; exit 1; }

  local matches=()
  while IFS= read -r file; do
    local file_id
    file_id="$(get_field "$file" id)"
    [[ "$file_id" == *"$query"* ]] && matches+=("$file")
  done < <(find "$dir" -name "*.md" -type f 2>/dev/null | sort)

  case ${#matches[@]} in
    0) echo "Error: no ticket matching '$query'" >&2; exit 1 ;;
    1) echo "${matches[0]}" ;;
    *) echo "Error: ambiguous ID '$query' — ${#matches[@]} matches" >&2; exit 1 ;;
  esac
}

get_field() {
  local file="$1" field="$2"
  awk -v f="$field" '
    /^---$/ { fm++; next }
    fm == 1 && match($0, "^" f ": ") { print substr($0, RSTART+RLENGTH); exit }
  ' "$file"
}

set_field() {
  local file="$1" field="$2" value="$3"
  awk -v f="$field" -v v="$value" '
    /^---$/ { fm++; print; next }
    fm == 1 && match($0, "^" f ": ") { print f ": " v; next }
    { print }
  ' "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"
}

get_title() {
  awk '/^---$/{fm++} fm==2 && /^# /{sub(/^# /,""); print; exit}' "$1"
}

cmd_create() {
  local title="" type="task" priority="2" description=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      -t|--type)        type="$2";        shift 2 ;;
      -p|--priority)    priority="$2";    shift 2 ;;
      -d|--description) description="$2"; shift 2 ;;
      -*) echo "Unknown option: $1" >&2; exit 1 ;;
      *)  [[ -z "$title" ]] && title="$1"; shift ;;
    esac
  done

  [[ -z "$title" ]] && { echo "Error: title required" >&2; exit 1; }

  local dir id file created
  dir="$(ensure_tickets_dir)"

  while true; do
    id="$(gen_id)"
    file="$dir/$id.md"
    [[ ! -f "$file" ]] && break
  done

  created="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

  {
    printf -- "---\n"
    printf "id: %s\n" "$id"
    printf "status: open\n"
    printf "created: %s\n" "$created"
    printf "type: %s\n" "$type"
    printf "priority: %s\n" "$priority"
    printf -- "---\n"
    printf "# %s\n" "$title"
    [[ -n "$description" ]] && printf "\n%s\n" "$description"
  } > "$file"

  echo "$id"
}

cmd_set_status() {
  local id="${1:-}" new_status="$2"
  [[ -z "$id" ]] && { echo "Error: ticket ID required" >&2; exit 1; }
  local file
  file="$(find_ticket "$id")"
  set_field "$file" status "$new_status"
  printf "%s: %s\n" "$(get_field "$file" id)" "$new_status"
}

cmd_ls() {
  local status_filter=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --status=*) status_filter="${1#--status=}"; shift ;;
      --status)   status_filter="$2"; shift 2 ;;
      *)          shift ;;
    esac
  done

  local dir
  dir="$(tickets_dir)"
  [[ ! -d "$dir" ]] && { echo "No tickets found."; return; }

  local found=0
  while IFS= read -r file; do
    local id status type priority title
    id="$(get_field "$file" id)"
    status="$(get_field "$file" status)"
    [[ -n "$status_filter" && "$status" != "$status_filter" ]] && continue
    type="$(get_field "$file" type)"
    priority="$(get_field "$file" priority)"
    title="$(get_title "$file")"
    printf "%-10s  %-12s  %-8s  p%s  %s\n" "$id" "$status" "$type" "$priority" "$title"
    (( found++ )) || true
  done < <(find "$dir" -name "*.md" -type f 2>/dev/null | sort)

  if [[ $found -eq 0 ]]; then
    echo "No tickets${status_filter:+ with status '$status_filter'}."
  fi
}

cmd_show() {
  [[ $# -eq 0 ]] && { echo "Usage: tkt show <id>" >&2; exit 1; }
  local file
  file="$(find_ticket "$1")"

  printf "ID:       %s\n" "$(get_field "$file" id)"
  printf "Status:   %s\n" "$(get_field "$file" status)"
  printf "Type:     %s\n" "$(get_field "$file" type)"
  printf "Priority: %s\n" "$(get_field "$file" priority)"
  printf "Created:  %s\n" "$(get_field "$file" created)"
  printf "Title:    %s\n" "$(get_title "$file")"

  local body
  body="$(awk '/^---$/{fm++; next} fm>=2 && !/^# /{print}' "$file")"
  if [[ -n "$body" ]]; then
    printf "\n%s\n" "$body"
  fi
}

cmd_help() {
  cat <<'EOF'
tkt — minimal ticket system

Usage: tkt <command> [args]

Commands:
  create [title] [options]  Create ticket, prints ID
    -d, --description       Description text
    -t, --type              Type (bug|feature|task|epic|chore) [default: task]
    -p, --priority          Priority 0-4, 0=highest [default: 2]
  start <id>                Set status to in_progress
  close <id>                Set status to closed
  reopen <id>               Set status to open
  ls [--status=X]           List tickets (unfiltered by default)
  show <id>                 Display ticket details

Tickets stored as markdown files in .tickets/
Supports partial ID matching (e.g., 'tkt show 8ms' matches 't-8ms5')
EOF
}

main() {
  local cmd="${1:-help}"
  shift || true

  case "$cmd" in
    create)         cmd_create "$@" ;;
    start)          cmd_set_status "${1:-}" in_progress ;;
    close)          cmd_set_status "${1:-}" closed ;;
    reopen)         cmd_set_status "${1:-}" open ;;
    ls|list)        cmd_ls "$@" ;;
    show)           cmd_show "$@" ;;
    help|--help|-h) cmd_help ;;
    --version|-v)   echo "tkt $VERSION" ;;
    *)              echo "Unknown command: $cmd" >&2; cmd_help; exit 1 ;;
  esac
}

main "$@"
