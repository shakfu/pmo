export type Issue = {
  id: number;
  project_id: number;
  name: string;
  severity: string;
  status: string;
  opened_on: string;
  closed_on?: string | null;
  description?: string | null;
  owner_id?: number | null;
  workpackage_id?: number | null;
  task_id?: number | null;
};

export type ChangeRequest = {
  id: number;
  project_id: number;
  name: string;
  status: string;
  submitted_on?: string | null;
  approved_on?: string | null;
  description?: string | null;
  impact_summary?: string | null;
  requested_by_id?: number | null;
  workpackage_id?: number | null;
};

export type Project = {
  id: number;
  businessunit_id: number;
  name: string;
  description: string;
  tender_no: string;
  scope_of_work: string;
  category: string;
  funding_currency: string;
  bid_issue_date: string;
  tender_purchase_date: string;
  tender_purchase_fee: number;
  bid_due_date: string;
  completion_period_m: number;
  bid_validity_d: number;
  include_vat: boolean;
  budget: number;
  bid_value: number;
  perf_bond_p: number;
  advance_pmt_p: number;
  issues: Issue[];
  change_requests: ChangeRequest[];
  status_history?: unknown[];
  resource_assignments?: unknown[];
};

export type BusinessUnit = {
  id: number;
  name: string;
  type: string;
  parent_id?: number | null;
  manager_id?: number | null;
  projects: Project[];
};

export type BusinessUnitInput = {
  name: string;
  type: string;
  parent_id?: number | null;
  manager_id?: number | null;
};

export type BusinessUnitUpdateInput = Partial<BusinessUnitInput>;

export type ProjectInput = {
  name: string;
  businessunit_id: number;
  description: string;
  tender_no: string;
  scope_of_work: string;
  category: string;
  funding_currency: string;
  bid_issue_date: string;
  tender_purchase_date: string;
  tender_purchase_fee: number;
  bid_due_date: string;
  completion_period_m: number;
  bid_validity_d: number;
  include_vat: boolean;
  budget: number;
  bid_value: number;
  perf_bond_p: number;
  advance_pmt_p: number;
};

export type ProjectUpdateInput = Partial<ProjectInput>;

export type IssueInput = {
  name: string;
  severity: string;
  status: string;
  opened_on: string;
  closed_on?: string | null;
  description?: string | null;
  owner_id?: number | null;
  workpackage_id?: number | null;
  task_id?: number | null;
};

export type IssueUpdateInput = Partial<IssueInput> & {
  project_id?: number;
};

export type ChangeRequestInput = {
  name: string;
  status: string;
  submitted_on?: string | null;
  approved_on?: string | null;
  description?: string | null;
  impact_summary?: string | null;
  requested_by_id?: number | null;
  workpackage_id?: number | null;
};

export type ChangeRequestUpdateInput = Partial<ChangeRequestInput> & {
  project_id?: number;
};
