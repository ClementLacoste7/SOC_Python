import json
import sys

import cli
from app.incident_service import close_incident, create_incident, start_incident
from app.schemas import Category, IncidentClose, IncidentCreate, Severity


def new_incident(severity: Severity) -> IncidentCreate:
    return IncidentCreate(title="Test incident", category=Category.OTHER, severity=severity)


def test_bilan_matches_test_data(session, reporter_a, analyst, monkeypatch, capsys):
    create_incident(session, reporter_a, new_incident(Severity.HIGH))
    started = create_incident(session, reporter_a, new_incident(Severity.HIGH))
    start_incident(session, analyst, started.id)
    closed = create_incident(session, reporter_a, new_incident(Severity.LOW))
    start_incident(session, analyst, closed.id)
    close_incident(session, analyst, closed.id, IncidentClose(conclusion="Solved"))

    # Run the real command and read what it prints on stdout
    monkeypatch.setattr(sys, "argv", ["cli.py", "bilan", "--format", "json"])
    cli.main()
    output = json.loads(capsys.readouterr().out)

    assert output == {
        "total": 3,
        "par_etat": {"nouveau": 1, "en_cours": 1, "clos": 1},
        "par_gravite": {"faible": 1, "moyenne": 0, "forte": 2},
    }


def test_bilan_on_empty_database(session, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["cli.py", "bilan"])
    cli.main()
    output = json.loads(capsys.readouterr().out)

    assert output["total"] == 0
    assert output["par_etat"] == {"nouveau": 0, "en_cours": 0, "clos": 0}
