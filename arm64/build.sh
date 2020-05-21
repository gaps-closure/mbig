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

#based off input parameters either run clean or build all
if [ "$CLEAN" == "1" ]
then
  #clean
  echo "CLEAN"
  make clean 
else
  #install

  #init build enviroment for arm64/aarch64
  pushd ../crosscompile
  source env-arm64
  popd

  #run make all
  make
fi
			

