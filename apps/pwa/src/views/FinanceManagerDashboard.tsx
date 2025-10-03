import { useMemo } from "react";

import { useProjects } from "../hooks/useProjects";

function FinanceManagerDashboard() {
  const { data, isLoading } = useProjects();

  const portfolioSnapshot = useMemo(() => {
    if (!data || !data.length) {
      return { budget: 0, bidValue: 0, variance: 0 };
    }
    const budget = data.reduce((sum, project) => sum + project.budget, 0);
    const bidValue = data.reduce((sum, project) => sum + project.bid_value, 0);
    return {
      budget,
      bidValue,
      variance: bidValue - budget
    };
  }, [data]);

  return (
    <section className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-slate-900">Financial Oversight</h1>
        <p className="mt-1 text-sm text-slate-600">
          Monitor spend, bid variance, and change requests impacting the bottom line.
        </p>
      </header>

      {isLoading ? (
        <p className="text-sm text-slate-500">Loading financial metrics…</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-3">
          <KpiCard title="Portfolio Budget" value={portfolioSnapshot.budget} tone="text-blue-700" />
          <KpiCard title="Committed Bid Value" value={portfolioSnapshot.bidValue} tone="text-emerald-700" />
          <KpiCard title="Variance" value={portfolioSnapshot.variance} tone="text-amber-700" />
        </div>
      )}

      <article className="rounded-lg bg-white p-4 shadow">
        <h2 className="text-lg font-semibold text-slate-800">Change requests pending approval</h2>
        <p className="text-sm text-slate-500">Use this list to prioritise financial reviews.</p>
        <div className="mt-3 rounded border border-dashed border-slate-200 px-3 py-6 text-center text-sm text-slate-400">
          Hook up `/api/projects/:id` change request feed to populate this widget.
        </div>
      </article>
    </section>
  );
}

function KpiCard({ title, value, tone }: { title: string; value: number; tone: string }) {
  return (
    <div className={`rounded-lg p-4 shadow bg-white`}>
      <p className="text-sm font-medium text-slate-500">{title}</p>
      <p className={`mt-2 text-2xl font-semibold ${tone}`}>
        {value.toLocaleString(undefined, { style: "currency", currency: "USD" })}
      </p>
    </div>
  );
}

export default FinanceManagerDashboard;
