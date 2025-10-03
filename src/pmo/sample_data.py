"""Utilities for seeding the database with representative sample data."""

from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from .models import (
    BusinessPlan,
    BusinessUnit,
    ChangeRequest,
    ChangeRequestStatus,
    ControlAccount,
    Initiative,
    Issue,
    IssueStatus,
    KeyResult,
    Objective,
    Position,
    Project,
    ProjectLifecycleStage,
    ProjectStatusHistory,
    ProjectType,
    ResourceAssignment,
    Risk,
    WorkPackage,
)


def create_sample_data(session: Session) -> dict[str, object]:
    """Populate the provided session with a coherent PMO dataset.

    Returns a dict containing the key top-level objects for convenience in tests
    or demo scripts.
    """

    bu = BusinessUnit(name="Acme Power", type="businessunit")

    ceo = Position(name="Chief Executive Officer", type="position", businessunit=bu)
    coo = Position(name="Chief Operations Officer", type="position", businessunit=bu, parent=ceo)
    pm = Position(name="Project Manager", type="position", businessunit=bu, parent=coo)

    bp = BusinessPlan(name="2025 Growth Plan", businessunit=bu)
    objective = Objective(name="Expand regional footprint", businessplan=bp)
    key_result = KeyResult(name="Launch 3 new substations", objective=objective)
    Initiative(name="Secure regulatory approvals", keyresult=key_result)

    project = Project(
        name="Riyadh Substation Upgrade",
        businessunit=bu,
        description="Modernize control systems and capacity",
        tender_no="ACME-RYD-001",
        scope_of_work="Upgrade transformers and SCADA integration",
        category=ProjectType.substation,
        funding_currency="SAR",
        bid_issue_date=date.today(),
        tender_purchase_date=date.today(),
        tender_purchase_fee=1250.0,
        bid_due_date=date.today(),
        completion_period_m=14,
        bid_validity_d=120,
        include_vat=True,
        budget=2_500_000.0,
        bid_value=2_450_000.0,
        perf_bond_p=10.0,
        advance_pmt_p=15.0,
    )

    control_account = ControlAccount(name="Mobilization", project=project, budget=500_000.0)
    work_package = WorkPackage(
        name="Site Preparation",
        controlaccount=control_account,
        is_planned=False,
        budget=150_000.0,
        start_date=date.today(),
        end_date=date.today(),
    )
    Risk(name="Permit delays", project=project)

    project.status_history.append(
        ProjectStatusHistory(
            name="Awarded",
            stage=ProjectLifecycleStage.awarded,
            effective_date=date.today(),
            notes="Client confirmed PO",
        )
    )

    ResourceAssignment(
        name="PM Allocation",
        project=project,
        position=pm,
        workpackage=work_package,
        role="Lead PM",
        allocation_percent=80.0,
        start_date=date.today(),
        end_date=None,
    )

    Issue(
        name="Vendor kickoff delay",
        project=project,
        workpackage=work_package,
        owner=pm,
        severity="medium",
        status=IssueStatus.open,
        opened_on=date.today(),
        closed_on=None,
        description="Vendor contracts still under review",
    )

    ChangeRequest(
        name="Add redundancy",
        project=project,
        workpackage=work_package,
        requested_by=coo,
        status=ChangeRequestStatus.submitted,
        submitted_on=date.today(),
        approved_on=None,
        description="Include dual power feeds",
        impact_summary="Schedule +3 weeks; budget +7%",
    )

    session.add(bu)
    session.commit()

    bu.managed_by = ceo
    session.commit()

    return {
        "business_unit": bu,
        "project": project,
        "work_package": work_package,
        "positions": {"ceo": ceo, "coo": coo, "pm": pm},
    }
