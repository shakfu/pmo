"""Pydantic schemas exposed by the FastAPI application."""

from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

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


class BusinessUnitCreateSchema(BaseModel):
    name: str
    type: str = "businessunit"
    parent_id: Optional[int] = None
    manager_id: Optional[int] = None


class BusinessUnitUpdateSchema(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    parent_id: Optional[int] = None
    manager_id: Optional[int] = None


class ProjectCreateSchema(BaseModel):
    name: str
    businessunit_id: int
    description: str
    tender_no: str
    scope_of_work: str
    category: ProjectType = ProjectType.substation
    funding_currency: str = "SAR"
    bid_issue_date: date = Field(default_factory=date.today)
    tender_purchase_date: date = Field(default_factory=date.today)
    tender_purchase_fee: float = 0.0
    bid_due_date: date = Field(default_factory=date.today)
    completion_period_m: int = 12
    bid_validity_d: int = 30
    include_vat: bool = False
    budget: float
    bid_value: float
    perf_bond_p: float = 0.0
    advance_pmt_p: float = 0.0


class ProjectUpdateSchema(BaseModel):
    name: Optional[str] = None
    businessunit_id: Optional[int] = None
    description: Optional[str] = None
    tender_no: Optional[str] = None
    scope_of_work: Optional[str] = None
    category: Optional[ProjectType] = None
    funding_currency: Optional[str] = None
    bid_issue_date: Optional[date] = None
    tender_purchase_date: Optional[date] = None
    tender_purchase_fee: Optional[float] = None
    bid_due_date: Optional[date] = None
    completion_period_m: Optional[int] = None
    bid_validity_d: Optional[int] = None
    include_vat: Optional[bool] = None
    budget: Optional[float] = None
    bid_value: Optional[float] = None
    perf_bond_p: Optional[float] = None
    advance_pmt_p: Optional[float] = None


class IssueCreateSchema(BaseModel):
    name: str
    project_id: Optional[int] = None
    workpackage_id: Optional[int] = None
    task_id: Optional[int] = None
    owner_id: Optional[int] = None
    status: IssueStatus = IssueStatus.open
    severity: str = "low"
    opened_on: date = Field(default_factory=date.today)
    closed_on: Optional[date] = None
    description: Optional[str] = None


class IssueUpdateSchema(BaseModel):
    name: Optional[str] = None
    project_id: Optional[int] = None
    workpackage_id: Optional[int] = None
    task_id: Optional[int] = None
    owner_id: Optional[int] = None
    status: Optional[IssueStatus] = None
    severity: Optional[str] = None
    opened_on: Optional[date] = None
    closed_on: Optional[date] = None
    description: Optional[str] = None


class ChangeRequestCreateSchema(BaseModel):
    name: str
    project_id: Optional[int] = None
    workpackage_id: Optional[int] = None
    requested_by_id: Optional[int] = None
    status: ChangeRequestStatus = ChangeRequestStatus.draft
    submitted_on: Optional[date] = None
    approved_on: Optional[date] = None
    description: Optional[str] = None
    impact_summary: Optional[str] = None


class ChangeRequestUpdateSchema(BaseModel):
    name: Optional[str] = None
    project_id: Optional[int] = None
    workpackage_id: Optional[int] = None
    requested_by_id: Optional[int] = None
    status: Optional[ChangeRequestStatus] = None
    submitted_on: Optional[date] = None
    approved_on: Optional[date] = None
    description: Optional[str] = None
    impact_summary: Optional[str] = None
