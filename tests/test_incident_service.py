import pytest

from app.errors import ConflictError, ForbiddenError, NotFoundError
from app.incident_service import (
    close_incident,
    create_incident,
    get_incident_for_user,
    list_incidents_for_user,
    start_incident,
)
from app.schemas import Category, IncidentClose, IncidentCreate, IncidentState, Severity

PHISHING = IncidentCreate(
    title="Suspicious email", category=Category.SUSPICIOUS_EMAIL, severity=Severity.HIGH
)
LOST_LAPTOP = IncidentCreate(
    title="Lost laptop", category=Category.LOST_DEVICE, severity=Severity.LOW
)
CONCLUSION = IncidentClose(conclusion="Sender blocked")


def titles(incidents):
    return [incident.title for incident in incidents]


def test_create_incident_sets_author_and_state(session, reporter_a):
    incident = create_incident(session, reporter_a, PHISHING)

    assert incident.id is not None
    assert incident.author_id == reporter_a.id
    assert incident.state == IncidentState.NEW
    assert incident.closed_at is None


def test_close_from_new_is_refused_and_state_unchanged(session, reporter_a, analyst):
    incident = create_incident(session, reporter_a, PHISHING)

    with pytest.raises(ConflictError):
        close_incident(session, analyst, incident.id, CONCLUSION)

    session.refresh(incident)
    assert incident.state == IncidentState.NEW
    assert incident.conclusion is None


def test_reporter_cannot_start_incident(session, reporter_a):
    incident = create_incident(session, reporter_a, PHISHING)

    with pytest.raises(ForbiddenError):
        start_incident(session, reporter_a, incident.id)

    session.refresh(incident)
    assert incident.state == IncidentState.NEW


def test_full_workflow_new_to_closed(session, reporter_a, analyst):
    incident = create_incident(session, reporter_a, PHISHING)

    started = start_incident(session, analyst, incident.id)
    assert started.state == IncidentState.IN_PROGRESS

    closed = close_incident(session, analyst, incident.id, CONCLUSION)
    assert closed.state == IncidentState.CLOSED
    assert closed.conclusion == "Sender blocked"
    assert closed.closed_at is not None


def test_closed_incident_cannot_be_started_again(session, reporter_a, analyst):
    incident = create_incident(session, reporter_a, PHISHING)
    start_incident(session, analyst, incident.id)
    close_incident(session, analyst, incident.id, CONCLUSION)

    with pytest.raises(ConflictError):
        start_incident(session, analyst, incident.id)

    session.refresh(incident)
    assert incident.state == IncidentState.CLOSED


def test_reporter_cannot_read_incident_of_another_reporter(session, reporter_a, reporter_b):
    incident = create_incident(session, reporter_a, PHISHING)

    with pytest.raises(ForbiddenError):
        get_incident_for_user(session, reporter_b, incident.id)

    assert get_incident_for_user(session, reporter_a, incident.id).id == incident.id


def test_unknown_incident_is_not_found(session, analyst):
    with pytest.raises(NotFoundError):
        get_incident_for_user(session, analyst, 999)


def test_filters_alone_and_combined(session, reporter_a, reporter_b, analyst):
    create_incident(session, reporter_a, PHISHING)
    started = create_incident(session, reporter_a, LOST_LAPTOP)
    start_incident(session, analyst, started.id)
    create_incident(session, reporter_b, PHISHING.model_copy(update={"title": "Other email"}))

    everything = list_incidents_for_user(session, analyst)
    assert titles(everything) == ["Suspicious email", "Lost laptop", "Other email"]

    by_state = list_incidents_for_user(session, analyst, state=IncidentState.NEW)
    assert titles(by_state) == ["Suspicious email", "Other email"]

    by_severity = list_incidents_for_user(session, analyst, severity=Severity.LOW)
    assert titles(by_severity) == ["Lost laptop"]

    combined = list_incidents_for_user(
        session, analyst, state=IncidentState.NEW, severity=Severity.LOW
    )
    assert combined == []


def test_filters_never_show_incidents_of_another_reporter(session, reporter_a, reporter_b):
    create_incident(session, reporter_a, PHISHING)
    create_incident(session, reporter_b, LOST_LAPTOP)

    assert titles(list_incidents_for_user(session, reporter_b)) == ["Lost laptop"]
    assert list_incidents_for_user(session, reporter_b, severity=Severity.HIGH) == []
