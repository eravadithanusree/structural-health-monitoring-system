"""
Central configuration for the Structural Health Monitoring System.
Keeping all tunables in one place avoids magic numbers scattered
across the codebase and makes the thresholds easy to defend/justify.
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    # --- Flask ---
    SECRET_KEY = os.environ.get("SHMS_SECRET_KEY", "dev-key-change-in-production")
    DEBUG = os.environ.get("SHMS_DEBUG", "True") == "True"
    HOST = os.environ.get("SHMS_HOST", "127.0.0.1")
    PORT = int(os.environ.get("SHMS_PORT", 5000))

    # --- Database ---
    DATABASE_PATH = os.path.join(BASE_DIR, "database", "monitor.db")
    SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")

    # --- ML ---
    MODEL_PATH = os.path.join(BASE_DIR, "ml", "model.pkl")
    DATASET_PATH = os.path.join(BASE_DIR, "dataset", "structural_data.csv")

    # --- Sensor safety thresholds (used as a rule-based fallback if the
    #     ML model is unavailable, and to annotate the dashboard) ---
    THRESHOLDS = {
        "vibration": {"warning": 4.0, "critical": 6.0},   # mm/s
        "strain": {"warning": 180, "critical": 250},       # microstrain (µɛ)
        "temperature": {"warning": 45, "critical": 60},    # Celsius
    }

    # --- History / pagination ---
    HISTORY_PAGE_SIZE = 50

    # --- Simulator ---
    SIMULATOR_INTERVAL_SECONDS = 3
