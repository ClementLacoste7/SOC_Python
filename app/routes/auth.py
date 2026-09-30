from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.auth_service import authenticate
from app.database import get_session
from app.schemas import Token
from app.security import create_access_token

router = APIRouter(tags=["auth"])


@router.post("/token", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)
) -> Token:
    user = authenticate(session, form.username, form.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(user.username))
