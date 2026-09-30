from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app import incident_service
from app.database import get_session
from app.deps import get_current_user
from app.models import Incident, User
from app.schemas import IncidentClose, IncidentCreate, IncidentRead, IncidentState, Severity

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post("", response_model=IncidentRead, status_code=status.HTTP_201_CREATED)
def create_incident(
    data: IncidentCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Incident:
    return incident_service.create_incident(session, user, data)


@router.get("", response_model=list[IncidentRead])
def list_incidents(
    etat: IncidentState | None = None,
    gravite: Severity | None = None,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[Incident]:
    # Unknown filter values are rejected with 422 by the enums
    return incident_service.list_incidents_for_user(session, user, etat, gravite)


@router.get("/{incident_id}", response_model=IncidentRead)
def read_incident(
    incident_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Incident:
    return incident_service.get_incident_for_user(session, user, incident_id)


@router.patch("/{incident_id}/start", response_model=IncidentRead)
def start_incident(
    incident_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Incident:
    return incident_service.start_incident(session, user, incident_id)


@router.patch("/{incident_id}/close", response_model=IncidentRead)
def close_incident(
    incident_id: int,
    data: IncidentClose,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Incident:
    return incident_service.close_incident(session, user, incident_id, data)
