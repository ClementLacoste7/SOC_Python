import logging

from sqlmodel import Session

from app import incident_repository
from app.errors import ConflictError, ForbiddenError, NotFoundError
from app.models import Incident, User, utc_now
from app.schemas import IncidentClose, IncidentCreate, IncidentState, Role, Severity

logger = logging.getLogger(__name__)


def create_incident(session: Session, user: User, data: IncidentCreate) -> Incident:
    # Author and state come from the server, never from the client
    incident = Incident(**data.model_dump(), author_id=user.id)
    incident = incident_repository.save_incident(session, incident)
    logger.info("Incident %d created by %r", incident.id, user.username)
    return incident


def get_incident_for_user(session: Session, user: User, incident_id: int) -> Incident:
    incident = incident_repository.get_incident(session, incident_id)
    if incident is None:
        raise NotFoundError("Incident not found")
    # Ownership check done on the server for every request
    if user.role != Role.ANALYST and incident.author_id != user.id:
        raise ForbiddenError("You can only read your own incidents")
    return incident


def list_incidents_for_user(
    session: Session,
    user: User,
    state: IncidentState | None = None,
    severity: Severity | None = None,
) -> list[Incident]:
    # A reporter only sees their own incidents, an analyst sees all of them
    author_id = None if user.role == Role.ANALYST else user.id
    return incident_repository.list_incidents(session, author_id, state, severity)


def start_incident(session: Session, user: User, incident_id: int) -> Incident:
    if user.role != Role.ANALYST:
        raise ForbiddenError("Only an analyst can start an incident")
    incident = get_incident_for_user(session, user, incident_id)
    if incident.state != IncidentState.NEW:
        raise ConflictError("Only a new incident can be started")
    incident.state = IncidentState.IN_PROGRESS
    logger.info("Incident %d started by %r", incident.id, user.username)
    return incident_repository.save_incident(session, incident)


def close_incident(session: Session, user: User, incident_id: int, data: IncidentClose) -> Incident:
    if user.role != Role.ANALYST:
        raise ForbiddenError("Only an analyst can close an incident")
    incident = get_incident_for_user(session, user, incident_id)
    # Closing straight from "nouveau" is refused
    if incident.state != IncidentState.IN_PROGRESS:
        raise ConflictError("Only an incident in progress can be closed")
    incident.state = IncidentState.CLOSED
    incident.conclusion = data.conclusion
    incident.closed_at = utc_now()
    logger.info("Incident %d closed by %r", incident.id, user.username)
    return incident_repository.save_incident(session, incident)


def build_summary(session: Session) -> dict:
    # Every state and severity is listed, even with a count of zero
    incidents = incident_repository.list_incidents(session)
    by_state = {state.value: 0 for state in IncidentState}
    by_severity = {severity.value: 0 for severity in Severity}
    for incident in incidents:
        by_state[incident.state] += 1
        by_severity[incident.severity] += 1
    return {"total": len(incidents), "par_etat": by_state, "par_gravite": by_severity}
