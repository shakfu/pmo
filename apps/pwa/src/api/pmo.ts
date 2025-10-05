import { apiFetch } from "./client";
import type {
  BusinessUnit,
  BusinessUnitInput,
  BusinessUnitUpdateInput,
  Project,
  ProjectInput,
  ProjectUpdateInput,
  Issue,
  IssueInput,
  IssueUpdateInput,
  ChangeRequest,
  ChangeRequestInput,
  ChangeRequestUpdateInput,
} from "../types";

export function listBusinessUnits(): Promise<BusinessUnit[]> {
  return apiFetch<BusinessUnit[]>("/api/business-units");
}

export function createBusinessUnit(payload: BusinessUnitInput): Promise<BusinessUnit> {
  return apiFetch<BusinessUnit>("/api/business-units", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateBusinessUnit(
  id: number,
  payload: BusinessUnitUpdateInput
): Promise<BusinessUnit> {
  return apiFetch<BusinessUnit>(`/api/business-units/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function deleteBusinessUnit(id: number): Promise<void> {
  return apiFetch<void>(`/api/business-units/${id}`, { method: "DELETE" });
}

export function createProject(payload: ProjectInput): Promise<Project> {
  return apiFetch<Project>("/api/projects", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateProject(id: number, payload: ProjectUpdateInput): Promise<Project> {
  return apiFetch<Project>(`/api/projects/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function deleteProject(id: number): Promise<void> {
  return apiFetch<void>(`/api/projects/${id}`, { method: "DELETE" });
}

export function createIssue(projectId: number, payload: IssueInput): Promise<Issue> {
  return apiFetch<Issue>(`/api/projects/${projectId}/issues`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateIssue(id: number, payload: IssueUpdateInput): Promise<Issue> {
  return apiFetch<Issue>(`/api/issues/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function deleteIssue(id: number): Promise<void> {
  return apiFetch<void>(`/api/issues/${id}`, { method: "DELETE" });
}

export function createChangeRequest(
  projectId: number,
  payload: ChangeRequestInput
): Promise<ChangeRequest> {
  return apiFetch<ChangeRequest>(`/api/projects/${projectId}/change-requests`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateChangeRequest(
  id: number,
  payload: ChangeRequestUpdateInput
): Promise<ChangeRequest> {
  return apiFetch<ChangeRequest>(`/api/change-requests/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function deleteChangeRequest(id: number): Promise<void> {
  return apiFetch<void>(`/api/change-requests/${id}`, { method: "DELETE" });
}

export function getProject(id: number): Promise<Project> {
  return apiFetch<Project>(`/api/projects/${id}`);
}
