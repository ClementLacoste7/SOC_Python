from enum import StrEnum


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
