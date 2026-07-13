"""
Trains a RandomForestClassifier on the structural sensor dataset and
persists it (+ metadata) to model.pkl via joblib.

Run standalone: python ml/train_model.py
"""

import os
import sys
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

FEATURES = ["vibration", "strain", "temperature"]
TARGET = "status"


def train():
    df = pd.read_csv(Config.DATASET_PATH)

    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=3,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)

    print(f"Test accuracy: {acc:.4f}")
    print(classification_report(y_test, preds))
    print("Confusion matrix:")
    print(confusion_matrix(y_test, preds))
    print("Feature importances:")
    for feat, imp in sorted(zip(FEATURES, model.feature_importances_), key=lambda x: -x[1]):
        print(f"  {feat}: {imp:.3f}")

    bundle = {
        "model": model,
        "features": FEATURES,
        "classes": list(model.classes_),
        "test_accuracy": acc,
    }
    joblib.dump(bundle, Config.MODEL_PATH)
    print(f"Saved model bundle to {Config.MODEL_PATH}")


if __name__ == "__main__":
    train()
