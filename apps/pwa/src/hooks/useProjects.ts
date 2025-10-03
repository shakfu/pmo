import { useQuery } from "@tanstack/react-query";

import type { BusinessUnit, Project } from "../types";

const API_BASE: string = (globalThis as any).__API_BASE__ ?? (typeof __API_BASE__ !== "undefined" ? __API_BASE__ : "");

async function fetchProjects(): Promise<Project[]> {
  const response = await fetch(`${API_BASE}/api/business-units`);
  if (!response.ok) {
    throw new Error(`Failed to fetch business units: ${response.statusText}`);
  }
  const units = (await response.json()) as BusinessUnit[];
  return units.flatMap((unit) => unit.projects ?? []);
}

export function useProjects() {
  return useQuery({
    queryKey: ["projects"],
    queryFn: fetchProjects,
    staleTime: 1000 * 60 * 5
  });
}
