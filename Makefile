.PHONY: all test clean

all: test

test:
	@uv run pytest

clean:
	@rm -rf build tests/build .pytest_cache
