import logging

from sqlmodel import Session

from app import user_repository
from app.models import User
from app.security import verify_password

logger = logging.getLogger(__name__)


def authenticate(session: Session, username: str, password: str) -> User | None:
    user = user_repository.get_user_by_username(session, username)
    # Same answer for unknown user and wrong password
    if user is None or not verify_password(password, user.hashed_password):
        logger.warning("Failed login for username %r", username)
        return None
    logger.info("Successful login for username %r", username)
    return user
