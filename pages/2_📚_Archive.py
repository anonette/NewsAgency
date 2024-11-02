import streamlit as st
import json
from datetime import datetime
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

COUNTRIES = {
    "IL": ("Israel", "🇮🇱"),
    "LB": ("Lebanon", "🇱🇧"),
    "IR": ("Iran", "🇮🇷"),
    "CZ": ("Czech Republic (control)", "🇨🇿")
}

# Initialize Google Drive service
@st.cache_resource
def get_drive_service():
    try:
        # Get the folder ID from secrets
        folder_id = st.secrets["folder_ids"]["text_archive"]
        
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        return build('drive', 'v3', credentials=credentials)
    except Exception as e:
        st.error(f"Failed to initialize Drive service: {str(e)}")
        return None

def get_country_files(service, country_code):
    """Get list of log files for a country from Google Drive"""
    try:
        folder_id = st.secrets["folder_ids"]["text_archive"]
        
        # Search for files in the country folder
        query = f"'{folder_id}' in parents and name contains '{country_code}' and name contains '_log.json' and trashed = false"
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        files = results.get('files', [])
        files.sort(key=lambda x: x['name'], reverse=True)
        return files
    except Exception as e:
        st.error(f"Error listing files: {str(e)}")
        return []

def load_json_data(service, file_id):
    """Load JSON data from Drive file"""
    try:
        request = service.files().get_media(fileId=file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        file.seek(0)
        data = json.loads(file.read().decode())
        
        # Verify required fields exist
        if not all(key in data for key in ['headlines', 'trends']):
            raise ValueError("Missing required fields in JSON data")
        return data
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def format_date(filename):
    """Format date from filename"""
    try:
        match = filename.split('_')[1]
        year = match[:4]
        month = match[4:6]
        day = match[6:8]
        date = datetime(int(year), int(month), int(day))
        return date.strftime('%A, %B %d, %Y')
    except:
        return filename

def get_audio_file(service, log_file_name, country_code):
    """Get audio file from Drive"""
    try:
        folder_id = st.secrets["folder_ids"][country_code]
        audio_filename = log_file_name.replace('_log.json', '_analysis.mp3')
        
        # Search for the audio file
        query = f"'{folder_id}' in parents and name = '{audio_filename}' and trashed = false"
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id)'
        ).execute()
        
        files = results.get('files', [])
        if files:
            request = service.files().get_media(fileId=files[0]['id'])
            audio_file = io.BytesIO()
            downloader = MediaIoBaseDownload(audio_file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            audio_file.seek(0)
            return audio_file.read()
        return None
    except Exception as e:
        st.warning(f"Could not load audio: {str(e)}")
        return None

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
    .subtitle {
        text-align: center;
        color: #34495e;
        font-size: 1.2em;
        margin-bottom: 1em;
        font-style: italic;
    }
    .description {
        text-align: center;
        color: #576574;
        font-size: 1.1em;
        margin: 0 auto 2em auto;
        max-width: 800px;
        line-height: 1.6;
    }
    .country-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
        padding: 20px 0;
    }
    .country-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .country-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .country-flag {
        font-size: 3em;
        margin-bottom: 10px;
    }
    .file-item {
        background: white;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .trend-item {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    .related-search {
        background: #e9ecef;
        border-radius: 15px;
        padding: 5px 10px;
        margin: 5px;
        display: inline-block;
        font-size: 0.9em;
    }
    .stButton button {
        border-radius: 5px;
        background-color: #2c3e50;
        color: white;
    }
    .stButton button:hover {
        background-color: #34495e;
    }
    hr.divider {
        border: none;
        height: 1px;
        background-color: #e0e0e0;
        margin: 2em 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Drive service
drive_service = get_drive_service()
if not drive_service:
    st.error("Failed to initialize Google Drive service")
    st.stop()

# Title, subtitle, and description
st.markdown('<h1 class="main-title">Middle East Pulse News Agency:<br>Nostalgia for Real Data in a Synthetic World</h1>', unsafe_allow_html=True)
st.markdown('<p class="description">Capturing the last traces of authentic human searches through Google Trends, this project contrasts official narratives with genuine public sentiment—a glimpse into the "real" in an era of synthetic media.</p>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# Get selected country from session state
if 'selected_country' not in st.session_state:
    st.session_state.selected_country = None

# Show country grid if no country selected
if not st.session_state.selected_country:
    cols = st.columns(2)
    for i, (code, (name, flag)) in enumerate(COUNTRIES.items()):
        with cols[i % 2]:
            if st.button(
                f"{flag} {name}",
                key=f"country_{code}",
                use_container_width=True,
                help=f"View analysis for {name}"
            ):
                st.session_state.selected_country = code
                st.rerun()

# Show country analysis
else:
    country_code = st.session_state.selected_country
    country_name = COUNTRIES[country_code][0]
    country_flag = COUNTRIES[country_code][1]

    if st.button("← Back to Countries"):
        st.session_state.selected_country = None
        st.rerun()

    st.header(f"{country_flag} {country_name}")

    # Get available files
    files = get_country_files(drive_service, country_code)
    if not files:
        st.warning("No analysis files available")
        st.stop()

    # Date selector
    selected_file = st.selectbox(
        "Select Date:",
        files,
        format_func=lambda x: format_date(x['name'])
    )

    if selected_file:
        # Load and display data
        data = load_json_data(drive_service, selected_file['id'])
        if data:
            with st.container():
                # Audio player
                audio_data = get_audio_file(drive_service, selected_file['name'], country_code)
                if audio_data:
                    st.audio(audio_data, format='audio/mp3')

                # Headlines
                st.subheader("📰 Official Headlines")
                for headline in data.get('headlines', []):
                    st.markdown(f"• {headline}")

                # Trends
                st.subheader("🔍 Google Trends")
                for trend in data.get('trends', []):
                    with st.expander(trend.get('title', 'Untitled Trend'), expanded=True):
                        for related in trend.get('related', []):
                            st.markdown(f'<span class="related-search">{related}</span>', unsafe_allow_html=True)

                # Analysis
                if data.get('analysis'):
                    st.subheader("🎭 Analysis")
                    st.markdown(data['analysis'])
