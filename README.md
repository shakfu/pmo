# PMO Platform

The PMO Platform models a project-management organisation in SQLAlchemy, exposes it through a FastAPI + SQLAdmin admin backend, generates Graphviz portfolio diagrams, and now ships with a Bun-powered React PWA for role-aware status reporting.

---

## Contents

- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Backend Setup](#backend-setup)
- [Database Seeding](#database-seeding)
- [Admin Dashboard & API](#admin-dashboard--api)
- [Command-Line Interface](#command-line-interface)
- [Testing](#testing)
- [Progressive Web App](#progressive-web-app)
- [Environment Variables](#environment-variables)
- [Security Notes](#security-notes)
- [Troubleshooting](#troubleshooting)

---

## Key Features

- Comprehensive SQLAlchemy domain model for business units, PMO OKRs, projects, risks, financials, and resource assignments.
- FastAPI REST layer with role-friendly JSON schemas and a SQLAdmin-backed web UI for CRUD operations.
- Graphviz rendering of organisational charts and project clusters via `BusinessUnit.mk_graph()`.
- CLI utilities for CRUD operations, diagram generation, and launching the admin server (with optional sample data seeding).
- React/TypeScript PWA (served via Bun + Vite) that surfaces different dashboards for project, finance, and general managers.

## Technology Stack

- **Python** `>=3.8`
- **SQLAlchemy** for ORM modelling
- **FastAPI** + **SQLAdmin** for REST + admin UI
- **Graphviz** for diagram output
- **uv** for dependency/runtime management (recommended)
- **Bun**, **React**, **Vite**, **Tailwind** for the PWA frontend
- **Pytest** for automated tests

## Project Structure

```
.
├── src/pmo/                # Core library (models, CLI, API, sample data)
├── tests/                  # Pytest suite
├── apps/pwa/               # Progressive Web App (Bun + React)
├── README.md               # This guide
├── CHANGELOG.md            # Release notes
├── pyproject.toml          # Python project configuration
└── Makefile                # Convenience tasks (test/clean)
```

## Prerequisites

- Python 3.8+
- Graphviz installed and available on `PATH` if you intend to render diagrams
- `uv` (recommended) or `pip` for dependency management
- Bun (v1.1+) for the PWA frontend

### Install uv (optional but recommended)

```bash
pip install uv
```

### Install Bun (macOS/Linux)

```bash
curl -fsSL https://bun.sh/install | bash
```

## Backend Setup

```bash
# Install Python dependencies (creates .venv managed by uv)
uv sync

# Run database migrations / metadata creation implicitly by starting the CLI
uv run python -m pmo.cli bu list
```

> **Note:** If the sandbox restricts access to `~/.cache`, set `UV_CACHE_DIR=.uv-cache` (or another writable directory) before running `uv` commands.

## Database Seeding

You can populate a demonstration dataset using the sample data helper. Pick one of the options below.

### Option A: API endpoint

```bash
curl -X POST http://127.0.0.1:8000/api/sample-data
```

### Option B: CLI seeding

```bash
uv run python -m pmo.cli --db sqlite:///pmo.db serve --seed
```

The `--seed` flag creates (or reuses) a default dataset and then launches the admin server.

## Admin Dashboard & API

1. Launch the backend:
   ```bash
   uv run python -m pmo.cli --db sqlite:///pmo.db serve --seed
   ```
2. Explore:
   - Admin UI: <http://127.0.0.1:8000/admin>
   - OpenAPI docs: <http://127.0.0.1:8000/docs>
   - Healthcheck: <http://127.0.0.1:8000/health>

### Important endpoints

- `GET /api/business-units` — business units with nested projects, issues, change requests, resource assignments, etc.
- `GET /api/projects/{id}` — detailed project view (lifecycle stages, issues, assignments).
- `POST /api/sample-data` — idempotent sample content seeding.

## Command-Line Interface

```bash
uv run python -m pmo.cli --help
```

Common subcommands:

- `bu` — manage business units (`create`, `list`, `get`, `update`, `delete`).
- `pos` — CRUD for positions.
- `proj` — create/list projects.
- `bp` / `obj` — business plan and objective management.
- `graph` — generate Graphviz diagrams (`--no-render` for headless usage).
- `serve` — start the FastAPI app (`--seed` optional, `--reload` for dev mode, `--host`/`--port` overrides).

## Testing

```bash
# Python tests (ensure UV_CACHE_DIR is writable if running in a sandbox)
UV_CACHE_DIR=.uv-cache uv run pytest

# Equivalent Make task
make test
```

## Progressive Web App

The PWA consumes the same API and provides dashboards tailored to user roles.

```bash
cd apps/pwa
bun install
bun run dev            # local development (http://127.0.0.1:5173)
# or
bun run build          # production bundle (dist/)
```

Configure the backend base URL in `apps/pwa/.env`:

```
PMO_API_BASE=http://127.0.0.1:8000
```

### Roles available in the UI

- **Project Manager** — highlights high-severity issues, milestone placeholders, delivery insights.
- **Finance Manager** — aggregates budget vs. bid value and change-request attention points.
- **General Manager** — summarises portfolio distribution and strategic follow-up items.

## Environment Variables

| Variable          | Scope       | Description                                         |
|-------------------|-------------|-----------------------------------------------------|
| `PMO_DATABASE_URL`| Backend     | Database URL used by FastAPI/CLI (defaults to sqlite)|
| `UV_CACHE_DIR`    | Backend dev | Overrides uv cache location (useful in sandboxes)   |
| `PMO_API_BASE`    | PWA         | Base URL for API calls from the frontend            |

## Security Notes

- Do **not** commit `.env` files, `.pem` keys, or other credentials (ignored via `.gitignore`).
- Run the admin UI behind authentication in production; SQLAdmin supports FastAPI dependencies for auth/permissions.
- When exposing the API publicly, add HTTPS, rate limiting, and CORS restrictions instead of the current permissive defaults.
- Regenerate and tailor Graphviz output directories to avoid leaking sensitive diagrams.

## Troubleshooting

| Issue                                    | Resolution                                                                 |
|------------------------------------------|----------------------------------------------------------------------------|
| `uv` panics about `system-configuration` | Set `UV_CACHE_DIR=.uv-cache` (or another writable directory)               |
| Graphviz command missing                 | Install Graphviz (`brew install graphviz`, `apt install graphviz`, etc.)  |
| PWA cannot reach backend                 | Check `PMO_API_BASE`, ensure backend is reachable and not blocked by CORS |
| Admin UI empty after seed                | Confirm sample data seed returned IDs and reload `/admin`                 |

For additional contributor guidance, read [`AGENTS.md`](AGENTS.md). The full change history is tracked in [`CHANGELOG.md`](CHANGELOG.md).
