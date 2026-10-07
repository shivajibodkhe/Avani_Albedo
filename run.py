#!/usr/bin/env python3
"""
Avani Albedo - Startup Launcher
Run this script to launch the local development server:
    python run.py
"""
import os
import sys
import uvicorn
from app.config import settings

if __name__ == "__main__":
    port = int(os.getenv("PORT", settings.PORT))
    host = os.getenv("HOST", settings.HOST)
    print("\n" + "="*60)
    print("🌍 AVANI ALBEDO: Prescriptive Climate Resilience Engine")
    print(f"📡 Serving on http://{host}:{port} (or http://localhost:{port})")
    print("📑 Interactive API docs: http://localhost:8000/docs")
    print("="*60 + "\n")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
