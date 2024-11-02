import streamlit as st
import os
import json
from datetime import datetime

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

def get_base_filename(filename):
    """Get base filename without timestamp"""
    parts = filename.split('_')
    if len(parts) >= 2:
        return f"{parts[0]}_{parts[1]}"  # Return country_date part
    return filename

def get_country_files(country_code):
    """Get list of log files and their corresponding MP3s"""
    try:
        # Get JSON files from text_archive inside archive
        json_path = os.path.join('..', 'archive', 'text_archive', country_code)
        json_files = [f for f in os.listdir(json_path) if f.endswith('_log.json')]
        
        # Get MP3 files from archive
        mp3_path = os.path.join('..', 'archive', country_code)
        mp3_files = [f for f in os.listdir(mp3_path) if f.endswith('_analysis.mp3')]
        
        # Get all unique dates
        dates = set()
        for f in json_files + mp3_files:
            base_name = get_base_filename(f)
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
                if get_base_filename(f).split('_')[1] == date_str:
                    json_match = f
                    break
            
            # Look for MP3 file
            for f in mp3_files:
                if get_base_filename(f).split('_')[1] == date_str:
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

def load_json_data(country_code, file_pair):
    """Load JSON data from file"""
    try:
        if not file_pair['json']:
            return None
            
        json_path = os.path.join('..', 'archive', 'text_archive', country_code, file_pair['json'])
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not all(key in data for key in ['headlines', 'trends']):
                raise ValueError("Missing required fields in JSON data")
            return data
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
    return None

def get_audio_file(country_code, file_pair):
    """Get audio file content"""
    try:
        if not file_pair['mp3']:
            return None
            
        mp3_path = os.path.join('..', 'archive', country_code, file_pair['mp3'])
        with open(mp3_path, 'rb') as f:
            return f.read()
    except Exception as e:
        st.error(f"Error loading audio: {str(e)}")
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
        # Load and display data
        data = load_json_data(country_code, selected_file)
        if data:
            with st.container():
                # Audio player
                audio_data = get_audio_file(country_code, selected_file)
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
                audio_data = get_audio_file(country_code, selected_file)
                if audio_data:
                    st.audio(audio_data, format='audio/mp3')
