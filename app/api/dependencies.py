from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import models  # assuming models.py has a User model
from jose import JWTError, jwt  # optional if using JWT-based auth

# Constants for JWT (update with your own secret & algorithm)
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# (Optional) Dependency to get current user using JWT token
def get_current_user(token: str = Depends(...), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

# Placeholder for other dependencies like permissions, rate limits, etc.
