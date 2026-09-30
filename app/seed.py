import logging

from sqlmodel import Session

from app import incident_repository, user_repository
from app.errors import ConflictError
from app.incident_service import close_incident, create_incident, start_incident
from app.models import User
from app.schemas import Category, IncidentClose, IncidentCreate, Role, Severity
from app.security import hash_password

logger = logging.getLogger(__name__)

# Fictional accounts, documented in the README
DEMO_PASSWORD = "Demo1234!"
DEMO_USERS = {"alice": Role.REPORTER, "bob": Role.REPORTER, "carol": Role.ANALYST}


def reset_demo_data(session: Session) -> None:
    # Guard: a database holding other accounts is not the demo database
    for user in user_repository.list_users(session):
        if user.username not in DEMO_USERS:
            raise ConflictError("Reset refused: this database contains non demo accounts")

    incident_repository.delete_all_incidents(session)
    user_repository.delete_all_users(session)

    users = {}
    for username, role in DEMO_USERS.items():
        user = User(username=username, hashed_password=hash_password(DEMO_PASSWORD), role=role)
        users[username] = user_repository.save_user(session, user)
    alice, bob, carol = users["alice"], users["bob"], users["carol"]

    # Incidents go through the services, so the demo data follows the rules
    create_incident(
        session,
        alice,
        IncidentCreate(
            title="Suspicious invoice email",
            description="Email asking to open an attached invoice",
            category=Category.SUSPICIOUS_EMAIL,
            severity=Severity.HIGH,
        ),
    )
    laptop = create_incident(
        session,
        alice,
        IncidentCreate(
            title="Laptop lost on the train",
            category=Category.LOST_DEVICE,
            severity=Severity.MEDIUM,
        ),
    )
    start_incident(session, carol, laptop.id)
    account = create_incident(
        session,
        bob,
        IncidentCreate(
            title="Login from an unknown country",
            category=Category.COMPROMISED_ACCOUNT,
            severity=Severity.HIGH,
        ),
    )
    start_incident(session, carol, account.id)
    close_incident(
        session, carol, account.id, IncidentClose(conclusion="Password reset, sessions revoked")
    )
    logger.info("Demo data reset with %d accounts and 3 incidents", len(users))
