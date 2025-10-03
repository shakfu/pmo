from pmo.models import (
    ChangeRequestStatus,
    IssueStatus,
    ProjectLifecycleStage,
    ProjectType,
    Project,
)


def test_models(session, sample_dataset):
    bu = sample_dataset["business_unit"]
    project: Project = sample_dataset["project"]
    positions = sample_dataset["positions"]

    graph = bu.mk_graph(render=False)

    refreshed_project = session.get(Project, project.id)
    assert refreshed_project is not None
    assert refreshed_project.category is ProjectType.substation
    assert refreshed_project.status_history[0].stage is ProjectLifecycleStage.awarded
    assert refreshed_project.resource_assignments[0].position.name == positions["pm"].name
    assert refreshed_project.issues[0].owner.name == positions["pm"].name
    assert refreshed_project.change_requests[0].status is ChangeRequestStatus.submitted
    assert positions["pm"].assignments[0].role == "Lead PM"
    assert IssueStatus.open in {issue.status for issue in refreshed_project.issues}
    assert ChangeRequestStatus.submitted in {
        change.status for change in refreshed_project.change_requests
    }
    assert "projectstatushistory" in graph.source
    assert "resourceassignment" in graph.source
    assert "issue" in graph.source
    assert "changerequest" in graph.source
