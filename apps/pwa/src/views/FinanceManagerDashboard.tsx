import { useEffect, useMemo, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import {
  createChangeRequest,
  deleteChangeRequest,
  updateChangeRequest,
} from "../api/pmo";
import { BUSINESS_UNITS_QUERY_KEY, useBusinessUnits } from "../hooks/useBusinessUnits";
import type {
  ChangeRequest,
  ChangeRequestInput,
  ChangeRequestUpdateInput,
  Project,
} from "../types";

const STATUS_OPTIONS = ["draft", "submitted", "approved", "rejected"] as const;

type ChangeRequestFormState = {
  project_id: number | "";
  name: string;
  status: string;
  submitted_on: string;
  approved_on: string;
  description: string;
  impact_summary: string;
};

type ProjectRow = Project & { businessUnitName: string };

type ChangeRequestRow = ChangeRequest & { projectName: string; businessUnitName: string };

const todayIso = () => new Date().toISOString().slice(0, 10);

function emptyChangeRequestForm(defaultProjectId?: number): ChangeRequestFormState {
  return {
    project_id: typeof defaultProjectId === "number" ? defaultProjectId : "",
    name: "",
    status: STATUS_OPTIONS[0],
    submitted_on: todayIso(),
    approved_on: "",
    description: "",
    impact_summary: "",
  };
}

function FinanceManagerDashboard() {
  const queryClient = useQueryClient();
  const { data: businessUnits, isLoading } = useBusinessUnits();

  const projectRows: ProjectRow[] = useMemo(() => {
    if (!businessUnits) return [];
    return businessUnits.flatMap((unit) =>
      unit.projects.map((project) => ({ ...project, businessUnitName: unit.name }))
    );
  }, [businessUnits]);

  const changeRequestRows: ChangeRequestRow[] = useMemo(() => {
    return projectRows.flatMap((project) =>
      project.change_requests.map((request) => ({
        ...request,
        projectName: project.name,
        businessUnitName: project.businessUnitName,
      }))
    );
  }, [projectRows]);

  const [formState, setFormState] = useState<ChangeRequestFormState>(() => emptyChangeRequestForm());
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  useEffect(() => {
    if (!projectRows.length) {
      return;
    }
    setFormState((prev) => {
      if (prev.project_id !== "") {
        return prev;
      }
      return emptyChangeRequestForm(projectRows[0].id);
    });
  }, [projectRows]);

  const portfolioSnapshot = useMemo(() => {
    if (!projectRows.length) {
      return { budget: 0, bidValue: 0, variance: 0 };
    }
    const budget = projectRows.reduce((sum, project) => sum + project.budget, 0);
    const bidValue = projectRows.reduce((sum, project) => sum + project.bid_value, 0);
    return { budget, bidValue, variance: bidValue - budget };
  }, [projectRows]);

  const createMutation = useMutation({
    mutationFn: ({ projectId, data }: { projectId: number; data: ChangeRequestInput }) =>
      createChangeRequest(projectId, data),
  });
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: ChangeRequestUpdateInput }) =>
      updateChangeRequest(id, data),
  });
  const deleteMutation = useMutation({ mutationFn: deleteChangeRequest });

  const isSaving = createMutation.isPending || updateMutation.isPending;

  const handleChange = (
    field: keyof ChangeRequestFormState,
    value: string | number
  ) => {
    setFormState((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit: React.FormEventHandler<HTMLFormElement> = async (event) => {
    event.preventDefault();
    setFormError(null);

    if (!formState.name.trim()) {
      setFormError("Change request name is required.");
      return;
    }
    if (!formState.project_id) {
      setFormError("Select a project.");
      return;
    }

    const payload: ChangeRequestInput = {
      name: formState.name.trim(),
      status: formState.status,
      submitted_on: formState.submitted_on || undefined,
      approved_on: formState.approved_on || undefined,
      description: formState.description.trim() || undefined,
      impact_summary: formState.impact_summary.trim() || undefined,
    };

    try {
      if (editingId) {
        await updateMutation.mutateAsync({
          id: editingId,
          data: { ...payload, project_id: Number(formState.project_id) },
        });
      } else {
        await createMutation.mutateAsync({
          projectId: Number(formState.project_id),
          data: payload,
        });
      }
      await queryClient.invalidateQueries({ queryKey: BUSINESS_UNITS_QUERY_KEY });
      resetForm();
    } catch (error) {
      setFormError(
        error instanceof Error ? error.message : "Failed to save change request."
      );
    }
  };

  const resetForm = () => {
    setEditingId(null);
    const defaultProjectId = projectRows[0]?.id;
    setFormState(emptyChangeRequestForm(defaultProjectId));
  };

  const startEdit = (row: ChangeRequestRow) => {
    setEditingId(row.id);
    setFormError(null);
    setFormState({
      project_id: row.project_id,
      name: row.name,
      status: row.status,
      submitted_on: row.submitted_on ?? "",
      approved_on: row.approved_on ?? "",
      description: row.description ?? "",
      impact_summary: row.impact_summary ?? "",
    });
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("Delete this change request?")) {
      return;
    }
    try {
      await deleteMutation.mutateAsync(id);
      await queryClient.invalidateQueries({ queryKey: BUSINESS_UNITS_QUERY_KEY });
      if (editingId === id) {
        resetForm();
      }
    } catch (error) {
      setFormError(error instanceof Error ? error.message : "Failed to delete change request.");
    }
  };

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
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-800">Change request workflow</h2>
          <button
            className="text-sm text-primary"
            type="button"
            onClick={resetForm}
          >
            {editingId ? "Cancel edit" : "Reset"}
          </button>
        </div>
        {formError && <p className="mt-2 text-sm text-red-600">{formError}</p>}
        <form className="mt-4 grid gap-4 md:grid-cols-2" onSubmit={handleSubmit}>
          <label className="text-sm text-slate-600">
            <span className="mb-1 block font-medium text-slate-700">Project</span>
            <select
              value={formState.project_id}
              onChange={(event) =>
                handleChange(
                  "project_id",
                  event.target.value ? Number(event.target.value) : ""
                )
              }
              className="w-full rounded border border-slate-200 px-3 py-2 text-sm"
              required
            >
              <option value="" disabled>
                Select project
              </option>
              {projectRows.map((project) => (
                <option key={project.id} value={project.id}>
                  {project.name}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm text-slate-600">
            <span className="mb-1 block font-medium text-slate-700">Title</span>
            <input
              type="text"
              value={formState.name}
              onChange={(event) => handleChange("name", event.target.value)}
              className="w-full rounded border border-slate-200 px-3 py-2 text-sm"
              placeholder="Add redundancy"
              required
            />
          </label>
          <label className="text-sm text-slate-600">
            <span className="mb-1 block font-medium text-slate-700">Status</span>
            <select
              value={formState.status}
              onChange={(event) => handleChange("status", event.target.value)}
              className="w-full rounded border border-slate-200 px-3 py-2 text-sm"
            >
              {STATUS_OPTIONS.map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm text-slate-600">
            <span className="mb-1 block font-medium text-slate-700">Submitted on</span>
            <input
              type="date"
              value={formState.submitted_on}
              onChange={(event) => handleChange("submitted_on", event.target.value)}
              className="w-full rounded border border-slate-200 px-3 py-2 text-sm"
            />
          </label>
          <label className="text-sm text-slate-600">
            <span className="mb-1 block font-medium text-slate-700">Approved on</span>
            <input
              type="date"
              value={formState.approved_on}
              onChange={(event) => handleChange("approved_on", event.target.value)}
              className="w-full rounded border border-slate-200 px-3 py-2 text-sm"
            />
          </label>
          <label className="md:col-span-2 text-sm text-slate-600">
            <span className="mb-1 block font-medium text-slate-700">Description</span>
            <textarea
              value={formState.description}
              onChange={(event) => handleChange("description", event.target.value)}
              className="w-full rounded border border-slate-200 px-3 py-2 text-sm"
              rows={2}
            />
          </label>
          <label className="md:col-span-2 text-sm text-slate-600">
            <span className="mb-1 block font-medium text-slate-700">Impact summary</span>
            <textarea
              value={formState.impact_summary}
              onChange={(event) => handleChange("impact_summary", event.target.value)}
              className="w-full rounded border border-slate-200 px-3 py-2 text-sm"
              rows={2}
            />
          </label>
          <div className="md:col-span-2 flex items-center gap-3">
            <button
              type="submit"
              className="rounded bg-primary px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
              disabled={isSaving}
            >
              {editingId ? "Update change request" : "Add change request"}
            </button>
            {editingId && (
              <button
                type="button"
                className="rounded border border-slate-300 px-4 py-2 text-sm text-slate-600"
                onClick={resetForm}
              >
                Cancel
              </button>
            )}
          </div>
        </form>

        <div className="mt-6 overflow-x-auto">
          <table className="w-full min-w-max table-auto text-left text-sm">
            <thead>
              <tr className="text-xs uppercase tracking-wide text-slate-500">
                <th className="px-3 py-2">Title</th>
                <th className="px-3 py-2">Project</th>
                <th className="px-3 py-2">Status</th>
                <th className="px-3 py-2">Submitted</th>
                <th className="px-3 py-2">Approved</th>
                <th className="px-3 py-2 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {changeRequestRows.map((row) => (
                <tr key={row.id} className="border-t border-slate-100">
                  <td className="px-3 py-2 font-medium text-slate-800">{row.name}</td>
                  <td className="px-3 py-2 text-slate-600">{row.projectName}</td>
                  <td className="px-3 py-2 text-slate-600">{row.status}</td>
                  <td className="px-3 py-2 text-slate-600">{row.submitted_on ?? "—"}</td>
                  <td className="px-3 py-2 text-slate-600">{row.approved_on ?? "—"}</td>
                  <td className="px-3 py-2 text-right">
                    <div className="flex justify-end gap-2">
                      <button
                        className="text-sm text-primary"
                        onClick={() => startEdit(row)}
                        type="button"
                      >
                        Edit
                      </button>
                      <button
                        className="text-sm text-red-600"
                        onClick={() => handleDelete(row.id)}
                        type="button"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {!changeRequestRows.length && (
                <tr>
                  <td className="px-3 py-4 text-sm text-slate-500" colSpan={6}>
                    No change requests recorded. Create one using the form above.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </article>
    </section>
  );
}

function KpiCard({ title, value, tone }: { title: string; value: number; tone: string }) {
  return (
    <div className={`rounded-lg bg-white p-4 shadow`}>
      <p className="text-sm font-medium text-slate-500">{title}</p>
      <p className={`mt-2 text-2xl font-semibold ${tone}`}>
        {value.toLocaleString(undefined, { style: "currency", currency: "USD" })}
      </p>
    </div>
  );
}

export default FinanceManagerDashboard;
