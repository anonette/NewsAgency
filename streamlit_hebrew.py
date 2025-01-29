import streamlit as st
import os
import json
import tempfile

# Set up credentials before importing other modules
try:
    st.write("Debug: Setting up credentials")
    
    # Check for required secrets
    if not hasattr(st.secrets, 'GOOGLE_APPLICATION_CREDENTIALS_JSON'):
        raise ValueError(
            "GOOGLE_APPLICATION_CREDENTIALS_JSON not found in Streamlit secrets.\n"
            "Please add your service account credentials to Streamlit secrets."
        )
    
    # Get credentials from secrets
    st.write("Debug: Loading credentials from secrets")
    try:
        creds_dict = json.loads(st.secrets.GOOGLE_APPLICATION_CREDENTIALS_JSON)
        st.write("Debug: Successfully parsed credentials JSON")
    except json.JSONDecodeError as e:
        st.write("Debug: Error parsing credentials JSON")
        raise ValueError(
            "Invalid JSON format in GOOGLE_APPLICATION_CREDENTIALS_JSON.\n"
            "Please ensure the credentials are properly formatted in Streamlit secrets."
        )
    
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
