from sqlmodel import Session

from app import incident_repository
from app.errors import ForbiddenError, NotFoundError
from app.models import Incident, User
from app.schemas import IncidentCreate, IncidentState, Role, Severity


def create_incident(session: Session, user: User, data: IncidentCreate) -> Incident:
    # Author and state come from the server, never from the client
    incident = Incident(**data.model_dump(), author_id=user.id)
    return incident_repository.save_incident(session, incident)


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
