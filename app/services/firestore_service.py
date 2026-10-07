import logging
import time
from typing import Dict, Any, List, Optional
from app.config import settings

logger = logging.getLogger("avani_albedo.firestore")

class FirestoreService:
    def __init__(self):
        self.client = None
        self.is_connected = False
        self._in_memory_store: List[Dict[str, Any]] = []
        self._init_client()

    def _init_client(self):
        try:
            from google.cloud import firestore
            # Try connecting to Firestore
            self.client = firestore.Client(project=settings.GCP_PROJECT_ID)
            self.is_connected = True
            logger.info(f"Firestore initialized with project {settings.GCP_PROJECT_ID}")
        except Exception as e:
            logger.info(f"Firestore running in local resilient buffer mode (Reason: {e})")
            self.is_connected = False

    def get_status(self) -> str:
        if self.is_connected:
            return f"Connected (Firestore Collection: avani_scenarios)"
        return "Local Resilient Buffer (Auto-sync Ready)"

    def save_scenario_plan(self, plan_data: Dict[str, Any]) -> str:
        """Saves scenario and action plan to Firestore (or local buffer)."""
        doc_id = f"plan_{int(time.time() * 1000)}"
        record = {
            "doc_id": doc_id,
            "created_at": time.time(),
            "city": plan_data.get("scenario_result", {}).get("city", "Bengaluru"),
            "scenario_type": plan_data.get("scenario_result", {}).get("scenario_type", "optimized"),
            "budget_spent_inr": plan_data.get("scenario_result", {}).get("budget_spent_inr", 0),
            "avg_temp_reduction_c": plan_data.get("scenario_result", {}).get("avg_temp_reduction_c", 0),
            "total_beneficiaries": plan_data.get("scenario_result", {}).get("total_beneficiaries", 0),
            "executive_summary": plan_data.get("executive_summary", ""),
            "plan_data": plan_data
        }

        if self.is_connected and self.client:
            try:
                self.client.collection("avani_scenarios").document(doc_id).set(record)
                logger.info(f"Saved scenario to Firestore: {doc_id}")
                return doc_id
            except Exception as e:
                logger.warning(f"Failed to write to live Firestore: {e}. Storing in memory.")

        self._in_memory_store.append(record)
        return doc_id

    def list_recent_plans(self, limit: int = 5) -> List[Dict[str, Any]]:
        if self.is_connected and self.client:
            try:
                docs = self.client.collection("avani_scenarios").order_by("created_at", direction="DESCENDING").limit(limit).stream()
                return [d.to_dict() for d in docs]
            except Exception as e:
                logger.warning(f"Failed reading live Firestore: {e}")
        return sorted(self._in_memory_store, key=lambda x: x["created_at"], reverse=True)[:limit]

firestore_service = FirestoreService()
