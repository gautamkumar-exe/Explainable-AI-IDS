"""
SentraX IDS – Training Module
==============================
Trains a Random Forest Classifier on a synthetic network traffic dataset
that mimics real intrusion detection features.

Run:  python train.py
Output: model/sentrax_model.pkl, model/scaler.pkl, model/feature_names.pkl
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.datasets import make_classification

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
MODEL_DIR   = "model"
MODEL_PATH  = os.path.join(MODEL_DIR, "sentrax_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
FEAT_PATH   = os.path.join(MODEL_DIR, "feature_names.pkl")

RANDOM_STATE = 42

FEATURE_NAMES = [
    "duration",          # Connection duration (seconds)
    "src_bytes",         # Bytes sent from source
    "dst_bytes",         # Bytes sent to destination
    "num_failed_logins", # Failed login attempts
    "num_file_creations",# Files created during session
    "num_shells",        # Shell commands executed
    "is_guest_login",    # Guest login flag (0/1)
    "count",             # Connections to same host (last 2s)
    "srv_count",         # Connections to same service (last 2s)
    "dst_host_count",    # Connections to destination host
]

NUM_FEATURES = len(FEATURE_NAMES)


# ─────────────────────────────────────────────
# DATA LOADING (Real Dataset)
# ─────────────────────────────────────────────
def load_real_dataset(path: str) -> pd.DataFrame:
    """
    Loads the cleaned NSL-KDD dataset.
    Maps 'normal' to 0 and all other attacks to 1.
    """
    print(f"Loading dataset from {path}...")
    df = pd.read_csv(path)
    
    # Check if required features exist
    missing = [f for f in FEATURE_NAMES if f not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")
        
    # Map labels: 'normal' -> 0, anything else -> 1
    df["label"] = df["label"].apply(lambda x: 0 if str(x).strip().lower() == "normal" else 1)
    
    return df


# ─────────────────────────────────────────────
# TRAINING PIPELINE
# ─────────────────────────────────────────────
def train():
    print("━" * 50)
    print("  SentraX IDS – Model Training")
    print("━" * 50)

    # 1. Load dataset
    csv_path = "/Users/gautamkumar/Downloads/nsl_kdd_dataset.csv"
    print(f"\n[1/5] Loading real network traffic dataset...")
    df = load_real_dataset(csv_path)
    
    # We will use only our 10 chosen features to keep the UI clean
    X = df[FEATURE_NAMES].values
    y = df["label"].values
    print(f"      Dataset shape: {X.shape}  |  Attack rate: {y.mean():.1%}")

    # 2. Train / test split
    print("\n[2/5] Splitting dataset (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    # 3. Feature scaling
    print("\n[3/5] Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled  = scaler.transform(X_test)

    # 4. Train Random Forest
    print("\n[4/5] Training Random Forest Classifier...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_split=5,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    model.fit(X_train_scaled, y_train)

    # 5. Evaluate
    print("\n[5/5] Evaluating model on test set...")
    y_pred = model.predict(X_test_scaled)
    acc    = accuracy_score(y_test, y_pred)
    print(f"\n      Accuracy: {acc:.4f} ({acc*100:.2f}%)")
    print("\n" + classification_report(y_test, y_pred,
                                       target_names=["Normal", "Attack"]))

    # 6. Save artifacts
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model,         MODEL_PATH)
    joblib.dump(scaler,        SCALER_PATH)
    joblib.dump(FEATURE_NAMES, FEAT_PATH)

    print(f"✅  Model saved   → {MODEL_PATH}")
    print(f"✅  Scaler saved  → {SCALER_PATH}")
    print(f"✅  Features saved → {FEAT_PATH}")
    print("\n━" * 50)
    print("  Training complete. Run:  streamlit run app.py")
    print("━" * 50)


if __name__ == "__main__":
    train()
