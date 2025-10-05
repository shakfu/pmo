import { useEffect, useMemo, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import {
  createIssue,
  createProject,
  deleteIssue,
  deleteProject,
  updateIssue,
  updateProject,
} from "../api/pmo";
import { BUSINESS_UNITS_QUERY_KEY, useBusinessUnits } from "../hooks/useBusinessUnits";
import type {
  Issue,
  IssueInput,
  Project,
  ProjectInput,
  ProjectUpdateInput,
} from "../types";

const CATEGORY_OPTIONS = ["substation", "ohtl", "ug_cable"] as const;
const ISSUE_STATUS_OPTIONS = ["open", "in_progress", "resolved", "closed"] as const;
const ISSUE_SEVERITY_OPTIONS = ["low", "medium", "high"] as const;

const todayIso = () => new Date().toISOString().slice(0, 10);

type ProjectFormState = {
  name: string;
  businessunit_id: number | "";
  description: string;
  tender_no: string;
  scope_of_work: string;
  category: string;
  budget: string;
  bid_value: string;
  bid_issue_date: string;
  bid_due_date: string;
  funding_currency: string;
  include_vat: boolean;
};

type IssueFormState = {
  name: string;
  severity: string;
  status: string;
  opened_on: string;
  closed_on: string;
  description: string;
};

type ProjectRow = Project & { businessUnitName: string };

function emptyProjectForm(defaultBusinessUnitId?: number): ProjectFormState {
  return {
    name: "",
    businessunit_id: typeof defaultBusinessUnitId === "number" ? defaultBusinessUnitId : "",
    description: "",
    tender_no: "",
    scope_of_work: "",
    category: CATEGORY_OPTIONS[0],
    budget: "",
    bid_value: "",
    bid_issue_date: todayIso(),
    bid_due_date: todayIso(),
    funding_currency: "SAR",
    include_vat: false,
  };
}

function emptyIssueForm(): IssueFormState {
  return {
    name: "",
    severity: ISSUE_SEVERITY_OPTIONS[0],
    status: ISSUE_STATUS_OPTIONS[0],
    opened_on: todayIso(),
    closed_on: "",
    description: "",
  };
}

function ProjectManagerDashboard() {
  const queryClient = useQueryClient();
  const { data: businessUnits, isLoading } = useBusinessUnits();

  const [projectForm, setProjectForm] = useState<ProjectFormState>(() => emptyProjectForm());
  const [editingProjectId, setEditingProjectId] = useState<number | null>(null);
  const [projectError, setProjectError] = useState<string | null>(null);
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
  const [issueForm, setIssueForm] = useState<IssueFormState>(() => emptyIssueForm());
  const [editingIssueId, setEditingIssueId] = useState<number | null>(null);
  const [issueError, setIssueError] = useState<string | null>(null);

  useEffect(() => {
    if (!businessUnits?.length) {
      return;
    }
    setProjectForm((prev) => {
      if (prev.businessunit_id !== "") {
        return prev;
      }
      return emptyProjectForm(businessUnits[0].id);
    });
  }, [businessUnits]);

  const projectRows: ProjectRow[] = useMemo(() => {
    if (!businessUnits) return [];
    return businessUnits.flatMap((unit) =>
      unit.projects.map((project) => ({ ...project, businessUnitName: unit.name }))
    );
  }, [businessUnits]);

  useEffect(() => {
    if (!projectRows.length) {
      setSelectedProjectId(null);
      return;
    }
    setSelectedProjectId((prev) => {
      if (prev && projectRows.some((project) => project.id === prev)) {
        return prev;
      }
      return projectRows[0].id;
    });
  }, [projectRows]);

  const criticalProjects = useMemo(() => {
    return projectRows.filter((project) =>
      project.issues?.some((issue) => issue.severity === "high" && issue.status !== "resolved")
    );
  }, [projectRows]);

  const currentProject = useMemo(
    () => projectRows.find((project) => project.id === selectedProjectId) ?? null,
    [projectRows, selectedProjectId]
  );

  useEffect(() => {
    if (selectedProjectId === null) {
      return;
    }
    setEditingIssueId(null);
    setIssueForm(emptyIssueForm());
    setIssueError(null);
  }, [selectedProjectId]);

  const createProjectMutation = useMutation({ mutationFn: createProject });
  const updateProjectMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: ProjectUpdateInput }) =>
      updateProject(id, data),
  });
  const deleteProjectMutation = useMutation({ mutationFn: deleteProject });

  const createIssueMutation = useMutation({
    mutationFn: ({ projectId, data }: { projectId: number; data: IssueInput }) =>
      createIssue(projectId, data),
  });
  const updateIssueMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: IssueInput }) =>
      updateIssue(id, data),
  });
  const deleteIssueMutation = useMutation({ mutationFn: deleteIssue });

  const isProjectSaving = createProjectMutation.isPending || updateProjectMutation.isPending;
  const isIssueSaving = createIssueMutation.isPending || updateIssueMutation.isPending;

  const handleProjectChange = (
    field: keyof ProjectFormState,
    value: string | number | boolean
  ) => {
    setProjectForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleProjectSubmit: React.FormEventHandler<HTMLFormElement> = async (event) => {
    event.preventDefault();
    setProjectError(null);

    if (!projectForm.name.trim()) {
      setProjectError("Project name is required.");
      return;
    }
    if (!projectForm.tender_no.trim()) {
      setProjectError("Tender number is required.");
      return;
    }
    if (!projectForm.businessunit_id) {
      setProjectError("Select a business unit.");
      return;
    }

    const budget = Number(projectForm.budget);
    const bidValue = Number(projectForm.bid_value);

    if (Number.isNaN(budget) || Number.isNaN(bidValue)) {
      setProjectError("Budget and bid value must be numbers.");
      return;
    }

    const payload: ProjectInput = {
      name: projectForm.name.trim(),
      businessunit_id: Number(projectForm.businessunit_id),
      description: projectForm.description.trim(),
      tender_no: projectForm.tender_no.trim(),
      scope_of_work: projectForm.scope_of_work.trim(),
      category: projectForm.category,
      funding_currency: projectForm.funding_currency.trim() || "SAR",
      bid_issue_date: projectForm.bid_issue_date,
      tender_purchase_date: projectForm.bid_issue_date,
      tender_purchase_fee: 0,
      bid_due_date: projectForm.bid_due_date,
      completion_period_m: 12,
      bid_validity_d: 30,
      include_vat: projectForm.include_vat,
      budget,
      bid_value: bidValue,
      perf_bond_p: 0,
      advance_pmt_p: 0,
    };

    try {
      if (editingProjectId) {
        await updateProjectMutation.mutateAsync({ id: editingProjectId, data: payload });
      } else {
        const created = await createProjectMutation.mutateAsync(payload);
        setSelectedProjectId(created.id);
      }
      await queryClient.invalidateQueries({ queryKey: BUSINESS_UNITS_QUERY_KEY });
      resetProjectForm();
    } catch (error) {
      setProjectError(
        error instanceof Error ? error.message : "Failed to save project."
      );
    }
  };

  const resetProjectForm = () => {
    setEditingProjectId(null);
    const defaultUnitId = businessUnits?.[0]?.id;
    setProjectForm(emptyProjectForm(defaultUnitId));
  };

  const startProjectEdit = (project: ProjectRow) => {
    setEditingProjectId(project.id);
    setProjectError(null);
    setProjectForm({
      name: project.name,
      businessunit_id: project.businessunit_id,
      description: project.description ?? "",
      tender_no: project.tender_no,
      scope_of_work: project.scope_of_work ?? "",
      category: project.category,
      budget: project.budget.toString(),
      bid_value: project.bid_value.toString(),
      bid_issue_date: project.bid_issue_date,
      bid_due_date: project.bid_due_date,
      funding_currency: project.funding_currency ?? "SAR",
      include_vat: project.include_vat,
    });
  };

  const handleProjectDelete = async (projectId: number) => {
    if (!window.confirm("Delete this project?")) {
      return;
    }
    try {
      await deleteProjectMutation.mutateAsync(projectId);
      await queryClient.invalidateQueries({ queryKey: BUSINESS_UNITS_QUERY_KEY });
      if (editingProjectId === projectId) {
        resetProjectForm();
      }
      if (selectedProjectId === projectId) {
        setSelectedProjectId(null);
      }
    } catch (error) {
      setProjectError(error instanceof Error ? error.message : "Failed to delete project.");
    }
  };

  const handleIssueChange = (
    field: keyof IssueFormState,
    value: string
  ) => {
    setIssueForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleIssueSubmit: React.FormEventHandler<HTMLFormElement> = async (event) => {
    event.preventDefault();
    setIssueError(null);

    if (!currentProject) {
      setIssueError("Select a project to manage issues.");
      return;
    }

    if (!issueForm.name.trim()) {
      setIssueError("Issue name is required.");
      return;
    }

    const payload: IssueInput = {
      name: issueForm.name.trim(),
      severity: issueForm.severity,
      status: issueForm.status,
      opened_on: issueForm.opened_on,
      closed_on: issueForm.closed_on || undefined,
      description: issueForm.description.trim() || undefined,
    };

    try {
      if (editingIssueId) {
        await updateIssueMutation.mutateAsync({ id: editingIssueId, data: payload });
      } else {
        await createIssueMutation.mutateAsync({ projectId: currentProject.id, data: payload });
      }
      await queryClient.invalidateQueries({ queryKey: BUSINESS_UNITS_QUERY_KEY });
      resetIssueForm();
    } catch (error) {
      setIssueError(error instanceof Error ? error.message : "Failed to save issue.");
    }
  };

  const resetIssueForm = () => {
    setEditingIssueId(null);
    setIssueForm(emptyIssueForm());
  };

  const startIssueEdit = (issue: Issue) => {
    setEditingIssueId(issue.id);
    setIssueError(null);
    setIssueForm({
      name: issue.name,
      severity: issue.severity,
      status: issue.status,
      opened_on: issue.opened_on,
      closed_on: issue.closed_on ?? "",
      description: issue.description ?? "",
    });
  };

  const handleIssueDelete = async (issueId: number) => {
    if (!window.confirm("Delete this issue?")) {
      return;
    }
    try {
      await deleteIssueMutation.mutateAsync(issueId);
      await queryClient.invalidateQueries({ queryKey: BUSINESS_UNITS_QUERY_KEY });
      if (editingIssueId === issueId) {
        resetIssueForm();
      }
    } catch (error) {
      setIssueError(error instanceof Error ? error.message : "Failed to delete issue.");
    }
  };

  const handleSelectProject = (projectId: number) => {
    setSelectedProjectId(projectId);
  };

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
                    {project.issues.find((issue) => issue.severity === "high")?.name ?? "No detail"}
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

      <article className="rounded-lg bg-white p-4 shadow">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-800">Project portfolio</h2>
          <button
            className="text-sm text-primary"
            onClick={() => {
              resetProjectForm();
              setProjectError(null);
            }}
            type="button"
          >
            {editingProjectId ? "Cancel edit" : "Reset form"}
          </button>
        </div>
        {projectError && <p className="mt-2 text-sm text-red-600">{projectError}</p>}
        <form className="mt-4 grid gap-4 md:grid-cols-2" onSubmit={handleProjectSubmit}>
          <label className="text-sm text-slate-600">
            <span className="mb-1 block font-medium text-slate-700">Project name</span>
            <input
              type="text"
              value={projectForm.name}
              onChange={(event) => handleProjectChange("name", event.target.value)}
              className="w-full rounded border border-slate-200 px-3 py-2 text-sm"
              placeholder="Riyadh Substation Upgrade"
              required
            />
          </label>
          <label className="text-sm text-slate-600">
            <span className="mb-1 block font-medium text-slate-700">Business unit</span>
            <select
              value={projectForm.businessunit_id}
              onChange={(event) =>
                handleProjectChange(
                  "businessunit_id",
                  event.target.value ? Number(event.target.value) : ""
                )
              }
              className="w-full rounded border border-slate-200 px-3 py-2 text-sm"
              required
            >
              <option value="" disabled>
                Select a unit
              </option>
              {businessUnits?.map((unit) => (
                <option key={unit.id} value={unit.id}>
                  {unit.name}
                </option>
              ))}
            </select>
          </label>
          <label className="md:col-span-2 text-sm text-slate-600">
            <span className="mb-1 block font-medium text-slate-700">Description</span>
            <textarea
              value={projectForm.description}
              onChange={(event) => handleProjectChange("description", event.target.value)}
              className="w-full rounded border border-slate-200 px-3 py-2 text-sm"
              rows={2}
              placeholder="Modernize control systems and capacity"
            />
          </label>
          <label className="text-sm text-slate-600">
            <span className="mb-1 block font-medium text-slate-700">Tender number</span>
            <input
              type="text"
              value={projectForm.tender_no}
              onChange={(event) => handleProjectChange("tender_no", event.target.value)}
              className="w-full rounded border border-slate-200 px-3 py-2 text-sm"
              required
            />
          </label>
          <label className="text-sm text-slate-600">
            <span className="mb-1 block font-medium text-slate-700">Scope of work</span>
            <input
              type="text"
              value={projectForm.scope_of_work}
              onChange={(event) => handleProjectChange("scope_of_work", event.target.value)}
              className="w-full rounded border border-slate-200 px-3 py-2 text-sm"
              placeholder="Upgrade transformers and SCADA"
            />
          </label>
          <label className="text-sm text-slate-600">
            <span className="mb-1 block font-medium text-slate-700">Category</span>
            <select
              value={projectForm.category}
              onChange={(event) => handleProjectChange("category", event.target.value)}
              className="w-full rounded border border-slate-200 px-3 py-2 text-sm"
            >
              {CATEGORY_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
          <label className="text-sm text-slate-600">
            <span className="mb-1 block font-medium text-slate-700">Budget</span>
            <input
              type="number"
              min="0"
              step="0.01"
              value={projectForm.budget}
              onChange={(event) => handleProjectChange("budget", event.target.value)}
              className="w-full rounded border border-slate-200 px-3 py-2 text-sm"
              required
            />
          </label>
          <label className="text-sm text-slate-600">
            <span className="mb-1 block font-medium text-slate-700">Bid value</span>
            <input
              type="number"
              min="0"
              step="0.01"
              value={projectForm.bid_value}
              onChange={(event) => handleProjectChange("bid_value", event.target.value)}
              className="w-full rounded border border-slate-200 px-3 py-2 text-sm"
              required
            />
          </label>
          <label className="text-sm text-slate-600">
            <span className="mb-1 block font-medium text-slate-700">Bid issue date</span>
            <input
              type="date"
              value={projectForm.bid_issue_date}
              onChange={(event) => handleProjectChange("bid_issue_date", event.target.value)}
              className="w-full rounded border border-slate-200 px-3 py-2 text-sm"
              required
            />
          </label>
          <label className="text-sm text-slate-600">
            <span className="mb-1 block font-medium text-slate-700">Bid due date</span>
            <input
              type="date"
              value={projectForm.bid_due_date}
              onChange={(event) => handleProjectChange("bid_due_date", event.target.value)}
              className="w-full rounded border border-slate-200 px-3 py-2 text-sm"
              required
            />
          </label>
          <label className="flex items-center gap-2 text-sm text-slate-600">
            <input
              type="checkbox"
              checked={projectForm.include_vat}
              onChange={(event) => handleProjectChange("include_vat", event.target.checked)}
              className="h-4 w-4 rounded border-slate-300"
            />
            <span className="font-medium text-slate-700">Include VAT</span>
          </label>
          <label className="text-sm text-slate-600">
            <span className="mb-1 block font-medium text-slate-700">Currency</span>
            <input
              type="text"
              value={projectForm.funding_currency}
              onChange={(event) => handleProjectChange("funding_currency", event.target.value)}
              className="w-full rounded border border-slate-200 px-3 py-2 text-sm"
            />
          </label>
          <div className="md:col-span-2 flex items-center gap-3">
            <button
              type="submit"
              className="rounded bg-primary px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
              disabled={isProjectSaving}
            >
              {editingProjectId ? "Update project" : "Add project"}
            </button>
            {editingProjectId && (
              <button
                type="button"
                className="rounded border border-slate-300 px-4 py-2 text-sm text-slate-600"
                onClick={resetProjectForm}
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
                <th className="px-3 py-2">Project</th>
                <th className="px-3 py-2">Business unit</th>
                <th className="px-3 py-2">Category</th>
                <th className="px-3 py-2">Budget</th>
                <th className="px-3 py-2">Bid value</th>
                <th className="px-3 py-2 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {projectRows.map((project) => (
                <tr key={project.id} className="border-t border-slate-100">
                  <td className="px-3 py-2 font-medium text-slate-800">{project.name}</td>
                  <td className="px-3 py-2 text-slate-600">{project.businessUnitName}</td>
                  <td className="px-3 py-2 text-slate-600">{project.category}</td>
                  <td className="px-3 py-2 text-slate-600">
                    {project.budget.toLocaleString(undefined, {
                      style: "currency",
                      currency: project.funding_currency || "USD",
                    })}
                  </td>
                  <td className="px-3 py-2 text-slate-600">
                    {project.bid_value.toLocaleString(undefined, {
                      style: "currency",
                      currency: project.funding_currency || "USD",
                    })}
                  </td>
                  <td className="px-3 py-2 text-right">
                    <div className="flex justify-end gap-2">
                      <button
                        className="text-sm text-primary"
                        onClick={() => {
                          startProjectEdit(project);
                          setSelectedProjectId(project.id);
                        }}
                        type="button"
                      >
                        Edit
                      </button>
                      <button
                        className="text-sm text-slate-500"
                        onClick={() => handleSelectProject(project.id)}
                        type="button"
                      >
                        Issues
                      </button>
                      <button
                        className="text-sm text-red-600"
                        onClick={() => handleProjectDelete(project.id)}
                        type="button"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {!projectRows.length && (
                <tr>
                  <td className="px-3 py-4 text-sm text-slate-500" colSpan={6}>
                    No projects captured yet. Add your first project using the form above.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </article>

      <article className="rounded-lg bg-white p-4 shadow">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-800">Issue tracker</h2>
          {currentProject && (
            <span className="text-sm text-slate-500">
              Managing issues for <strong className="font-semibold text-slate-700">{currentProject.name}</strong>
            </span>
          )}
        </div>
        {issueError && <p className="mt-2 text-sm text-red-600">{issueError}</p>}
        {currentProject ? (
          <>
            <form className="mt-4 grid gap-4 md:grid-cols-2" onSubmit={handleIssueSubmit}>
              <label className="text-sm text-slate-600">
                <span className="mb-1 block font-medium text-slate-700">Issue title</span>
                <input
                  type="text"
                  value={issueForm.name}
                  onChange={(event) => handleIssueChange("name", event.target.value)}
                  className="w-full rounded border border-slate-200 px-3 py-2 text-sm"
                  required
                />
              </label>
              <label className="text-sm text-slate-600">
                <span className="mb-1 block font-medium text-slate-700">Severity</span>
                <select
                  value={issueForm.severity}
                  onChange={(event) => handleIssueChange("severity", event.target.value)}
                  className="w-full rounded border border-slate-200 px-3 py-2 text-sm"
                >
                  {ISSUE_SEVERITY_OPTIONS.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </label>
              <label className="text-sm text-slate-600">
                <span className="mb-1 block font-medium text-slate-700">Status</span>
                <select
                  value={issueForm.status}
                  onChange={(event) => handleIssueChange("status", event.target.value)}
                  className="w-full rounded border border-slate-200 px-3 py-2 text-sm"
                >
                  {ISSUE_STATUS_OPTIONS.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </label>
              <label className="text-sm text-slate-600">
                <span className="mb-1 block font-medium text-slate-700">Opened on</span>
                <input
                  type="date"
                  value={issueForm.opened_on}
                  onChange={(event) => handleIssueChange("opened_on", event.target.value)}
                  className="w-full rounded border border-slate-200 px-3 py-2 text-sm"
                  required
                />
              </label>
              <label className="text-sm text-slate-600">
                <span className="mb-1 block font-medium text-slate-700">Closed on</span>
                <input
                  type="date"
                  value={issueForm.closed_on}
                  onChange={(event) => handleIssueChange("closed_on", event.target.value)}
                  className="w-full rounded border border-slate-200 px-3 py-2 text-sm"
                />
              </label>
              <label className="md:col-span-2 text-sm text-slate-600">
                <span className="mb-1 block font-medium text-slate-700">Notes</span>
                <textarea
                  value={issueForm.description}
                  onChange={(event) => handleIssueChange("description", event.target.value)}
                  className="w-full rounded border border-slate-200 px-3 py-2 text-sm"
                  rows={2}
                />
              </label>
              <div className="md:col-span-2 flex items-center gap-3">
                <button
                  type="submit"
                  className="rounded bg-primary px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
                  disabled={isIssueSaving}
                >
                  {editingIssueId ? "Update issue" : "Add issue"}
                </button>
                {editingIssueId && (
                  <button
                    type="button"
                    className="rounded border border-slate-300 px-4 py-2 text-sm text-slate-600"
                    onClick={resetIssueForm}
                  >
                    Cancel
                  </button>
                )}
              </div>
            </form>

            <ul className="mt-6 space-y-3">
              {currentProject.issues.map((issue) => (
                <li key={issue.id} className="rounded border border-slate-200 px-3 py-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-slate-800">{issue.name}</p>
                      <p className="text-xs text-slate-500">
                        Severity <span className="font-medium text-slate-700">{issue.severity}</span> · Status {issue.status}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <button
                        className="text-sm text-primary"
                        onClick={() => startIssueEdit(issue)}
                        type="button"
                      >
                        Edit
                      </button>
                      <button
                        className="text-sm text-red-600"
                        onClick={() => handleIssueDelete(issue.id)}
                        type="button"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                  {issue.description && (
                    <p className="mt-2 text-sm text-slate-600">{issue.description}</p>
                  )}
                </li>
              ))}
              {!currentProject.issues.length && (
                <li className="rounded border border-dashed border-slate-200 px-3 py-4 text-sm text-slate-500">
                  No issues logged yet. Capture an issue using the form above.
                </li>
              )}
            </ul>
          </>
        ) : (
          <p className="mt-3 text-sm text-slate-500">
            Add a project first to begin tracking issues.
          </p>
        )}
      </article>
    </section>
  );
}

export default ProjectManagerDashboard;
