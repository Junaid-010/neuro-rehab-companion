Neuro-Rehabilitation Support Engine University of London / Goldsmiths

BSc Computer Science Final Year Project (CM3070)

Student: Muhammad Junaid

Project Template: CM3020 Template 4.1 (Orchestrating AI models to achieve a goal)

📌 Project Overview The Neuro-Rehabilitation Support Engine is a stroke-specific, edge-native, AI-driven web app to support stroke patients in unsupervised home physical therapy.

Patients are sometimes unaware of their body compensating for the lack of immediate physiotherapist supervision when they switch from in-clinic rehabilitation to home rehab, and can become aware of these pathological mechanisms when the switch is made (e.g. trunk leaning, shoulder hiking etc.). This project fills in that clinical "Blind Spot" by providing a normal consumer laptop webcam with the ability to be a real-time biomechanical assessment and conversational support suite.

Important Medical Disclaimer: This is a technical computer science prototype software for demonstration of the real-time orchestration of AI models on edge hardware. It is not a registered medical device and has never been used in a clinical trial over a long enough period of time with stroke patients. It is used for research and engineering demo.

This is known as Triple-Model Edge Orchestration. This is referred to as a key feature, Triple-Model Edge Orchestration. The application meets the CM3020 Template 4.1 rubric, by leveraging three different AI models, all managed and deployed in the edge environment, while maintaining patient data privacy and not using cloud APIs:

Real-Time Kinematic Tracking (Real-Time Tracking): Provides an extension of real-time tracking, achieving 33 3D skeletal landmarks per video frame, with a ~30ms inference window on local CPU hardware, using MediaPipe BlazePose.

Postural Compensation Detection (Geometric FSM): A mathematical Finite State Machine (FSM) is implemented to continuously monitor and calculate the geometric joint angles by vector dot-products, and detect postural compensation. It activates software events on the spot, if the patient exceeds safe biomechanical limits (e.g. if the patient's trunk leans 25 degrees).

Acoustic NLP Engine (Vosk + DistilBERT): For psychological check-in, the patient's audio is transcribed locally using the Vosk offline speech recognition engine. The transcript is then fed to a quantized Hugging Face Small Language Model (distilbert-base-uncased-finetuned-sst-2-english), which performs a fast sentiment classification, and activates empathetic UI responses.

Cryptographic Role Based Access Control (RBAC): Has a dual portal structure, with the user going to a Patient Portal or Clinician Portal. It uses a 16-byte cryptographically random salt combined with PBKDF2-HMAC-SHA256 password hashing to ensure security.

Structured ML: Generates and stores a structured 10-point kinematic feature vector (incl. angular_velocity, joint_angle, compensation_metric) in local SQLite database and stores these for future model training.

🏗️ System Architecture This project follows the "100% Software-Driven Brain" paradigm, in which the concept of physical robotics is abandoned and everything is driven by software.

Capture frames using OpenCV, estimate the pose using MediaPipe, and evaluate the pose's kinematics using the FSM Engine.

Steps: Transcribe audio with Vosk (offline transcription) and analyze the sentiment with Hugging Face DistilBERT using the asynchronous voice generation (asynchronous TTS) feature of macOS.

Persistance Layer: Local sqlite database with encrypted user credentials, session telemetry, and psychological NLP logs.

Frontend: Streamlit is running an interactive, edge-native web interface, with no cloud requirements.

⚙️ Installation & Setup Prerequisites Supported operating systems: macOS (Intel Core i7 / Apple Silicon optimised) or Windows 10/11.

Aim to use Python version 3.12 (Strongly recommended).Do use Python 3.12 (Strongly recommended)

Software: Punch in Tune, a music production program.Frequency: You can record music anytime you want.

Step-by-Step Guide

Cloning the Repository
Bash git clone https://github.com/Junaid-010/neuro-rehab-companion.git cd neuro-rehab-companion Create the Virtual Environment.Set up Virtual Environment

2.This project is strongly recommended to be run in a virtual environment to avoid dependency conflicts.

Bash Create the virtual environment.Create a virtual environment: source venv/bin/activate (On Windows: venv\Scripts\activate)

Install all necessary Dependencies
Bash To install the required packages, run: pip install -r requirements.txt Create procedural UI Animations. The application's code is written in Python and is used for mathematically drawing the clinical demonstration animations, instead of loading videos from outside. To run the generator script once:

Bash python generate_video.py This will produce reach_demo.gif, slide_demo.gif and bilateral_demo.gif in the root directory.

Open a new application.
Change your working folder to the one containing the database. The SQLite Database will be automatically initialized when the Application runs.
Bash streamlit run app.py Note: The first time the Psychological Check-In is run, it will take a few moments to download the ~250MB DistilBERT model to the local cache. Any further runs will run immediately without being connected (unattached) to the internet.

📂 Project Structure Plaintext neuro-rehab-companion/ ├── app.py # Main entry point and RBAC routing │ └── ...creation functions... │ # SQLITEGateway functions for database creation.│ └── ...telemetry logging functions... │ # Telemetry logging functions. │ └── generate_video.py # Procedural animation generator (Pillow) │ ├── utils.py # Utility to handle input and output files ├── screening.py # Full-body safety scan logic (MediaPipe) ├── pages/ │──── 2_Accompanying_Check-in_NLP.py # UI for accompanying check-in NLP │ └── 2_Clinician_Portal.py # UI to review telemetric data and monitor patients ├── neuro_kinematics/
│ ├── game.py # Abstract game classes and other constants │ ├── hemiparetic_reach.py script to get FSM parameters for anterior MCA.│ ├── hemiparetic_reach.py script to get FSM parameters for anterior MCA. │ ├── tabletop_app.py # Hemorrhoids FSM parameters The following file is included:The following file is included: ├── utils/ │ └── ui_theme.py # SVG icons and CSS injections ├── tests/ # TDD validation suite (auth, FSM, NLP, screening) └── requirements.txt # Python dependencies

🔮 Future Work Future extensions to this project will include:

Generative SLM Integration: Switching current DistilBERT classification model to a fully generative local Small Language Model (e.g., Llama 3 8B) model for dynamic conversational support, once optimized for edge hardware acceleration.

Predictive Machine Learning Classifiers: Using the 10 point SQLite telemetry vector generated to train a Random Forest Classifier to predict patient fatigue prior to biomechanical failure.

Clinical Trials: ethical task-based testing of stroke survivors to demonstrate clinical effectiveness with actual clinical subjects, rather than relying on computational subjects.