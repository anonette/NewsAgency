import streamlit as st
import os
import json
from datetime import datetime
from pathlib import Path

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

# Get base directory (parent of archive_app)
BASE_DIR = Path(__file__).parent.parent

def get_base_filename(filename):
    """Get base filename without timestamp"""
    parts = filename.split('_')
    if len(parts) >= 2:
        return f"{parts[0]}_{parts[1]}"  # Return country_date part
    return filename

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_country_files(country_code):
    """Get list of log files and their corresponding MP3s"""
    try:
        with st.spinner('Loading file list...'):
            # Get JSON files from text_archive
            text_archive_path = BASE_DIR / 'archive' / 'text_archive' / country_code
            json_files = []
            if text_archive_path.exists():
                json_files = [f for f in text_archive_path.glob('*_log.json')]
            
            # Get MP3 files from country folder
            country_path = BASE_DIR / 'archive' / country_code
            mp3_files = []
            if country_path.exists():
                mp3_files = [f for f in country_path.glob('*_analysis.mp3')]
            
            # Get all unique dates
            dates = set()
            for f in json_files + mp3_files:
                base_name = get_base_filename(f.name)
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
                    if get_base_filename(f.name).split('_')[1] == date_str:
                        json_match = f
                        break
                
                # Look for MP3 file
                for f in mp3_files:
                    if get_base_filename(f.name).split('_')[1] == date_str:
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

@st.cache_data(ttl=3600)  # Cache JSON data for 1 hour
def load_json_data(file_pair):
    """Load JSON data from file"""
    try:
        if not file_pair['json']:
            return None
            
        with st.spinner('Loading data...'):
            with open(file_pair['json'], 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not all(key in data for key in ['headlines', 'trends']):
                raise ValueError("Missing required fields in JSON data")
            return data
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

@st.cache_data(ttl=3600)  # Cache audio files for 1 hour
def get_audio_file(file_pair):
    """Get audio file"""
    try:
        if not file_pair['mp3']:
            return None
            
        with st.spinner('Loading audio...'):
            with open(file_pair['mp3'], 'rb') as f:
                return f.read()
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
    .stSpinner {
        text-align: center;
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<h1 class="main-title">Middle East Pulse News Agency:<br>Nostalgia for Real Data in a Synthetic World</h1>', unsafe_allow_html=True)
st.markdown('<p class="description">Capturing the last traces of authentic human searches through Google Trends, this project contrasts official narratives with genuine public sentiment—a glimpse into the "real" in an era of synthetic media.</p>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# Get selected country from session state
if 'selected_country' not in st.session_state:
    st.session_state.selected_country = None
    st.session_state.preloaded_data = None

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
        st.session_state.preloaded_data = None
        st.rerun()

    st.header(f"{country_flag} {country_name}")

    # Get available files
    files = get_country_files(country_code)
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
        # Preload data for the selected date if not already loaded
        if (not st.session_state.preloaded_data or 
            st.session_state.preloaded_data['date'] != selected_file['date']):
            with st.spinner("Loading content..."):
                data = load_json_data(selected_file)
                audio_data = get_audio_file(selected_file)
                st.session_state.preloaded_data = {
                    'date': selected_file['date'],
                    'data': data,
                    'audio': audio_data
                }
        else:
            data = st.session_state.preloaded_data['data']
            audio_data = st.session_state.preloaded_data['audio']

        with st.container():
            # Audio player
            if audio_data:
                st.audio(audio_data, format='audio/mp3')

            if data:
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
