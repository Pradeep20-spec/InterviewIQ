from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uuid
import bcrypt
import jwt
import os
import time
import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from database import execute_query

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

JWT_SECRET = os.getenv("JWT_SECRET", "")
if not JWT_SECRET:
    raise RuntimeError(
        "JWT_SECRET environment variable is not set. "
        "Add JWT_SECRET=<random-64-char-hex> to your .env file before starting the server."
    )

JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# ── Simple in-memory rate limiter ────────────────────────────────────
# Tracks timestamps of recent requests per IP; max 10 auth attempts per 60 s.
_rl_store: dict[str, list[float]] = defaultdict(list)
_RL_MAX = 10
_RL_WINDOW = 60  # seconds

def _rate_limit(request: Request) -> None:
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    timestamps = [t for t in _rl_store[ip] if now - t < _RL_WINDOW]
    if len(timestamps) >= _RL_MAX:
        raise HTTPException(
            status_code=429,
            detail=f"Too many requests. Please wait {_RL_WINDOW} seconds and try again.",
        )
    timestamps.append(now)
    _rl_store[ip] = timestamps


# --- Request / Response models ---

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    success: bool
    data: dict | None = None
    error: str | None = None


# --- Helpers ---

def create_token(user_id: str, email: str, name: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "name": name,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Dependency that extracts the current user from the JWT token."""
    return verify_token(credentials.credentials)


# --- Routes ---

@router.post("/register")
async def register(request: RegisterRequest, req: Request, _rl: None = Depends(_rate_limit)):
    """Register a new user account."""
    # Check if email already exists
    existing = execute_query(
        "SELECT id FROM users WHERE email = %s", (request.email,)
    )
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    # Hash password
    password_hash = bcrypt.hashpw(request.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    user_id = str(uuid.uuid4())

    # Insert user – the schema already has name & email; we add password_hash column via ALTER if needed
    try:
        execute_query(
            """INSERT INTO users (id, email, name, password_hash)
               VALUES (%s, %s, %s, %s)""",
            (user_id, request.email, request.name, password_hash),
            fetch=False,
        )
    except Exception as e:
        # If password_hash column doesn't exist yet, create it and retry
        if "password_hash" in str(e).lower() or "unknown column" in str(e).lower():
            execute_query(
                "ALTER TABLE users ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT ''",
                fetch=False,
            )
            execute_query(
                """INSERT INTO users (id, email, name, password_hash)
                   VALUES (%s, %s, %s, %s)""",
                (user_id, request.email, request.name, password_hash),
                fetch=False,
            )
        else:
            raise HTTPException(status_code=500, detail=str(e))

    token = create_token(user_id, request.email, request.name)

    return {
        "success": True,
        "data": {
            "token": token,
            "user": {"id": user_id, "email": request.email, "name": request.name},
        },
    }


@router.post("/login")
async def login(request: LoginRequest, req: Request, _rl: None = Depends(_rate_limit)):
    """Log in with email and password."""
    rows = execute_query(
        "SELECT id, email, name, password_hash FROM users WHERE email = %s",
        (request.email,),
    )
    if not rows:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user = rows[0]
    if not bcrypt.checkpw(request.password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token(user["id"], user["email"], user["name"])

    return {
        "success": True,
        "data": {
            "token": token,
            "user": {"id": user["id"], "email": user["email"], "name": user["name"]},
        },
    }


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    rows = execute_query(
        "SELECT id, email, name, created_at FROM users WHERE id = %s",
        (current_user["sub"],),
    )
    if not rows:
        raise HTTPException(status_code=404, detail="User not found")

    user = rows[0]
    # Convert datetime for JSON serialisation
    if isinstance(user.get("created_at"), datetime):
        user["created_at"] = user["created_at"].isoformat()

    return {"success": True, "data": user}
