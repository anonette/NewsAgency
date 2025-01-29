import streamlit as st
import os
import json
import tempfile

# Set up credentials before importing other modules
try:
    st.write("Debug: Setting up credentials")
    creds_json = st.secrets["GOOGLE_APPLICATION_CREDENTIALS_JSON"]
    st.write("Debug: Found credentials in secrets")
    
    # Create credentials dict
    creds_dict = json.loads(creds_json)
    st.write("Debug: Parsed credentials JSON")
    
    # Create credentials object
    from google.oauth2 import service_account
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    st.write("Debug: Created credentials object")
    
    # Set up storage client in session state
    from google.cloud import storage
    st.session_state.storage_client = storage.Client(
        project='israel-trends-viewer',
        credentials=credentials
    )
    st.write("Debug: Created storage client in session state")
except Exception as e:
    st.error(f"Failed to set up credentials: {str(e)}")
    st.stop()

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
    
    # Import and run israel4_viewer
    from israel4_viewer import main as israel4_viewer_main
    israel4_viewer_main(config_set=True)

if __name__ == "__main__":
    main()
