import { useMemo } from "react";

import { useProjects } from "../hooks/useProjects";

function ProjectManagerDashboard() {
  const { data, isLoading } = useProjects();

  const criticalProjects = useMemo(() => {
    if (!data) return [];
    return data.filter((project) => project.issues?.some((issue) => issue.severity === "high"));
  }, [data]);

  return (
    <section className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-slate-900">Project Delivery</h1>
        <p className="mt-1 text-sm text-slate-600">
          Track execution health, blockers, and resource utilisation across in-flight initiatives.
        </p>
      </header>

      {isLoading ? (
        <p className="text-sm text-slate-500">Loading portfolio…</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          <article className="rounded-lg bg-white p-4 shadow">
            <h2 className="text-lg font-semibold text-slate-800">Projects at risk</h2>
            <p className="text-sm text-slate-500">Issues flagged as high severity in the last sync.</p>
            <ul className="mt-3 space-y-2">
              {criticalProjects.map((project) => (
                <li key={project.id} className="rounded border border-red-200 bg-red-50 px-3 py-2">
                  <p className="text-sm font-medium text-red-800">{project.name}</p>
                  <p className="text-xs text-red-600">
                    {project.issues?.find((issue) => issue.severity === "high")?.name ?? "No detail"}
                  </p>
                </li>
              ))}
              {!criticalProjects.length && (
                <li className="rounded border border-emerald-100 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
                  No high-severity issues reported.
                </li>
              )}
            </ul>
          </article>

          <article className="rounded-lg bg-white p-4 shadow">
            <h2 className="text-lg font-semibold text-slate-800">Upcoming milestones</h2>
            <p className="text-sm text-slate-500">
              Sync milestone data from the API to surface crucial dates here.
            </p>
            <div className="mt-3 rounded border border-dashed border-slate-200 px-3 py-6 text-center text-sm text-slate-400">
              Milestone feed not connected yet.
            </div>
          </article>
        </div>
      )}
    </section>
  );
}

export default ProjectManagerDashboard;
