import pytest

from app import user_repository
from app.errors import ConflictError
from app.incident_service import build_summary
from app.models import User
from app.security import verify_password
from app.seed import DEMO_PASSWORD, reset_demo_data

EXPECTED_SUMMARY = {
    "total": 3,
    "par_etat": {"nouveau": 1, "en_cours": 1, "clos": 1},
    "par_gravite": {"faible": 0, "moyenne": 1, "forte": 2},
}


def test_reset_demo_creates_accounts_and_incidents(session):
    reset_demo_data(session)

    users = user_repository.list_users(session)
    assert sorted(user.username for user in users) == ["alice", "bob", "carol"]
    assert all(verify_password(DEMO_PASSWORD, user.hashed_password) for user in users)
    assert build_summary(session) == EXPECTED_SUMMARY


def test_reset_demo_can_be_replayed(session):
    reset_demo_data(session)
    reset_demo_data(session)

    assert len(user_repository.list_users(session)) == 3
    assert build_summary(session) == EXPECTED_SUMMARY


def test_reset_demo_is_refused_on_a_database_with_other_accounts(session):
    reset_demo_data(session)
    user_repository.save_user(session, User(username="dave", hashed_password="x", role="declarant"))

    with pytest.raises(ConflictError):
        reset_demo_data(session)

    assert len(user_repository.list_users(session)) == 4
    assert build_summary(session) == EXPECTED_SUMMARY
