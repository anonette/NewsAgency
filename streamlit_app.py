import streamlit as st
from israel_trends import fetch_trends as fetch_israel_trends
from lebanon_trends import fetch_trends as fetch_lebanon_trends
from iran_trends import fetch_trends as fetch_iran_trends
import base64
import glob
import os

def get_latest_audio_file(country_prefix):
    """Get the most recent audio file for the given country prefix"""
    pattern = f"archive/{country_prefix}_*_analysis.mp3"
    files = glob.glob(pattern)
    if files:
        return max(files, key=os.path.getctime)
    return None

def get_audio_player_html(audio_path):
    """Generate HTML code for audio player"""
    audio_placeholder = st.empty()
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

def main():
    st.set_page_config(
        page_title="Trends to Stories",
        page_icon="📊",
        layout="wide"
    )

    # Header with Archive Link
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title("🔍 Official News vs. Real Searches")
        st.markdown("### Revealing the Gap Between Headlines and Reality")
    with col2:
        st.markdown("")  # Spacing
        st.markdown("")  # Spacing
        st.markdown("""
        <a href="http://localhost:8503" target="_blank" style="
            text-decoration: none;
            background-color: #f0f2f6;
            color: #262730;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            border: 1px solid #e0e2e6;
            font-weight: 500;
            display: inline-block;
            text-align: center;
        ">📚 View Archive</a>
        """, unsafe_allow_html=True)

    # Country selector with flags
    country_options = {
        "Israel": ("IL", "🇮🇱", fetch_israel_trends),
        "Lebanon": ("LE", "🇱🇧", fetch_lebanon_trends),
        "Iran": ("IR", "🇮🇷", fetch_iran_trends)
    }

    # Create two columns for layout
    col1, col2 = st.columns([2, 3])

    with col1:
        country = st.selectbox(
            "Choose a country to analyze:",
            list(country_options.keys()),
            format_func=lambda x: f"{country_options[x][1]} {x}"
        )

        # Get country code and fetch function
        country_code, flag, fetch_function = country_options[country]
        
        if st.button(f"Analyze {flag} {country}", use_container_width=True):
            with st.spinner(f"Analyzing {country}..."):
                # Run the analysis
                try:
                    results = fetch_function()
                    
                    if results and 'trends_data' in results:
                        st.session_state.results = results
                        st.session_state.current_country = country
                        st.session_state.current_flag = flag
                        st.session_state.current_code = country_code
                    else:
                        st.error(f"No data found for {country}")
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

    with col2:
        if 'results' in st.session_state and 'current_country' in st.session_state:
            results = st.session_state.results
            country = st.session_state.current_country
            flag = st.session_state.current_flag
            code = st.session_state.current_code
            
            # Create two columns for comparison
            news_col, trends_col = st.columns(2)
            
            with news_col:
                st.header("📰 Official Headlines")
                if 'headlines' in results and results['headlines']:
                    for headline in results['headlines']:
                        st.markdown(f"• {headline}")
                else:
                    st.info("No recent headlines found")
            
            with trends_col:
                st.header("🔍 What People Search For")
                for trend in results['trends_data']:
                    with st.expander(f"**{trend['title']}**", expanded=True):
                        if trend['related']:
                            st.markdown("Related searches:")
                            for related in trend['related']:
                                st.markdown(f"• {related}")
                        else:
                            st.info("No related searches found")
            
            # Show analysis if available
            if 'analysis' in results and results['analysis']:
                st.markdown("---")
                st.header("🎭 The Reality Behind the Headlines")
                st.markdown(results['analysis'])
                
                # Show audio player if file exists
                audio_file = get_latest_audio_file(code)
                if audio_file:
                    st.subheader("🔊 Listen to Analysis")
                    st.markdown("---")
                    audio_player = get_audio_player_html(audio_file)
                    st.markdown(audio_player, unsafe_allow_html=True)
                    st.caption(f"Audio file: {os.path.basename(audio_file)}")

if __name__ == "__main__":
    main()
