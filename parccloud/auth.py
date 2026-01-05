"""
parcCloud Authentication Module

Simple, secure authentication gateway for Newton API.
- Free user signup
- Email/password authentication
- Admin access (for Jared)
- JWT-like tokens with expiration

Storage: JSON file (upgrade to proper DB later if needed)
"""

import hashlib
import secrets
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

# Storage location (use /tmp on Render for persistence within instance)
STORAGE_DIR = Path(os.environ.get("NEWTON_STORAGE", "/tmp/newton"))
USERS_FILE = STORAGE_DIR / "parccloud_users.json"

# Token expiration
TOKEN_EXPIRY_HOURS = 24 * 7  # 1 week

# Admin credentials (set via environment variables for security)
ADMIN_KEY = os.environ.get("PARCCLOUD_ADMIN_KEY", "newton-admin-2026")
ADMIN_SECRET = os.environ.get("PARCCLOUD_ADMIN_SECRET", "ask-newton-go")


# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class SignUpRequest(BaseModel):
    name: str
    email: str
    password: str


class SignInRequest(BaseModel):
    email: str
    password: str


class AdminAuthRequest(BaseModel):
    adminKey: str
    adminSecret: str


class UserInfo(BaseModel):
    id: str
    name: str
    email: str
    is_admin: bool = False
    created_at: str
    tier: str = "free"


class AuthResponse(BaseModel):
    success: bool
    message: str = ""
    token: Optional[str] = None
    expires: Optional[str] = None
    user: Optional[Dict[str, Any]] = None
    redirect: str = "/"


# ═══════════════════════════════════════════════════════════════════════════════
# STORAGE HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _ensure_storage():
    """Ensure storage directory and file exist."""
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    if not USERS_FILE.exists():
        USERS_FILE.write_text(json.dumps({"users": {}, "sessions": {}}))


def _load_data() -> Dict:
    """Load user data from JSON file."""
    _ensure_storage()
    try:
        return json.loads(USERS_FILE.read_text())
    except (json.JSONDecodeError, FileNotFoundError):
        return {"users": {}, "sessions": {}}


def _save_data(data: Dict):
    """Save user data to JSON file."""
    _ensure_storage()
    USERS_FILE.write_text(json.dumps(data, indent=2))


def _hash_password(password: str, salt: str = None) -> tuple:
    """Hash password with salt using SHA-256."""
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return hashed, salt


def _generate_token() -> str:
    """Generate a secure random token."""
    return secrets.token_urlsafe(32)


def _generate_user_id() -> str:
    """Generate a unique user ID."""
    return f"usr_{secrets.token_hex(8)}"


# ═══════════════════════════════════════════════════════════════════════════════
# AUTHENTICATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def signup(name: str, email: str, password: str) -> AuthResponse:
    """Create a new free account."""
    email = email.lower().strip()
    name = name.strip()

    # Validation
    if len(name) < 1:
        return AuthResponse(success=False, message="Name is required")

    if len(password) < 8:
        return AuthResponse(success=False, message="Password must be at least 8 characters")

    if "@" not in email or "." not in email:
        return AuthResponse(success=False, message="Invalid email address")

    # Load existing users
    data = _load_data()

    # Check if email exists
    for user in data["users"].values():
        if user["email"] == email:
            return AuthResponse(success=False, message="Email already registered. Try signing in.")

    # Create new user
    user_id = _generate_user_id()
    hashed, salt = _hash_password(password)

    user = {
        "id": user_id,
        "name": name,
        "email": email,
        "password_hash": hashed,
        "password_salt": salt,
        "is_admin": False,
        "tier": "free",
        "created_at": datetime.utcnow().isoformat(),
    }

    # Generate session token
    token = _generate_token()
    expires = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)

    # Store user and session
    data["users"][user_id] = user
    data["sessions"][token] = {
        "user_id": user_id,
        "expires": expires.isoformat(),
        "is_admin": False,
    }
    _save_data(data)

    return AuthResponse(
        success=True,
        message="Account created successfully",
        token=token,
        expires=expires.isoformat(),
        user={
            "id": user_id,
            "name": name,
            "email": email,
            "is_admin": False,
            "tier": "free",
        },
        redirect="/",
    )


def signin(email: str, password: str) -> AuthResponse:
    """Sign in with email and password."""
    email = email.lower().strip()

    data = _load_data()

    # Find user by email
    user = None
    for u in data["users"].values():
        if u["email"] == email:
            user = u
            break

    if not user:
        return AuthResponse(success=False, message="No account found with this email")

    # Verify password
    hashed, _ = _hash_password(password, user["password_salt"])
    if hashed != user["password_hash"]:
        return AuthResponse(success=False, message="Incorrect password")

    # Generate new session token
    token = _generate_token()
    expires = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)

    # Store session
    data["sessions"][token] = {
        "user_id": user["id"],
        "expires": expires.isoformat(),
        "is_admin": user.get("is_admin", False),
    }
    _save_data(data)

    return AuthResponse(
        success=True,
        message="Signed in successfully",
        token=token,
        expires=expires.isoformat(),
        user={
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "is_admin": user.get("is_admin", False),
            "tier": user.get("tier", "free"),
        },
        redirect="/",
    )


def admin_auth(admin_key: str, admin_secret: str) -> AuthResponse:
    """Authenticate as admin."""
    # Verify admin credentials
    if admin_key != ADMIN_KEY or admin_secret != ADMIN_SECRET:
        return AuthResponse(success=False, message="Invalid admin credentials")

    # Generate admin session token
    token = _generate_token()
    expires = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)

    data = _load_data()
    data["sessions"][token] = {
        "user_id": "admin",
        "expires": expires.isoformat(),
        "is_admin": True,
    }
    _save_data(data)

    return AuthResponse(
        success=True,
        message="Admin access granted",
        token=token,
        expires=expires.isoformat(),
        user={
            "id": "admin",
            "name": "Administrator",
            "email": "admin@parccloud.io",
            "is_admin": True,
            "tier": "admin",
        },
        redirect="/",
    )


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify a session token and return user info if valid."""
    if not token:
        return None

    data = _load_data()
    session = data["sessions"].get(token)

    if not session:
        return None

    # Check expiration
    expires = datetime.fromisoformat(session["expires"])
    if datetime.utcnow() > expires:
        # Clean up expired session
        del data["sessions"][token]
        _save_data(data)
        return None

    # Get user info
    if session["user_id"] == "admin":
        return {
            "id": "admin",
            "name": "Administrator",
            "is_admin": True,
            "tier": "admin",
        }

    user = data["users"].get(session["user_id"])
    if not user:
        return None

    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "is_admin": user.get("is_admin", False),
        "tier": user.get("tier", "free"),
    }


def logout(token: str) -> bool:
    """Invalidate a session token."""
    data = _load_data()
    if token in data["sessions"]:
        del data["sessions"][token]
        _save_data(data)
        return True
    return False


def get_user_count() -> int:
    """Get total number of registered users."""
    data = _load_data()
    return len(data["users"])
