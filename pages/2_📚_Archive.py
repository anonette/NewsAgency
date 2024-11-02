import streamlit as st
import json
import os
from datetime import datetime
import requests
from urllib.parse import urlparse, parse_qs

COUNTRIES = {
    "IL": ("Israel", "🇮🇱"),
    "LB": ("Lebanon", "🇱🇧"),
    "IR": ("Iran", "🇮🇷"),
    "CZ": ("Czech Republic (control)", "🇨🇿")
}

def get_file_id_from_url(url):
    """Extract file ID from Google Drive URL"""
    try:
        parsed = urlparse(url)
        if 'drive.google.com' in parsed.netloc:
            if 'folders' in parsed.path:
                return parsed.path.split('/')[-1]
            elif 'id=' in url:
                return parse_qs(parsed.query)['id'][0]
    except:
        pass
    return None

def get_drive_files(country_code):
    """Get list of log files from Google Drive text_archive"""
    try:
        # Get the text_archive folder URL from secrets
        folder_url = st.secrets["text_archive_drive_url"]
        folder_id = get_file_id_from_url(folder_url)
        
        if not folder_id:
            st.error("Invalid Drive folder URL")
            return []
        
        # Construct the direct download URL
        files_url = f"https://drive.google.com/drive/folders/{folder_id}/{country_code}"
        
        # Use requests to get file listing (this will be public read-only access)
        response = requests.get(files_url)
        if response.status_code != 200:
            return []
        
        # Parse the response to get file listings
        # This will work because the folder is set to "Anyone with the link can view"
        files = []
        for item in response.json():
            if item['name'].endswith('_log.json'):
                files.append({
                    'name': item['name'],
                    'id': item['id']
                })
        
        files.sort(key=lambda x: x['name'], reverse=True)
        return files
    except Exception as e:
        st.error(f"Error listing Drive files: {str(e)}")
        return []

def load_json_data(file_info):
    """Load JSON data from Drive"""
    try:
        # Construct direct download URL for the file
        file_url = f"https://drive.google.com/uc?export=download&id={file_info['id']}"
        
        # Download and parse JSON
        response = requests.get(file_url)
        if response.status_code != 200:
            raise ValueError("Failed to download file")
        
        data = response.json()
        
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

def get_audio_file(log_file_name, country_code):
    """Get audio file from Drive"""
    try:
        audio_filename = log_file_name.replace('_log.json', '_analysis.mp3')
        folder_url = st.secrets["text_archive_drive_url"]
        folder_id = get_file_id_from_url(folder_url)
        
        if not folder_id:
            return None
            
        # Construct audio file URL
        audio_url = f"https://drive.google.com/uc?export=download&id={folder_id}/{country_code}/{audio_filename}"
        
        # Download audio file
        response = requests.get(audio_url)
        if response.status_code == 200:
            return response.content
        return None
    except Exception as e:
        st.warning(f"Could not load audio: {str(e)}")
        return None

st.set_page_config(
    page_title="Middle East Pulse News Agency",
    page_icon="🌍",
    layout="wide"
)

# [CSS styles remain the same...]

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
    files = get_drive_files(country_code)
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
        data = load_json_data(selected_file)
        if data:
            with st.container():
                # Audio player
                audio_data = get_audio_file(selected_file['name'], country_code)
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
