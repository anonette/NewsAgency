import os
import json
import tempfile

def setup_google_credentials():
    """
    Set up Google Cloud credentials from environment variable.
    In Streamlit Cloud, the credentials JSON is stored as a string in an environment variable.
    This function creates a temporary file with the credentials for the google-cloud-storage library.
    """
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
                print("Google Cloud credentials configured successfully")
        else:
            print("No Google Cloud credentials found in environment variables")
            
    except Exception as e:
        print(f"Error setting up Google Cloud credentials: {str(e)}")

if __name__ == "__main__":
    setup_google_credentials()
