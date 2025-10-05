import { useMemo, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import {
  createBusinessUnit,
  deleteBusinessUnit,
  updateBusinessUnit,
} from "../api/pmo";
import { BUSINESS_UNITS_QUERY_KEY, useBusinessUnits } from "../hooks/useBusinessUnits";
import type {
  BusinessUnit,
  BusinessUnitInput,
  BusinessUnitUpdateInput,
  Project,
} from "../types";

const UNIT_TYPES = ["businessunit"] as const;

type BusinessUnitFormState = {
  name: string;
  type: string;
  parent_id: number | "";
};

function emptyForm(): BusinessUnitFormState {
  return {
    name: "",
    type: UNIT_TYPES[0],
    parent_id: "",
  };
}

function GeneralManagerDashboard() {
  const queryClient = useQueryClient();
  const { data: businessUnits = [], isLoading } = useBusinessUnits();

  const summary = useMemo(() => {
    if (!businessUnits.length) {
      return { total: 0, byCategory: {} as Record<string, number> };
    }
    const byCategory: Record<string, number> = {};
    businessUnits.forEach((unit) => {
      unit.projects.forEach((project: Project) => {
        const category = project.category;
        byCategory[category] = (byCategory[category] ?? 0) + 1;
      });
    });
    return { total: businessUnits.reduce((sum, unit) => sum + unit.projects.length, 0), byCategory };
  }, [businessUnits]);

  const [formState, setFormState] = useState<BusinessUnitFormState>(() => emptyForm());
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  const createMutation = useMutation({ mutationFn: createBusinessUnit });
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: BusinessUnitUpdateInput }) =>
      updateBusinessUnit(id, data),
  });
  const deleteMutation = useMutation({ mutationFn: deleteBusinessUnit });

  const isSaving = createMutation.isPending || updateMutation.isPending;

  const handleChange = (
    field: keyof BusinessUnitFormState,
    value: string | number
  ) => {
    setFormState((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit: React.FormEventHandler<HTMLFormElement> = async (event) => {
    event.preventDefault();
    setFormError(null);

    if (!formState.name.trim()) {
      setFormError("Business unit name is required.");
      return;
    }

    const payload: BusinessUnitInput = {
      name: formState.name.trim(),
      type: formState.type,
      parent_id: formState.parent_id === "" ? undefined : Number(formState.parent_id),
    };

    try {
      if (editingId) {
        await updateMutation.mutateAsync({ id: editingId, data: payload });
      } else {
        await createMutation.mutateAsync(payload);
      }
      await queryClient.invalidateQueries({ queryKey: BUSINESS_UNITS_QUERY_KEY });
      resetForm();
    } catch (error) {
      setFormError(
        error instanceof Error ? error.message : "Failed to save business unit."
      );
    }
  };

  const resetForm = () => {
    setEditingId(null);
    setFormState(emptyForm());
  };

  const startEdit = (unit: BusinessUnit) => {
    setEditingId(unit.id);
    setFormError(null);
    setFormState({
      name: unit.name,
      type: unit.type,
      parent_id: unit.parent_id ?? "",
    });
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("Delete this business unit? Associated projects will also be removed.")) {
      return;
    }
    try {
      await deleteMutation.mutateAsync(id);
      await queryClient.invalidateQueries({ queryKey: BUSINESS_UNITS_QUERY_KEY });
      if (editingId === id) {
        resetForm();
      }
    } catch (error) {
      setFormError(error instanceof Error ? error.message : "Failed to delete business unit.");
    }
  };

  const availableParents = businessUnits.filter((unit) => unit.id !== editingId);

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
                <li
                  key={category}
                  className="flex items-center justify-between rounded border border-slate-200 px-3 py-2 text-sm"
                >
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

      <article className="rounded-lg bg-white p-4 shadow">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-800">Business unit registry</h2>
          <button
            type="button"
            className="text-sm text-primary"
            onClick={resetForm}
          >
            {editingId ? "Cancel edit" : "Reset"}
          </button>
        </div>
        {formError && <p className="mt-2 text-sm text-red-600">{formError}</p>}
        <form className="mt-4 grid gap-4 md:grid-cols-3" onSubmit={handleSubmit}>
          <label className="text-sm text-slate-600 md:col-span-2">
            <span className="mb-1 block font-medium text-slate-700">Name</span>
            <input
              type="text"
              value={formState.name}
              onChange={(event) => handleChange("name", event.target.value)}
              className="w-full rounded border border-slate-200 px-3 py-2 text-sm"
              placeholder="Acme Power"
              required
            />
          </label>
          <label className="text-sm text-slate-600">
            <span className="mb-1 block font-medium text-slate-700">Type</span>
            <select
              value={formState.type}
              onChange={(event) => handleChange("type", event.target.value)}
              className="w-full rounded border border-slate-200 px-3 py-2 text-sm"
            >
              {UNIT_TYPES.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm text-slate-600 md:col-span-2">
            <span className="mb-1 block font-medium text-slate-700">Parent unit</span>
            <select
              value={formState.parent_id}
              onChange={(event) =>
                handleChange(
                  "parent_id",
                  event.target.value ? Number(event.target.value) : ""
                )
              }
              className="w-full rounded border border-slate-200 px-3 py-2 text-sm"
            >
              <option value="">No parent</option>
              {availableParents.map((unit) => (
                <option key={unit.id} value={unit.id}>
                  {unit.name}
                </option>
              ))}
            </select>
          </label>
          <div className="md:col-span-3 flex items-center gap-3">
            <button
              type="submit"
              className="rounded bg-primary px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
              disabled={isSaving}
            >
              {editingId ? "Update business unit" : "Add business unit"}
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
                <th className="px-3 py-2">Name</th>
                <th className="px-3 py-2">Type</th>
                <th className="px-3 py-2">Projects</th>
                <th className="px-3 py-2">Parent</th>
                <th className="px-3 py-2 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {businessUnits.map((unit) => (
                <tr key={unit.id} className="border-t border-slate-100">
                  <td className="px-3 py-2 font-medium text-slate-800">{unit.name}</td>
                  <td className="px-3 py-2 text-slate-600">{unit.type}</td>
                  <td className="px-3 py-2 text-slate-600">{unit.projects.length}</td>
                  <td className="px-3 py-2 text-slate-600">
                    {businessUnits.find((candidate) => candidate.id === unit.parent_id)?.name ?? "—"}
                  </td>
                  <td className="px-3 py-2 text-right">
                    <div className="flex justify-end gap-2">
                      <button
                        className="text-sm text-primary"
                        onClick={() => startEdit(unit)}
                        type="button"
                      >
                        Edit
                      </button>
                      <button
                        className="text-sm text-red-600"
                        onClick={() => handleDelete(unit.id)}
                        type="button"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {!businessUnits.length && (
                <tr>
                  <td className="px-3 py-4 text-sm text-slate-500" colSpan={5}>
                    No business units found. Create one using the form above.
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

export default GeneralManagerDashboard;
