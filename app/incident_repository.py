from sqlmodel import Session

from app.models import Incident


def save_incident(session: Session, incident: Incident) -> Incident:
    session.add(incident)
    session.commit()
    session.refresh(incident)
    return incident


def get_incident(session: Session, incident_id: int) -> Incident | None:
    return session.get(Incident, incident_id)
