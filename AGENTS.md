# Repository Guidelines

## Project Structure & Module Organization
- `src/pmo/` contains the SQLAlchemy domain models in `models.py` and the CLI in `cli.py`; keep new ORM entities with related Graphviz helpers here.
- `tests/` houses pytest suites plus shared fixtures in `conftest.py` and sample workbook `data.xlsx`; mirror runtime paths when adding fixtures.
- Generated diagrams land in `build/`; treat it as disposable output and exclude large binaries from version control.

## Build, Test, and Development Commands
- `uv sync` installs the pinned dependencies from `pyproject.toml`/`uv.lock`.
- `uv run python -m pmo.cli --db sqlite:///pmo.db bu list` is the quickest sanity check of the CLI wiring.
- `uv run pytest` executes all tests; `make test` wraps the same call, and `make clean` clears caches and build artifacts.
- For ad-hoc scripts, prefer `uv run python path/to/script.py` so the project environment is respected.
- Launch the admin dashboard with `uv run uvicorn pmo.api.app:app --reload`, or start it preloaded via `uv run python -m pmo.cli --db sqlite:///pmo.db serve --seed`; seed demo content later with `POST /api/sample-data` or directly in SQLAdmin.
- The mobile-first PWA lives under `apps/pwa/`; run `bun install && bun run dev` to preview role-based dashboards backed by the same API.

## Coding Style & Naming Conventions
- Target Python 3.8+ with PEP 8 spacing (4-space indents) and type hints that match existing signatures.
- ORM classes stay `CamelCase`, mapped attributes remain `snake_case`, and Enum members stay lowercase like `ProjectType.substation`.
- Group SQLAlchemy imports and keep session lifecycles inside context managers for clarity.

## Testing Guidelines
- Name new test modules `test_<area>.py` and keep helper fixtures in `conftest.py` or direct module-level fixtures.
- When adding schema or CLI features, include regression tests that exercise both ORM persistence and CLI command paths.
- Run `uv run pytest -q` before pushing; capture new sample spreadsheets under `tests/` with descriptive filenames.

## Commit & Pull Request Guidelines
- Existing history favors short, imperative subjects (`snap`, `added cli`); stick to ≤50 characters and expand detail in the body when needed.
- Reference related issues or tickets, describe schema/CLI impacts, and note any new outputs under `build/` in the PR description.
- Provide reproduction steps or example CLI invocations when behavior changes so reviewers can verify quickly.

## Agent-Specific Tips
- Centralize database shape changes in `models.py` and wire corresponding CLI verbs in `cli.py` to keep the interface coherent.
- Update documentation or README snippets whenever new commands or graph outputs affect contributor expectations.
