import streamlit as st
import os
import json
from datetime import datetime
import requests
from pathlib import Path

# Configuration and setup
st.set_page_config(
    page_title="Middle East Pulse News Agency",
    page_icon="🌍",
    layout="wide"
)

# Server configuration
SERVER_URL = "http://95.216.199.241:8080"

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

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_country_files(country_code):
    """Get list of log files from server"""
    try:
        with st.spinner('Loading file list...'):
            # Get JSON files list
            json_response = requests.get(f"{SERVER_URL}/{country_code}")
            if json_response.status_code != 200:
                st.error(f"Error accessing server: {json_response.status_code}")
                return []
            
            # Parse filenames from response
            files = []
            for line in json_response.text.split('\n'):
                if '_log.json' in line or '_analysis.mp3' in line:
                    files.append(line.strip())
            
            # Get all unique dates
            dates = set()
            for filename in files:
                if '_log.json' in filename or '_analysis.mp3' in filename:
                    base_name = get_base_filename(filename)
                    date_str = base_name.split('_')[1]
                    dates.add(date_str)
            
            # Create file pairs for all dates
            file_pairs = []
            for date_str in dates:
                json_file = f"{country_code}_{date_str}_log.json"
                mp3_file = f"{country_code}_{date_str}_analysis.mp3"
                
                # Check if files exist
                json_exists = any(json_file in f for f in files)
                mp3_exists = any(mp3_file in f for f in files)
                
                if json_exists or mp3_exists:
                    file_pairs.append({
                        'date': date_str,
                        'json': json_file if json_exists else None,
                        'mp3': mp3_file if mp3_exists else None
                    })
            
            return sorted(file_pairs, key=lambda x: x['date'], reverse=True)
    except Exception as e:
        st.error(f"Error accessing files: {str(e)}")
        return []

@st.cache_data(ttl=3600)  # Cache JSON data for 1 hour
def load_json_data(country_code, filename):
    """Load JSON data from server"""
    try:
        if not filename:
            return None
            
        with st.spinner('Loading data...'):
            response = requests.get(f"{SERVER_URL}/{country_code}/{filename}")
            if response.status_code != 200:
                st.error(f"Error loading data: {response.status_code}")
                return None
            
            data = response.json()
            if not all(key in data for key in ['headlines', 'trends']):
                raise ValueError("Missing required fields in JSON data")
            return data
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

@st.cache_data(ttl=3600)  # Cache audio files for 1 hour
def get_audio_url(country_code, filename):
    """Get audio URL from server"""
    if not filename:
        return None
    return f"{SERVER_URL}/{country_code}/{filename}"

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

def has_rtl_text(text):
    """Check if text contains RTL characters (Hebrew or Arabic)"""
    return any(ord(c) > 0x590 and ord(c) < 0x6FF for c in text)

# Add custom CSS with RTL support
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
    .trend-container {
        margin-bottom: 1em;
        padding: 1em;
        border-radius: 5px;
        background-color: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .trend-title {
        font-size: 1.1em;
        font-weight: 500;
        margin-bottom: 0.5em;
    }
    .related-searches {
        margin-top: 0.5em;
        margin-left: 1em;
        color: #666;
    }
    .no-related {
        color: #999;
        font-style: italic;
        font-size: 0.9em;
        margin-left: 1em;
    }
    [dir="rtl"] {
        text-align: right !important;
        direction: rtl !important;
    }
    .rtl-container {
        display: flex;
        flex-direction: row-reverse;
        justify-content: flex-start;
        align-items: center;
        gap: 0.5em;
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
        data = load_json_data(country_code, selected_file['json'])
        if data:
            with st.container():
                # Audio player
                if selected_file['mp3']:
                    audio_url = get_audio_url(country_code, selected_file['mp3'])
                    if audio_url:
                        st.audio(audio_url, format='audio/mp3')

                # Headlines
                st.subheader("📰 Official Headlines")
                for headline in data.get('headlines', []):
                    # Check if headline contains RTL text
                    if has_rtl_text(headline):
                        # Display RTL text with proper direction
                        st.markdown(f'<div dir="rtl" style="text-align: right;">• {headline}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f"• {headline}")

                # Trends
                st.subheader("🔍 Google Trends")
                trends = data.get('trends', [])
                
                # Display each trend in a container
                for i, trend in enumerate(trends, 1):
                    title = trend.get('title', 'Untitled Trend')
                    related_searches = trend.get('related', [])
                    
                    # Check if title contains RTL text
                    has_rtl_title = has_rtl_text(title)
                    
                    # Create related searches HTML
                    related_html = ""
                    if related_searches:
                        related_spans = []
                        for related in related_searches:
                            # Check if related search contains RTL text
                            has_rtl_related = has_rtl_text(related)
                            if has_rtl_related:
                                related_spans.append(f'<span class="related-search" dir="rtl" style="text-align: right;">{related}</span>')
                            else:
                                related_spans.append(f'<span class="related-search">{related}</span>')
                        related_html = '<div class="related-searches">Related searches: ' + ''.join(related_spans) + '</div>'
                    else:
                        related_html = '<div class="no-related">No related searches found</div>'
                    
                    # Display the trend with proper RTL support
                    st.markdown(f"""
                    <div class="trend-container">
                        <div class="trend-title" {f'dir="rtl" style="text-align: right;"' if has_rtl_title else ''}>
                            {i}. {title}
                        </div>
                        {related_html}
                    </div>
                    """, unsafe_allow_html=True)

                # Analysis
                if data.get('analysis'):
                    st.subheader("🎭 Analysis")
                    st.markdown(data['analysis'])
        else:
            st.info("No data available for this date")
            if selected_file['mp3']:
                audio_url = get_audio_url(country_code, selected_file['mp3'])
                if audio_url:
                    st.audio(audio_url, format='audio/mp3')
