#set up enviroment form AARCH64 cross compile

#copy in some defaults
export CC = aarch64-none-linux-gnu-gcc
export AR = aarch64-none-linux-gnu-ar
export LDFLAGS = $(AARCH64_LDFLAGS)
export CFLAGS = $(AARCH64_CFLAGS)

all: partitioner hal
ARM64DIR=$(shell pwd)

.PHONY: partitioner
partitioner:
	mkdir -p capo/partitioner/src
	$(MAKE) -C ../../capo/partitioner/src/ \
		CFLAGS="-Wall -g $(CFLAGS)" \
		OBJDIR="$(ARM64DIR)/capo/partitioner/src"

.PHONY: hal
hal:
	mkdir -p hal/daemon
	mkdir -p hal/api
	mkdir -p hal/log
	mkdir -p hal/zc
	mkdir -p hal/appgen/6month-demo
	mkdir -p hal/appgen/apptest
	$(MAKE) -C ../../hal/ \
		CFLAGS="-O2 -Wall -Wstrict-prototypes $(CFLAGS)" \
	        LDFLAGS="$(LDFLAGS) -L$(ARM64DIR)/hal/arm64_prebuild -lsodium -lunwind -llzma  -lc -lstdc++ -lpthread -ldl" \
		STATICZMQ="$(ARM64DIR)/hal/arm64_prebuild/libzmq.a" \
		OBJDIR="$(ARM64DIR)/hal"

clean:
	rm -rf capo hal/daemon hal/api hal/log hal/zc hal/appgen
