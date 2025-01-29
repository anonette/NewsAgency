import streamlit as st
import os
import json
import tempfile
from israel4_viewer import main as israel4_viewer_main

def setup_cloud_credentials():
    """Set up Google Cloud credentials from environment variable"""
    try:
        # Check if credentials are provided as environment variable
        creds_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
        if creds_json:
            # Create temporary file for credentials
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                # Write credentials to temp file
                json.dump(json.loads(creds_json), f)
                # Set environment variable to temp file path
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f.name
                return True
        else:
            # For local development, use key.json
            key_path = os.path.join(os.path.dirname(__file__), 'key.json')
            if os.path.exists(key_path):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_path
                return True
            return False
    except Exception as e:
        st.error(f"Error setting up credentials: {str(e)}")
        return False

def main():
    # Set page config first
    st.set_page_config(
        page_title="Israel Trends Analysis",
        page_icon="🇮🇱",
        layout="wide"
    )

    # Hide streamlit default menu
    st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    div[data-testid="stSidebarNav"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

    # Set up cloud credentials
    if not setup_cloud_credentials():
        st.error("Failed to set up Google Cloud credentials")
        return

    # Run israel4_viewer with config_set=True since we're setting it here
    israel4_viewer_main(config_set=True)

if __name__ == "__main__":
    main()
