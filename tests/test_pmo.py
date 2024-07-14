from datetime import date

from pmo.models import (
    create_engine, Base, Session,
    BusinessUnit, Position,
    BusinessPlan, Project, ControlAccount,
    Risk, WorkPackage, WorkBreakdownStructure,
    Objective, KeyResult, Initiative
)

DEBUG=True

def test_models():
    if DEBUG:
        engine = create_engine("sqlite://", echo=True)
    else:
        engine = create_engine("sqlite:///biz.db", echo=False)

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        bu = BusinessUnit(name="acme")
        # org structure
        ceo = Position(name="ceo", type="position", businessunit=bu, manages=bu)
        coo = Position(name="coo", type="position", businessunit=bu, parent=ceo)
        mgr1 = Position(name="mgr1", type="position", businessunit=bu, parent=coo)
        mgr2 = Position(name="mgr2", type="position", businessunit=bu, parent=coo)

        # bp planning
        bp = BusinessPlan(name="3-year bizplan", businessunit=bu)
        ob1 = Objective(name="Crush the competition through acquisitions", businessplan=bp)
        kr1 = KeyResult(name="Acquire 3 small players in our industry", objective=ob1)
        in1 = Initiative(name="Secure M&A financing approval from banks", keyresult=kr1)

        # project planning
        p1 = Project(name="Build gas-station", businessunit=bu)
        ca1 = ControlAccount(name="Mobilization", project=p1)
        r1 = Risk(name="schedule risk", project=p1)
        wp1 = WorkPackage(name="Project management", controlaccount=ca1, start_date=date.today(), end_date=date.today())

        session.add_all([bu, bp, r1])
        session.commit()
        bu.mk_graph()
