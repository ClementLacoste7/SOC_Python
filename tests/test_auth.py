from datetime import UTC, datetime, timedelta

import jwt

from app.config import settings
from app.security import ALGORITHM, decode_access_token, verify_password


def make_token(username: str, minutes: int, key: str = settings.secret_key) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=minutes)
    return jwt.encode({"sub": username, "exp": expire}, key, algorithm=ALGORITHM)


def test_login_returns_token_for_the_right_user(headers_a, reporter_a):
    scheme, token = headers_a["Authorization"].split(" ")

    assert scheme == "Bearer"
    assert decode_access_token(token) == reporter_a.username


def test_wrong_password_and_unknown_user_get_the_same_401(client, reporter_a):
    wrong_password = client.post("/token", data={"username": "alice", "password": "wrong"})
    unknown_user = client.post("/token", data={"username": "ghost", "password": "wrong"})

    assert wrong_password.status_code == 401
    assert unknown_user.status_code == 401
    assert wrong_password.json() == unknown_user.json()
    assert "access_token" not in wrong_password.json()


def test_expired_token_is_rejected(client, reporter_a):
    expired = make_token(reporter_a.username, minutes=-1)

    response = client.get("/incidents", headers={"Authorization": f"Bearer {expired}"})

    assert response.status_code == 401


def test_token_signed_with_another_key_is_rejected(client, reporter_a):
    forged = make_token(reporter_a.username, minutes=5, key="another-key-0123456789-0123456789")

    response = client.get("/incidents", headers={"Authorization": f"Bearer {forged}"})

    assert response.status_code == 401


def test_password_is_stored_hashed(reporter_a):
    assert reporter_a.hashed_password != "Test1234!"
    assert reporter_a.hashed_password.startswith("$2b$")
    assert verify_password("Test1234!", reporter_a.hashed_password)
    assert not verify_password("wrong", reporter_a.hashed_password)
