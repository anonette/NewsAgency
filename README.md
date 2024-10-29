# Trends to Stories

A Streamlit application that analyzes search trends and news headlines across multiple countries, generating audio summaries of the findings.

## Quick Deploy to Streamlit Cloud

1. Fork this repository to your GitHub account

2. Go to [Streamlit Cloud](https://streamlit.io/cloud)

3. Click "New app" and select your forked repository

4. Configure the deployment:
   - Repository: Your forked repository
   - Branch: main
   - Main file path: streamlit_app.py

5. Add these secrets in Streamlit Cloud settings:
   ```
   OPENAI_API_KEY = "your-openai-api-key"
   NEWSAPI_KEY = "your-newsapi-key"
   ```

6. Click "Deploy"

## Local Development Setup

1. Clone the repository

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a .env file with your API keys:
   ```
   OPENAI_API_KEY=your-openai-api-key
   NEWSAPI_KEY=your-newsapi-key
   ```

4. Run the app:
   ```bash
   streamlit run streamlit_app.py
   ```

## Project Structure

- `streamlit_app.py`: Main Streamlit application
- `archive.py`: Archive page for audio files
- `*_trends.py`: Country-specific trend analysis modules
- `core_utils.py`: Shared utility functions
- `requirements.txt`: Project dependencies

## Features

- Real-time trend analysis for multiple countries
- Comparison of official headlines with public search interests
- AI-generated analysis of the gap between news and searches
- Audio summaries accessible via Google Drive
- Archive view of historical analyses

## Audio Files

Audio files are stored in a public Google Drive folder for easy access:
[Archive Folder](https://drive.google.com/drive/folders/17xIMeFyuv1thVSH1vpvto5smTXihx8Hy)

## Pages

1. Main Page (`/`):
   - Country selection
   - Real-time trend analysis
   - Comparison of headlines and searches
   - AI-generated insights

2. Archive Page (`/archive`):
   - Historical audio analyses
   - Organized by country and date
   - Direct access to audio files
