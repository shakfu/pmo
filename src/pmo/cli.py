#!/usr/bin/env python3
"""
PMO CLI - Command Line Interface for Project Management Office

Provides CRUD operations for business units, positions, projects, and business plans.
"""

import argparse
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from .models import (
    Base,
    BusinessUnit,
    Position,
    Project,
    ControlAccount,
    WorkPackage,
    BusinessPlan,
    Objective,
    KeyResult,
    Initiative,
    Risk,
    ProjectType,
)


class PMOCli:
    """Main CLI class for PMO operations"""

    def __init__(self, db_url: str = "sqlite:///pmo.db"):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)

    def get_session(self):
        """Get database session"""
        return Session(self.engine)

    # BusinessUnit CRUD operations
    def create_business_unit(self, name: str, unit_type: str = "businessunit", parent_id: Optional[int] = None):
        """Create a new business unit"""
        with self.get_session() as session:
            bu = BusinessUnit(name=name, type=unit_type, parent_id=parent_id)
            session.add(bu)
            session.commit()
            print(f"Created BusinessUnit: {bu}")
            return bu.id

    def list_business_units(self):
        """List all business units"""
        with self.get_session() as session:
            units = session.query(BusinessUnit).all()
            if not units:
                print("No business units found.")
                return
            
            print("Business Units:")
            for unit in units:
                parent_info = f" (parent: {unit.parent.name})" if unit.parent else ""
                manager_info = f" (managed by: {unit.managed_by.name})" if unit.managed_by else ""
                print(f"  {unit.id}: {unit.name} [{unit.type}]{parent_info}{manager_info}")

    def get_business_unit(self, unit_id: int):
        """Get business unit by ID"""
        with self.get_session() as session:
            unit = session.get(BusinessUnit, unit_id)
            if not unit:
                print(f"Business unit {unit_id} not found.")
                return None
            print(f"BusinessUnit: {unit}")
            return unit

    def update_business_unit(self, unit_id: int, name: Optional[str] = None, manager_id: Optional[int] = None):
        """Update business unit"""
        with self.get_session() as session:
            unit = session.get(BusinessUnit, unit_id)
            if not unit:
                print(f"Business unit {unit_id} not found.")
                return
            
            if name:
                unit.name = name
            if manager_id:
                manager = session.get(Position, manager_id)
                if manager:
                    unit.managed_by = manager
                else:
                    print(f"Manager {manager_id} not found.")
                    return
            
            session.commit()
            print(f"Updated BusinessUnit: {unit}")

    def delete_business_unit(self, unit_id: int):
        """Delete business unit"""
        with self.get_session() as session:
            unit = session.get(BusinessUnit, unit_id)
            if not unit:
                print(f"Business unit {unit_id} not found.")
                return
            
            session.delete(unit)
            session.commit()
            print(f"Deleted BusinessUnit {unit_id}")

    # Position CRUD operations
    def create_position(self, name: str, businessunit_id: int, position_type: str = "position", parent_id: Optional[int] = None):
        """Create a new position"""
        with self.get_session() as session:
            bu = session.get(BusinessUnit, businessunit_id)
            if not bu:
                print(f"Business unit {businessunit_id} not found.")
                return
            
            pos = Position(name=name, type=position_type, businessunit=bu, parent_id=parent_id)
            session.add(pos)
            session.commit()
            print(f"Created Position: {pos}")
            return pos.id

    def list_positions(self, businessunit_id: Optional[int] = None):
        """List positions, optionally filtered by business unit"""
        with self.get_session() as session:
            query = session.query(Position)
            if businessunit_id:
                query = query.filter(Position.businessunit_id == businessunit_id)
            
            positions = query.all()
            if not positions:
                print("No positions found.")
                return
            
            print("Positions:")
            for pos in positions:
                parent_info = f" (reports to: {pos.parent.name})" if pos.parent else ""
                manages_info = f" (manages: {pos.manages.name})" if pos.manages else ""
                print(f"  {pos.id}: {pos.name} [{pos.businessunit.name}]{parent_info}{manages_info}")

    # Project CRUD operations
    def create_project(self, name: str, businessunit_id: int, description: str, tender_no: str, 
                      scope_of_work: str, category: str = "substation", budget: float = 0.0, 
                      bid_value: float = 0.0):
        """Create a new project"""
        with self.get_session() as session:
            bu = session.get(BusinessUnit, businessunit_id)
            if not bu:
                print(f"Business unit {businessunit_id} not found.")
                return
            
            try:
                project_type = ProjectType[category]
            except KeyError:
                print(f"Invalid project category: {category}. Valid options: {list(ProjectType.__members__.keys())}")
                return
            
            project = Project(
                name=name,
                businessunit=bu,
                description=description,
                tender_no=tender_no,
                scope_of_work=scope_of_work,
                category=project_type,
                budget=budget,
                bid_value=bid_value,
                bid_issue_date=date.today(),
                tender_purchase_date=date.today(),
                bid_due_date=date.today(),
                completion_period_m=12,
                bid_validity_d=90,
            )
            session.add(project)
            session.commit()
            print(f"Created Project: {project}")
            return project.id

    def list_projects(self, businessunit_id: Optional[int] = None):
        """List projects, optionally filtered by business unit"""
        with self.get_session() as session:
            query = session.query(Project)
            if businessunit_id:
                query = query.filter(Project.businessunit_id == businessunit_id)
            
            projects = query.all()
            if not projects:
                print("No projects found.")
                return
            
            print("Projects:")
            for project in projects:
                print(f"  {project.id}: {project.name} [{project.businessunit.name}]")
                print(f"    Tender: {project.tender_no} | Budget: {project.budget} | Category: {project.category.name}")

    # BusinessPlan CRUD operations
    def create_business_plan(self, name: str, businessunit_id: int):
        """Create a new business plan"""
        with self.get_session() as session:
            bu = session.get(BusinessUnit, businessunit_id)
            if not bu:
                print(f"Business unit {businessunit_id} not found.")
                return
            
            bp = BusinessPlan(name=name, businessunit=bu)
            session.add(bp)
            session.commit()
            print(f"Created BusinessPlan: {bp}")
            return bp.id

    def list_business_plans(self, businessunit_id: Optional[int] = None):
        """List business plans, optionally filtered by business unit"""
        with self.get_session() as session:
            query = session.query(BusinessPlan)
            if businessunit_id:
                query = query.filter(BusinessPlan.businessunit_id == businessunit_id)
            
            plans = query.all()
            if not plans:
                print("No business plans found.")
                return
            
            print("Business Plans:")
            for plan in plans:
                obj_count = len(plan.objectives)
                print(f"  {plan.id}: {plan.name} [{plan.businessunit.name}] ({obj_count} objectives)")

    # Objective CRUD operations
    def create_objective(self, name: str, businessplan_id: int):
        """Create a new objective"""
        with self.get_session() as session:
            bp = session.get(BusinessPlan, businessplan_id)
            if not bp:
                print(f"Business plan {businessplan_id} not found.")
                return
            
            obj = Objective(name=name, businessplan=bp)
            session.add(obj)
            session.commit()
            print(f"Created Objective: {obj}")
            return obj.id

    # Graph generation
    def generate_graph(self, businessunit_id: int):
        """Generate organizational graph for a business unit"""
        with self.get_session() as session:
            unit = session.get(BusinessUnit, businessunit_id)
            if not unit:
                print(f"Business unit {businessunit_id} not found.")
                return
            
            try:
                unit.mk_graph()
                print(f"Graph generated for {unit.name} in build/ directory")
            except Exception as e:
                print(f"Error generating graph: {e}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="PMO CLI - Project Management Office tool")
    parser.add_argument("--db", default="sqlite:///pmo.db", help="Database URL (default: sqlite:///pmo.db)")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # BusinessUnit commands
    bu_parser = subparsers.add_parser("bu", help="Business unit operations")
    bu_subparsers = bu_parser.add_subparsers(dest="bu_action")
    
    bu_create = bu_subparsers.add_parser("create", help="Create business unit")
    bu_create.add_argument("name", help="Business unit name")
    bu_create.add_argument("--type", default="businessunit", help="Unit type")
    bu_create.add_argument("--parent-id", type=int, help="Parent business unit ID")
    
    bu_subparsers.add_parser("list", help="List business units")
    
    bu_get = bu_subparsers.add_parser("get", help="Get business unit")
    bu_get.add_argument("id", type=int, help="Business unit ID")
    
    bu_update = bu_subparsers.add_parser("update", help="Update business unit")
    bu_update.add_argument("id", type=int, help="Business unit ID")
    bu_update.add_argument("--name", help="New name")
    bu_update.add_argument("--manager-id", type=int, help="Manager position ID")
    
    bu_delete = bu_subparsers.add_parser("delete", help="Delete business unit")
    bu_delete.add_argument("id", type=int, help="Business unit ID")
    
    # Position commands
    pos_parser = subparsers.add_parser("pos", help="Position operations")
    pos_subparsers = pos_parser.add_subparsers(dest="pos_action")
    
    pos_create = pos_subparsers.add_parser("create", help="Create position")
    pos_create.add_argument("name", help="Position name")
    pos_create.add_argument("businessunit_id", type=int, help="Business unit ID")
    pos_create.add_argument("--type", default="position", help="Position type")
    pos_create.add_argument("--parent-id", type=int, help="Parent position ID")
    
    pos_list = pos_subparsers.add_parser("list", help="List positions")
    pos_list.add_argument("--bu-id", type=int, help="Filter by business unit ID")
    
    # Project commands
    proj_parser = subparsers.add_parser("proj", help="Project operations")
    proj_subparsers = proj_parser.add_subparsers(dest="proj_action")
    
    proj_create = proj_subparsers.add_parser("create", help="Create project")
    proj_create.add_argument("name", help="Project name")
    proj_create.add_argument("businessunit_id", type=int, help="Business unit ID")
    proj_create.add_argument("description", help="Project description")
    proj_create.add_argument("tender_no", help="Tender number")
    proj_create.add_argument("scope_of_work", help="Scope of work")
    proj_create.add_argument("--category", default="substation", 
                            choices=list(ProjectType.__members__.keys()), help="Project category")
    proj_create.add_argument("--budget", type=float, default=0.0, help="Project budget")
    proj_create.add_argument("--bid-value", type=float, default=0.0, help="Bid value")
    
    proj_list = proj_subparsers.add_parser("list", help="List projects")
    proj_list.add_argument("--bu-id", type=int, help="Filter by business unit ID")
    
    # BusinessPlan commands
    bp_parser = subparsers.add_parser("bp", help="Business plan operations")
    bp_subparsers = bp_parser.add_subparsers(dest="bp_action")
    
    bp_create = bp_subparsers.add_parser("create", help="Create business plan")
    bp_create.add_argument("name", help="Business plan name")
    bp_create.add_argument("businessunit_id", type=int, help="Business unit ID")
    
    bp_list = bp_subparsers.add_parser("list", help="List business plans")
    bp_list.add_argument("--bu-id", type=int, help="Filter by business unit ID")
    
    # Objective commands
    obj_parser = subparsers.add_parser("obj", help="Objective operations")
    obj_subparsers = obj_parser.add_subparsers(dest="obj_action")
    
    obj_create = obj_subparsers.add_parser("create", help="Create objective")
    obj_create.add_argument("name", help="Objective name")
    obj_create.add_argument("businessplan_id", type=int, help="Business plan ID")
    
    # Graph command
    graph_parser = subparsers.add_parser("graph", help="Generate organizational graph")
    graph_parser.add_argument("businessunit_id", type=int, help="Business unit ID")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = PMOCli(args.db)
    
    # Handle BusinessUnit commands
    if args.command == "bu":
        if args.bu_action == "create":
            cli.create_business_unit(args.name, args.type, args.parent_id)
        elif args.bu_action == "list":
            cli.list_business_units()
        elif args.bu_action == "get":
            cli.get_business_unit(args.id)
        elif args.bu_action == "update":
            cli.update_business_unit(args.id, args.name, args.manager_id)
        elif args.bu_action == "delete":
            cli.delete_business_unit(args.id)
        else:
            bu_parser.print_help()
    
    # Handle Position commands
    elif args.command == "pos":
        if args.pos_action == "create":
            cli.create_position(args.name, args.businessunit_id, args.type, args.parent_id)
        elif args.pos_action == "list":
            cli.list_positions(args.bu_id)
        else:
            pos_parser.print_help()
    
    # Handle Project commands
    elif args.command == "proj":
        if args.proj_action == "create":
            cli.create_project(args.name, args.businessunit_id, args.description, 
                             args.tender_no, args.scope_of_work, args.category, 
                             args.budget, args.bid_value)
        elif args.proj_action == "list":
            cli.list_projects(args.bu_id)
        else:
            proj_parser.print_help()
    
    # Handle BusinessPlan commands
    elif args.command == "bp":
        if args.bp_action == "create":
            cli.create_business_plan(args.name, args.businessunit_id)
        elif args.bp_action == "list":
            cli.list_business_plans(args.bu_id)
        else:
            bp_parser.print_help()
    
    # Handle Objective commands
    elif args.command == "obj":
        if args.obj_action == "create":
            cli.create_objective(args.name, args.businessplan_id)
        else:
            obj_parser.print_help()
    
    # Handle Graph command
    elif args.command == "graph":
        cli.generate_graph(args.businessunit_id)


if __name__ == "__main__":
    main()