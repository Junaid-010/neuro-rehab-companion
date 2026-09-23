# Neuro-Rehabilitation Support Engine

**University of London / Goldsmiths**

**BSc Computer Science Final Year Project (CM3070)**

**Student:** Muhammad Junaid

**Project Template:** CM3020 Template 4.1 (Orchestrating AI models to achieve a goal)

---

## 📌 Project Overview

The Neuro-Rehabilitation Support Engine is an edge-native, AI-orchestrated web application designed to support stroke survivors during unsupervised home physical therapy.

When transitioning from in-clinic care to home rehabilitation, patients often develop pathological compensatory mechanisms (such as trunk leaning or shoulder hiking) because they lack the immediate supervision of a physiotherapist. This project addresses that clinical "Blind Spot" by transforming a standard consumer laptop webcam into a real-time biomechanical assessment and conversational support suite.

**Important Medical Disclaimer:** This software is a *technical computer science prototype* designed to demonstrate the real-time orchestration of AI models on edge hardware. It is not a certified medical device and has not undergone longitudinal clinical trials with stroke patients. It is intended for research and engineering demonstration purposes only.

---

## 🚀 Key Features

* **Real-Time Kinematic Tracking:** Utilizes MediaPipe BlazePose to extract 33 3D skeletal landmarks from standard RGB video frames, operating at a ~30ms inference window on local CPU hardware.


* **Postural Compensation Detection:** Implements a mathematical Finite State Machine (FSM) to continuously monitor and calculate geometric joint angles, triggering immediate software events if a patient exceeds safe biomechanical thresholds (e.g., 25-degree trunk lean).


* **Asynchronous Auditory Scaffolding:** Employs a custom WebRTC-based Vosk Speech-to-Text (STT) engine and local OS subprocesses for Text-to-Speech (TTS), delivering non-blocking voice feedback without freezing the visual tracking loop.


* **Psychological Companion Module:** Simulates a conversational "digital buddy" via an NLP module that mirrors the user's emotional energy, validates their effort, and encourages long-term exercise adherence. *(Note: Currently implemented via deterministic heuristics to preserve critical CPU resources for the vision pipeline).*


* **Dual-Portal RBAC Architecture:** Features Role-Based Access Control, routing users to either a streamlined Patient Portal for active exercises or a Clinician Portal for reviewing SQLite-persisted kinematic telemetry and sentiment logs.



---

## 🏗️ System Architecture

This project adheres to the "100% Software-Driven Brain" paradigm, pivoting away from physical robotics to focus entirely on software orchestration.

1. **Vision Domain:** OpenCV (frame capture) ➔ MediaPipe (pose estimation) ➔ FSM Heuristics (kinematic evaluation).
2. **Audio/NLP Domain:** Vosk (offline transcription) ➔ Sentiment Analysis Heuristics ➔ pyttsx3/macOS native TTS (asynchronous voice generation).
3. **Persistence Layer:** Local SQLite database handling encrypted user credentials, session telemetry, and psychological NLP logs.
4. **Frontend:** Streamlit running an interactive, edge-native web interface accessible without cloud dependencies.



---

## ⚙️ Installation & Setup

### Prerequisites

* **Operating System:** macOS (Optimized for Intel Core i7 / Apple Silicon)
* **Python:** Version 3.9 to 3.12
* **Hardware:** Integrated Webcam and Microphone

### Step-by-Step Guide

**1. Clone the Repository**

```bash
git clone https://github.com/Junaid-010/neuro-rehab-companion.git
cd neuro-rehab-companion

```

**2. Set Up the Virtual Environment**
It is highly recommended to run this project inside a virtual environment to prevent dependency conflicts.

```bash
python3 -m venv venv
source venv/bin/activate

```

**3. Install Dependencies**

```bash
pip install -r requirements.txt

```

*(Ensure your `requirements.txt` includes `streamlit`, `opencv-python`, `mediapipe`, `SpeechRecognition`, `audio-recorder-streamlit`, and any other required libraries).*

**4. Initialize the Database**
The SQLite database will automatically initialize upon running the application for the first time, generating the `neuro_rehab.db` file locally.

**5. Launch the Application**

```bash
streamlit run app.py

```

This will open the application in your default web browser (typically at `http://localhost:8501`).

---

## 📂 Project Structure

```text
neuro-rehab-companion/
├── app.py                      # Main entry point and Auth routing
├── database.py                 # SQLite schema, queries, and telemetry logging
├── psychology.py               # NLP heuristic module for sentiment analysis
├── screening.py                # Full-body safety scan logic
├── pages/
│   ├── 1_Patient_Portal.py     # UI for active kinematic tracking and NLP check-in
│   └── 2_Clinician_Portal.py   # UI for telemetric data review and patient monitoring
├── neuro_kinematics/           # FSM modules for specific exercises
│   ├── hemiparetic_reach.py
│   ├── tabletop_slide.py
│   └── bilateral_posture.py
├── utils/
│   └── ui_theme.py             # SVG icons and CSS injections
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation

```

---

## 🔮 Future Work

Based on the current evaluation, future extensions of this project include:

1. **Generative SLM Integration:** Replacing the heuristic NLP mock with a quantized local Small Language Model (e.g., Hugging Face `transformers`) to provide truly generative, context-aware psychological accompaniment, pending optimized hardware acceleration.


2. **Machine Learning Classifiers:** Transitioning from deterministic geometric FSM thresholds to a Random Forest classifier trained on personalized patient baselines.


3. **Clinical Trials:** Conducting ethically approved, task-based evaluations with representative stroke survivors to establish true clinical efficacy beyond computational benchmarking.
