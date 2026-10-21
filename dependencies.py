
import os

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db

load_dotenv()

bearer_scheme = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    secret = os.getenv("JWT_SECRET_KEY")
    algorithm = os.getenv("JWT_ALGORITHM", "HS256")

    if not secret:
        raise HTTPException(
            status_code=500,
            detail="JWT configuration is missing.",
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            secret,
            algorithms=[algorithm],
        )
        subject = payload.get("sub")
        user_id = int(subject)
        if user_id <= 0:
            raise ValueError("Invalid user ID")
    except (jwt.InvalidTokenError, TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"id": user_id, "claims": payload}


def require_file_access(
    user: dict = Depends(get_current_user),
):
    return user


def get_db_dependency(db: Session = Depends(get_db)):
    return db
