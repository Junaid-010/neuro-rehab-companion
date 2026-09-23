import streamlit as st
import pandas as pd
import database as db
from utils.ui_theme import inject_clinician_theme, render_brand_header, get_icon_svg

st.set_page_config(page_title="Clinician Dashboard", page_icon="🩺", layout="wide", initial_sidebar_state="expanded")

if not st.session_state.get("authenticated") or st.session_state.get("user", {}).get("role") != "Clinician (Admin)":
    st.switch_page("app.py")

user = st.session_state.user
inject_clinician_theme()

st.sidebar.markdown(f"<h3 style='display: flex; align-items: center; color: #F8FAFC;'>{get_icon_svg('User', 20, '#F8FAFC')} Dr. {user['full_name']}</h3>", unsafe_allow_html=True)
st.sidebar.divider()

st.sidebar.header(f"🔍 Patient Directory")
patients = db.get_all_patients()
patient_options = {"Overview (Select a Patient)": None}
for p in patients:
    patient_options[f"ID: {p['user_id']} — {p['full_name']}"] = p['user_id']

selected_patient_label = st.sidebar.selectbox("Active Patient File:", list(patient_options.keys()))
selected_patient_id = patient_options[selected_patient_label]

st.sidebar.divider()

st.sidebar.markdown(f"<h3 style='display: flex; align-items: center; color: #F8FAFC;'>{get_icon_svg('Settings', 20, '#F8FAFC')} Architecture Overrides</h3>", unsafe_allow_html=True)
st.sidebar.selectbox("Pose Engine:", ["MediaPipe BlazePose (Active)", "YOLOv8-Pose (Simulated)", "OpenPose (Simulated)"])
st.sidebar.selectbox("STT Engine:", ["SpeechRecognition (Active)", "Whisper Tiny (Simulated)", "Google Cloud API (Simulated)"])

st.sidebar.divider()
if st.sidebar.button("System Log Out", type="primary"):
    st.session_state.clear()
    st.switch_page("app.py")

render_brand_header(compact=True)

if not selected_patient_id:
    st.title("Clinician Telemetry Dashboard")
    st.info("👈 Please select a patient from the sidebar directory to load their clinical file.")
    st.stop()

conn = db.get_connection()
patient_name = [p['full_name'] for p in patients if p['user_id'] == selected_patient_id][0]
st.title(f"Clinical File: {patient_name} (ID: {selected_patient_id})")

tab1, tab2, tab3 = st.tabs(["📉 Kinematic Telemetry", "🧠 Psychological Logs", "🏆 Progress Scale"])

with tab1:
    st.markdown("### Joint Kinematics & Posture Analysis")
    with st.expander("ℹ️ How to interpret this kinematic data (Click to expand)"):
        st.markdown("""
        * **Joint Angle (Degrees):** Measures the extension of the patient's elbow or arm. A higher degree indicates successful extension. Poor extension indicates muscle spasticity or weakness.
        * **Compensation Metric (Degrees / Units):** Measures 'Trunk Lean' or 'Shoulder Hike'. If this line spikes, the patient is using harmful compensatory movements rather than isolating the targeted muscle group.
        * **Clinical Value:** Use this to objectively track if the patient's Range of Motion (ROM) is improving over weeks of telerehabilitation.
        """)
        
    query = f"""
        SELECT t.timestamp, t.exercise_name, t.joint_angle, t.compensation_metric 
        FROM kinematic_telemetry t
        JOIN exercise_sessions s ON t.session_id = s.session_id
        WHERE t.user_id = {selected_patient_id}
        ORDER BY t.timestamp DESC LIMIT 500
    """
    kinematic_df = pd.read_sql_query(query, conn)
    
    if not kinematic_df.empty:
        st.line_chart(kinematic_df, y=["joint_angle", "compensation_metric"])
        st.dataframe(kinematic_df, use_container_width=True)
    else:
        st.info("No kinematic data recorded for this patient.")

with tab2:
    st.markdown("### Longitudinal Sentiment Tracking")
    with st.expander("ℹ️ How to interpret this psychological data"):
        st.markdown("""
        * **Sentiment Label:** Categorized dynamically based on the patient's post-session audio check-in.
        * **Clinical Value:** Sustained 'Needs Support' or 'Mixed' labels correlate strongly with patient burnout and reduced neuroplasticity. Use this data to adjust the difficulty of their prescribed physical exercises or recommend psychological counseling.
        """)
        
    query = f"SELECT timestamp, transcription, sentiment_label FROM psychology_logs WHERE user_id = {selected_patient_id} ORDER BY timestamp DESC"
    psych_df = pd.read_sql_query(query, conn)
    
    if not psych_df.empty:
        st.dataframe(psych_df, use_container_width=True)
    else:
        st.info("No psychological logs recorded.")

with tab3:
    st.markdown("### Recovery Scale & Session History")
    query = f"SELECT * FROM user_progress WHERE user_id = {selected_patient_id}"
    prog_df = pd.read_sql_query(query, conn)
    
    if not prog_df.empty:
        total = prog_df.iloc[0]['total_sessions']
        level = min((total // 3) + 1, 10)
        
        st.markdown(f"**Current Recovery Milestone: Level {level}**")
        st.progress(level / 10.0)
        st.write("---")
        
        cols = st.columns(4)
        cols[0].metric("Total Sessions", total)
        cols[1].metric("Total Repetitions", prog_df.iloc[0]['total_repetitions'])
        cols[2].metric("Current Streak", f"{prog_df.iloc[0]['current_streak']} Days")
        cols[3].metric("Best Streak", f"{prog_df.iloc[0]['best_streak']} Days")
    else:
        st.info("No progress recorded yet.")

conn.close()