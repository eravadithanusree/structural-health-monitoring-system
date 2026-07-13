"""
Loads the trained model bundle once and exposes a single predict() function.
Falls back to a transparent rule-based classifier (using config thresholds)
if the model file is missing, so the API never hard-fails.
"""

import os
import joblib
from config import Config

_bundle = None


def _load():
    global _bundle
    if _bundle is None and os.path.exists(Config.MODEL_PATH):
        _bundle = joblib.load(Config.MODEL_PATH)
    return _bundle


def _rule_based_fallback(vibration, strain, temperature):
    t = Config.THRESHOLDS
    if (
        vibration >= t["vibration"]["critical"]
        or strain >= t["strain"]["critical"]
        or temperature >= t["temperature"]["critical"]
    ):
        return "Damaged", 0.75
    if (
        vibration >= t["vibration"]["warning"]
        or strain >= t["strain"]["warning"]
        or temperature >= t["temperature"]["warning"]
    ):
        return "Damaged", 0.55
    return "Healthy", 0.8


def predict(vibration, strain, temperature):
    """Returns (status: str, confidence: float 0-1)."""
    bundle = _load()
    if bundle is None:
        return _rule_based_fallback(vibration, strain, temperature)

    model = bundle["model"]
    features = [[vibration, strain, temperature]]
    proba = model.predict_proba(features)[0]
    classes = list(model.classes_)
    pred_idx = proba.argmax()
    status = classes[pred_idx]
    confidence = float(proba[pred_idx])
    return status, round(confidence, 4)
