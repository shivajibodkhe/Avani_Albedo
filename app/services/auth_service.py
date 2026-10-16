import os
import time
import secrets
from typing import Dict, Any, Optional, List
from app.config import settings

class AuthService:
    def __init__(self):
        # In-memory session store: token -> { email, expires_at }
        self._active_sessions: Dict[str, Dict[str, Any]] = {}
        
    @property
    def is_auth_enabled(self) -> bool:
        return os.getenv("AUTH_ENABLED", "true").lower() in ("true", "1", "yes")

    @property
    def judge_password(self) -> str:
        return os.getenv("JUDGE_PASSWORD", "AvaniJudge@2026")

    @property
    def allowed_emails(self) -> List[str]:
        raw = os.getenv("ALLOWED_EMAILS", "srbodkhe@gmail.com")
        return [e.strip().lower() for e in raw.split(",") if e.strip()]

    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticates a user against the judge password and allowed emails.
        Supports username 'judges' and admin email (srbodkhe@gmail.com).
        """
        clean_id = email.strip().lower()
        clean_pw = password.strip()
        
        # Check password
        if clean_pw != self.judge_password:
            return None
            
        # Role determination
        if clean_id == "srbodkhe@gmail.com":
            role = "Super Admin"
            display_name = clean_id
        elif clean_id in ("judges", "judge", "judges@avani.eco"):
            role = "Judge / Evaluator"
            display_name = "judges"
        elif clean_id in self.allowed_emails:
            role = "Super Admin" if clean_id == "srbodkhe@gmail.com" else "Municipal Planner"
            display_name = clean_id
        else:
            return None
            
        token = secrets.token_hex(24)
        expires_at = time.time() + (86400 * 7) # 7-day session
        
        user_info = {
            "email": display_name,
            "role": role,
            "expires_at": expires_at
        }
        
        self._active_sessions[token] = user_info
        return {
            "token": token,
            "email": user_info["email"],
            "role": user_info["role"]
        }

    def create_session(self, email: str, role: str) -> str:
        """Creates and stores an active 7-day session token for an authenticated user."""
        token = secrets.token_hex(24)
        expires_at = time.time() + (86400 * 7)
        self._active_sessions[token] = {
            "email": email.strip().lower(),
            "role": role,
            "expires_at": expires_at
        }
        return token

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        if not self.is_auth_enabled:
            return {"email": "guest@avani.eco", "role": "Municipal Planner"}
            
        session = self._active_sessions.get(token)
        if not session:
            return None
            
        if time.time() > session["expires_at"]:
            del self._active_sessions[token]
            return None
            
        return session

    def logout_token(self, token: str):
        if token in self._active_sessions:
            del self._active_sessions[token]

auth_service = AuthService()
