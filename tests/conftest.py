import os

# Dedicated test database and key, set before the app is imported
os.environ["DATABASE_URL"] = "sqlite:///./test_incidents.db"
os.environ["SECRET_KEY"] = "test-key-only-for-pytest-0123456789abcdef"

import pytest
from sqlmodel import Session, SQLModel

from app.database import engine
from app.models import User
from app.schemas import Role
from app.security import hash_password

TEST_PASSWORD = "Test1234!"
# Hashed once because bcrypt is slow on purpose
TEST_PASSWORD_HASH = hash_password(TEST_PASSWORD)


@pytest.fixture
def session():
    # Fresh tables for every test, so data is reproducible
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def add_user(session: Session, username: str, role: Role) -> User:
    user = User(username=username, hashed_password=TEST_PASSWORD_HASH, role=role)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def reporter_a(session):
    return add_user(session, "alice", Role.REPORTER)


@pytest.fixture
def reporter_b(session):
    return add_user(session, "bob", Role.REPORTER)


@pytest.fixture
def analyst(session):
    return add_user(session, "carol", Role.ANALYST)
