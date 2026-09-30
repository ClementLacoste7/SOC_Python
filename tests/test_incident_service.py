import pytest

from app.errors import ConflictError, ForbiddenError
from app.incident_service import close_incident, create_incident, start_incident
from app.schemas import Category, IncidentClose, IncidentCreate, IncidentState, Severity

PHISHING = IncidentCreate(
    title="Suspicious email", category=Category.SUSPICIOUS_EMAIL, severity=Severity.HIGH
)
CONCLUSION = IncidentClose(conclusion="Sender blocked")


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
