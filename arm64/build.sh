#!/bin/bash

BUILD="$(pwd)/build"

usage_exit() {
  [[ -n "$1" ]] && echo $1
  echo "Usage: $0 [ -d ] [ -a <arch list> ]\\"
  echo "-h        Help"
  echo "-c        Clean up"
  echo ""

  exit 1
}

handle_opts() {
  local OPTIND
  while getopts "c" options; do
    case "${options}" in
      c) CLEAN=1                ;;
      h) usage_exit             ;;
      :) usage_exit "Error: -${OPTARG} requires an argument." ;;
      *) usage_exit             ;;
    esac
  done
}

handle_opts "$@"

echo "BUILD=${BUILD}"

#init build enviroment for aarch64
pushd ../crosscompile
source env-aarch64
popd

if [ "$CLEAN" == "1" ]
then
  #clean
  echo "CLEAN"
  make clean 
else
  #install
  make
fi
			

