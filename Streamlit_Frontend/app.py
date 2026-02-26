import streamlit as st
import streamlit.components.v1 as components

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Smart Recipe Recommender",
    page_icon="🍽️",
    layout="wide"
)

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>

/* Full black background */
.stApp {
    background-color: #000000 !important;
}

/* Remove white padding */
.block-container {
    padding-top: 2rem !important;
    background-color: #000000 !important;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #000000 !important;
    border-right: 2px solid #00FFFF !important;
}

/* Make all sidebar text white */
section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Sidebar button style */
section[data-testid="stSidebar"] button {
    background-color: transparent !important;
    border: none !important;
    text-align: left !important;
    width: 100% !important;
    padding: 8px 12px !important;
    border-left: 4px solid transparent !important;
    font-weight: 500 !important;
}

/* Hover effect */
section[data-testid="stSidebar"] button:hover {
    color: #00FFFF !important;
    border-left: 4px solid #00FFFF !important;
    background-color: #111111 !important;
}

/* Image glow */
.glow-img img {
    border-radius: 20px;
    box-shadow: 0px 0px 40px rgba(0,255,255,0.6);
}

/* Small image style */
.small-img img {
    width: 90%;
    border-radius: 20px;
    box-shadow: 0px 0px 35px rgba(0,255,255,0.6);
}

</style>
""", unsafe_allow_html=True)
st.sidebar.markdown("<br><br>", unsafe_allow_html=True)

# Logout button simply links to Flask /logout
st.sidebar.markdown("""
    <a href="http://127.0.0.1:5000/logout" target="_self">
        <button style="
            width: 100%; padding: 10px; background-color:#000; color:#00FFFF; 
            border:none; font-weight:bold; cursor:pointer;">
            Logout
        </button>
    </a>
""", unsafe_allow_html=True)
# ---------- MAIN LANDING SECTION ----------
col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown("""
        <h1 style='color:#00FFFF; font-size:40px;'>
            AI Diet Recommendation System
        </h1>
        <p style='color:#cccccc; font-size:18px; line-height:1.6;'>
            Smart Personalized Nutrition Planning using AI/ML.
            Get customized meal plans based on your health goals,
            calorie needs and lifestyle.
        </p>
    """, unsafe_allow_html=True)

with col2:
    st.markdown('<div class="small-img">', unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1546069901-ba9599a7e63c")
    st.markdown('</div>', unsafe_allow_html=True)