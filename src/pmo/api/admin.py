"""Admin dashboard configuration using sqladmin."""

from __future__ import annotations

from sqladmin import Admin, ModelView

from ..models import (
    BusinessPlan,
    BusinessUnit,
    ChangeRequest,
    ControlAccount,
    Issue,
    Position,
    Project,
    ProjectStatusHistory,
    ResourceAssignment,
    WorkPackage,
)


class BusinessUnitAdmin(ModelView, model=BusinessUnit):
    column_list = [BusinessUnit.id, BusinessUnit.name, BusinessUnit.type, BusinessUnit.manager_id]
    column_searchable_list = [BusinessUnit.name]


class ProjectAdmin(ModelView, model=Project):
    column_list = [
        Project.id,
        Project.name,
        Project.tender_no,
        Project.businessunit_id,
        Project.category,
        Project.budget,
        Project.bid_value,
    ]
    column_searchable_list = [Project.name, Project.tender_no]
    column_sortable_list = [Project.bid_due_date, Project.budget]


class WorkPackageAdmin(ModelView, model=WorkPackage):
    column_list = [WorkPackage.id, WorkPackage.name, WorkPackage.controlaccount_id, WorkPackage.start_date, WorkPackage.end_date]


class ControlAccountAdmin(ModelView, model=ControlAccount):
    column_list = [ControlAccount.id, ControlAccount.name, ControlAccount.project_id, ControlAccount.budget]


class PositionAdmin(ModelView, model=Position):
    column_list = [Position.id, Position.name, Position.businessunit_id, Position.parent_id]


class ProjectStatusAdmin(ModelView, model=ProjectStatusHistory):
    column_list = [
        ProjectStatusHistory.id,
        ProjectStatusHistory.project_id,
        ProjectStatusHistory.stage,
        ProjectStatusHistory.effective_date,
    ]


class ResourceAssignmentAdmin(ModelView, model=ResourceAssignment):
    column_list = [
        ResourceAssignment.id,
        ResourceAssignment.project_id,
        ResourceAssignment.position_id,
        ResourceAssignment.workpackage_id,
        ResourceAssignment.role,
        ResourceAssignment.allocation_percent,
    ]


class IssueAdmin(ModelView, model=Issue):
    column_list = [Issue.id, Issue.project_id, Issue.severity, Issue.status, Issue.owner_id]
    column_searchable_list = [Issue.name]


class ChangeRequestAdmin(ModelView, model=ChangeRequest):
    column_list = [
        ChangeRequest.id,
        ChangeRequest.project_id,
        ChangeRequest.status,
        ChangeRequest.requested_by_id,
        ChangeRequest.submitted_on,
    ]
    column_searchable_list = [ChangeRequest.name]


class BusinessPlanAdmin(ModelView, model=BusinessPlan):
    column_list = [BusinessPlan.id, BusinessPlan.name, BusinessPlan.businessunit_id]
    column_searchable_list = [BusinessPlan.name]


ADMIN_VIEWS = [
    BusinessUnitAdmin,
    ProjectAdmin,
    ControlAccountAdmin,
    WorkPackageAdmin,
    PositionAdmin,
    ProjectStatusAdmin,
    ResourceAssignmentAdmin,
    IssueAdmin,
    ChangeRequestAdmin,
    BusinessPlanAdmin,
]


def setup_admin(app, engine):
    admin = Admin(app, engine)

    for view in ADMIN_VIEWS:
        if isinstance(view, type) and issubclass(view, ModelView):
            admin.add_view(view)

    return admin
