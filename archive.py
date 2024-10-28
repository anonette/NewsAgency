import streamlit as st
import os
import json
from datetime import datetime
import glob
import base64
import io

# Create archive directory structure if it doesn't exist
ARCHIVE_DIR = "archive"
COUNTRIES = {
    "IL": "Israel",
    "LB": "Lebanon",  # Changed from 'LE' to 'LB' to match lebanon_trends.py
    "IR": "Iran"
}

def get_country_audio_files(country_code):
    """Get audio files for a specific country from its subdirectory"""
    # Look only in the country-specific subdirectory
    country_dir = os.path.join(ARCHIVE_DIR, country_code)
    if not os.path.exists(country_dir):
        return []
        
    pattern = os.path.join(country_dir, f"{country_code}_*_analysis.mp3")
    files = glob.glob(pattern)
    
    # Sort files by date (newest first)
    files.sort(reverse=True)
    
    return files

def main():
    st.set_page_config(
        page_title="Middle East Pulse",
        page_icon="🌍",
        layout="wide"
    )

    st.title("🌍 Middle East Pulse: The People's Voice in Synthetic Times")
    st.markdown("### News Agency with a regional focus, amplifying authentic public sentiments in a post-truth era.")

    # Initialize session state for country
    if 'current_country' not in st.session_state:
        st.session_state.current_country = None

    # Country selector
    country = st.selectbox(
        "Choose a country:",
        list(COUNTRIES.keys()),
        format_func=lambda x: f"{COUNTRIES[x]} ({x})"
    )

    # Clear cache if country changed
    if st.session_state.current_country != country:
        st.session_state.clear()
        st.session_state.current_country = country
        st.rerun()

    # Get audio files for selected country
    audio_files = get_country_audio_files(country)

    if audio_files:
        st.subheader("🔊 Podcast")
        
        # Display each audio file
        for audio_path in audio_files:
            filename = os.path.basename(audio_path)
            
            # Extract date from filename
            try:
                date_str = filename.split('_')[1]
                date = datetime.strptime(date_str, "%Y%m%d").strftime("%B %d, %Y")
            except:
                date = "Unknown Date"
            
            with st.expander(f"**{date}**", expanded=True):
                try:
                    # Read audio file
                    with open(audio_path, 'rb') as f:
                        audio_bytes = f.read()
                    
                    # Use Streamlit's native audio component
                    st.audio(audio_bytes, format='audio/mp3')
                    st.caption(filename)
                except Exception as e:
                    st.error(f"Error loading audio file {filename}: {str(e)}")
    else:
        st.info(f"No podcast episodes found for {COUNTRIES[country]}")

if __name__ == "__main__":
    main()
