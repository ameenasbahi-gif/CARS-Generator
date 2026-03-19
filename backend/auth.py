"""
Auth helpers using only Python stdlib — no external libraries.
"""
import hashlib
import hmac
import secrets
import base64
import os
from datetime import datetime, timezone, timedelta

AUTH_SECRET = os.environ.get("AUTH_SECRET", "cars-mcat-fallback-secret-key-2026")
TOKEN_TTL_HOURS = 24


def hash_password(password: str) -> str:
    """Return 'sha256$salt$hash' string."""
    salt = secrets.token_hex(16)
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"sha256${salt}${h}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored 'sha256$salt$hash'."""
    try:
        scheme, salt, expected = stored_hash.split("$", 2)
    except ValueError:
        return False
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return hmac.compare_digest(h, expected)


def create_token(user_id: int, username: str) -> str:
    """Create a signed token: base64(payload):signature"""
    timestamp = int(datetime.now(timezone.utc).timestamp())
    payload = f"{user_id}:{username}:{timestamp}"
    payload_b64 = base64.urlsafe_b64encode(payload.encode()).decode()
    sig = hmac.new(AUTH_SECRET.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
    return f"{payload_b64}.{sig}"


def verify_token(token: str):
    """Return {user_id, username} if valid and not expired, else None."""
    try:
        payload_b64, sig = token.rsplit(".", 1)
    except ValueError:
        return None

    expected_sig = hmac.new(AUTH_SECRET.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected_sig):
        return None

    try:
        payload = base64.urlsafe_b64decode(payload_b64.encode()).decode()
        user_id_str, username, timestamp_str = payload.split(":", 2)
        user_id = int(user_id_str)
        timestamp = int(timestamp_str)
    except Exception:
        return None

    age_hours = (datetime.now(timezone.utc).timestamp() - timestamp) / 3600
    if age_hours > TOKEN_TTL_HOURS:
        return None

    return {"user_id": user_id, "username": username}
