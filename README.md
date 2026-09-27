 Neuro-Rehabilitation Support Engine

University of London / Goldsmiths BSc Computer Science Final Year Project (CM3070) 
Student: Muhammad Junaid

CM3020 Project Template 4.1 (Orchestrating AI models to achieve a goal)


Project Overview

Neuro-Rehabilitation Support Engine is an edge-native, AI orchestrated web application to monitor and support stroke survivors in unsupervised home physical therapy.

Patients can start to use pathological compensation patterns after leaving in-clinic care and starting home rehab without direct supervision from a physiotherapist, e.g. leaning forwards with the trunk, or hiking the shoulders. This work tackles that monitoring "blind spot" by creating a standard consumer webcam-based system that transforms into a real-time biomechanical assessment and conversational assistance system.

This software is a technical prototype of computer science that is intended to show the capability of real-time orchestration of AI models on the edge hardware. Not a registered medical device, nor has it been clinically tested over a long period of time with stroke patients. For research, architectural evaluation and engineering demonstration purposes only.


Triple-Model Edge Native Orchestration: 
Key Features:

This application meets the rubric requirements of the CM3020 Template 4.1, by orchestrating the 3 different AI models completely on the edge hardware. This approach guarantees patients' data privacy while also avoiding the use of cloud APIs:

Real-Time Kinematic Tracking (Vision): Leverages MediaPipe BlazePose to get 33 3D skeletal landmarks from typical RGB video frames, running at ~30ms inference window on local CPU devices.
Postural Compensation Detection (Geometric FSM): Enables a mathematical Finite State Machine (FSM) to get geometric joint angles continuously by vector dot-products. It activates "on the fly" software events when patients breach the biomechanical limits (e.g. a 25° lean on the trunk).
Acoustic NLP Engine (Vosk + DistilBERT): Allows to process the speech of the patient and translate it into text on the device, using the Vosk offline speech recognition engine (combined with DistilBERT). The transcript is sent to a quantized Hugging Face Small Language Model called “distilbert-base-uncased-finetuned-sst-2-english”, which is capable of making fast sentiment classifications and responding to the user's sentiment in the UI.
Cryptographic Role Based Access Control (RBAC): Includes a dual portal design with an isolation between the Patient and Clinician environments. Passive, using PBKDF2-HMAC-SHA256 password hashing and a 16-byte cryptographically random salt that is not included with the password.
Structured ML Telemetry: Stores and stores a structured 10 point kinematic feature vector that includes features such as `angular_velocity`, `joint_angle`, and `compensation_metric` which are used for future model training in a locally stored SQLite database.



System Architecture :

This project follows the "100% Software-Driven Brain" paradigm, which is about software, and not physical robotics.

The first step is to capture the frames using OpenCV, then detect the pose using MediaPipe, and finally evaluate the frame using the FSM Engine.
This is considered the Audio/NLP Domain where Vosk (offline transcription) is paired with Hugging Face DistilBERT (sentiment analysis) and macOS native TTS (asynchronous voice generation).
3. Persistence Layer: Encrypted user credentials, session telemetry and psychological NLP logs stored locally in SQLite.
4. Frontend: Streamlit executing an interactive, edge-native web interface without cloud relying on.


Installation and Setup:

Prerequisites:

Running System: macOS (Intel Core i7/ Apple Silicon version) or Windows 10/11.
Programming Language(s): Python: Version 3.12 (Strongly Recommended).
Built-in Web Camera and Microphone.

Step-by-Step Guide:

1. Cloning the Repository

```bash
git clone https://github.com/Junaid-010/neuro-rehab-companion.git
cd neuro-rehab-companion

```

Now you need to create the Virtual Environment and then you need to configure the Virtual Environment.
This project is strongly recommended to be run in a virtual environment to avoid possible dependency issues.

```bash
python3 -m venv venv
source venv/bin/activate

```

(even on Windows, do: `venv\Scripts\activate`).

3. Install Dependencies

```bash
pip install -r requirements.txt

```

Creating UI Animations using Procedural approach.
The app generates clinical demonstration animations on program automatically rather than loading them from external videos, but if they are, they are stored in the application. To run the script for the generator one time:

```bash
python generate_video.py

```

This will create the files `reach_demo.gif`, `slide_demo.gif` and `bilateral_demo.gif` in your root directory.

6. Insert the first two records into the Database.7. Open the Database and run the program.
If it's the first time running the app, the SQLite database file will be initialized automatically.

```bash
streamlit run app.py

```

The first time the Psychological Check-In is accessed, the model (~250MB) DistilBERT will be downloaded to the local cache for a short time. All other executions will be executed instantly without Internet connection.



Project Structure:

```text
neuro-rehab-companion/
├── app.py                       Main entry point and RBAC routing
├── database.py                  SQLite schema, PBKDF2 cryptography, and telemetry logging
├── generate_video.py            Procedural animation generator (Pillow)
├── psychology.py                Hugging Face DistilBERT NLP inference engine
├── screening.py                 Full-body safety scan logic (MediaPipe)
├── pages/
│   ├── 1_Patient_Portal.py      UI for active kinematic tracking and Vosk NLP check-in
│   └── 2_Clinician_Portal.py    UI for telemetric data review and patient monitoring
├── neuro_kinematics/           
│   ├── base_movement.py         Abstract FSM engine and vector math calculations
│   ├── hemiparetic_reach.py     Anterior MCA FSM parameters
│   ├── tabletop_slide.py        Hemorrhagic FSM parameters
│   └── bilateral_posture.py     Posterior FSM parameters
├── utils/
│   └── ui_theme.py              SVG icons and CSS injections
├── tests/                       TDD validation suite (auth, FSM, NLP, screening)
└── requirements.txt             Python dependencies

```



Future Work:

Based on the above assessment, future development plans of the project involve:

2. Generative SLM Integration: Switching from the existing DistilBERT classification model to a purely Generative local Small Language Model (e.g., Llama 3 8B) for dynamic conversational support, once edge hardware is optimized and accelerated accordingly.
Predictive Machine Learning Classifiers: Using the vector of 10-point SQLite telemetry, train a Random Forest classifier that is able to predict patient fatigue before a biomechanical failure.
3. Clinical Trials: Performing task-based evaluations with representative stroke survivors that are ethically approved clinical tests to demonstrate the actual clinical effectiveness of 3D models and baseline accuracy that extend well beyond computational simulation.