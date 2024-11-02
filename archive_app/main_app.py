import streamlit as st
import os
import json
from datetime import datetime
import requests

# Server URL - change this for deployment
SERVER_URL = "http://localhost:8000"

COUNTRIES = {
    "IL": ("Israel", "🇮🇱"),
    "LB": ("Lebanon", "🇱🇧"),
    "IR": ("Iran", "🇮🇷"),
    "CZ": ("Czech Republic (control)", "🇨🇿")
}

def get_country_files(country_code):
    """Get list of log files for a country from server"""
    try:
        # Try local path first (for development)
        local_path = os.path.join('..', 'text_archive', country_code)
        if os.path.exists(local_path):
            files = [f for f in os.listdir(local_path) if f.endswith('_log.json')]
            files.sort(reverse=True)
            return files
        
        # If local path doesn't exist or we're deployed, use server
        url = f"{SERVER_URL}/list/{country_code}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error getting file list from server: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error listing files: {str(e)}")
        return []

def load_json_data(country_code, filename):
    """Load JSON data from server"""
    try:
        # Try local path first (for development)
        local_path = os.path.join('..', 'text_archive', country_code, filename)
        if os.path.exists(local_path):
            with open(local_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not all(key in data for key in ['headlines', 'trends']):
                    raise ValueError("Missing required fields in JSON data")
                return data
        
        # If local path doesn't exist or we're deployed, use server
        url = f"{SERVER_URL}/text_archive/{country_code}/{filename}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if not all(key in data for key in ['headlines', 'trends']):
                raise ValueError("Missing required fields in JSON data")
            return data
        else:
            st.error(f"Error loading data from server: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def get_audio_file(country_code, log_filename):
    """Get audio file from server"""
    try:
        audio_filename = log_filename.replace('_log.json', '_analysis.mp3')
        
        # Try local path first (for development)
        local_path = os.path.join('..', 'archive', country_code, audio_filename)
        if os.path.exists(local_path):
            with open(local_path, 'rb') as f:
                return f.read()
        
        # If local path doesn't exist or we're deployed, use server
        url = f"{SERVER_URL}/archive/{country_code}/{audio_filename}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        return None
    except Exception as e:
        st.warning(f"Could not load audio file: {str(e)}")
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

def main():
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
        files = get_country_files(country_code)
        if not files:
            st.warning("No valid analysis files available")
            return

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

if __name__ == "__main__":
    main()
