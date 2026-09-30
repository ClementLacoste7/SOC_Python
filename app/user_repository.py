from sqlmodel import Session, delete, select

from app.models import User


def get_user_by_username(session: Session, username: str) -> User | None:
    return session.exec(select(User).where(User.username == username)).first()


def save_user(session: Session, user: User) -> User:
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def list_users(session: Session) -> list[User]:
    return list(session.exec(select(User)).all())


def delete_all_users(session: Session) -> None:
    session.exec(delete(User))
    session.commit()
