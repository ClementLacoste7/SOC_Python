from datetime import datetime
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


class IncidentState(StrEnum):
    NEW = "nouveau"
    IN_PROGRESS = "en_cours"
    CLOSED = "clos"


class Severity(StrEnum):
    LOW = "faible"
    MEDIUM = "moyenne"
    HIGH = "forte"


class Category(StrEnum):
    SUSPICIOUS_EMAIL = "courriel_suspect"
    LOST_DEVICE = "poste_perdu"
    COMPROMISED_ACCOUNT = "compte_compromis"
    OTHER = "autre"


class Role(StrEnum):
    REPORTER = "declarant"
    ANALYST = "analyste"


# Strip spaces so "   " is rejected like an empty string
Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
LongText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]


class IncidentCreate(BaseModel):
    # Reject unknown fields such as state or author_id sent by the client
    model_config = ConfigDict(extra="forbid")

    title: Title
    description: str = Field(default="", max_length=2000)
    category: Category
    severity: Severity


class IncidentClose(BaseModel):
    model_config = ConfigDict(extra="forbid")

    conclusion: LongText


class IncidentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    category: Category
    severity: Severity
    state: IncidentState
    author_id: int
    created_at: datetime
    closed_at: datetime | None
    conclusion: str | None
