import streamlit as st

# Configure page settings
st.set_page_config(
    page_title="Middle East Pulse News Agency",
    page_icon="🌍",
    layout="wide"
)

# Add custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: #f5f5f5;
    }
    .main-title {
        text-align: center;
        color: #2c3e50;
        font-size: 2.5em;
        margin-bottom: 0.5em;
        font-weight: 600;
        line-height: 1.3;
    }
    .description {
        text-align: center;
        color: #576574;
        font-size: 1.1em;
        margin: 2em auto;
        max-width: 800px;
        line-height: 1.6;
    }
    .message {
        text-align: center;
        color: #e74c3c;
        font-size: 1.3em;
        margin: 1em auto;
        max-width: 800px;
        line-height: 1.6;
        padding: 1em;
        background-color: #fdf2f0;
        border-radius: 10px;
    }
    .link {
        text-align: center;
        font-size: 1.2em;
        margin: 1em auto;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-title">Middle East Pulse News Agency:<br>Nostalgia for Real Data in a Synthetic World</h1>', unsafe_allow_html=True)

# Move notice
st.markdown('<div class="message">⚠️ This project has moved to a new location.</div>', unsafe_allow_html=True)
st.markdown('<p class="link">Please visit: <a href="http://95.216.199.241:8501/">http://95.216.199.241:8501/</a></p>', unsafe_allow_html=True)

# Description
st.markdown('<p class="description">Capturing the last traces of authentic human searches through Google Trends, this project contrasts official narratives with genuine public sentiment—a glimpse into the "real" in an era of synthetic media.</p>', unsafe_allow_html=True)
