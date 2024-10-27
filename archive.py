import streamlit as st
import os
import json
from datetime import datetime
import glob
import base64
import shutil

# Create archive directory structure if it doesn't exist
ARCHIVE_DIR = "archive"
COUNTRIES = {
    "IL": "Israel",
    "LE": "Lebanon",
    "IR": "Iran"
}

def setup_archive():
    """Create archive directory structure"""
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)
    
    for code in COUNTRIES.keys():
        country_dir = os.path.join(ARCHIVE_DIR, code)
        if not os.path.exists(country_dir):
            os.makedirs(country_dir)

def archive_analysis(country_code, date=None):
    """Archive the latest analysis for a country"""
    if date is None:
        date = datetime.now().strftime("%Y%m%d")
    
    # Find the latest audio file
    audio_pattern = f"{country_code}_*_analysis.mp3"
    audio_files = glob.glob(audio_pattern)
    if not audio_files:
        return False
    
    latest_audio = max(audio_files, key=os.path.getctime)
    timestamp = latest_audio.split('_')[1]  # Get timestamp from audio filename
    
    # Create date directory in country archive
    country_dir = os.path.join(ARCHIVE_DIR, country_code)
    date_dir = os.path.join(country_dir, date)
    if not os.path.exists(date_dir):
        os.makedirs(date_dir)
    
    # Copy audio file to archive
    archived_audio = os.path.join(date_dir, os.path.basename(latest_audio))
    shutil.copy2(latest_audio, archived_audio)
    
    # Create analysis data file
    analysis_data = {
        'timestamp': timestamp,
        'headlines': [],  # Will be populated from streamlit session state
        'trends': [],    # Will be populated from streamlit session state
        'analysis': ''   # Will be populated from streamlit session state
    }
    
    if 'results' in st.session_state:
        results = st.session_state.results
        analysis_data['headlines'] = results.get('headlines', [])
        analysis_data['trends'] = [
            {'title': t['title'], 'related': t['related']} 
            for t in results.get('trends_data', [])
        ]
        analysis_data['analysis'] = results.get('analysis', '')
    
    # Save analysis data as JSON
    analysis_file = os.path.join(date_dir, f"{country_code}_{timestamp}_data.json")
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, ensure_ascii=False, indent=2)
    
    return True

def get_audio_player_html(audio_path):
    """Generate HTML code for audio player"""
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()
    audio_base64 = base64.b64encode(audio_bytes).decode()
    audio_player = f"""
        <audio controls>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            Your browser does not support the audio element.
        </audio>
    """
    return audio_player

def display_analysis_data(data_file):
    """Display archived analysis data"""
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Display headlines
    if data['headlines']:
        st.subheader("📰 Headlines")
        for headline in data['headlines']:
            st.markdown(f"• {headline}")
    
    # Display trends
    if data['trends']:
        st.subheader("🔍 Trending Searches")
        for trend in data['trends']:
            with st.expander(f"**{trend['title']}**", expanded=False):
                if trend['related']:
                    st.markdown("Related searches:")
                    for related in trend['related']:
                        st.markdown(f"• {related}")
    
    # Display analysis
    if data['analysis']:
        st.subheader("✒️ Analysis")
        st.markdown(data['analysis'])

def main():
    st.set_page_config(
        page_title="Trends Archive",
        page_icon="📚",
        layout="wide"
    )

    st.title("📚 Trends Analysis Archive")
    st.markdown("### Historical Analysis by Country and Date")

    # Setup archive structure
    setup_archive()

    # Country selector
    country = st.selectbox(
        "Choose a country:",
        list(COUNTRIES.keys()),
        format_func=lambda x: f"{COUNTRIES[x]} ({x})"
    )

    # Get available dates for selected country
    country_dir = os.path.join(ARCHIVE_DIR, country)
    if os.path.exists(country_dir):
        dates = sorted([d for d in os.listdir(country_dir) if os.path.isdir(os.path.join(country_dir, d))], reverse=True)
        
        if dates:
            selected_date = st.selectbox(
                "Choose a date:",
                dates,
                format_func=lambda x: datetime.strptime(x, "%Y%m%d").strftime("%B %d, %Y")
            )

            # Display archived analysis
            date_dir = os.path.join(country_dir, selected_date)
            
            # Get all analysis files for the selected date
            data_files = sorted(glob.glob(os.path.join(date_dir, f"{country}_*_data.json")))
            audio_files = sorted(glob.glob(os.path.join(date_dir, f"{country}_*_analysis.mp3")))
            
            if data_files:
                for i, (data_file, audio_file) in enumerate(zip(data_files, audio_files)):
                    timestamp = data_file.split('_')[1]
                    analysis_time = datetime.strptime(timestamp, "%Y%m%d_%H%M%S").strftime("%I:%M %p")
                    
                    st.markdown(f"## Analysis from {analysis_time}")
                    st.markdown("---")
                    
                    # Display analysis data
                    display_analysis_data(data_file)
                    
                    # Display audio player
                    st.subheader("🔊 Audio Version")
                    audio_player = get_audio_player_html(audio_file)
                    st.markdown(audio_player, unsafe_allow_html=True)
                    st.caption(f"Audio file: {os.path.basename(audio_file)}")
                    
                    if i < len(data_files) - 1:
                        st.markdown("---")
            else:
                st.info(f"No archived analyses found for {selected_date}")
        else:
            st.info(f"No archived analyses found for {COUNTRIES[country]}")
    else:
        st.error(f"Archive directory not found for {COUNTRIES[country]}")

    # Archive current analysis
    st.markdown("---")
    st.subheader("📥 Archive Current Analysis")
    
    if st.button("Archive Latest Analysis"):
        if archive_analysis(country):
            st.success("Successfully archived latest analysis!")
        else:
            st.error("No analysis found to archive")

if __name__ == "__main__":
    main()
