# pmo

An sqlalchemy schema for a basic project mgmt system.

Generates a graphviz graph.


## Requirements

Requires `sqlalchemy`, `graphviz`

Development requirements: `pytest`

## Admin API

Launch the FastAPI-powered admin dashboard to inspect and edit the schema:

```
uv run uvicorn pmo.api.app:app --reload
```

or seed and launch from the project CLI:

```
uv run python -m pmo.cli --db sqlite:///pmo.db serve --seed
```

Visit `http://127.0.0.1:8000/admin` for the SQLAlchemy-backed UI or `http://127.0.0.1:8000/docs` for the REST endpoints. Use `POST /api/sample-data` to seed demo content, then browse projects and related records directly in the dashboard.
