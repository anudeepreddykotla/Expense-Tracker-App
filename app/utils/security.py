import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError

# Configuration for JWT
# You should store these securely, e.g., in environment variables
SECRET_KEY = "your-secret-key" # Replace with a strong, random key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_DAYS = 7    # 7 days

# Reverted to original password hashing and verification
def get_password_hash(password: str) -> str:
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
    return f"{salt}:{pwd_hash}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        salt, pwd_hash = hashed_password.split(':', 1)
        return pwd_hash == hashlib.sha256(f"{plain_password}{salt}".encode()).hexdigest()
    except (ValueError, TypeError):
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def authenticate_user(db, email: str, password: str):
    from app.db.models import User # Import here to avoid circular dependency
    from sqlalchemy import select

    user = await db.execute(select(User).where(User.email == email))
    user = user.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user
