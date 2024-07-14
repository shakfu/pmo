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
from datetime import datetime, date
from typing import List, Optional, TYPE_CHECKING
if TYPE_CHECKING:
    import graphviz


from sqlalchemy import ForeignKey, String, Integer, Float, create_engine
from sqlalchemy.orm import (DeclarativeBase, Mapped, Session, mapped_column,
                            relationship)
from sqlalchemy.orm import declared_attr


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

    def register(self, graph: 'graphviz.Digraph', edge=None):
        graph.node(self.idx, self.name, **self.__node_attr__)
        if edge:
            graph.edge(self.idx, edge.idx)


    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id!r}, name={self.name!r})"


# -----------------------------------------------------------------------------
# Org

class BusinessUnit(CommonMixin, Base):
    __node_attr__ = { 'shape':'circle', 'fillcolor': 'grey'}

    __mapper_args__ = {
        "polymorphic_on": "type",
        "polymorphic_identity": "businessunit",
    }

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id = mapped_column(ForeignKey(f"businessunit.id"))
    type: Mapped[str]
    name: Mapped[str]

    parent = relationship("BusinessUnit", back_populates="children", remote_side=[id])
    children = relationship("BusinessUnit")

    managed_by: Mapped["Position"] = relationship(back_populates="manages")

    positions: Mapped[List["Position"]] = relationship(
        back_populates="businessunit", cascade="all, delete-orphan",
        overlaps="managed_by"
    )

    projects: Mapped[List["Project"]] = relationship(
        back_populates="businessunit", cascade="all, delete-orphan"
    )

    businessplans: Mapped[List["BusinessPlan"]] = relationship(
        back_populates="businessunit", cascade="all, delete-orphan"
    )

    def mk_graph(self):
        import graphviz
        g = graphviz.Digraph('pmo', comment='dag',)
        # graph_attr=dict(rankdir="LR")

        self.register(g)
        self.managed_by.register(g, edge=self)
        # with g.subgraph(name='cluster_0') as c:
        #     c.attr(style='filled', color='lightgrey')
        #     c.node_attr.update(cstyle='filled', color='white')
        #     c.edges([('a0', 'a1'), ('a1', 'a2'), ('a2', 'a3')])
        #     c.attr(label='process #1')
        with g.subgraph(name="cluster_1") as c:
            c.attr(color='blue')
            c.node_attr['style'] = 'filled'
            # c.edges([('b0', 'b1'), ('b1', 'b2'), ('b2', 'b3')])
            c.attr(label='orgchart')
            for pos in self.positions:
                pos.register(c, edge=pos.parent)

        for p in self.projects:
            p.register(g, edge=self)

        with g.subgraph(name="cluster_2") as c:
            c.attr(color='blue')
            c.node_attr['style'] = 'filled'
            c.attr(label='projects')
            for p in self.projects:
                # p.register(c, edge=self)
                for ca in p.controlaccounts:
                    ca.register(c, edge=p)
                    for w in ca.workpackages:
                        w.register(c, edge=ca)
                for r in p.risks:
                    r.register(c, edge=p)

        for bp in self.businessplans:
            bp.register(g, edge=self)

        with g.subgraph(name="cluster_3") as c:
            c.attr(color='blue')
            c.node_attr['style'] = 'filled'
            c.attr(label='businessplans')
            for bp in self.businessplans:
                for obj in bp.objectives:
                    obj.register(c, edge=bp)
                    for k in obj.keyresults:
                        k.register(c, edge=obj)
                        for ini in k.initiatives:
                            ini.register(c, edge=k)
        g.render(directory='build', view=True)


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
    __node_attr__ = { 'shape':'box', 'style': 'filled', 'fillcolor': 'honeydew'}

    __mapper_args__ = {
        "polymorphic_on": "type",
        "polymorphic_identity": "position",
    }

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id = mapped_column(ForeignKey(f"position.id"))
    type: Mapped[str]
    name: Mapped[str]

    parent = relationship("Position", back_populates="children", remote_side=[id])
    children = relationship("Position")

    businessunit_id: Mapped[int] = mapped_column(ForeignKey("businessunit.id"))
    businessunit: Mapped["BusinessUnit"] = relationship(back_populates="positions",
        overlaps="managed_by")

    manages: Mapped["BusinessUnit"] = relationship(back_populates="managed_by",
        overlaps="businessunit,positions")

# -----------------------------------------------------------------------------
# Planning / OKR

class BusinessPlan(CommonMixin, Base):
    __node_attr__ = { 'shape':'box', 'style': 'filled', 'fillcolor': 'lightyellow'}

    businessunit_id: Mapped[int] = mapped_column(ForeignKey("businessunit.id"))
    businessunit: Mapped["BusinessUnit"] = relationship(back_populates="businessplans")

    objectives: Mapped[List["Objective"]] = relationship(
        back_populates="businessplan", cascade="all, delete-orphan"
    )

class Objective(CommonMixin, Base):
    """A significant, concrete, clearly defined goal.

    i.e. where you want to go
    """
    __node_attr__ = { 'style': 'rounded,filled', 'shape':'box', 'fillcolor': 'aqua'}

    businessplan_id: Mapped[int] = mapped_column(ForeignKey("businessplan.id"))
    businessplan: Mapped["BusinessPlan"] = relationship(back_populates="objectives")
    keyresults: Mapped[List["KeyResult"]] = relationship(
        back_populates="objective", cascade="all, delete-orphan"
    )

class KeyResult(CommonMixin, Base):
    """Measurable success criteria used to track the achievement of an Objective
    """
    __node_attr__ = { 'style': 'rounded,filled', 'shape':'box', 'fillcolor': 'gainsboro'}

    objective_id: Mapped[int] = mapped_column(ForeignKey("objective.id"))
    objective: Mapped["Objective"] = relationship(back_populates="keyresults")
    initiatives: Mapped[List["Initiative"]] = relationship(
        back_populates="keyresult", cascade="all, delete-orphan"
    )

class Initiative(CommonMixin, Base):
    """Plans and activities to help move forward KeyResult(s) and achieve the Objective.
    """
    __node_attr__ = { 'style': 'rounded,filled', 'shape':'box', 'fillcolor': 'aliceblue'}

    keyresult_id: Mapped[int] = mapped_column(ForeignKey("keyresult.id"))
    keyresult: Mapped["KeyResult"] = relationship(back_populates="initiatives")


# -----------------------------------------------------------------------------
# Projects

class Project(CommonMixin, Base):
    __node_attr__ = { 'shape':'box', 'style': 'filled', 'fillcolor': 'lightgreen'}

    businessunit_id: Mapped[int] = mapped_column(ForeignKey("businessunit.id"))
    businessunit: Mapped["BusinessUnit"] = relationship(back_populates="projects")
    controlaccounts: Mapped[List["ControlAccount"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    risks: Mapped[List["Risk"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class ControlAccount(CommonMixin, Base):
    """CA: A management control point where scope, budget, actual cost, and schedule
    are integrated and compared to earned value for performance measurement.

    Each control account may be further decomposed into work packages and/or
    planning packages.
    """
    __node_attr__ = { 'shape':'box', 'style': 'filled', 'fillcolor': 'lightpink'}

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
    __node_attr__ = { 'shape':'note', 'style': 'filled', 'fillcolor': 'darkseagreen1'}

    controlaccount_id: Mapped[int] = mapped_column(ForeignKey("controlaccount.id"))
    controlaccount: Mapped["ControlAccount"] = relationship(back_populates="workpackages")
    is_planned: Mapped[bool] = mapped_column(insert_default=False) # i.e. is still a planning package
    budget: Mapped[float] = mapped_column(insert_default=0.0)
    start_date: Mapped[date]
    end_date: Mapped[date]

class WorkBreakdownStructure(CommonMixin, Base):
    """WBS: A hierarchical decomposition of the total scope of work to be carried out
    by the project team to accomplish project objectives and create the required
    deliverables.
    """

class Risk(CommonMixin, Base):
    __node_attr__ = { 'shape':'parallelogram', 'style': 'filled', 'fillcolor': 'cornflowerblue'}

    project_id: Mapped[int] = mapped_column(ForeignKey("project.id"))
    project: Mapped["Project"] = relationship(back_populates="risks")
