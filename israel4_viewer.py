import streamlit as st
import json
import os
from datetime import datetime
from cloud_storage import CloudStorage

# Initialize storage variable
storage = None

def initialize_storage():
    """Initialize cloud storage with error handling"""
    global storage
    try:
        # Check if storage client exists in session state
        if 'storage_client' not in st.session_state:
            raise ValueError("Storage client not found in session state. Please ensure streamlit_hebrew.py is the entry point.")
        
        # Create CloudStorage instance using existing client
        storage = CloudStorage()
        
    except Exception as e:
        import traceback
        error_details = f"""
        Error initializing storage. Please check:
        1. The app is launched through streamlit_hebrew.py
        2. Storage client is properly initialized in session state
        
        Error: {str(e)}
        
        Stack trace:
        {traceback.format_exc()}
        """
        st.error("Failed to initialize storage")
        st.code(error_details, language="text")
        raise e

def load_analysis_by_date(date_str):
    """Load analysis JSON for a specific date"""
    return storage.load_analysis(date_str)

def get_available_dates():
    """Get list of dates with available analyses"""
    return storage.get_available_dates()

def get_audio_url(timestamp):
    """Get signed URL for audio file"""
    return storage.get_audio_url(timestamp)

def main(config_set=False):
    """
    Main function to display the viewer
    Args:
        config_set: Boolean indicating if page config has already been set
    """
    if not config_set:
        st.set_page_config(
            page_title="Israel Trends Analysis",
            page_icon="🇮🇱",
            layout="wide",
            initial_sidebar_state="expanded"
        )

    # Add sidebar content
    with st.sidebar:
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

    # Initialize storage
    initialize_storage()
    
    # Get available dates
    dates = get_available_dates()

    if not dates:
        st.info("No archived analyses found")
        return

    # Date selector
    selected_date = st.selectbox(
        "בחר תאריך:",  # Choose date in Hebrew
        dates,
        format_func=lambda x: x.strftime('%A, %d %B %Y'),  # e.g., "Sunday, 26 January 2025"
        index=0  # Default to most recent
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
                        st.markdown(f"""<div dir="rtl" style="text-align: right;">• {headline}</div>""", unsafe_allow_html=True)

                with trends_col:
                    st.header("Popular Searches")
                    for trend in analysis_data['trends']:
                        with st.expander(f"""<div dir="rtl" style="text-align: right;">**{trend['title']}**</div>""", expanded=True):
                            if trend['related']:
                                st.markdown("""<div dir="rtl" style="text-align: right;">Related searches:</div>""", unsafe_allow_html=True)
                                for related in trend['related']:
                                    st.markdown(f"""<div dir="rtl" style="text-align: right;">• {related}</div>""", unsafe_allow_html=True)

            with tab2:
                st.header("Philosophical Analysis")
                st.markdown(f"""<div dir="rtl" style="text-align: right;">{analysis_data['analysis']}</div>""", unsafe_allow_html=True)

            with tab3:
                st.header("Audio Version")
                audio_url = get_audio_url(analysis_data['timestamp'])
                if audio_url:
                    st.audio(audio_url)
                    st.markdown("*Listen to the analysis in Hebrew*")
                    st.markdown(f"[Download Audio]({audio_url})")
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
