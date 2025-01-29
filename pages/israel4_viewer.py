import streamlit as st
import json
import os
from datetime import datetime
import glob

def load_analysis_by_date(date_str):
    """Load analysis JSON for a specific date"""
    try:
        # Search for files matching the date pattern
        archive_path = os.path.join('archive', 'text_archive', 'IL2')
        pattern = os.path.join(archive_path, f"IL2_{date_str}*_log.json")
        matching_files = glob.glob(pattern)
        
        if not matching_files:
            return None
            
        # Load the first matching file
        with open(matching_files[0], 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading analysis: {str(e)}")
        return None

def get_available_dates():
    """Get list of dates with available analyses"""
    try:
        archive_path = os.path.join('archive', 'text_archive', 'IL2')
        if not os.path.exists(archive_path):
            return []
            
        # Get all JSON files and extract dates
        files = glob.glob(os.path.join(archive_path, "IL2_*_log.json"))
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

def get_audio_file(timestamp):
    """Get audio file path for a specific analysis"""
    audio_path = os.path.join('archive', 'IL2', f"IL2_{timestamp}_analysis.mp3")
    return audio_path if os.path.exists(audio_path) else None

def main():
    # Page config
    st.set_page_config(
        page_title="Israel Trends Analysis",
        page_icon="🇮🇱",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Add dark mode toggle in sidebar
    with st.sidebar:
        theme = "dark" if st.toggle("Dark Mode", value=False) else "light"
        st.markdown(f"""
        <style>
            .stApp {{
                background-color: {'#0e1117' if theme == 'dark' else '#ffffff'};
                color: {'#fafafa' if theme == 'dark' else '#000000'};
            }}
            .stMarkdown {{
                color: {'#fafafa' if theme == 'dark' else '#000000'};
            }}
            .stMetric {{
                background-color: {'#1e2227' if theme == 'dark' else '#f0f2f6'};
            }}
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("""
        ### About
        This viewer displays Žižek-style analyses of Israeli trends, comparing official headlines with popular searches to reveal societal patterns.
        
        ### Features
        - 📊 Trend Analysis
        - 🎵 Audio Narration
        - 📱 Sharing Options
        - 📅 Historical Archive
        """)

    st.title("🇮🇱 Israel Trends Analysis")
    st.markdown("### Browse Žižek-style analyses of Israeli trends")

    # Get available dates
    dates = get_available_dates()

    if not dates:
        st.info("No archived analyses found")
        return

    # Create columns for search and filter
    search_col, date_col = st.columns([1, 1])
    
    with search_col:
        # Add date search
        search_date = st.date_input(
            "Search specific date:",
            value=None,
            min_value=min(dates).date(),
            max_value=max(dates).date()
        )
        
        if search_date:
            # Find closest available date
            closest_date = min(dates, key=lambda x: abs(x.date() - search_date))
            selected_date = closest_date
        else:
            selected_date = dates[0]  # Default to most recent

    with date_col:
        # Date selector with filtered dates
        selected_date = st.selectbox(
            "Or choose from available dates:",
            dates,
            format_func=lambda x: x.strftime('%Y-%m-%d (%A)'),
            index=dates.index(selected_date)
        )

    if selected_date:
        date_str = selected_date.strftime('%Y%m%d')
        analysis_data = load_analysis_by_date(date_str)

        if analysis_data:
            # Display metadata with improved styling
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                st.metric("📰 Headlines", len(analysis_data['headlines']), 
                         help="Number of official news headlines analyzed")
            with col2:
                st.metric("🔍 Trends", len(analysis_data['trends']),
                         help="Number of trending search terms analyzed")
            with col3:
                analysis_time = datetime.strptime(analysis_data['timestamp'], '%Y%m%d_%H%M%S')
                st.markdown(f"""
                <div style='text-align: right; padding: 1rem;'>
                    <em>Analysis generated on {analysis_time.strftime('%A, %B %d at %H:%M:%S')}</em>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("---")
            
            # Create tabs for different views
            tab1, tab2, tab3, tab4 = st.tabs(["📰 News vs. Trends", "🎭 Analysis", "🔊 Audio", "📤 Share"])
            
            with tab1:
                # Display headlines and trends in columns
                news_col, trends_col = st.columns(2)

                with news_col:
                    st.header("Official Headlines")
                    for headline in analysis_data['headlines']:
                        st.markdown(f"• {headline}")

                with trends_col:
                    st.header("Popular Searches")
                    for trend in analysis_data['trends']:
                        with st.expander(f"**{trend['title']}**", expanded=True):
                            if trend['related']:
                                st.markdown("Related searches:")
                                for related in trend['related']:
                                    st.markdown(f"• {related}")

            with tab2:
                st.header("Philosophical Analysis")
                st.markdown(analysis_data['analysis'])

            with tab3:
                st.header("Audio Version")
                audio_file = get_audio_file(analysis_data['timestamp'])
                if audio_file:
                    st.audio(audio_file)
                    st.markdown("*Listen to the analysis in Hebrew*")
                    # Add download button
                    with open(audio_file, 'rb') as f:
                        st.download_button(
                            label="Download Audio",
                            data=f,
                            file_name=f"israel_trends_{analysis_data['timestamp']}.mp3",
                            mime="audio/mp3"
                        )
                else:
                    st.info("Audio analysis not available for this date")
                    
            with tab4:
                st.header("Share Analysis")
                # Generate shareable text
                share_text = f"""Israel Trends Analysis for {selected_date.strftime('%Y-%m-%d')}

Headlines:
{chr(10).join('• ' + h for h in analysis_data['headlines'])}

Top Trends:
{chr(10).join('• ' + t['title'] for t in analysis_data['trends'])}

Analysis:
{analysis_data['analysis']}
"""
                # Add copy button
                st.code(share_text, language=None)
                st.button("Copy to Clipboard", key="copy_btn", 
                         help="Click to copy the full analysis to your clipboard")

            # Add explanation of the analysis style
            with st.expander("ℹ️ About this Analysis"):
                st.markdown("""
                This analysis is generated in the style of Slavoj Žižek, examining the absurdity of capitalism 
                in Israel 2025 through Google search patterns. It reveals:
                
                - Contradictions in the free market during emergency situations
                - Social mechanisms during crisis
                - How capitalism functions in extreme conditions
                - The gap between official proclamations and daily reality
                
                The analysis combines social critique with dark humor, highlighting the irony between 
                national theater and real life through elegant sarcasm.
                """)
        else:
            st.error("Failed to load analysis data")

if __name__ == "__main__":
    main()
