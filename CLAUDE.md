# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python project that implements a SQLAlchemy schema for a project management system (PMO). The system models business units, organizational structures, business plans with OKR methodology (Objectives, Key Results, Initiatives), and project management components including control accounts, work packages, and risk management.

## Common Commands

### Testing
- Run tests: `uv run pytest`
- Run tests (using Makefile): `make test`

### Development
- Dependencies are managed with `uv` and defined in `pyproject.toml`
- Python path for tests is configured to include `src/` directory
- Clean build artifacts: `make clean`

## Architecture Overview

### Core Models Hierarchy
The system is built around a hierarchical structure defined in `src/pmo/models.py`:

```
Base (SQLAlchemy DeclarativeBase)
├── BusinessUnit (Organization structure with self-referential hierarchy)
│   ├── BusinessPlan (Strategic planning)
│   │   └── Objective → KeyResult → Initiative (OKR methodology)
│   ├── Project (Project management)
│   │   ├── ControlAccount → WorkPackage (Work breakdown)
│   │   └── Risk (Risk management)
│   └── Position (Organizational positions with hierarchy)
```

### Key Design Patterns
- **CommonMixin**: Shared attributes and behaviors across all models including automatic table naming, standard ID/name fields, and graph visualization support
- **Polymorphic inheritance**: BusinessUnit and Position use SQLAlchemy polymorphic inheritance with type discriminators
- **Cascade relationships**: Parent-child relationships use `cascade="all, delete-orphan"` for proper cleanup
- **Graph visualization**: Built-in Graphviz integration via `mk_graph()` method on BusinessUnit

### Database Schema
- Primary models: BusinessUnit, Position, BusinessPlan, Project, ControlAccount, WorkPackage, Risk, Objective, KeyResult, Initiative
- All models inherit from CommonMixin providing: `id` (primary key), `name` (string), `idx` (computed property), graph registration methods
- Foreign key relationships maintain referential integrity throughout the hierarchy

### Visualization Features
- Graphviz integration for organizational and project structure visualization
- Each model class defines `__node_attr__` for graph styling
- `BusinessUnit.mk_graph()` generates comprehensive organizational diagrams with clustered subgraphs for orgchart, projects, and business plans
- Outputs rendered graphs to `build/` directory

## Testing Structure
- Tests use pytest with configuration in `pyproject.toml`
- `tests/conftest.py` provides Excel workbook fixture for data testing
- `tests/test_pmo.py` contains comprehensive model integration tests demonstrating full object hierarchy creation
- Test database uses SQLite with optional echo mode for debugging

## CLI Interface

The project includes a comprehensive command-line interface in `src/pmo/cli.py` providing CRUD operations for all major entities:

### Usage
```bash
uv run python -m pmo.cli --help
```

### Available Commands
- `bu` - Business unit operations (create, list, get, update, delete)
- `pos` - Position operations (create, list)  
- `proj` - Project operations (create, list)
- `bp` - Business plan operations (create, list)
- `obj` - Objective operations (create)
- `graph` - Generate organizational graphs using Graphviz

### Examples
```bash
# Create a business unit
uv run python -m pmo.cli bu create "Acme Corp"

# Create positions with hierarchy  
uv run python -m pmo.cli pos create "CEO" 1
uv run python -m pmo.cli pos create "CTO" 1 --parent-id 1

# Set management relationships
uv run python -m pmo.cli bu update 1 --manager-id 1

# Create projects with full details
uv run python -m pmo.cli proj create "Data Center" 1 "Build facility" "TND-001" "50MW facility" --budget 5000000

# Generate organizational charts
uv run python -m pmo.cli graph 1
```

The CLI handles database initialization, relationship management, and provides comprehensive error handling.


