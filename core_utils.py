import os
import json
import requests
import warnings
import textwrap
from datetime import datetime, timedelta
from deep_translator import GoogleTranslator
from openai import OpenAI
from newsapi import NewsApiClient
from dotenv import load_dotenv
import xml.etree.ElementTree as ET

# Load environment variables
load_dotenv()

# Initialize clients
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))

# Suppress pandas warnings
warnings.filterwarnings('ignore', category=FutureWarning)

# News sources to filter out
NEWS_SOURCES = {
    'cnn', 'bbc', 'fox news', 'nyt', 'new york times',
    'reuters', 'associated press', 'ap news'
}

JOURNALIST_PERSONA = """You're a journalist with the biting wit of Christopher Hitchens, tasked with analyzing the collective psyche through search trends. Your unique talent lies in using these digital footprints—what people search for in private—to expose the raw, unfiltered reality beneath official narratives.

Your job is to decode these search patterns like a psychological X-ray, revealing the true preoccupations, fears, and absurdities that occupy people's minds while the state trumpets its grand narratives. Use dark humor and sharp insight to contrast the public face of events with the private thoughts revealed through search trends, showing how these digital confessions often tell a more honest story than any official report."""

def generate_audio(text):
    """Generate audio using ElevenLabs text-to-speech"""
    try:
        url = "https://api.elevenlabs.io/v1/text-to-speech/TxGEqnHWrfWFTfGW9XjX"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": os.getenv('ELEVENLABS_API_KEY')
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            audio_file = "analysis.mp3"
            with open(audio_file, "wb") as f:
                f.write(response.content)
            return True
            
        else:
            print(f"Error: ElevenLabs API request failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error with text-to-speech: {str(e)}")
        return False

def is_news_source(text):
    """Check if the term is a news source"""
    return any(source in text.lower() for source in NEWS_SOURCES)

def clean_text(text):
    """Clean up text formatting"""
    paragraphs = text.replace('\r\n', '\n').replace('\r', '\n').split('\n\n')
    cleaned = []
    
    for para in paragraphs:
        cleaned_para = ' '.join(para.split())
        if cleaned_para:
            cleaned.append(textwrap.fill(cleaned_para, width=100))
    
    return '\n\n'.join(cleaned)

def translate_text(text, lang_code):
    """Translate text to English if it's not in English"""
    try:
        if all(ord(char) < 128 for char in text.replace(' ', '')):
            return text
            
        translator = GoogleTranslator(source=lang_code, target='en')
        try:
            result = translator.translate(text)
            if result and result != text:
                return result
        except Exception as e:
            print(f"Translation error with specific language {lang_code}: {str(e)}")
            pass
            
        print(f"Attempting auto-detection translation for: {text}")
        translator = GoogleTranslator(source='auto', target='en')
        result = translator.translate(text)
        return result
    except Exception as e:
        print(f"Translation error for '{text}': {str(e)}")
        return text

def get_suggestions(keyword, lang_code):
    """Get Google's search suggestions for a keyword"""
    try:
        url = "http://suggestqueries.google.com/complete/search"
        params = {
            "client": "firefox",
            "q": keyword,
            "hl": lang_code
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/94.0'
        }
        
        print(f"Fetching suggestions for keyword: {keyword} with language: {lang_code}")
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = json.loads(response.text)
            if len(data) > 1 and isinstance(data[1], list):
                suggestions = data[1][:5]
                translated = [translate_text(s, lang_code) for s in suggestions if s != keyword]
                print(f"Found {len(translated)} suggestions for {keyword}")
                return translated
                
        print(f"No suggestions found for {keyword}")
        return []
    except Exception as e:
        print(f"Error getting suggestions for '{keyword}': {str(e)}")
        return []

def get_trending_searches(country_code):
    """Get trending searches from Google Trends RSS feed"""
    try:
        url = f"https://trends.google.com/trending/rss?geo={country_code}"
        print(f"Fetching trends for country code: {country_code}")
        response = requests.get(url)
        print(f"Trends API response status: {response.status_code}")
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            trends = []
            for item in root.findall('.//item/title'):
                if item.text:
                    trends.append(item.text)
            print(f"Found {len(trends)} trends for {country_code}")
            return trends[:5]
            
        print(f"No trends found for {country_code}")
        return []
    except Exception as e:
        print(f"Error fetching trends for {country_code}: {str(e)}")
        return []

def generate_analysis(trends_data, headlines, country_name):
    """Generate analysis contrasting trends with news"""
    try:
        context = {
            'trends': [{'title': t['title'], 'related': t['related']} for t in trends_data],
            'headlines': headlines
        }

        prompt = f"""Analyze these search trends and headlines from {country_name}, using the search patterns as a window into the collective psyche:

Official Headlines:
{json.dumps(context['headlines'], indent=2)}

What People Secretly Search For:
{json.dumps(context['trends'], indent=2)}

Write a brief, biting analysis (2 paragraphs) that:
1. Uses these search trends as psychological evidence to expose what people really think and feel beneath the official narrative
2. Interprets the search patterns as revealing unconscious truths, fears, and preoccupations that the news won't acknowledge
3. Shows how these private digital confessions tell a more honest story about daily life than public statements
4. Employs dark humor to highlight the gap between the state's grand narrative and the raw psychological reality revealed in search trends

Keep it sharp and psychologically insightful, treating the search trends as a collective Rorschach test that reveals uncomfortable truths. Each paragraph should be a single continuous line."""

        print(f"Generating analysis for {country_name}")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": JOURNALIST_PERSONA},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=500
        )
        return clean_text(response.choices[0].message.content)
    except Exception as e:
        print(f"Error generating analysis: {str(e)}")
        return f"Error generating analysis: {str(e)}"
