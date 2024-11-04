import streamlit as st

st.set_page_config(
    page_title="Middle East Pulse News Agency",
    page_icon="🌍",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-message {
        text-align: center;
        padding: 2rem;
        background-color: #f8f9fa;
        border-radius: 10px;
        margin: 2rem auto;
        max-width: 800px;
    }
    .redirect-link {
        color: #0066cc;
        text-decoration: underline;
        font-weight: bold;
    }
    .info-text {
        color: #666;
        font-size: 1.1em;
        line-height: 1.6;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Main content
st.markdown("""
<div class="main-message">
    <h1>🌍 Middle East Pulse News Agency</h1>
    <p class="info-text">
        This service has moved to a new address. Please visit:
        <br><br>
        <a class="redirect-link" href="http://95.216.199.241:8501/" target="_blank">http://95.216.199.241:8501/</a>
        <br><br>
        We are currently in the process of deploying an improved version on Streamlit.
    </p>
</div>
""", unsafe_allow_html=True)
