# auth/utils.py

from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# —— Password hashing setup ——
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# —— JWT setup ——
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict | None:
    """
    Decode and validate a JWT. Returns the payload or None if invalid/expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Optional: you can check expiration here, but jose will raise if expired
        return payload
    except JWTError:
        return None


# —— Dependency for FastAPI protected routes ——
bearer_scheme = HTTPBearer()

async def get_current_username(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> str:
    """
    FastAPI dependency to:
      1) extract the Bearer token
      2) decode & validate it
      3) return the 'sub' (username) field from payload
    Raises 401 if missing/invalid.
    """
    token = creds.credentials
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload["sub"]