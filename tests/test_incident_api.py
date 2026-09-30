from sqlmodel import select

from app.models import Incident

PHISHING = {"title": "Suspicious email", "category": "courriel_suspect", "severity": "forte"}
LOST_LAPTOP = {"title": "Lost laptop", "category": "poste_perdu", "severity": "faible"}


def count_incidents(session) -> int:
    return len(session.exec(select(Incident)).all())


def test_create_incident_returns_201_with_author_and_state(client, headers_a, reporter_a):
    response = client.post("/incidents", json=PHISHING, headers=headers_a)

    assert response.status_code == 201
    body = response.json()
    assert body["author_id"] == reporter_a.id
    assert body["state"] == "nouveau"
    assert body["title"] == "Suspicious email"


def test_unknown_severity_or_empty_title_is_rejected_without_creation(client, headers_a, session):
    unknown_severity = client.post(
        "/incidents", json={**PHISHING, "severity": "critique"}, headers=headers_a
    )
    empty_title = client.post("/incidents", json={**PHISHING, "title": "   "}, headers=headers_a)

    assert unknown_severity.status_code == 422
    assert empty_title.status_code == 422
    assert count_incidents(session) == 0


def test_client_cannot_choose_state_or_author(client, headers_a, session):
    response = client.post(
        "/incidents", json={**PHISHING, "state": "clos", "author_id": 99}, headers=headers_a
    )

    assert response.status_code == 422
    assert count_incidents(session) == 0


def test_missing_or_invalid_token_is_rejected_without_creation(client, session):
    no_token = client.post("/incidents", json=PHISHING)
    bad_token = client.post(
        "/incidents", json=PHISHING, headers={"Authorization": "Bearer not-a-token"}
    )

    assert no_token.status_code == 401
    assert bad_token.status_code == 401
    assert count_incidents(session) == 0


def test_reporter_gets_403_on_incident_of_another_reporter(client, headers_a, headers_b):
    incident_id = client.post("/incidents", json=PHISHING, headers=headers_a).json()["id"]

    response = client.get(f"/incidents/{incident_id}", headers=headers_b)

    assert response.status_code == 403
    assert "title" not in response.json()
    assert client.get(f"/incidents/{incident_id}", headers=headers_a).status_code == 200


def test_unknown_incident_returns_404(client, headers_analyst):
    assert client.get("/incidents/999", headers=headers_analyst).status_code == 404


def test_close_refused_from_new_and_without_conclusion(client, headers_a, headers_analyst):
    incident_id = client.post("/incidents", json=PHISHING, headers=headers_a).json()["id"]
    close_url = f"/incidents/{incident_id}/close"

    from_new = client.patch(close_url, json={"conclusion": "Done"}, headers=headers_analyst)
    assert from_new.status_code == 409

    client.patch(f"/incidents/{incident_id}/start", headers=headers_analyst)
    empty = client.patch(close_url, json={"conclusion": "  "}, headers=headers_analyst)
    assert empty.status_code == 422

    current = client.get(f"/incidents/{incident_id}", headers=headers_analyst).json()
    assert current["state"] == "en_cours"
    assert current["conclusion"] is None


def test_full_workflow_over_http(client, headers_a, headers_analyst):
    incident_id = client.post("/incidents", json=PHISHING, headers=headers_a).json()["id"]

    started = client.patch(f"/incidents/{incident_id}/start", headers=headers_analyst)
    assert started.status_code == 200
    assert started.json()["state"] == "en_cours"

    closed = client.patch(
        f"/incidents/{incident_id}/close",
        json={"conclusion": "Sender blocked"},
        headers=headers_analyst,
    )
    assert closed.status_code == 200
    assert closed.json()["state"] == "clos"
    assert closed.json()["closed_at"] is not None

    # A closed incident can still be read by its author
    assert client.get(f"/incidents/{incident_id}", headers=headers_a).json()["state"] == "clos"


def test_filters_over_http(client, headers_a, headers_b, headers_analyst):
    client.post("/incidents", json=PHISHING, headers=headers_a)
    client.post("/incidents", json=LOST_LAPTOP, headers=headers_b)

    def titles(query: str, headers: dict) -> list[str]:
        response = client.get(f"/incidents{query}", headers=headers)
        return [incident["title"] for incident in response.json()]

    assert titles("", headers_analyst) == ["Suspicious email", "Lost laptop"]
    assert titles("?gravite=faible", headers_analyst) == ["Lost laptop"]
    assert titles("?etat=nouveau&gravite=forte", headers_analyst) == ["Suspicious email"]
    assert titles("?etat=clos", headers_analyst) == []
    assert titles("?gravite=faible", headers_a) == []
    assert client.get("/incidents?etat=fini", headers=headers_analyst).status_code == 422
