#!/usr/bin/env bash

tickets_dir() {
  local dir="$PWD"
  while [[ "$dir" != "/" ]]; do
    [[ -d "$dir/.tickets" ]] && echo "$dir/.tickets" && return 0
    [[ -d "$dir/.git" ]] && echo "$dir/.tickets" && return 0
    dir="$(dirname "$dir")"
  done
  echo "$PWD/.tickets"
}

project_root() {
  dirname "$(tickets_dir)"
}
