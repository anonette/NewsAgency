import streamlit as st
import json
import os
from datetime import datetime
import glob

def load_analysis_by_date(country_code, date_str):
    """Load analysis JSON for a specific date"""
    try:
        # Search for files matching the date pattern
        archive_path = os.path.join('archive', 'text_archive', country_code)
        pattern = os.path.join(archive_path, f"{country_code}_{date_str}*_log.json")
        matching_files = glob.glob(pattern)
        
        if not matching_files:
            return None
            
        # Load the first matching file
        with open(matching_files[0], 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading analysis: {str(e)}")
        return None

def get_available_dates(country_code):
    """Get list of dates with available analyses"""
    try:
        archive_path = os.path.join('archive', 'text_archive', country_code)
        if not os.path.exists(archive_path):
            return []
            
        # Get all JSON files and extract dates
        files = glob.glob(os.path.join(archive_path, f"{country_code}_*_log.json"))
        dates = []
        for file in files:
            # Extract date from filename (format: IL2_20250126_152118_log.json)
            date_str = os.path.basename(file).split('_')[1]
            try:
                date = datetime.strptime(date_str, '%Y%m%d')
                dates.append(date)
            except ValueError:
                continue
        
        # Sort dates in reverse chronological order
        return sorted(set(dates), reverse=True)
    except Exception as e:
        st.error(f"Error getting dates: {str(e)}")
        return []

def get_audio_file(country_code, timestamp):
    """Get audio file path for a specific analysis"""
    audio_path = os.path.join('archive', country_code, f"{country_code}_{timestamp}_analysis.mp3")
    return audio_path if os.path.exists(audio_path) else None

def main():
    st.title("📚 Historical Analysis Archive")
    st.markdown("### Browse past analyses and insights")

    # Country selector with flags
    country_options = {
        "Israel": ("IL2", "🇮🇱"),
        "Lebanon": ("LB", "🇱🇧"),
        "Iran": ("IR", "🇮🇷"),
        "Czech Republic": ("CZ", "🇨🇿")
    }

    # Create columns for filters
    col1, col2 = st.columns([1, 2])

    with col1:
        country = st.selectbox(
            "Select Country:",
            list(country_options.keys()),
            format_func=lambda x: f"{country_options[x][1]} {x}"
        )

    # Get country code and available dates
    country_code, flag = country_options[country]
    dates = get_available_dates(country_code)

    if not dates:
        st.info(f"No archived analyses found for {country}")
        return

    with col2:
        selected_date = st.selectbox(
            "Select Date:",
            dates,
            format_func=lambda x: x.strftime('%Y-%m-%d')
        )

    if selected_date:
        date_str = selected_date.strftime('%Y%m%d')
        analysis_data = load_analysis_by_date(country_code, date_str)

        if analysis_data:
            # Display headlines and trends in columns
            news_col, trends_col = st.columns(2)

            with news_col:
                st.header("📰 Headlines")
                for headline in analysis_data['headlines']:
                    st.markdown(f"• {headline}")

            with trends_col:
                st.header("🔍 Trending Searches")
                for trend in analysis_data['trends']:
                    with st.expander(f"**{trend['title']}**", expanded=True):
                        if trend['related']:
                            st.markdown("Related searches:")
                            for related in trend['related']:
                                st.markdown(f"• {related}")

            # Display analysis and audio
            st.markdown("---")
            st.header("🎭 Analysis")
            st.markdown(analysis_data['analysis'])

            # Audio player
            audio_file = get_audio_file(country_code, analysis_data['timestamp'])
            if audio_file:
                st.markdown("---")
                st.header("🔊 Audio Analysis")
                st.audio(audio_file)
            else:
                st.info("Audio analysis not available for this date")
        else:
            st.error("Failed to load analysis data")

if __name__ == "__main__":
    main()
