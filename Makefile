.PHONY: all test clean install api api-serve cli-bu-list pwa-install pwa-dev pwa-build pwa-typecheck

UV ?= uv
DB_URL ?= sqlite:///pmo.db
PWA_DIR := apps/pwa

all: test

install:
	@$(UV) sync

test:
	@$(UV) run pytest

api:
	@$(UV) run uvicorn pmo.api.app:app --reload --host 0.0.0.0 --port 8000

api-serve:
	@$(UV) run python -m pmo.cli --db $(DB_URL) serve --reload --seed

cli-bu-list:
	@$(UV) run python -m pmo.cli --db $(DB_URL) bu list

pwa-install:
	@cd $(PWA_DIR) && bun install

pwa-dev:
	@cd $(PWA_DIR) && bun run dev

pwa-build:
	@cd $(PWA_DIR) && bun run build

pwa-typecheck:
	@cd $(PWA_DIR) && bunx tsc --noEmit

clean:
	@rm -rf build tests/build .pytest_cache
