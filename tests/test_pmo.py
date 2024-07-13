from datetime import date

from pmo.models import (
    create_engine, Base, Session, BusinessUnit,
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
        bp = BusinessPlan(name="3-year bizplan", businessunit=bu)
        p1 = Project(name="Build gas-station", businessunit=bu)
        ca1 = ControlAccount(name="Mobilization", project=p1)
        r1 = Risk(name="schedule risk", project=p1)
        wp1 = WorkPackage(name="Project management", controlaccount=ca1, start_date=date.today(), end_date=date.today())
        ob1 = Objective(name="Crush the competition through acquisitions")
        kr1 = KeyResult(name="Acquire 3 small players in our industry")
        in1 = Initiative(name="Secure M&A financing approval from banks")
        bu.objectives = [ob1]
        kr1.initiatives = [in1]
        ob1.keyresults = [kr1]
        session.add_all([bu, ob1, kr1, in1])
        session.commit()
        bu.mk_graph()