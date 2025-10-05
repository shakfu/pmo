import { useMemo } from "react";

import type { Project } from "../types";
import { useBusinessUnits } from "./useBusinessUnits";

export function useProjects() {
  const query = useBusinessUnits();

  const projects = useMemo<Project[]>(() => {
    if (!query.data) return [];
    return query.data.flatMap((unit) => unit.projects);
  }, [query.data]);

  return {
    ...query,
    data: projects,
  } as typeof query & { data: Project[] };
}
