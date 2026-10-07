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
        return os.getenv("JUDGE_PASSWORD", "avani2026")

    @property
    def allowed_emails(self) -> List[str]:
        raw = os.getenv("ALLOWED_EMAILS", "srbodkhe@gmail.com,judge@hackathon.com,evaluator@ai-builder.cup")
        return [e.strip().lower() for e in raw.split(",") if e.strip()]

    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticates a user against the judge password and allowed emails whitelist.
        """
        clean_email = email.strip().lower()
        clean_pw = password.strip()
        
        # Check password
        if clean_pw != self.judge_password:
            return None
            
        # Check whitelist (if configured)
        whitelist = self.allowed_emails
        if whitelist and clean_email not in whitelist and not clean_email.endswith("@hackathon.com"):
            # Allow whitelisted emails or any @hackathon.com domain
            return None
            
        token = secrets.token_hex(24)
        expires_at = time.time() + (86400 * 7) # 7-day session
        
        user_info = {
            "email": clean_email,
            "role": "Judge / Evaluator" if "judge" in clean_email or "eval" in clean_email else "Municipal Planner",
            "expires_at": expires_at
        }
        
        self._active_sessions[token] = user_info
        return {
            "token": token,
            "email": user_info["email"],
            "role": user_info["role"]
        }

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
