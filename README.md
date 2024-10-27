# Trends to Stories

A web application that analyzes the gap between official news narratives and what people actually care about, revealed through their search patterns. The app generates psychological insights from the contrast between headlines and search trends, presenting them in both text and audio formats.

## Features

- Fetches current news headlines about Israel
- Retrieves trending Google searches and related suggestions
- Generates insightful analysis using GPT-4
- Converts analysis to speech using ElevenLabs
- Presents everything in a clean web interface using Streamlit

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your_openai_key
NEWS_API_KEY=your_newsapi_key
ELEVENLABS_API_KEY=your_elevenlabs_key
```

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

The app will be available at http://localhost:8501

## How it Works

1. The app fetches current news headlines about Israel using the NewsAPI
2. It retrieves trending Google searches from Israel
3. For each trend, it gets related search suggestions
4. GPT-4 analyzes the contrast between official headlines and search trends
5. The analysis is converted to speech using ElevenLabs
6. Everything is presented in a web interface where you can:
   - View the official headlines
   - See what people are actually searching for
   - Read the psychological analysis
   - Listen to the analysis being read aloud

## Files

- `app.py`: Streamlit web interface
- `test_trends.py`: Core functionality for fetching and analyzing trends
- `requirements.txt`: Project dependencies
- `.env`: API keys and configuration
