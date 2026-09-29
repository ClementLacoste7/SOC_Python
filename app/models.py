from datetime import UTC, datetime

from sqlmodel import Field, SQLModel

from app.schemas import IncidentState


def utc_now() -> datetime:
    return datetime.now(UTC)


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, max_length=50)
    hashed_password: str
    # Role value stored as plain text, like the incident enums
    role: str


class Incident(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=2000)
    # Enum values are stored as plain text, validated by the schemas
    category: str
    severity: str = Field(index=True)
    state: str = Field(default=IncidentState.NEW, index=True)
    author_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=utc_now)
    closed_at: datetime | None = None
    conclusion: str | None = None
