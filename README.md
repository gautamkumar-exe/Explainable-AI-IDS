# SentraX: Explainable AI Intrusion Detection System (IDS)

SentraX is a production-grade, hyper-modern Security Operations Center (SOC) dashboard and Intrusion Detection System powered by Machine Learning and Explainable AI (XAI).

![SentraX Dashboard](frontend/public/sentrax_logo.png)

## Features
- **Real-Time Network Telemetry:** Live simulation of packet feeds mapped from the NSL-KDD dataset.
- **Explainable AI (SHAP):** Clear visibility into *why* the ML model flagged traffic as malicious, offering feature-by-feature impact breakdown.
- **Dynamic Risk Engine:** Real-time calculation of threat levels and system vulnerability.
- **Advanced Event Logging:** Persistent thread-safe logging of all network inferences, including IP, Port, Protocol, and exact Attack Categories (DoS, Probe, U2R, R2L).
- **Manual Inference Engine:** A testing bay for security analysts to input custom payload metrics and test the ML model directly.

## Tech Stack
- **Backend:** FastAPI, Python, Scikit-Learn, SHAP, Pandas.
- **Frontend:** React, Vite, Recharts, Lucide-React.
- **Model:** Random Forest Classifier (Trained on NSL-KDD).

## Getting Started

### 1. Prerequisites
- Node.js (v16+)
- Python (3.9+)

### 2. Installation
Install the required Python packages for the ML backend:
```bash
pip install -r requirements.txt
```

Install the Node modules for the Vite frontend:
```bash
cd frontend
npm install
```

### 3. Running the Application
A `start.sh` script is provided to easily boot both the backend and frontend simultaneously.

```bash
# Make sure the script is executable
chmod +x start.sh

# Run the project
./start.sh
```
- **Backend API:** `http://localhost:8000`
- **Frontend Dashboard:** `http://localhost:5173`

## Architecture Overview
- `api.py`: FastAPI backend that handles ML routing, the real-time simulation feed, and the live log store.
- `model.py`: Model loader, prediction pipeline, and SHAP explainer integration.
- `frontend/`: The React/Vite application featuring a dark-themed, premium UI designed for cybersecurity professionals.
