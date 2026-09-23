import streamlit as st
import time
import database as db
from utils.ui_theme import get_icon_svg

st.set_page_config(page_title="Neuro-Rehabilitation Companion", page_icon="🧠", layout="centered", initial_sidebar_state="collapsed")
st.markdown("""<style>[data-testid="collapsedControl"], [data-testid="stSidebar"] {display: none !important;} .stApp {background-color: #FAF7F2;} h1, h2, h3 {color: #3E2723;}</style>""", unsafe_allow_html=True)

db.init_db()

if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "user" not in st.session_state: st.session_state.user = None
if "onboarding_step" not in st.session_state: st.session_state.onboarding_step = "landing"

if st.session_state.authenticated and st.session_state.user:
    role = st.session_state.user.get("role")
    if role == "Patient": st.switch_page("pages/1_Patient_Portal.py")
    elif role == "Clinician (Admin)": st.switch_page("pages/2_Clinician_Portal.py")
    else: st.stop()

if st.session_state.onboarding_step == "landing":
    st.markdown(f"<div style='text-align: center; margin-bottom: 20px;'>{get_icon_svg('Brain', 60, '#3E2723')}</div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>Welcome to Your Recovery Journey</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #5D4037;'>Your personal assistant for physical therapy at home.</h4><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🌟 I am a New Patient", type="primary", use_container_width=True):
            st.session_state.onboarding_step = "register"
            st.rerun()
        if st.button("Log In (Returning Patient)", use_container_width=True):
            st.session_state.onboarding_step = "login"
            st.rerun()
            
    st.write("---")
    with st.expander(f"{get_icon_svg('Lock', 18)} Doctor & Therapist Login"):
        c_user = st.text_input("Staff ID")
        c_pass = st.text_input("Password", type="password")
        if st.button("Secure Login"):
            user = db.authenticate_user(c_user, c_pass)
            if user and user['role'] == "Clinician (Admin)":
                st.session_state.authenticated = True
                st.session_state.user = db.sanitize_user_record(user)
                st.rerun()
            else:
                st.error("Access Denied. Please check your credentials.")

elif st.session_state.onboarding_step == "login":
    st.markdown("## Patient Sign In")
    with st.container(border=True):
        l_user = st.text_input("Username")
        l_pass = st.text_input("Password", type="password")
        if st.button("Sign In", type="primary"):
            user = db.authenticate_user(l_user, l_pass)
            if user and user['role'] == "Patient":
                st.session_state.temp_user = user
                st.session_state.onboarding_step = "triage_scan" 
                st.rerun()
            else:
                st.error("Incorrect username or password.")
        if st.button("Back"):
            st.session_state.onboarding_step = "landing"
            st.rerun()

elif st.session_state.onboarding_step == "register":
    st.markdown("## Create Your Profile")
    with st.container(border=True):
        new_user = st.text_input("Choose a Username")
        new_pass = st.text_input("Choose a Password", type="password")
        name = st.text_input("Your Full Name")
        age = st.number_input("Your Age", min_value=18, max_value=100, value=60)
        stroke_type = st.selectbox("What type of stroke did you have? (If known)", ["Ischemic (Anterior MCA)", "Ischemic (Posterior)", "Hemorrhagic", "Not Sure"])
        affected_side = st.radio("Which side of your body needs therapy?", ["Left", "Right"])
        
        if st.button("Create Profile & Log In", type="primary"):
            success, msg = db.register_user(new_user, new_pass, name, age, stroke_type, affected_side)
            if success:
                st.success("Profile created! Redirecting...")
                time.sleep(1.5)
                st.session_state.onboarding_step = "login"
                st.rerun()
            else:
                st.error(msg)
        if st.button("Back"):
            st.session_state.onboarding_step = "landing"
            st.rerun()

elif st.session_state.onboarding_step == "triage_scan":
    st.session_state.authenticated = True
    st.session_state.user = db.sanitize_user_record(st.session_state.temp_user)
    st.rerun()