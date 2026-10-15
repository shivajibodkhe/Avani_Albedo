import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=True)

class Settings:
    APP_NAME: str = "Avani Albedo"
    APP_SLOGAN: str = "Optimizing Albedo, Cooling the Earth."
    APP_VERSION: str = "1.0.0"
    
    # Mode
    APP_MODE: str = os.getenv("APP_MODE", "auto")
    
    # Gemini / AI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # GCP
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "avani-albedo")
    GCP_REGION: str = os.getenv("GCP_REGION", "asia-south1")
    USE_EARTH_ENGINE_LIVE: bool = os.getenv("USE_EARTH_ENGINE_LIVE", "false").lower() in ("true", "1", "yes")
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

settings = Settings()
