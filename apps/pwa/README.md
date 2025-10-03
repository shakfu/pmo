# PMO Insights PWA

A role-driven Progressive Web App built with React, TypeScript, Vite, Tailwind, and Bun. It consumes the FastAPI/SQLAdmin backend and surfaces dashboards tailored to project, finance, and general managers.

## Getting started

```bash
cd apps/pwa
bun install
bun run dev # or bun run build
```

The app expects the backend to be running (e.g. `uv run python -m pmo.cli --db sqlite:///pmo.db serve --seed`).

Create an `.env` in this directory (or export the variable) to override the API base URL:

```
PMO_API_BASE=http://localhost:8000
```

## Role-based dashboards

- **Project Manager** – highlights high-severity issues, upcoming milestones, and delivery health.
- **Finance Manager** – tracks portfolio budget, committed bid value, and change requests with financial impact.
- **General Manager** – aggregates project load, category mix, and suggested strategic actions.

Switch roles from the header select to see contextual widgets.

## PWA features

- Offline-ready service worker via `vite-plugin-pwa` (auto-update).
- Installable manifest with placeholder icons (drop real assets in `public/icons`).
- Responsive navigation and Tailwind styling for mobile-first use.

## Next steps

- Wire the finance and milestone widgets to dedicated API endpoints (`/api/projects/:id`).
- Add authentication + role mapping once the backend exposes sessions/JWT.
- Extend caching/offline strategy (React Query + background sync) as needed.
