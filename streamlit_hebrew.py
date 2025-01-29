import streamlit as st
import os
import json
import tempfile

def setup_cloud_credentials():
    """Set up Google Cloud credentials from Streamlit secrets or local file"""
    try:
        # Try to get credentials from Streamlit secrets first
        if hasattr(st.secrets, 'GOOGLE_APPLICATION_CREDENTIALS_JSON'):
            try:
                # Create temporary file for credentials
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    json.dump(json.loads(st.secrets.GOOGLE_APPLICATION_CREDENTIALS_JSON), f)
                    temp_path = f.name
                
                # Set environment variable to temp file path
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_path
                # Also set BUCKET_NAME from secrets if available
                if hasattr(st.secrets, 'BUCKET_NAME'):
                    os.environ['BUCKET_NAME'] = st.secrets.BUCKET_NAME
                print(f"Using credentials from Streamlit secrets")
                return True
            except Exception as e:
                st.error(
                    "Error processing Google Cloud credentials from Streamlit secrets. Please check:\n"
                    "1. The credentials JSON in .streamlit/secrets.toml is properly formatted\n"
                    "2. The JSON content is valid\n"
                    f"\nError: {str(e)}"
                )
                return False
        else:
            # For local development, use key.json
            key_path = os.path.join(os.path.dirname(__file__), 'key.json')
            if os.path.exists(key_path):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_path
                print(f"Using local key.json: {key_path}")
                return True
            
            st.error(
                "Google Cloud credentials not found. Please either:\n"
                "1. Set credentials in Streamlit Cloud secrets\n"
                "2. Place key.json file in the project directory for local development"
            )
            return False
    except Exception as e:
        st.error(
            "Unexpected error setting up credentials:\n"
            f"{str(e)}\n\n"
            "Please check your configuration."
        )
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

    # Import and run israel4_viewer after credentials are set up
    from israel4_viewer import main as israel4_viewer_main
    israel4_viewer_main(config_set=True)

if __name__ == "__main__":
    main()
