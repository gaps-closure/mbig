# MBIG Cross Compile tools

This directory contains scripts and static files to install cross compilers, includes, and libraries for various targets.
Initially the only target is arm64, representing a gneeric aarch64 box running ubuntu eoan

To manually use cd to this directory and source the env-*arch* you wish to run. This will fetch (if needed) any compilers and add them to your path for the remainder of your shell session.

Many automated shell scripts will source this to ensure the enviroment is set up correctly

## ARM64 ##

init script: env-aarch64

- GCC is downloaded from developer.arm.com
- aarch64libs contains libraries (shared and static) for libconfig, liblzma, libsodium, and libunwind from an arm64 ubuntu eoan install
- aarch64includees contains the libconfig.h from a arm64 ubuntu eaon install, in addition to zmq headers from zeromq3_4.3.2 (see README.txt in build/src/mbig/arm64/hal/arm64_prebuild/README.txt from additional details

