.PHONY: all test clean

all: test

test:
	@pytest

clean:
	@rm -rf build tests/build .pytest_cache
