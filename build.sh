#!/bin/bash

BUILD="$(pwd)/build"

usage_exit() {
  [[ -n "$1" ]] && echo $1
  echo "Usage: $0 [ -d ] [ -a <arch list> ]\\"
  echo "-h        Help"
  echo "-c        Clean up"
  echo "-a        <ARCH1,ARCH2,...>"
  echo "-d        Dry run"
  echo ""
  echo "Supported cross compiled architectures:"
  echo " - arm64"

  exit 1
}

handle_opts() {
  local OPTIND
  while getopts "dca:" options; do
    case "${options}" in
      c) CLEAN=1                ;;
      d) DRY_RUN="--dry-run"    ;;
      a) ARCH_LIST=$OPTARG      ;;
      h) usage_exit             ;;
      :) usage_exit "Error: -${OPTARG} requires an argument." ;;
      *) usage_exit             ;;
    esac
  done
}

handle_opts "$@"

echo "BUILD=${BUILD}"

if [ "$CLEAN" == "1" ]
then
  #clean
  echo "clean arm64"
  pushd arm64
  ./build.sh -c
  popd

else
  #install
  readarray -d ',' -t archarr <<< "$ARCH_LIST"
  for (( n=0; n < ${#archarr[*]}; n++))
  do
    ARCH=$(echo "${archarr[n]}")
    if [ "$DRY_RUN" == "--dry-run" ]
    then
      echo Build Architecture $ARCH
      continue
    fi
    case "$ARCH" in
      arm64)
        ######## ARM64 setup #######
        echo "Prepare arm64"
	pushd arm64
	./build.sh
	popd
        ;;
      *)
        echo "Skipping unknown Arch [$ARCH]"
        ;;
    esac
  done
fi
			
if [ "$ARCH_LIST" == "" ]
then
  echo "Nothing to do"
fi

