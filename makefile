all: install

install:
	./scripts/install.sh

run:
	./scripts/run.sh

.PHONY: all install run