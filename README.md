# 🚀 SentraX: Explainable AI Intrusion Detection System (IDS)

---

## 📌 Overview

SentraX is a **production-grade, modern Security Operations Center (SOC) dashboard** and Intrusion Detection System powered by **Machine Learning** and **Explainable AI (XAI)**.

It provides real-time intrusion detection with **transparent, interpretable insights**, helping analysts understand *why* a threat was detected.

![SentraX Dashboard](frontend/public/sentrax_logo.png)

---

## ⚙️ Features

* 🔍 **Real-Time Network Telemetry**
  Live simulation of packet streams using the NSL-KDD dataset

* 🧠 **Explainable AI (SHAP)**
  Feature-level explanation showing why traffic is classified as malicious

* ⚡ **Dynamic Risk Engine**
  Real-time threat scoring and system vulnerability assessment

* 📊 **Advanced Event Logging**
  Thread-safe logging of:

  * IP Address
  * Port
  * Protocol
  * Attack Type (DoS, Probe, U2R, R2L)

* 🧪 **Manual Inference Engine**
  Allows analysts to input custom values and test predictions

* 🚀 **One-Command Startup**
  Launch full system using:

  ```bash
  ./start.sh
  ```

---

## 🧠 Architecture

```text
Frontend (React + Vite)
        ↓
FastAPI Backend (API Layer)
        ↓
ML Model (Random Forest)
        ↓
Prediction + SHAP Explainability
```

---

## 🛠️ Tech Stack

### Backend:

* Python
* FastAPI
* Scikit-learn
* SHAP
* Pandas

### Frontend:

* React
* Vite
* Recharts
* Lucide Icons

### Model:

* Random Forest Classifier
* Trained on NSL-KDD dataset

---

## 📂 Project Structure

```text
SentraX_IDS/
│
├── frontend/                # React + Vite UI
│   ├── src/
│   ├── public/
│   └── ...
│
├── model/                   # Backend + ML logic
│   ├── api.py              # API routes
│   ├── model.py            # Prediction + SHAP
│   ├── train.py            # Model training
│   ├── app.py              # Server entry point
│   └── requirements.txt
│
├── start.sh                 # One-command startup
└── README.md
```

---

## 🚀 Getting Started

### 1️⃣ Prerequisites

* Node.js (v16+)
* Python (3.9+)

---

### 2️⃣ Run the Project (Recommended)

```bash
chmod +x start.sh
./start.sh
```

✔ This will:

* Install dependencies
* Train/load model
* Start backend server
* Launch frontend

---

### 🌐 Access the Application

* **Frontend Dashboard:** http://localhost:5173
* **Backend API:** http://localhost:8000

---

## 🔄 Workflow

```text
User Input → Frontend → API → Model → Prediction → SHAP Explanation → UI Display
```

---

## 🧩 Core Components

* **api.py**
  Handles API requests, real-time simulation, and logging

* **model.py**
  Loads trained model, performs predictions, and generates SHAP explanations

* **train.py**
  Trains the ML model using NSL-KDD dataset

* **frontend/**
  Interactive SOC dashboard with real-time visuals

---

## 👨‍💻 Author

**gautamkumar-exe**

---

## ⭐ Note

SentraX is designed as a **deployable prototype IDS system** combining machine learning with explainable AI for transparent cybersecurity analysis.
