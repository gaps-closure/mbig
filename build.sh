#!/bin/bash

BUILD="$(pwd)/build"

usage_exit() {
  [[ -n "$1" ]] && echo $1
  echo "Usage: $0 [ -d ] \\"
  echo "-h        Help"
  echo "-c        Clean up"
  echo "-d        Dry run"
  exit 1
}

handle_opts() {
  local OPTIND
  while getopts "dc" options; do
    case "${options}" in
      c) CLEAN=1                ;;
      d) DRY_RUN="--dry-run"    ;;
      h) usage_exit             ;;
      :) usage_exit "Error: -${OPTARG} requires an argument." ;;
      *) usage_exit             ;;
    esac
  done
}

handle_opts "$@"

echo "BUILD=${BUILD}"

echo "Nothing to do"
