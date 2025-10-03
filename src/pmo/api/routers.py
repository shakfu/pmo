"""API routers exposing CRUD-ish endpoints for PMO models."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from ..models import BusinessUnit, Project
from ..sample_data import create_sample_data
from .dependencies import session_dependency
from .schemas import BusinessUnitSchema, ProjectSchema


router = APIRouter(prefix="/api", tags=["pmo"])


@router.get("/business-units", response_model=list[BusinessUnitSchema])
def list_business_units(session: Session = Depends(session_dependency)):
    units = (
        session.query(BusinessUnit)
        .options(
            joinedload(BusinessUnit.projects).joinedload(Project.status_history),
            joinedload(BusinessUnit.projects).joinedload(Project.resource_assignments),
            joinedload(BusinessUnit.projects).joinedload(Project.issues),
            joinedload(BusinessUnit.projects).joinedload(Project.change_requests),
            joinedload(BusinessUnit.businessplans),
            joinedload(BusinessUnit.positions),
        )
        .all()
    )
    return units


@router.get("/projects/{project_id}", response_model=ProjectSchema)
def get_project(project_id: int, session: Session = Depends(session_dependency)):
    project = (
        session.query(Project)
        .options(
            joinedload(Project.status_history),
            joinedload(Project.resource_assignments),
            joinedload(Project.issues),
            joinedload(Project.change_requests),
        )
        .filter(Project.id == project_id)
        .one_or_none()
    )
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.post("/sample-data", status_code=status.HTTP_201_CREATED)
def seed_sample_data(session: Session = Depends(session_dependency)):
    data = create_sample_data(session)
    return {
        "business_unit_id": data["business_unit"].id,
        "project_id": data["project"].id,
    }
