"""
Neuro-Rehabilitation Support Engine
------------------------------------
Shared UI theme, styling utilities, and Lucide SVG icons.
"""

import streamlit as st

# ================================================================
# APPLICATION BRANDING
# ================================================================

APP_NAME = "Neuro-Rehabilitation Support Engine"
APP_SUBTITLE = "AI-Orchestrated Kinematic Guidance for Stroke Telerehabilitation"

# ================================================================
# COLOR DICTIONARIES
# ================================================================

PATIENT_COLORS = {
    "background": "#FAF7F2",       # Warm Sand
    "primary_text": "#3E2723",     # Slate Brown
    "secondary_text": "#5D4037",
    "forest_green": "#2D6A4F",
    "terracotta": "#E07A5F",
    "white": "#FFFFFF",
    "soft_border": "#E8DED3",
}

CLINICIAN_COLORS = {
    "background": "#F4F7FA",
    "surface": "#FFFFFF",
    "surface_alt": "#EEF2F6",
    "sidebar": "#1F2937",
    "sidebar_secondary": "#273548",
    "primary_text": "#172033",
    "secondary_text": "#5B677A",
    "clinical_blue": "#2563EB",
    "clinical_blue_dark": "#1D4ED8",
    "forest_green": "#2D6A4F",
    "terracotta": "#E07A5F",
    "warning": "#D97706",
    "danger": "#DC2626",
    "border": "#D9E1EA",
    "engineering_panel": "#111827",
    "engineering_text": "#E5E7EB",
}

# ================================================================
# CSS INJECTIONS
# ================================================================

def inject_patient_theme():
    """Apply the Clinical Zen Patient Portal theme (No Sidebar)."""
    st.markdown(
        f"""
        <style>
        [data-testid="collapsedControl"] {{ display: none !important; }}
        [data-testid="stSidebar"] {{ display: none !important; }}
        .stApp, .main {{ background-color: {PATIENT_COLORS["background"]}; }}
        h1, h2, h3 {{ color: {PATIENT_COLORS["primary_text"]}; }}
        p, label {{ color: {PATIENT_COLORS["secondary_text"]}; }}
        div[data-testid="stMetricValue"] {{ color: {PATIENT_COLORS["terracotta"]}; }}
        div[data-testid="stMetricLabel"] {{ color: {PATIENT_COLORS["secondary_text"]}; }}
        .stButton > button {{ border-radius: 12px; border: 1px solid {PATIENT_COLORS["soft_border"]}; padding: 0.65rem 1rem; font-weight: 600; transition: all 0.2s ease; }}
        .stButton > button:hover {{ transform: translateY(-1px); }}
        div[data-testid="stProgress"] > div > div {{ background-color: {PATIENT_COLORS["forest_green"]}; }}
        input, textarea {{ border-radius: 10px !important; }}
        hr {{ border-color: {PATIENT_COLORS["soft_border"]}; }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def inject_clinician_theme():
    """Apply the Hybrid Technical Clinical Console theme (With Sidebar)."""
    st.markdown(
        f"""
        <style>
        .stApp, .main {{ background-color: {CLINICIAN_COLORS["background"]}; }}
        [data-testid="stSidebar"] {{ background-color: {CLINICIAN_COLORS["sidebar"]}; border-right: 1px solid #334155; }}
        [data-testid="stSidebar"] * {{ color: #F8FAFC; }}
        [data-testid="stSidebarNav"] {{ display: none; }}
        h1, h2, h3 {{ color: {CLINICIAN_COLORS["primary_text"]}; }}
        p {{ color: {CLINICIAN_COLORS["secondary_text"]}; }}
        div[data-testid="stMetric"] {{ background-color: {CLINICIAN_COLORS["surface"]}; border: 1px solid {CLINICIAN_COLORS["border"]}; border-radius: 12px; padding: 1rem; }}
        div[data-testid="stMetricValue"] {{ color: {CLINICIAN_COLORS["clinical_blue"]}; }}
        .stButton > button {{ border-radius: 8px; font-weight: 600; transition: all 0.15s ease; }}
        .stButton > button:hover {{ transform: translateY(-1px); }}
        [data-testid="stDataFrame"] {{ border: 1px solid {CLINICIAN_COLORS["border"]}; border-radius: 10px; }}
        button[data-baseweb="tab"] {{ font-weight: 600; }}
        hr {{ border-color: {CLINICIAN_COLORS["border"]}; }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# ================================================================
# LUCIDE ICON SYSTEM (Stage 12 & 14)
# ================================================================

LUCIDE_ICONS = {
    "Brain": '<path d="M9.5 2A2.5 2.5 0 0 0 7 4.5v15a2.5 2.5 0 0 0 4.9 1.22 2.5 2.5 0 0 0 4.2 0A2.5 2.5 0 0 0 21 19.5v-15a2.5 2.5 0 0 0-5-2.5 2.5 2.5 0 0 0-4 2 2.5 2.5 0 0 0-2.5-2Z"/>',
    "Activity": '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    "User": '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    "CheckCircle": '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
    "Mic": '<path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/>'
}

def get_icon_svg(name, size=24, color="currentColor"):
    """Returns the raw HTML/SVG string for a given Lucide icon."""
    path = LUCIDE_ICONS.get(name, "")
    if not path:
        return ""
    return f'''
    <svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" 
         fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" 
         class="lucide lucide-{name.lower()}" style="vertical-align: middle; margin-right: 8px;">
        {path}
    </svg>
    '''

def render_brand_header(compact=False):
    """
    Renders the application identity using the new Lucide SVG icon system.
    """
    brain_icon = get_icon_svg("Brain", size=28 if compact else 40, color="#2563EB" if compact else "#3E2723")
    
    if compact:
        # Collapsed into a single line to prevent Streamlit from treating it as a code block!
        st.markdown(f"<div style='padding: 0.4rem 0; margin-bottom: 1rem; display: flex; align-items: center;'>{brain_icon}<span style='font-size: 1.05rem; font-weight: 700; letter-spacing: 0.02em;'>{APP_NAME}</span></div>", unsafe_allow_html=True)
    else:
        # Collapsed into a single line for the main login screen too
        st.markdown(f"<div style='text-align: center; padding: 1.5rem 0 1rem 0;'><div style='display: flex; justify-content: center; align-items: center; margin-bottom: 10px;'>{brain_icon}</div><div style='font-size: 2.2rem; font-weight: 800; letter-spacing: -0.02em; color: #3E2723;'>{APP_NAME}</div><div style='margin-top: 0.5rem; font-size: 1rem; opacity: 0.75; color: #5D4037;'>{APP_SUBTITLE}</div></div>", unsafe_allow_html=True)