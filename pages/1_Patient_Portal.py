import streamlit as st
import cv2
import mediapipe as mp
import time
import io
import datetime
import subprocess
import speech_recognition as sr
from audio_recorder_streamlit import audio_recorder
import database as db

from screening import FullBodyReadinessScan
from utils.ui_theme import inject_patient_theme, get_icon_svg
from psychology import PsychologicalCompanion

from neuro_kinematics.hemiparetic_reach import HemipareticReachMovement
from neuro_kinematics.tabletop_slide import TabletopSlideMovement
from neuro_kinematics.bilateral_posture import BilateralPostureMovement

st.set_page_config(page_title="My Recovery", layout="wide", initial_sidebar_state="collapsed")
if not st.session_state.get("authenticated") or st.session_state.get("user", {}).get("role") != "Patient":
    st.switch_page("app.py")

user = st.session_state.user
inject_patient_theme()

if "macro_state" not in st.session_state: st.session_state.macro_state = "SAFETY_SCAN"
if "db_session_id" not in st.session_state: st.session_state.db_session_id = None
if "final_reps" not in st.session_state: st.session_state.final_reps = 0
if "session_start_time" not in st.session_state: st.session_state.session_start_time = None

target_reps = 5

def trigger_voice(text):
    subprocess.Popen(["say", text])

# ================================================================
# DYNAMIC EXERCISE ROUTING
# ================================================================
stroke_type = user.get("stroke_type", "Not Sure")

if "Hemorrhagic" in stroke_type:
    ExerciseModule = TabletopSlideMovement
    ex_name = "Tabletop Towel Slide"
    video_file = "slide_demo.gif"
elif "Posterior" in stroke_type:
    ExerciseModule = BilateralPostureMovement
    ex_name = "Bilateral Balance Alignment"
    video_file = "bilateral_demo.gif"
else:
    ExerciseModule = HemipareticReachMovement
    ex_name = "Hemiparetic Arm Reach"
    video_file = "reach_demo.gif"

# ================================================================
# UI HEADER & PROGRESS SCALE
# ================================================================
col_left, col_right = st.columns([5, 1])
with col_left:
    st.markdown(f"<h1 style='display: flex; align-items: center;'>{get_icon_svg('User', 32, '#3E2723')} Hello, {user['full_name'].split()[0]}.</h1>", unsafe_allow_html=True)
with col_right:
    if st.button("Log Out", use_container_width=True):
        st.session_state.clear()
        st.switch_page("app.py")

conn = db.get_connection()
prog_df = conn.execute("SELECT total_sessions FROM user_progress WHERE user_id = ?", (user['user_id'],)).fetchone()
conn.close()
total_sessions = prog_df['total_sessions'] if prog_df else 0

current_level = min((total_sessions // 3) + 1, 10)
progress_percentage = (current_level / 10.0)

st.markdown(f"**Recovery Scale: Level {current_level}**")
st.progress(progress_percentage)
st.write("---")

# ====================================================================
# STATE 1: SAFETY_SCAN
# ====================================================================
if st.session_state.macro_state == "SAFETY_SCAN":
    st.markdown(f"<h3 style='display: flex; align-items: center;'>{get_icon_svg('Activity', 28)} Full Body Posture Check</h3>", unsafe_allow_html=True)
    st.write("Please step back so your camera can see your shoulders and hips.")
    
    if st.button("Start Scanner", type="primary"):
        screener = FullBodyReadinessScan()
        cap = cv2.VideoCapture(0)
        start_time = time.time()
        scan_ph = st.empty()
        safe = False
        
        while cap.isOpened() and (time.time() - start_time < 5):
            ret, frame = cap.read()
            if not ret: break
            rgb = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
            safe, msg = screener.evaluate_full_body_readiness(rgb)
            cv2.putText(rgb, "Scanning posture...", (50, 50), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 2)
            scan_ph.image(rgb)
            
        cap.release()
        scan_ph.empty()
        
        if safe:
            st.session_state.macro_state = "SESSION_IDLE"
            st.rerun()
        else:
            st.error(msg)
            if st.button("Try Again"): st.rerun()

# ====================================================================
# STATE 2: SESSION_IDLE 
# ====================================================================
elif st.session_state.macro_state == "SESSION_IDLE":
    st.markdown("### Today's Rehabilitation Plan")
    st.success(f"Posture check passed! You are cleared for {target_reps} repetitions of the **{ex_name}**.")
    
    if st.button("Begin Session Timer", type="primary"):
        st.session_state.db_session_id = db.create_exercise_session(user['user_id'])
        st.session_state.session_start_time = time.time()
        st.session_state.macro_state = "ACTIVE"
        st.rerun()

# ====================================================================
# STATE 3: ACTIVE (Side-by-Side Video & Camera)
# ====================================================================
elif st.session_state.macro_state == "ACTIVE":
    
    elapsed_time = int(time.time() - st.session_state.session_start_time)
    formatted_time = str(datetime.timedelta(seconds=elapsed_time))
    
    # Top bar for Header and Timer
    col_top1, col_top2 = st.columns([3, 1])
    with col_top1:
        st.markdown(f"<h3 style='display: flex; align-items: center;'>{get_icon_svg('Activity', 24)} Active Exercise: {ex_name}</h3>", unsafe_allow_html=True)
    with col_top2:
        st.metric("⏱️ Elapsed Time", formatted_time)
        if st.button("🛑 End Early", key="user_stop"):
            st.session_state.macro_state = "CHECK_IN"
            st.rerun()

    st.write("---")
    
    # Side-by-Side Layout for Demo and Camera
    col_demo, col_cam = st.columns(2)
    
    with col_demo:
        st.markdown("#### Demonstration")
        try:
            st.image(video_file, use_container_width=True)
            st.caption("Move in sync with the model.")
        except Exception:
            st.error(f"Missing {video_file}. Please run generate_video.py first.")
            
    with col_cam:
        st.markdown("#### Your Camera")
        video_pane = st.empty()

    st.write("---")
    st.markdown("#### Repetition Goals")
    checklist_pane = st.empty()

    module = ExerciseModule()
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    cap = cv2.VideoCapture(0)
    
    trigger_voice("Session started. Follow the demonstration.")
    is_calib, last_voice = False, time.time()
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        rgb = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
        res = pose.process(rgb)
        
        reps, feedback, is_breach = 0, "", False
        if res.pose_landmarks:
            if not is_calib:
                is_calib = True
                feedback = "Perfect. Begin reaching."
            else:
                reps, feedback, is_breach, ml_features = module.evaluate_stroke_kinematics(res.pose_landmarks.landmark, mp_pose)
                db.log_kinematic_telemetry(st.session_state.db_session_id, user['user_id'], ex_name, ml_features)
            
            mp.solutions.drawing_utils.draw_landmarks(rgb, res.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            
            if feedback and (time.time() - last_voice > 4.0):
                trigger_voice(feedback)
                last_voice = time.time()
                
        checklist_html = ""
        for i in range(1, target_reps + 1):
            if i <= reps:
                checklist_html += f"<div style='color:#2D6A4F; font-weight:bold; margin-bottom:10px;'>✅ Repetition {i} Completed</div>"
            elif i == reps + 1:
                checklist_html += f"<div style='color:#E07A5F; font-weight:bold; margin-bottom:10px;'>🔄 Repetition {i} In Progress...</div>"
            else:
                checklist_html += f"<div style='color:#5D4037; margin-bottom:10px;'>⏳ Repetition {i} Waiting</div>"
                
        checklist_pane.markdown(checklist_html, unsafe_allow_html=True)
        video_pane.image(rgb)
        
        if reps >= target_reps:
            st.session_state.final_reps = reps
            st.session_state.macro_state = "CHECK_IN"
            break 
            
        time.sleep(0.01)
        
    cap.release()
    if st.session_state.macro_state == "CHECK_IN":
        st.rerun()

# ====================================================================
# STATE 4: CHECK_IN (Psychological NLP)
# ====================================================================
elif st.session_state.macro_state == "CHECK_IN":
    st.markdown(f"<h3 style='display: flex; align-items: center;'>{get_icon_svg('Mic', 24)} Psychological Check-In</h3>", unsafe_allow_html=True)
    st.write("Physical therapy takes emotional energy. Tell me how you are feeling, or type it below.")
    
    col_audio, col_text = st.columns([1, 2])
    with col_audio:
        audio_bytes = audio_recorder(text="Tap to Speak", recording_color="#E07A5F", neutral_color="#2D6A4F", icon_size="2x")
    with col_text:
        manual_text = st.text_input("Or type your thoughts here:")
    
    patient_text = None
    
    if manual_text:
        patient_text = manual_text
    elif audio_bytes:
        with st.spinner("Processing audio..."):
            try:
                r = sr.Recognizer()
                with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
                    audio_data = r.record(source)
                    patient_text = r.recognize_google(audio_data)
            except sr.UnknownValueError:
                st.error("Audio unclear. Please try speaking closer to the microphone, or type your response.")
            except sr.RequestError as e:
                st.error(f"Could not reach Speech Recognition service. Please type your response. (API Error: {e})")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                
    # if patient_text:
    #     psych = PsychologicalCompanion()
    #     sentiment, reply = psych.analyze_sentiment_and_respond(patient_text)
    #     db.log_psychology_sentiment(st.session_state.db_session_id, user['user_id'], patient_text, sentiment, reply)
    #     trigger_voice(reply)
        
    #     st.write(f"**You shared:** *\"{patient_text}\"*")
    #     st.success(f"**Your Companion:** {reply}")
        
    #     if st.button("Complete Session", type="primary"):
    #         db.conclude_exercise_session(st.session_state.db_session_id, st.session_state.final_reps)
    #         st.session_state.macro_state = "COMPLETED"
    #         st.rerun()
    
    if patient_text:
        psych = PsychologicalCompanion()
        
        # SLM processes the text to get the Mood (sentiment) and the empathetic reply
        sentiment, reply = psych.analyze_sentiment_and_respond(patient_text)
        
        # Log to SQLite
        db.log_psychology_sentiment(st.session_state.db_session_id, user['user_id'], patient_text, sentiment, reply)
        
        st.write(f"**You shared:** *\"{patient_text}\"*")
        
        # ==========================================================
        # DYNAMIC UI RENDERING BASED ON DETECTED MOOD
        # ==========================================================
        st.markdown("### Your Digital Companion Says:")
        
        # Clean the sentiment string just in case it has extra spaces or capitalization
        detected_mood = str(sentiment).strip().lower()
        
        if detected_mood in ["positive", "happy", "optimistic", "good"]:
            st.success(f"**Mood Detected:** {sentiment.capitalize()} 🌟")
            st.info(f"💬 {reply}")
        elif detected_mood in ["negative", "frustrated", "sad", "tired", "angry"]:
            st.warning(f"**Mood Detected:** {sentiment.capitalize()} 💙 (Tough days are a normal part of neuroplasticity)")
            st.info(f"💬 {reply}")
        else:
            # Fallback for Neutral, Mixed, or Unknown sentiments
            st.write(f"**Mood Detected:** {sentiment.capitalize()} ⚖️")
            st.info(f"💬 {reply}")
            
        # Trigger the voice response asynchronously so the UI doesn't freeze
        trigger_voice(reply)
        # ==========================================================
        
        if st.button("Complete Session", type="primary"):
            db.conclude_exercise_session(st.session_state.db_session_id, st.session_state.final_reps)
            st.session_state.macro_state = "COMPLETED"
            st.rerun()

# ====================================================================
# STATE 5: COMPLETED 
# ====================================================================
elif st.session_state.macro_state == "COMPLETED":
    st.balloons()
    
    total_time = int(time.time() - st.session_state.session_start_time)
    final_time = str(datetime.timedelta(seconds=total_time))
    
    st.markdown(f"<h3 style='display: flex; align-items: center;'>{get_icon_svg('CheckCircle', 32, '#2D6A4F')} Session Complete!</h3>", unsafe_allow_html=True)
    st.info(f"You completed {st.session_state.final_reps} reps in {final_time}. Your progress has been saved.")
    
    if st.button("Return Home"):
        st.session_state.macro_state = "SAFETY_SCAN"
        st.rerun()