import streamlit as st
import os
import json
import tempfile

# Set up credentials before importing other modules
try:
    st.write("Debug: Setting up credentials")
    
    # Debug: Print all available secrets
    st.write("Debug: All available secrets:", dir(st.secrets))
    st.write("Debug: Secrets dict:", st.secrets.to_dict())
    
    # Check for required secrets in general section
    if not hasattr(st.secrets, 'general') or not hasattr(st.secrets.general, 'GOOGLE_APPLICATION_CREDENTIALS_JSON'):
        st.write("Debug: Missing required secret in general section")
        st.write("Debug: Available sections:", dir(st.secrets))
        if hasattr(st.secrets, 'general'):
            st.write("Debug: Available general secrets:", dir(st.secrets.general))
        raise ValueError(
            "GOOGLE_APPLICATION_CREDENTIALS_JSON not found in Streamlit secrets general section.\n"
            "Please add your service account credentials to Streamlit secrets under [general]."
        )
    
    # Get credentials from secrets
    st.write("Debug: Loading credentials from secrets")
    raw_creds = st.secrets.general.GOOGLE_APPLICATION_CREDENTIALS_JSON
    st.write("Debug: Raw credentials type:", type(raw_creds))
    st.write("Debug: Raw credentials starts with:", raw_creds[:50] if raw_creds else "None")
    
    # Parse and clean credentials
    try:
        # Parse JSON and handle any formatting issues
        creds_dict = json.loads(raw_creds)
        st.write("Debug: Successfully parsed credentials JSON")
        
        # Fix private key formatting if needed
        private_key = creds_dict.get('private_key', '')
        if private_key:
            # Ensure proper line endings
            private_key = private_key.replace('\\n', '\n')
            if not private_key.startswith('-----BEGIN PRIVATE KEY-----\n'):
                private_key = '-----BEGIN PRIVATE KEY-----\n' + private_key
            if not private_key.endswith('\n-----END PRIVATE KEY-----\n'):
                private_key = private_key + '\n-----END PRIVATE KEY-----\n'
            creds_dict['private_key'] = private_key
            st.write("Debug: Fixed private key formatting")
        
        # Create credentials object
        from google.oauth2 import service_account
        credentials = service_account.Credentials.from_service_account_info(creds_dict)
        st.write("Debug: Created credentials object")
    except Exception as e:
        st.write("Debug: Error processing credentials:", str(e))
        raise ValueError(f"Failed to process credentials: {str(e)}")
    
    # Get bucket name from secrets
    bucket_name = getattr(st.secrets.general, 'BUCKET_NAME', 'israel-trends-archive')
    st.write("Debug: Using bucket name:", bucket_name)
    st.write("Debug: Available general attributes:", dir(st.secrets.general))
    
    # Set up storage client in session state
    from google.cloud import storage
    st.session_state.storage_client = storage.Client(
        project='israel-trends-viewer',
        credentials=credentials
    )
    st.write("Debug: Created storage client in session state")
    
    # Test bucket access
    try:
        bucket = st.session_state.storage_client.bucket(bucket_name)
        # List a few blobs to test access
        next(bucket.list_blobs(max_results=1), None)
        st.write("Debug: Successfully accessed bucket")
    except Exception as e:
        st.write("Debug: Error accessing bucket:", str(e))
        raise ValueError(f"Failed to access bucket {bucket_name}: {str(e)}")
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
