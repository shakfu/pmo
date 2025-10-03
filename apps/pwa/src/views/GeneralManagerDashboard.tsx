import { useMemo } from "react";

import { useProjects } from "../hooks/useProjects";

function GeneralManagerDashboard() {
  const { data, isLoading } = useProjects();

  const summary = useMemo(() => {
    if (!data || !data.length) {
      return { total: 0, byCategory: {} as Record<string, number> };
    }
    const byCategory: Record<string, number> = {};
    data.forEach((project) => {
      const category = project.category;
      byCategory[category] = (byCategory[category] ?? 0) + 1;
    });
    return { total: data.length, byCategory };
  }, [data]);

  return (
    <section className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-slate-900">Executive Snapshot</h1>
        <p className="mt-1 text-sm text-slate-600">
          High-level view of portfolio load, with quick links into risk and finance dashboards.
        </p>
      </header>

      {isLoading ? (
        <p className="text-sm text-slate-500">Loading snapshot…</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          <article className="rounded-lg bg-white p-4 shadow">
            <h2 className="text-lg font-semibold text-slate-800">Portfolio distribution</h2>
            <p className="text-sm text-slate-500">Counts by project category.</p>
            <ul className="mt-3 space-y-2">
              {Object.entries(summary.byCategory).map(([category, count]) => (
                <li key={category} className="flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm">
                  <span className="font-medium text-slate-700">{category}</span>
                  <span className="text-slate-500">{count}</span>
                </li>
              ))}
              {!Object.keys(summary.byCategory).length && (
                <li className="rounded border border-slate-200 px-3 py-2 text-sm text-slate-500">
                  No projects loaded yet.
                </li>
              )}
            </ul>
          </article>

          <article className="rounded-lg bg-white p-4 shadow">
            <h2 className="text-lg font-semibold text-slate-800">Strategic actions</h2>
            <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm text-slate-600">
              <li>Review high-risk projects and ensure mitigation owners are defined.</li>
              <li>Validate finance approvals for open change requests.</li>
              <li>Align resource assignments with upcoming milestones.</li>
            </ol>
          </article>
        </div>
      )}
    </section>
  );
}

export default GeneralManagerDashboard;
