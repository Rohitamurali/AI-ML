# utils/css.py
import streamlit as st

def load_sidebar_css():
    st.markdown("""
    <style>

    /* Sidebar Background */
    section[data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 2px solid #00FFFF !important;
    }

    /* Hide unwanted labels / boxes */
    section[data-testid="stSidebar"] label {
        display: none !important;
    }

    /* Remove default radio highlight */
    section[data-testid="stSidebar"] div[aria-checked="true"] {
        background-color: transparent !important;
    }

    /* Sidebar Buttons (White Text) */
    section[data-testid="stSidebar"] .stButton > button {
        background-color: transparent;
        color: white !important;
        border: none;
        text-align: left;
        width: 100%;
        padding: 8px 10px;
        font-size: 16px;
        font-weight: 500;
        border-left: 3px solid transparent;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        color: #00FFFF !important;
        background-color: #111111 !important;
        border-left: 3px solid #00FFFF;
    }

    /* Logout Button Special */
    section[data-testid="stSidebar"] .logout-btn > button {
        color: #00FFFF !important;
        border: 1.5px solid #00FFFF !important;
        border-radius: 8px !important;
        background-color: transparent !important;
        font-weight: 600 !important;
        margin-top: 20px;
    }

    section[data-testid="stSidebar"] .logout-btn > button:hover {
        background-color: #00FFFF !important;
        color: black !important;
    }
    /* Sidebar header text (like app name) */
section[data-testid="stSidebar"] * {
    color: white !important;
}
section[data-testid="stSidebarNav"] {
    color: white !important;
}

    </style>
    """, unsafe_allow_html=True)