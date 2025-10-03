"""Pydantic schemas exposed by the FastAPI application."""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel

from ..models import ChangeRequestStatus, IssueStatus, ProjectLifecycleStage, ProjectType


class BaseSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class PositionSchema(BaseSchema):
    parent_id: Optional[int]
    businessunit_id: int


class ProjectStatusSchema(BaseSchema):
    stage: ProjectLifecycleStage
    effective_date: date
    notes: Optional[str]


class ResourceAssignmentSchema(BaseSchema):
    position_id: int
    project_id: int
    workpackage_id: Optional[int]
    task_id: Optional[int]
    role: str
    allocation_percent: float
    start_date: date
    end_date: Optional[date]


class IssueSchema(BaseSchema):
    project_id: int
    workpackage_id: Optional[int]
    task_id: Optional[int]
    owner_id: Optional[int]
    status: IssueStatus
    severity: str
    opened_on: date
    closed_on: Optional[date]
    description: Optional[str]


class ChangeRequestSchema(BaseSchema):
    project_id: int
    workpackage_id: Optional[int]
    requested_by_id: Optional[int]
    status: ChangeRequestStatus
    submitted_on: Optional[date]
    approved_on: Optional[date]
    description: Optional[str]
    impact_summary: Optional[str]


class WorkPackageSchema(BaseSchema):
    controlaccount_id: int
    is_planned: bool
    budget: float
    start_date: date
    end_date: date


class ControlAccountSchema(BaseSchema):
    project_id: int
    budget: float


class ProjectSchema(BaseSchema):
    businessunit_id: int
    description: str
    tender_no: str
    scope_of_work: str
    category: ProjectType
    funding_currency: str
    bid_issue_date: date
    tender_purchase_date: date
    tender_purchase_fee: float
    bid_due_date: date
    completion_period_m: int
    bid_validity_d: int
    include_vat: bool
    budget: float
    bid_value: float
    perf_bond_p: float
    advance_pmt_p: float

    status_history: list[ProjectStatusSchema]
    resource_assignments: list[ResourceAssignmentSchema]
    issues: list[IssueSchema]
    change_requests: list[ChangeRequestSchema]


class BusinessPlanSchema(BaseSchema):
    businessunit_id: int


class BusinessUnitSchema(BaseSchema):
    type: str
    parent_id: Optional[int]
    manager_id: Optional[int]

    projects: list[ProjectSchema]
    businessplans: list[BusinessPlanSchema]
    positions: list[PositionSchema]
