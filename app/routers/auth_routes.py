from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.core.database import get_db
from app.models import User
from app.utils.auth import verify_password, create_access_token,decode_access_token
from app.schema.auth import *

router = APIRouter(prefix="/auth", tags=["Authentication"])


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(payload.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_access_token({
        "user_id": user.id,
        "role": user.role.name
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }
