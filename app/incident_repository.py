from sqlmodel import Session, delete, select

from app.models import Incident


def save_incident(session: Session, incident: Incident) -> Incident:
    session.add(incident)
    session.commit()
    session.refresh(incident)
    return incident


def get_incident(session: Session, incident_id: int) -> Incident | None:
    return session.get(Incident, incident_id)


def list_incidents(
    session: Session,
    author_id: int | None = None,
    state: str | None = None,
    severity: str | None = None,
) -> list[Incident]:
    # Each filter is optional, combined filters must all match
    query = select(Incident)
    if author_id is not None:
        query = query.where(Incident.author_id == author_id)
    if state is not None:
        query = query.where(Incident.state == state)
    if severity is not None:
        query = query.where(Incident.severity == severity)
    return list(session.exec(query.order_by(Incident.id)).all())


def delete_all_incidents(session: Session) -> None:
    session.exec(delete(Incident))
    session.commit()
