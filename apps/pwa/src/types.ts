export type Issue = {
  id: number;
  name: string;
  severity: string;
  status: string;
};

export type Project = {
  id: number;
  name: string;
  budget: number;
  bid_value: number;
  category: string;
  issues: Issue[];
  change_requests?: { id: number; status: string; name: string }[];
};

export type BusinessUnit = {
  id: number;
  name: string;
  projects: Project[];
};
