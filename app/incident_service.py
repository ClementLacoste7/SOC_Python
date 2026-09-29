from sqlmodel import Session

from app import incident_repository
from app.models import Incident, User
from app.schemas import IncidentCreate


def create_incident(session: Session, user: User, data: IncidentCreate) -> Incident:
    # Author and state come from the server, never from the client
    incident = Incident(**data.model_dump(), author_id=user.id)
    return incident_repository.save_incident(session, incident)
