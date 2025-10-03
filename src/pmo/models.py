"""pmo.py

Base
    BusinessUnit
        BusinessPlan
            Objective
            KeyResult
            Initiative
        Project
            ControlAccount
                WorkPackage
                    WorkBreakdownStructure
            Risk
"""

from datetime import date
import enum

from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    import graphviz


from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy.orm import declared_attr


# -----------------------------------------------------------------------------
# Enums


class ProjectType(enum.Enum):
    substation = 0
    ohtl = 1
    ug_cable = 2


class ProjectLifecycleStage(enum.Enum):
    prospect = "prospect"
    bidding = "bidding"
    awarded = "awarded"
    in_progress = "in_progress"
    closed = "closed"


class IssueStatus(enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class ChangeRequestStatus(enum.Enum):
    draft = "draft"
    submitted = "submitted"
    approved = "approved"
    rejected = "rejected"


# -----------------------------------------------------------------------------
# Abstract


class Base(DeclarativeBase):
    """base class"""


class CommonMixin:
    """define a series of common elements that may be applied to mapped
    classes using this class as a mixin class."""

    __name__: str = ""
    __node_attr__: dict[str, str] = {}

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    # __table_args__ = {"mysql_engine": "InnoDB"}
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    @property
    def idx(self) -> str:
        return self.__class__.__name__.lower() + str(self.id)

    def register(self, graph: "graphviz.Digraph", edge=None):
        graph.node(self.idx, self.name, **self.__node_attr__)
        if edge:
            graph.edge(self.idx, edge.idx)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id!r}, name={self.name!r})"


# -----------------------------------------------------------------------------
# Org


class BusinessUnit(CommonMixin, Base):
    __node_attr__ = {"shape": "circle", "fillcolor": "grey"}

    __mapper_args__ = {
        "polymorphic_on": "type",
        "polymorphic_identity": "businessunit",
    }

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id = mapped_column(ForeignKey("businessunit.id"))
    manager_id: Mapped[Optional[int]] = mapped_column(ForeignKey("position.id"))
    type: Mapped[str]
    name: Mapped[str]

    parent = relationship("BusinessUnit", back_populates="children", remote_side=[id])
    children = relationship("BusinessUnit")

    managed_by: Mapped[Optional["Position"]] = relationship(
        back_populates="manages", foreign_keys=[manager_id]
    )

    positions: Mapped[List["Position"]] = relationship(
        back_populates="businessunit",
        cascade="all, delete-orphan",
        foreign_keys="Position.businessunit_id",
        overlaps="managed_by",
    )

    projects: Mapped[List["Project"]] = relationship(
        back_populates="businessunit", cascade="all, delete-orphan"
    )

    businessplans: Mapped[List["BusinessPlan"]] = relationship(
        back_populates="businessunit", cascade="all, delete-orphan"
    )

    def mk_graph(
        self,
        directory: str = "build",
        filename: Optional[str] = None,
        *,
        render: bool = True,
        view: bool = False,
    ):
        import graphviz

        g = graphviz.Digraph(
            "pmo",
            comment="dag",
        )
        # graph_attr=dict(rankdir="LR")

        self.register(g)
        if self.managed_by:
            self.managed_by.register(g, edge=self)

        # see: https://github.com/microsoft/pylance-release/issues/4688
        subgraph = g.subgraph(name="cluster_1")
        assert subgraph is not None
        with subgraph as c:
            c.attr(color="blue")
            c.node_attr["style"] = "filled"
            c.attr(label="orgchart")
            for pos in self.positions:
                pos.register(c, edge=pos.parent)

        for p in self.projects:
            p.register(g, edge=self)

        subgraph = g.subgraph(name="cluster_2")
        assert subgraph is not None
        with subgraph as c:
            c.attr(color="blue")
            c.node_attr["style"] = "filled"
            c.attr(label="projects")
            for p in self.projects:
                # p.register(c, edge=self)
                for ca in p.controlaccounts:
                    ca.register(c, edge=p)
                    for w in ca.workpackages:
                        w.register(c, edge=ca)
                for r in p.risks:
                    r.register(c, edge=p)
                for status in p.status_history:
                    status.register(c, edge=p)
                for assignment in p.resource_assignments:
                    parent = assignment.task or assignment.workpackage or p
                    assignment.register(c, edge=parent)
                for issue in p.issues:
                    parent = issue.task or issue.workpackage or p
                    issue.register(c, edge=parent)
                for change in p.change_requests:
                    parent = change.workpackage or p
                    change.register(c, edge=parent)

        for bp in self.businessplans:
            bp.register(g, edge=self)

        subgraph = g.subgraph(name="cluster_3")
        assert subgraph is not None
        with subgraph as c:
            c.attr(color="blue")
            c.node_attr["style"] = "filled"
            c.attr(label="businessplans")
            for bp in self.businessplans:
                for obj in bp.objectives:
                    obj.register(c, edge=bp)
                    for k in obj.keyresults:
                        k.register(c, edge=obj)
                        for ini in k.initiatives:
                            ini.register(c, edge=k)
        if render:
            g.render(filename=filename, directory=directory, view=view)
        return g


# class Cluster(BusinessUnit):
#     __mapper_args__ = {
#         "polymorphic_identity": "cluster",
#     }

# -----------------------------------------------------------------------------
# Org


class Position(CommonMixin, Base):
    """A position of responsibility in an organization structure

    Can be filled or vacant
    """

    __node_attr__ = {"shape": "box", "style": "filled", "fillcolor": "honeydew"}

    __mapper_args__ = {
        "polymorphic_on": "type",
        "polymorphic_identity": "position",
    }

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id = mapped_column(ForeignKey("position.id"))
    type: Mapped[str]
    name: Mapped[str]

    parent = relationship("Position", back_populates="children", remote_side=[id])
    children = relationship("Position")

    businessunit_id: Mapped[int] = mapped_column(ForeignKey("businessunit.id"))
    businessunit: Mapped["BusinessUnit"] = relationship(
        back_populates="positions",
        foreign_keys=[businessunit_id],
        overlaps="managed_by",
    )

    manages: Mapped[Optional["BusinessUnit"]] = relationship(
        back_populates="managed_by",
        foreign_keys="BusinessUnit.manager_id",
        overlaps="businessunit,positions",
    )
    assignments: Mapped[List["ResourceAssignment"]] = relationship(
        "ResourceAssignment",
        back_populates="position",
    )
    owned_issues: Mapped[List["Issue"]] = relationship(
        "Issue",
        back_populates="owner",
        foreign_keys="Issue.owner_id",
    )
    requested_changes: Mapped[List["ChangeRequest"]] = relationship(
        "ChangeRequest",
        back_populates="requested_by",
        foreign_keys="ChangeRequest.requested_by_id",
    )


# -----------------------------------------------------------------------------
# Planning / OKR


class BusinessPlan(CommonMixin, Base):
    __node_attr__ = {"shape": "box", "style": "filled", "fillcolor": "lightyellow"}

    businessunit_id: Mapped[int] = mapped_column(ForeignKey("businessunit.id"))
    businessunit: Mapped["BusinessUnit"] = relationship(back_populates="businessplans")

    objectives: Mapped[List["Objective"]] = relationship(
        back_populates="businessplan", cascade="all, delete-orphan"
    )


class Objective(CommonMixin, Base):
    """A significant, concrete, clearly defined goal.

    i.e. where you want to go
    """

    __node_attr__ = {"style": "rounded,filled", "shape": "box", "fillcolor": "aqua"}

    businessplan_id: Mapped[int] = mapped_column(ForeignKey("businessplan.id"))
    businessplan: Mapped["BusinessPlan"] = relationship(back_populates="objectives")
    keyresults: Mapped[List["KeyResult"]] = relationship(
        back_populates="objective", cascade="all, delete-orphan"
    )


class KeyResult(CommonMixin, Base):
    """Measurable success criteria used to track the achievement of an Objective"""

    __node_attr__ = {
        "style": "rounded,filled",
        "shape": "box",
        "fillcolor": "gainsboro",
    }

    objective_id: Mapped[int] = mapped_column(ForeignKey("objective.id"))
    objective: Mapped["Objective"] = relationship(back_populates="keyresults")
    initiatives: Mapped[List["Initiative"]] = relationship(
        back_populates="keyresult", cascade="all, delete-orphan"
    )


class Initiative(CommonMixin, Base):
    """Plans and activities to help move forward KeyResult(s) and achieve the Objective."""

    __node_attr__ = {
        "style": "rounded,filled",
        "shape": "box",
        "fillcolor": "aliceblue",
    }

    keyresult_id: Mapped[int] = mapped_column(ForeignKey("keyresult.id"))
    keyresult: Mapped["KeyResult"] = relationship(back_populates="initiatives")


# -----------------------------------------------------------------------------
# Projects


class Project(CommonMixin, Base):
    __node_attr__ = {"shape": "box", "style": "filled", "fillcolor": "lightgreen"}

    businessunit_id: Mapped[int] = mapped_column(ForeignKey("businessunit.id"))
    businessunit: Mapped["BusinessUnit"] = relationship(back_populates="projects")
    controlaccounts: Mapped[List["ControlAccount"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    risks: Mapped[List["Risk"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    contracts: Mapped[List["Contract"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    milestones: Mapped[List["Milestone"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    status_history: Mapped[List["ProjectStatusHistory"]] = relationship(
        "ProjectStatusHistory",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="ProjectStatusHistory.effective_date",
        foreign_keys="ProjectStatusHistory.project_id",
    )
    issues: Mapped[List["Issue"]] = relationship(
        "Issue",
        back_populates="project",
        cascade="all, delete-orphan",
        foreign_keys="Issue.project_id",
    )
    change_requests: Mapped[List["ChangeRequest"]] = relationship(
        "ChangeRequest",
        back_populates="project",
        cascade="all, delete-orphan",
        foreign_keys="ChangeRequest.project_id",
    )
    resource_assignments: Mapped[List["ResourceAssignment"]] = relationship(
        "ResourceAssignment",
        back_populates="project",
        cascade="all, delete-orphan",
        foreign_keys="ResourceAssignment.project_id",
    )

    description: Mapped[str]
    tender_no: Mapped[str] = mapped_column(
        unique=True, doc="Tender reference number as per tender invitation"
    )
    scope_of_work: Mapped[str]
    category: Mapped[ProjectType] = mapped_column(
        Enum(ProjectType), default=ProjectType.substation, doc="Project category"
    )
    funding_currency: Mapped[str] = mapped_column(default="SAR")
    bid_issue_date: Mapped[date] = mapped_column(
        doc="The date the tender was released by the client"
    )
    tender_purchase_date: Mapped[date]
    tender_purchase_fee: Mapped[float] = mapped_column(default=0.0)
    bid_due_date: Mapped[date]
    completion_period_m: Mapped[int] = mapped_column(
        default=12, doc="When project should be delivered in months from date of award"
    )
    bid_validity_d: Mapped[int]
    include_vat: Mapped[bool] = mapped_column(default=False, doc="Include VAT in price")
    budget: Mapped[float]
    bid_value: Mapped[float]
    perf_bond_p: Mapped[float] = mapped_column(default=0.0)
    advance_pmt_p: Mapped[float] = mapped_column(default=0.0)


class ControlAccount(CommonMixin, Base):
    """CA: A management control point where scope, budget, actual cost, and schedule
    are integrated and compared to earned value for performance measurement.

    Each control account may be further decomposed into work packages and/or
    planning packages.
    """

    __node_attr__ = {"shape": "box", "style": "filled", "fillcolor": "lightpink"}

    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"))
    project: Mapped["Project"] = relationship(back_populates="controlaccounts")
    workpackages: Mapped[List["WorkPackage"]] = relationship(
        back_populates="controlaccount", cascade="all, delete-orphan"
    )
    budget: Mapped[float] = mapped_column(insert_default=0.0)


class WorkPackage(CommonMixin, Base):
    """WP: The work defined at the lowest level of the work breakdown structure (WBS)
    for which cost can be estimated and managed.

    Each work package has a unique scope of work, budget scheduled start and
    completion dates, and make only belong to one control account.
    """

    __node_attr__ = {"shape": "note", "style": "filled", "fillcolor": "darkseagreen1"}

    controlaccount_id: Mapped[int] = mapped_column(ForeignKey("controlaccount.id"))
    controlaccount: Mapped["ControlAccount"] = relationship(
        back_populates="workpackages"
    )
    tasks: Mapped[List["Task"]] = relationship(
        back_populates="workpackage", cascade="all, delete-orphan"
    )
    resource_assignments: Mapped[List["ResourceAssignment"]] = relationship(
        "ResourceAssignment",
        back_populates="workpackage",
        foreign_keys="ResourceAssignment.workpackage_id",
    )
    issues: Mapped[List["Issue"]] = relationship(
        "Issue",
        back_populates="workpackage",
        foreign_keys="Issue.workpackage_id",
    )
    change_requests: Mapped[List["ChangeRequest"]] = relationship(
        "ChangeRequest",
        back_populates="workpackage",
        foreign_keys="ChangeRequest.workpackage_id",
    )
    is_planned: Mapped[bool] = mapped_column(
        insert_default=False
    )  # i.e. is still a planning package
    budget: Mapped[float] = mapped_column(insert_default=0.0)
    start_date: Mapped[date]
    end_date: Mapped[date]


class WorkBreakdownStructure(CommonMixin, Base):
    """WBS: A hierarchical decomposition of the total scope of work to be carried out
    by the project team to accomplish project objectives and create the required
    deliverables.
    """


class Risk(CommonMixin, Base):
    __node_attr__ = {
        "shape": "parallelogram",
        "style": "filled",
        "fillcolor": "cornflowerblue",
    }

    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"))
    project: Mapped["Project"] = relationship(back_populates="risks")


# -----------------------------------------------------------------------------
# Financial Management


class Contract(CommonMixin, Base):
    __node_attr__ = {"shape": "box", "style": "filled", "fillcolor": "lightgoldenrodyellow"}

    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"))
    project: Mapped["Project"] = relationship(back_populates="contracts")
    value: Mapped[float] = mapped_column(default=0.0)
    status: Mapped[str]


class Budget(CommonMixin, Base):
    __node_attr__ = {"shape": "box", "style": "filled", "fillcolor": "lightcyan"}

    project_id: Mapped[Optional[int]] = mapped_column(ForeignKey("project.id"))
    workpackage_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("workpackage.id", ondelete="SET NULL")
    )
    planned: Mapped[float] = mapped_column(default=0.0)
    actual: Mapped[float] = mapped_column(default=0.0)


class Expense(CommonMixin, Base):
    __node_attr__ = {"shape": "box", "style": "filled", "fillcolor": "lavender"}

    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"))
    workpackage_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("workpackage.id", ondelete="SET NULL")
    )
    amount: Mapped[float]
    date: Mapped[date]
    description: Mapped[str]


# -----------------------------------------------------------------------------
# Project and Task Management


class Task(CommonMixin, Base):
    __node_attr__ = {"shape": "ellipse", "style": "filled", "fillcolor": "seashell"}

    workpackage_id: Mapped[int] = mapped_column(ForeignKey("workpackage.id"))
    workpackage: Mapped["WorkPackage"] = relationship(back_populates="tasks")
    start_date: Mapped[date]
    end_date: Mapped[date]
    is_complete: Mapped[bool] = mapped_column(default=False)
    resource_assignments: Mapped[List["ResourceAssignment"]] = relationship(
        "ResourceAssignment",
        back_populates="task",
        foreign_keys="ResourceAssignment.task_id",
    )
    issues: Mapped[List["Issue"]] = relationship(
        "Issue",
        back_populates="task",
        foreign_keys="Issue.task_id",
    )


class Milestone(CommonMixin, Base):
    __node_attr__ = {"shape": "diamond", "style": "filled", "fillcolor": "khaki"}

    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"))
    project: Mapped["Project"] = relationship(back_populates="milestones")
    due_date: Mapped[date]
    is_complete: Mapped[bool] = mapped_column(default=False)


class Dependency(Base):
    __tablename__ = "dependency"
    id: Mapped[int] = mapped_column(primary_key=True)
    predecessor_id: Mapped[int] = mapped_column(ForeignKey("task.id"))
    successor_id: Mapped[int] = mapped_column(ForeignKey("task.id"))

    predecessor: Mapped["Task"] = relationship(foreign_keys=[predecessor_id])
    successor: Mapped["Task"] = relationship(foreign_keys=[successor_id])


class ProjectStatusHistory(CommonMixin, Base):
    __node_attr__ = {
        "shape": "box",
        "style": "filled",
        "fillcolor": "lightsteelblue",
    }

    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"))
    project: Mapped["Project"] = relationship(
        back_populates="status_history",
        foreign_keys=[project_id],
    )
    stage: Mapped[ProjectLifecycleStage] = mapped_column(Enum(ProjectLifecycleStage))
    effective_date: Mapped[date]
    notes: Mapped[Optional[str]] = mapped_column(default=None)


class ResourceAssignment(CommonMixin, Base):
    __node_attr__ = {
        "shape": "box",
        "style": "filled",
        "fillcolor": "mintcream",
    }

    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"))
    project: Mapped["Project"] = relationship(
        back_populates="resource_assignments",
        foreign_keys=[project_id],
    )
    position_id: Mapped[int] = mapped_column(ForeignKey("position.id"))
    position: Mapped["Position"] = relationship(
        back_populates="assignments",
        foreign_keys=[position_id],
    )
    workpackage_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("workpackage.id", ondelete="SET NULL")
    )
    workpackage: Mapped[Optional["WorkPackage"]] = relationship(
        back_populates="resource_assignments",
        foreign_keys=[workpackage_id],
    )
    task_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("task.id", ondelete="SET NULL")
    )
    task: Mapped[Optional["Task"]] = relationship(
        back_populates="resource_assignments",
        foreign_keys=[task_id],
    )
    role: Mapped[str]
    allocation_percent: Mapped[float] = mapped_column(default=100.0)
    start_date: Mapped[date]
    end_date: Mapped[Optional[date]]


class Issue(CommonMixin, Base):
    __node_attr__ = {
        "shape": "box",
        "style": "filled",
        "fillcolor": "salmon",
    }

    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"))
    project: Mapped["Project"] = relationship(
        back_populates="issues",
        foreign_keys=[project_id],
    )
    workpackage_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("workpackage.id", ondelete="SET NULL")
    )
    workpackage: Mapped[Optional["WorkPackage"]] = relationship(
        back_populates="issues",
        foreign_keys=[workpackage_id],
    )
    task_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("task.id", ondelete="SET NULL")
    )
    task: Mapped[Optional["Task"]] = relationship(
        back_populates="issues",
        foreign_keys=[task_id],
    )
    owner_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("position.id", ondelete="SET NULL")
    )
    owner: Mapped[Optional["Position"]] = relationship(
        back_populates="owned_issues",
        foreign_keys=[owner_id],
    )
    status: Mapped[IssueStatus] = mapped_column(
        Enum(IssueStatus), default=IssueStatus.open
    )
    severity: Mapped[str]
    opened_on: Mapped[date]
    closed_on: Mapped[Optional[date]]
    description: Mapped[Optional[str]] = mapped_column(default=None)


class ChangeRequest(CommonMixin, Base):
    __node_attr__ = {
        "shape": "box",
        "style": "filled",
        "fillcolor": "lightcoral",
    }

    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"))
    project: Mapped["Project"] = relationship(
        back_populates="change_requests",
        foreign_keys=[project_id],
    )
    workpackage_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("workpackage.id", ondelete="SET NULL")
    )
    workpackage: Mapped[Optional["WorkPackage"]] = relationship(
        back_populates="change_requests"
    )
    requested_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("position.id", ondelete="SET NULL")
    )
    requested_by: Mapped[Optional["Position"]] = relationship(
        back_populates="requested_changes",
        foreign_keys=[requested_by_id],
    )
    status: Mapped[ChangeRequestStatus] = mapped_column(
        Enum(ChangeRequestStatus), default=ChangeRequestStatus.draft
    )
    submitted_on: Mapped[Optional[date]]
    approved_on: Mapped[Optional[date]]
    description: Mapped[Optional[str]] = mapped_column(default=None)
    impact_summary: Mapped[Optional[str]] = mapped_column(default=None)
