import os
import time
import logging
from typing import Dict, Any, List, Optional
from app.config import settings

logger = logging.getLogger("avani_albedo.admin")

class AdminService:
    def __init__(self):
        # 1. Registered Users Store
        self._users: Dict[str, Dict[str, Any]] = {
            "srbodkhe@gmail.com": {
                "email": "srbodkhe@gmail.com",
                "role": "Super Admin",
                "status": "Active", # Active, Suspended, Pending
                "created_at": time.time() - 86400 * 5,
                "last_active": time.time(),
                "provider": "firebase/google",
                "login_count": 24
            },
            "judge@hackathon.com": {
                "email": "judge@hackathon.com",
                "role": "Judge / Evaluator",
                "status": "Active",
                "created_at": time.time() - 86400 * 2,
                "last_active": time.time() - 3600,
                "provider": "judge_demo",
                "login_count": 8
            }
        }

        # 2. Alerts / Registration Requests Store
        self._alerts: List[Dict[str, Any]] = [
            {
                "id": "alert_sample_1",
                "user_email": "evaluator.ai.cup@gmail.com",
                "type": "New Registration Request",
                "timestamp": time.time() - 1800,
                "status": "pending", # pending, approved, rejected
                "message": "Unregistered user attempted login via Firebase Google Sign-In. Awaiting admin approval."
            }
        ]

        # 3. API Quotas & Usage Tracking
        self._quotas: Dict[str, Any] = {
            "gemini_calls": {
                "used": 14,
                "limit": 1500,
                "label": "Gemini 2.5 Flash Calls / Day (Free Tier: 1,500 RPD)"
            },
            "optimizer_runs": {
                "used": 42,
                "limit": 5000,
                "label": "OR-Tools SCIP Optimizer Solves / Day"
            },
            "earth_engine_queries": {
                "used": 8,
                "limit": 2000,
                "label": "Earth Engine / BigQuery Spatial Queries / Day"
            },
            "active_sessions": {
                "used": 2,
                "limit": 100,
                "label": "Concurrent Active Sessions"
            }
        }

    # ================= USER MANAGEMENT =================
    def list_users(self) -> List[Dict[str, Any]]:
        return list(self._users.values())

    def get_user(self, email: str) -> Optional[Dict[str, Any]]:
        return self._users.get(email.strip().lower())

    def update_user_status(self, email: str, status: str) -> bool:
        clean = email.strip().lower()
        if clean in self._users:
            self._users[clean]["status"] = status
            logger.info(f"Updated user {clean} status to {status}")
            return True
        return False

    def add_or_update_user(self, email: str, role: str = "Researcher", status: str = "Active", provider: str = "firebase") -> Dict[str, Any]:
        clean = email.strip().lower()
        if clean in self._users:
            self._users[clean]["last_active"] = time.time()
            self._users[clean]["login_count"] = self._users[clean].get("login_count", 0) + 1
            return self._users[clean]

        user = {
            "email": clean,
            "role": role,
            "status": status,
            "created_at": time.time(),
            "last_active": time.time(),
            "provider": provider,
            "login_count": 1
        }
        self._users[clean] = user
        return user

    def delete_user(self, email: str) -> bool:
        clean = email.strip().lower()
        if clean == "srbodkhe@gmail.com":
            return False # Protect super admin
        if clean in self._users:
            del self._users[clean]
            return True
        return False

    # ================= ALERTS & REGISTRATION NOTIFICATIONS =================
    def list_alerts(self) -> List[Dict[str, Any]]:
        return sorted(self._alerts, key=lambda x: x["timestamp"], reverse=True)

    def trigger_registration_alert(self, email: str, details: str = "") -> Dict[str, Any]:
        """Triggered when an unregistered user attempts to log in."""
        clean = email.strip().lower()
        alert_id = f"alert_{int(time.time() * 1000)}"
        alert = {
            "id": alert_id,
            "user_email": clean,
            "type": "New Registration Request",
            "timestamp": time.time(),
            "status": "pending",
            "message": details or f"User {clean} attempted login via Firebase but is not yet registered. Needs Admin approval."
        }
        self._alerts.append(alert)
        # Add to users as Pending
        self.add_or_update_user(clean, role="Pending Evaluator", status="Pending", provider="firebase")
        logger.warning(f"SECURITY ALERT: Unregistered login attempt by {clean}. Alert logged for admin.")
        return alert

    def resolve_alert(self, alert_id: str, action: str) -> bool:
        for alert in self._alerts:
            if alert["id"] == alert_id:
                if action == "approve":
                    alert["status"] = "approved"
                    self.update_user_status(alert["user_email"], "Active")
                elif action == "reject":
                    alert["status"] = "rejected"
                    self.update_user_status(alert["user_email"], "Suspended")
                return True
        return False

    # ================= QUOTAS & USAGE TRACKING =================
    def increment_metric(self, metric_key: str):
        if metric_key in self._quotas:
            self._quotas[metric_key]["used"] += 1

    def get_quotas(self) -> Dict[str, Any]:
        return self._quotas

    def update_quota_limit(self, metric_key: str, new_limit: int):
        if metric_key in self._quotas:
            self._quotas[metric_key]["limit"] = new_limit

    # ================= CONFIGURATION & API KEYS =================
    def get_runtime_config(self) -> Dict[str, Any]:
        return {
            "gemini_api_key_configured": bool(settings.GEMINI_API_KEY),
            "gemini_api_key_masked": (settings.GEMINI_API_KEY[:6] + "..." + settings.GEMINI_API_KEY[-4:]) if settings.GEMINI_API_KEY else "Not Configured",
            "gcp_project_id": settings.GCP_PROJECT_ID,
            "gcp_region": settings.GCP_REGION,
            "use_earth_engine_live": settings.USE_EARTH_ENGINE_LIVE,
            "app_mode": settings.APP_MODE,
            "allowed_emails": os.getenv("ALLOWED_EMAILS", "srbodkhe@gmail.com,judge@hackathon.com"),
            "admin_email": "srbodkhe@gmail.com"
        }

    def update_runtime_config(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        if "gemini_api_key" in updates and updates["gemini_api_key"]:
            settings.GEMINI_API_KEY = updates["gemini_api_key"].strip()
            os.environ["GEMINI_API_KEY"] = settings.GEMINI_API_KEY

        if "gcp_project_id" in updates and updates["gcp_project_id"]:
            settings.GCP_PROJECT_ID = updates["gcp_project_id"].strip()
            os.environ["GCP_PROJECT_ID"] = settings.GCP_PROJECT_ID

        if "use_earth_engine_live" in updates:
            settings.USE_EARTH_ENGINE_LIVE = bool(updates["use_earth_engine_live"])
            os.environ["USE_EARTH_ENGINE_LIVE"] = str(settings.USE_EARTH_ENGINE_LIVE).lower()

        if "allowed_emails" in updates and updates["allowed_emails"]:
            os.environ["ALLOWED_EMAILS"] = updates["allowed_emails"].strip()

        logger.info("Runtime configuration updated by Admin")
        return self.get_runtime_config()

admin_service = AdminService()
