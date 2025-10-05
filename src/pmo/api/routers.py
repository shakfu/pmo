"""API routers exposing CRUD-ish endpoints for PMO models."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session, joinedload

from ..models import BusinessUnit, ChangeRequest, Issue, Project
from ..sample_data import create_sample_data
from .dependencies import session_dependency
from .schemas import (
    BusinessUnitCreateSchema,
    BusinessUnitSchema,
    BusinessUnitUpdateSchema,
    ChangeRequestCreateSchema,
    ChangeRequestSchema,
    ChangeRequestUpdateSchema,
    IssueCreateSchema,
    IssueSchema,
    IssueUpdateSchema,
    ProjectCreateSchema,
    ProjectSchema,
    ProjectUpdateSchema,
)


router = APIRouter(prefix="/api", tags=["pmo"])


def _business_unit_query(session: Session):
    return (
        session.query(BusinessUnit)
        .options(
            joinedload(BusinessUnit.projects).joinedload(Project.status_history),
            joinedload(BusinessUnit.projects).joinedload(Project.resource_assignments),
            joinedload(BusinessUnit.projects).joinedload(Project.issues),
            joinedload(BusinessUnit.projects).joinedload(Project.change_requests),
            joinedload(BusinessUnit.businessplans),
            joinedload(BusinessUnit.positions),
        )
    )


def _project_query(session: Session):
    return (
        session.query(Project)
        .options(
            joinedload(Project.status_history),
            joinedload(Project.resource_assignments),
            joinedload(Project.issues),
            joinedload(Project.change_requests),
        )
    )


def _get_business_unit_or_404(session: Session, business_unit_id: int) -> BusinessUnit:
    business_unit = (
        _business_unit_query(session)
        .filter(BusinessUnit.id == business_unit_id)
        .one_or_none()
    )
    if not business_unit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Business unit not found"
        )
    return business_unit


def _get_project_or_404(session: Session, project_id: int) -> Project:
    project = _project_query(session).filter(Project.id == project_id).one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


def _get_issue_or_404(session: Session, issue_id: int) -> Issue:
    issue = session.get(Issue, issue_id)
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
    return issue


def _get_change_request_or_404(session: Session, change_request_id: int) -> ChangeRequest:
    change_request = session.get(ChangeRequest, change_request_id)
    if not change_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Change request not found",
        )
    return change_request


@router.get("/business-units", response_model=list[BusinessUnitSchema])
def list_business_units(session: Session = Depends(session_dependency)):
    units = _business_unit_query(session).all()
    return units


@router.get("/projects/{project_id}", response_model=ProjectSchema)
def get_project(project_id: int, session: Session = Depends(session_dependency)):
    project = _get_project_or_404(session, project_id)
    return project


@router.post(
    "/business-units",
    response_model=BusinessUnitSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_business_unit(
    payload: BusinessUnitCreateSchema, session: Session = Depends(session_dependency)
):
    business_unit = BusinessUnit(**payload.model_dump())
    session.add(business_unit)
    session.commit()
    return _get_business_unit_or_404(session, business_unit.id)


@router.put("/business-units/{business_unit_id}", response_model=BusinessUnitSchema)
def update_business_unit(
    business_unit_id: int,
    payload: BusinessUnitUpdateSchema,
    session: Session = Depends(session_dependency),
):
    business_unit = _get_business_unit_or_404(session, business_unit_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(business_unit, field, value)
    session.commit()
    session.refresh(business_unit)
    return _get_business_unit_or_404(session, business_unit.id)


@router.delete("/business-units/{business_unit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_business_unit(business_unit_id: int, session: Session = Depends(session_dependency)):
    business_unit = _get_business_unit_or_404(session, business_unit_id)
    session.delete(business_unit)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/projects",
    response_model=ProjectSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_project(payload: ProjectCreateSchema, session: Session = Depends(session_dependency)):
    _get_business_unit_or_404(session, payload.businessunit_id)
    project = Project(**payload.model_dump())
    session.add(project)
    session.commit()
    return _get_project_or_404(session, project.id)


@router.put("/projects/{project_id}", response_model=ProjectSchema)
def update_project(
    project_id: int,
    payload: ProjectUpdateSchema,
    session: Session = Depends(session_dependency),
):
    project = _get_project_or_404(session, project_id)
    data = payload.model_dump(exclude_unset=True)
    if "businessunit_id" in data:
        _get_business_unit_or_404(session, data["businessunit_id"])
    for field, value in data.items():
        setattr(project, field, value)
    session.commit()
    session.refresh(project)
    return _get_project_or_404(session, project.id)


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, session: Session = Depends(session_dependency)):
    project = _get_project_or_404(session, project_id)
    session.delete(project)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/projects/{project_id}/issues",
    response_model=IssueSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_issue(
    project_id: int,
    payload: IssueCreateSchema,
    session: Session = Depends(session_dependency),
):
    _get_project_or_404(session, project_id)
    data = payload.model_dump(exclude_unset=True)
    data["project_id"] = project_id
    issue = Issue(**data)
    session.add(issue)
    session.commit()
    session.refresh(issue)
    return issue


@router.put("/issues/{issue_id}", response_model=IssueSchema)
def update_issue(
    issue_id: int,
    payload: IssueUpdateSchema,
    session: Session = Depends(session_dependency),
):
    issue = _get_issue_or_404(session, issue_id)
    data = payload.model_dump(exclude_unset=True)
    if "project_id" in data and data["project_id"] is not None:
        _get_project_or_404(session, data["project_id"])
    for field, value in data.items():
        setattr(issue, field, value)
    session.commit()
    session.refresh(issue)
    return issue


@router.delete("/issues/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_issue(issue_id: int, session: Session = Depends(session_dependency)):
    issue = _get_issue_or_404(session, issue_id)
    session.delete(issue)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/projects/{project_id}/change-requests",
    response_model=ChangeRequestSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_change_request(
    project_id: int,
    payload: ChangeRequestCreateSchema,
    session: Session = Depends(session_dependency),
):
    _get_project_or_404(session, project_id)
    data = payload.model_dump(exclude_unset=True)
    data["project_id"] = project_id
    change_request = ChangeRequest(**data)
    session.add(change_request)
    session.commit()
    session.refresh(change_request)
    return change_request


@router.put(
    "/change-requests/{change_request_id}",
    response_model=ChangeRequestSchema,
)
def update_change_request(
    change_request_id: int,
    payload: ChangeRequestUpdateSchema,
    session: Session = Depends(session_dependency),
):
    change_request = _get_change_request_or_404(session, change_request_id)
    data = payload.model_dump(exclude_unset=True)
    if "project_id" in data and data["project_id"] is not None:
        _get_project_or_404(session, data["project_id"])
    for field, value in data.items():
        setattr(change_request, field, value)
    session.commit()
    session.refresh(change_request)
    return change_request


@router.delete(
    "/change-requests/{change_request_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_change_request(
    change_request_id: int, session: Session = Depends(session_dependency)
):
    change_request = _get_change_request_or_404(session, change_request_id)
    session.delete(change_request)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/sample-data", status_code=status.HTTP_201_CREATED)
def seed_sample_data(session: Session = Depends(session_dependency)):
    data = create_sample_data(session)
    return {
        "business_unit_id": data["business_unit"].id,
        "project_id": data["project"].id,
    }
