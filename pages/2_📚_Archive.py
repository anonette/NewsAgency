import streamlit as st
import os
import json
from datetime import datetime
import base64

COUNTRIES = {
    "IL": ("Israel", "🇮🇱"),
    "LB": ("Lebanon", "🇱🇧"),
    "IR": ("Iran", "🇮🇷"),
    "CZ": ("Czech Republic", "🇨🇿")
}

def load_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

def format_date(filename):
    # Extract date from filename format: XX_YYYYMMDD_HHMMSS
    try:
        date_str = filename.split('_')[1]
        date_obj = datetime.strptime(date_str, '%Y%m%d')
        return date_obj.strftime('%A, %B %d, %Y')
    except:
        return filename

def get_audio_data(file_path):
    try:
        with open(file_path, "rb") as f:
            audio_bytes = f.read()
            b64 = base64.b64encode(audio_bytes).decode()
            return f'data:audio/mp3;base64,{b64}'
    except Exception as e:
        st.error(f"Error loading audio: {str(e)}")
        return None

def list_country_files(country_code):
    archive_path = os.path.join('text_archive', country_code)
    try:
        files = [f for f in os.listdir(archive_path) if f.endswith('_log.json')]
        files.sort(reverse=True)
        return files
    except Exception as e:
        st.error(f"Error listing files: {str(e)}")
        return []

def main():
    st.set_page_config(
        page_title="Trends Analysis Archive",
        page_icon="📚",
        layout="wide"
    )

    st.title("📚 Trends Analysis Archive")

    # Create grid layout for country cards
    cols = st.columns(2)
    for i, (code, (name, flag)) in enumerate(COUNTRIES.items()):
        with cols[i % 2]:
            with st.expander(f"{flag} {name}", expanded=True):
                files = list_country_files(code)
                
                if not files:
                    st.info(f"No analysis files available for {name}")
                    continue

                # Date selector
                selected_file = st.selectbox(
                    f"Select date for {name}:",
                    files,
                    format_func=format_date,
                    key=f"date_select_{code}"
                )

                if selected_file:
                    # Load and display analysis data
                    json_path = os.path.join('text_archive', code, selected_file)
                    data = load_json_file(json_path)
                    
                    if data:
                        # Audio player
                        audio_filename = selected_file.replace('_log.json', '_analysis.mp3')
                        audio_path = os.path.join('archive', code, audio_filename)
                        
                        if os.path.exists(audio_path):
                            audio_data = get_audio_data(audio_path)
                            if audio_data:
                                st.markdown(f'<audio controls src="{audio_data}"></audio>', unsafe_allow_html=True)
                        else:
                            st.warning("Audio file not available")

                        # Display headlines
                        st.subheader("📰 Official Headlines")
                        for headline in data.get('headlines', []):
                            st.markdown(f"• {headline}")

                        # Display trends
                        st.subheader("🔍 Google Trends")
                        for trend in data.get('trends', []):
                            with st.expander(f"**{trend['title']}**", expanded=True):
                                if trend['related']:
                                    for related in trend['related']:
                                        st.markdown(f"• {related}")

                        # Display analysis
                        if data.get('analysis'):
                            st.subheader("🎭 Analysis")
                            st.markdown(data['analysis'])

    # Add navigation hint
    st.sidebar.markdown("← Return to analysis by clicking 'Trends to Stories' in the sidebar")

if __name__ == "__main__":
    main()
