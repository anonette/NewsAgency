import streamlit as st
import os
import json
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# Configuration and setup
st.set_page_config(
    page_title="Middle East Pulse News Agency",
    page_icon="🌍",
    layout="wide"
)

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

def get_base_filename(filename):
    """Get base filename without timestamp"""
    parts = filename.split('_')
    if len(parts) >= 2:
        return f"{parts[0]}_{parts[1]}"  # Return country_date part
    return filename

def get_country_files(service, country_code):
    """Get list of log files and their corresponding MP3s"""
    try:
        # Get JSON files from text_archive folder and its subfolders
        text_folder_id = st.secrets["folder_ids"]
        json_query = f"'{text_folder_id}' in parents and name contains '{country_code}' and name contains '_log.json' and trashed = false"
        
        # Debugging: Print the query and folder ID
        st.write(f"Debug: JSON Query - {json_query}")
        st.write(f"Debug: Text Folder ID - {text_folder_id}")
        
        json_results = service.files().list(
            q=json_query,
            spaces='drive',
            fields='files(id, name, parents)'
        ).execute()
        json_files = json_results.get('files', [])
        
        # Search in subfolders
        subfolders_query = f"'{text_folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        subfolders_results = service.files().list(
            q=subfolders_query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        subfolders = subfolders_results.get('files', [])
        
        for subfolder in subfolders:
            subfolder_id = subfolder['id']
            subfolder_json_query = f"'{subfolder_id}' in parents and name contains '{country_code}' and name contains '_log.json' and trashed = false"
            subfolder_json_results = service.files().list(
                q=subfolder_json_query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            json_files.extend(subfolder_json_results.get('files', []))
        
        # Debugging: Print the retrieved JSON files
        st.write(f"Debug: Retrieved JSON Files - {json_files}")
        
        # Get MP3 files from country folder
        country_folder_id = st.secrets["folder_ids"][country_code]
        mp3_query = f"'{country_folder_id}' in parents and name contains '_analysis.mp3' and trashed = false"
        mp3_results = service.files().list(
            q=mp3_query,
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        mp3_files = mp3_results.get('files', [])
        
        # Get all unique dates
        dates = set()
        for f in json_files + mp3_files:
            base_name = get_base_filename(f['name'])
            date_str = base_name.split('_')[1]
            dates.add(date_str)
        
        # Create file pairs for all dates
        file_pairs = []
        for date_str in dates:
            # Find matching files
            json_match = None
            mp3_match = None
            
            # Look for JSON file
            for f in json_files:
                if get_base_filename(f['name']).split('_')[1] == date_str:
                    json_match = f
                    break
            
            # Look for MP3 file
            for f in mp3_files:
                if get_base_filename(f['name']).split('_')[1] == date_str:
                    mp3_match = f
                    break
            
            file_pairs.append({
                'date': date_str,
                'json': json_match,
                'mp3': mp3_match
            })
        
        return sorted(file_pairs, key=lambda x: x['date'], reverse=True)
    except Exception as e:
        st.error(f"Error accessing files: {str(e)}")
        return []

def load_json_data(service, file_pair):
    """Load JSON data from Drive file"""
    try:
        if not file_pair['json']:
            return None
            
        request = service.files().get_media(fileId=file_pair['json']['id'])
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        file.seek(0)
        data = json.loads(file.read().decode())
        
        if not all(key in data for key in ['headlines', 'trends']):
            raise ValueError("Missing required fields in JSON data")
        return data
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def get_audio_file(service, file_pair):
    """Get audio file from Drive"""
    try:
        if not file_pair['mp3']:
            return None
            
        request = service.files().get_media(fileId=file_pair['mp3']['id'])
        audio_file = io.BytesIO()
        downloader = MediaIoBaseDownload(audio_file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        audio_file.seek(0)
        return audio_file.read()
    except Exception as e:
        st.warning(f"Could not load audio: {str(e)}")
        return None

def format_date(file_pair):
    """Format date from filename"""
    try:
        date_str = file_pair['date']
        date = datetime.strptime(date_str, '%Y%m%d')
        formatted = date.strftime('%A, %B %d, %Y')
        
        # Add indicators for missing files
        status = []
        if not file_pair['json']:
            status.append("No Data")
        if not file_pair['mp3']:
            status.append("No Audio")
            
        if status:
            formatted += f" ({', '.join(status)})"
            
        return formatted
    except:
        return file_pair['date']

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
        margin: 0 auto 2em auto;
        max-width: 800px;
        line-height: 1.6;
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

# Title and description
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
        format_func=format_date
    )

    if selected_file:
        # Load and display data
        data = load_json_data(drive_service, selected_file)
        if data:
            with st.container():
                # Audio player
                audio_data = get_audio_file(drive_service, selected_file)
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
        else:
            st.info("No data available for this date")
            if selected_file['mp3']:
                audio_data = get_audio_file(drive_service, selected_file)
                if audio_data:
                    st.audio(audio_data, format='audio/mp3')
