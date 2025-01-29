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
    raw_creds = st.secrets.GOOGLE_APPLICATION_CREDENTIALS_JSON
    st.write("Debug: Raw credentials type:", type(raw_creds))
    st.write("Debug: Raw credentials starts with:", raw_creds[:50] if raw_creds else "None")
    
    # Clean up the JSON string
    if isinstance(raw_creds, str):
        # Remove any leading/trailing whitespace
        cleaned_creds = raw_creds.strip()
        # Remove any triple quotes if present
        cleaned_creds = cleaned_creds.replace("'''", "")
        st.write("Debug: Cleaned credentials start:", cleaned_creds[:50])
        
        try:
            creds_dict = json.loads(cleaned_creds)
            st.write("Debug: Successfully parsed credentials JSON")
        except json.JSONDecodeError as e:
            st.write("Debug: JSON parse error:", str(e))
            st.write("Debug: Error position:", e.pos)
            st.write("Debug: Error line:", e.lineno)
            st.write("Debug: Error column:", e.colno)
            raise ValueError(
                "Invalid JSON format in GOOGLE_APPLICATION_CREDENTIALS_JSON.\n"
                "Please ensure the credentials are properly formatted in Streamlit secrets.\n"
                f"Error: {str(e)}"
            )
    else:
        st.write("Debug: Unexpected credentials type")
        raise ValueError(
            "GOOGLE_APPLICATION_CREDENTIALS_JSON must be a string.\n"
            f"Got type: {type(raw_creds)}"
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
