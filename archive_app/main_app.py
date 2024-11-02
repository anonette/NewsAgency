import streamlit as st
import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup

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

# Base URL where files are hosted
base_url = "http://95.216.199.241:8080/"

def fetch_directories():
    """Fetch available country directories"""
    response = requests.get(base_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        return [link.get('href') for link in soup.find_all('a') if link.get('href').endswith('/') and link.get('href') != '../']
    else:
        st.error(f"Could not fetch directories. Server returned status: {response.status_code}")
        return []

def fetch_files(subfolder=""):
    """Fetch files from a specific country directory"""
    url = base_url + subfolder
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        files = [link.get('href') for link in soup.find_all('a') 
                if not link.get('href').endswith('/') and link.get('href') != '../']
        
        # Group files by date
        file_pairs = []
        dates = set()
        
        for file in files:
            if '_log.json' in file or '_analysis.mp3' in file:
                date_str = file.split('_')[1]
                dates.add(date_str)
        
        for date_str in dates:
            json_match = next((f for f in files if f'_{date_str}_log.json' in f), None)
            mp3_match = next((f for f in files if f'_{date_str}_analysis.mp3' in f), None)
            
            file_pairs.append({
                'date': date_str,
                'json': json_match,
                'mp3': mp3_match
            })
        
        return sorted(file_pairs, key=lambda x: x['date'], reverse=True)
    else:
        st.error(f"Could not fetch files. Server returned status: {response.status_code}")
        return []

def load_json_data(subfolder, json_file):
    """Load JSON data from file"""
    try:
        if not json_file:
            return None
            
        url = base_url + subfolder + json_file
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if not all(key in data for key in ['headlines', 'trends']):
                raise ValueError("Missing required fields in JSON data")
            return data
        return None
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
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
    files = fetch_files(f"{country_code}/")
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
        data = load_json_data(f"{country_code}/", selected_file['json'])
        if data:
            with st.container():
                # Audio player
                if selected_file['mp3']:
                    audio_url = base_url + country_code + "/" + selected_file['mp3']
                    st.audio(audio_url, format='audio/mp3')

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
                audio_url = base_url + country_code + "/" + selected_file['mp3']
                st.audio(audio_url, format='audio/mp3')
