import streamlit as st
import os
import json
from datetime import datetime
import glob

# Get the absolute path to the archive directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)  # Go up one level to project root
TEXT_ARCHIVE_DIR = os.path.join(BASE_DIR, "archive", "text_archive")

COUNTRIES = {
    "IL": "Israel",
    "LB": "Lebanon",
    "IR": "Iran"
}

def save_analysis_log(country_code, headlines, trends_data, analysis):
    """Save analysis log to country-specific directory"""
    try:
        # Create country-specific directory
        country_dir = os.path.join(TEXT_ARCHIVE_DIR, country_code)
        os.makedirs(country_dir, exist_ok=True)
        
        # Create log data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_data = {
            "timestamp": timestamp,
            "headlines": headlines,
            "trends": trends_data,
            "analysis": analysis
        }
        
        # Save to JSON file
        filename = f"{country_code}_{timestamp}_log.json"
        filepath = os.path.join(country_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        print(f"Log saved as: {filepath}")
        return True
    except Exception as e:
        print(f"Error saving log: {str(e)}")
        return False

def get_country_logs(country_code):
    """Get all log files for a specific country"""
    country_dir = os.path.join(TEXT_ARCHIVE_DIR, country_code)
    if not os.path.exists(country_dir):
        return []
    
    pattern = os.path.join(country_dir, f"{country_code}_*_log.json")
    files = glob.glob(pattern)
    
    # Sort files by date (newest first)
    files.sort(reverse=True)
    
    return files

def format_trends_data(trends_data):
    """Format trends data for display"""
    formatted = []
    for i, trend in enumerate(trends_data, 1):
        trend_text = [f"{i}. {trend['title']}"]
        if trend['related']:
            trend_text.append("   Related Searches:")
            for related in trend['related']:
                trend_text.append(f"   - {related}")
        formatted.append("\n".join(trend_text))
    return "\n\n".join(formatted)

def main():
    st.set_page_config(
        page_title="Middle East Pulse - Text Archive",
        page_icon="📚",
        layout="wide"
    )

    st.title("📚 Middle East Pulse: Text Archive")
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

    # Get log files for selected country
    log_files = get_country_logs(country)

    if log_files:
        st.subheader("📝 Historical Records")
        
        # Display each log file
        for log_path in log_files:
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
                
                # Extract date from timestamp
                date_str = log_data['timestamp'].split('_')[0]
                date = datetime.strptime(date_str, "%Y%m%d").strftime("%B %d, %Y")
                
                with st.expander(f"**{date}**", expanded=True):
                    # Display headlines
                    st.markdown("#### 📰 Headlines")
                    for i, headline in enumerate(log_data['headlines'], 1):
                        st.markdown(f"{i}. {headline}")
                    
                    # Display trends
                    st.markdown("#### 🔍 Trending Searches")
                    formatted_trends = format_trends_data(log_data['trends'])
                    st.text(formatted_trends)
                    
                    # Display analysis
                    st.markdown("#### 🎭 Analysis")
                    st.markdown(log_data['analysis'])
                    
                    # Show filename as caption
                    st.caption(os.path.basename(log_path))
            
            except Exception as e:
                st.error(f"Error loading log file {os.path.basename(log_path)}: {str(e)}")
    else:
        st.info(f"No historical records found for {COUNTRIES[country]}")

if __name__ == "__main__":
    main()
