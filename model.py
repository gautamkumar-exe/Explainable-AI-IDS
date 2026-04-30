import os
import numpy as np
import pandas as pd
import joblib
import shap
import random

# Paths
MODEL_DIR   = "model"
MODEL_PATH  = os.path.join(MODEL_DIR, "sentrax_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
FEAT_PATH   = os.path.join(MODEL_DIR, "feature_names.pkl")

# Expanded Attack Categories based on NSL-KDD
ATTACK_CATEGORIES = {
    "normal": "Normal",
    "dos": "DoS",
    "probe": "Probe",
    "r2l": "R2L",
    "u2r": "U2R"
}

# Mapping specific labels to categories
LABEL_TO_CAT = {
    'back': 'dos', 'land': 'dos', 'neptune': 'dos', 'pod': 'dos', 'smurf': 'dos', 'teardrop': 'dos', 'mailbomb': 'dos', 'apache2': 'dos', 'processtable': 'dos', 'udpstorm': 'dos',
    'satan': 'probe', 'ipsweep': 'probe', 'nmap': 'probe', 'portsweep': 'probe', 'mscan': 'probe', 'saint': 'probe',
    'guess_passwd': 'r2l', 'ftp_write': 'r2l', 'imap': 'r2l', 'phf': 'r2l', 'multihop': 'r2l', 'warezmaster': 'r2l', 'warezclient': 'r2l', 'spy': 'r2l', 'xlock': 'r2l', 'xsnoop': 'r2l', 'snmpgetattack': 'r2l', 'snmpguess': 'r2l', 'httptunnel': 'r2l', 'sendmail': 'r2l', 'named': 'r2l',
    'buffer_overflow': 'u2r', 'loadmodule': 'u2r', 'perl': 'u2r', 'rootkit': 'u2r', 'sqlattack': 'u2r', 'xterm': 'u2r', 'ps': 'u2r',
    'normal': 'normal'
}

class SentraXModel:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = None
        self._explainer = None
        self.metrics = {
            "accuracy": 0.8002,
            "precision": 0.80,
            "recall": 1.00,
            "f1": 0.89
        }

    def load(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model not found at '{MODEL_PATH}'.")
        self.model = joblib.load(MODEL_PATH)
        self.scaler = joblib.load(SCALER_PATH)
        self.feature_names = joblib.load(FEAT_PATH)
        return self

    @property
    def explainer(self):
        if self._explainer is None:
            self._explainer = shap.TreeExplainer(self.model)
        return self._explainer

def preprocess(raw_input: dict, model: SentraXModel) -> np.ndarray:
    values = np.array([float(raw_input[f]) for f in model.feature_names]).reshape(1, -1)
    return model.scaler.transform(values)

def predict(scaled_input: np.ndarray, model: SentraXModel) -> dict:
    probas = model.model.predict_proba(scaled_input)[0]
    class_id = int(np.argmax(probas))
    label = "Attack" if class_id == 1 else "Normal"
    
    # Heuristic for attack category based on features if it's an attack
    category = "Normal"
    if label == "Attack":
        # Simplified logic for demo: use feature patterns to guess category
        # In a real multiclass model, this would be the actual prediction
        if scaled_input[0, 7] > 0.8: # high count
            category = "DoS"
        elif scaled_input[0, 3] > 0.5: # high failed logins
            category = "R2L"
        else:
            category = random.choice(["Probe", "U2R", "DoS"])

    return {
        "label": label,
        "category": category,
        "confidence": float(probas[class_id]),
        "probas": probas.tolist(),
    }

def explain(scaled_input: np.ndarray, model: SentraXModel) -> dict:
    shap_values_all = model.explainer.shap_values(scaled_input)
    if isinstance(shap_values_all, list):
        sv = shap_values_all[1][0]
    else:
        sv = shap_values_all[0, :, 1] if shap_values_all.ndim == 3 else shap_values_all[0]

    shap_df = pd.DataFrame({
        "Feature": model.feature_names,
        "SHAP Value": sv,
        "Abs SHAP": np.abs(sv),
    }).sort_values("Abs SHAP", ascending=False).reset_index(drop=True)

    return {
        "shap_data": shap_df.to_dict(orient="records"),
        "metrics": model.metrics
    }

def run_pipeline(raw_input: dict, model: SentraXModel) -> dict:
    scaled = preprocess(raw_input, model)
    prediction = predict(scaled, model)
    explanation = explain(scaled, model)
    return {**prediction, **explanation}
