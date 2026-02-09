"""
parcCloud - Authentication Gateway for Newton API

Like iCloud, but for Newton. The beach before the storm.
"""

from .auth import (
    signup,
    signin,
    admin_auth,
    verify_token,
    logout,
    get_user_count,
    SignUpRequest,
    SignInRequest,
    AdminAuthRequest,
    AuthResponse,
    UserInfo,
)

__all__ = [
    "signup",
    "signin",
    "admin_auth",
    "verify_token",
    "logout",
    "get_user_count",
    "SignUpRequest",
    "SignInRequest",
    "AdminAuthRequest",
    "AuthResponse",
    "UserInfo",
]
