import streamlit as st
import os
import json
from datetime import datetime
import requests

COUNTRIES = {
    "IL": "Israel",
    "LB": "Lebanon",
    "IR": "Iran",
    "CZ": "Czech Republic"
}

# Main archive folder
ARCHIVE_URL = "https://drive.google.com/drive/folders/17xIMeFyuv1thVSH1vpvto5smTXihx8Hy"

def main():
    st.set_page_config(
        page_title="Middle East Pulse - Archive",
        page_icon="🌍",
        layout="wide"
    )

    st.title("🌍 Middle East Pulse Archive")
    st.markdown("### Historical Analysis Archive")

    # Create columns for each country
    cols = st.columns(len(COUNTRIES))
    
    for i, (code, name) in enumerate(COUNTRIES.items()):
        with cols[i]:
            st.subheader(f"{name} 🎙️")
            st.markdown(f"Latest analyses for {name}:")
            
            # Display sample dates (these will be visible in the archive folder)
            st.markdown("• October 28, 2024")
            st.markdown("• October 27, 2024")
            st.markdown("• October 26, 2024")
            
            st.markdown("---")

    # Add main archive link with clear instructions
    st.markdown("---")
    st.markdown("""
    ### 📚 Access the Complete Archive
    
    All audio analyses are available in our Google Drive archive:
    
    1. [Open Archive Folder]({})
    2. Click on a country folder (IL, LB, IR, CZ)
    3. Select an audio file to listen or download
    
    Each audio file contains a comprehensive analysis of the gap between official headlines and public search interests for that date.
    """.format(ARCHIVE_URL))

    # Add navigation back to main page
    st.sidebar.markdown("""
    [← Back to Analysis](/)
    """)

    # Add helpful note about file naming
    st.sidebar.markdown("""
    ### 📝 File Naming Format
    
    Audio files follow this format:
    `XX_YYYYMMDD_HHMMSS_analysis.mp3`
    
    Where:
    - XX: Country code (IL, LB, IR, CZ)
    - YYYYMMDD: Date
    - HHMMSS: Time
    """)

if __name__ == "__main__":
    main()
