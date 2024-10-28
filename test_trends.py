import sys
import time
from datetime import datetime, timedelta
from deep_translator import GoogleTranslator
import warnings
import requests
import json
import os
from openai import OpenAI
from dotenv import load_dotenv
import textwrap
from newsapi import NewsApiClient
import xml.etree.ElementTree as ET

# Load environment variables
load_dotenv()

# Initialize clients
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))

# Country configurations
COUNTRY_CONFIGS = {
    'IL': {
        'name': 'Israel',
        'news_query': 'Israel OR Israeli',
        'lang_code': 'iw'  # Hebrew language code for Google Translate
    },
    'LB': {
        'name': 'Lebanon',
        'news_query': 'Lebanon OR Lebanese',
        'lang_code': 'ar'  # Arabic language code for Google Translate
    }
}

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
        # ElevenLabs API endpoint
        url = "https://api.elevenlabs.io/v1/text-to-speech/TxGEqnHWrfWFTfGW9XjX"  # Josh voice ID
        
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
            # Save audio to file
            audio_file = "analysis.mp3"
            with open(audio_file, "wb") as f:
                f.write(response.content)
            return True
            
        else:
            print(f"Error: API request failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error with text-to-speech: {str(e)}")
        return False

def is_news_source(text):
    """Check if the term is a news source"""
    return any(source in text.lower() for source in NEWS_SOURCES)

def get_current_news(country_code):
    """Get current top headlines about the selected country"""
    try:
        config = COUNTRY_CONFIGS[country_code]
        
        # Get date range for last 24 hours
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        
        # Search for country-related news
        headlines = newsapi.get_everything(
            q=config['news_query'],
            language='en',
            sort_by='relevancy',
            from_param=start_date.strftime('%Y-%m-%d'),
            to=end_date.strftime('%Y-%m-%d')
        )
        
        # Get unique headlines
        seen = set()
        unique_headlines = []
        for article in headlines['articles']:
            title = article['title']
            if title and title not in seen and not any(source.lower() in title.lower() for source in NEWS_SOURCES):
                seen.add(title)
                unique_headlines.append(title)
                if len(unique_headlines) >= 5:
                    break
        
        return unique_headlines
    except Exception as e:
        print(f"Error fetching news: {str(e)}")
        return []

def clean_text(text):
    """Clean up text formatting"""
    paragraphs = text.replace('\r\n', '\n').replace('\r', '\n').split('\n\n')
    cleaned = []
    
    for para in paragraphs:
        # Join all lines and clean up spaces
        cleaned_para = ' '.join(para.split())
        if cleaned_para:
            cleaned.append(textwrap.fill(cleaned_para, width=100))
    
    return '\n\n'.join(cleaned)

def translate_text(text, country_code):
    """Translate text to English if it's not in English"""
    try:
        # Skip translation for Latin script text
        if all(ord(char) < 128 for char in text.replace(' ', '')):
            return text
            
        # Try translation from country's language to English
        config = COUNTRY_CONFIGS[country_code]
        translator = GoogleTranslator(source=config['lang_code'], target='en')
        try:
            result = translator.translate(text)
            if result and result != text:
                print(f"Translated: {text} -> {result}")
                return result
        except:
            # Fallback to auto-detect if specific language translation fails
            translator = GoogleTranslator(source='auto', target='en')
            result = translator.translate(text)
            print(f"Translated (auto): {text} -> {result}")
            return result
    except Exception as e:
        print(f"Translation error for '{text}': {str(e)}")
        return text

def get_suggestions(keyword, country_code):
    """Get Google's search suggestions for a keyword"""
    try:
        config = COUNTRY_CONFIGS[country_code]
        
        # Try getting suggestions in country's language
        url = "http://suggestqueries.google.com/complete/search"
        params = {
            "client": "firefox",
            "q": keyword,
            "hl": config['lang_code']
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/94.0'
        }
        
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = json.loads(response.text)
            if len(data) > 1 and isinstance(data[1], list):
                suggestions = data[1][:5]
                # Translate suggestions to English
                return [translate_text(s, country_code) for s in suggestions if s != keyword]
                
        return []
    except Exception as e:
        print(f"Error getting suggestions for '{keyword}': {str(e)}")
        return []

def generate_analysis(trends_data, headlines, country_code):
    """Generate analysis contrasting trends with news"""
    context = {
        'trends': [{'title': t['title'], 'related': t['related']} for t in trends_data],
        'headlines': headlines
    }

    config = COUNTRY_CONFIGS[country_code]
    prompt = f"""Analyze these search trends and headlines from {config['name']}, using the search patterns as a window into the collective psyche:

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

    try:
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
        return f"Error generating analysis: {str(e)}"

def get_trending_searches(country_code):
    """Get trending searches from Google Trends RSS feed"""
    try:
        url = f"https://trends.google.com/trending/rss?geo={country_code}"
        response = requests.get(url)
        if response.status_code == 200:
            # Parse XML
            root = ET.fromstring(response.content)
            # Find all item titles (trending searches)
            trends = []
            for item in root.findall('.//item/title'):
                if item.text:
                    trends.append(item.text)
            return trends[:5]  # Return top 5 trends
        return []
    except Exception as e:
        print(f"Error fetching trends: {str(e)}")
        return []

def fetch_trends(country_code):
    """Fetch trends and news, then generate analysis"""
    try:
        # Get current news
        headlines = get_current_news(country_code)
        
        # Get trending searches
        trending_searches = get_trending_searches(country_code)
        if trending_searches:
            trends_data = []
            processed_trends = set()
            
            for keyword in trending_searches:
                trend_english = translate_text(keyword, country_code)
                
                if not is_news_source(keyword) and trend_english.lower() not in processed_trends:
                    processed_trends.add(trend_english.lower())
                    suggestions = get_suggestions(keyword, country_code)
                    
                    trends_data.append({
                        'title': trend_english,
                        'related': suggestions
                    })
                    
                    time.sleep(0.5)
            
            if trends_data and headlines:
                # Generate analysis
                analysis = generate_analysis(trends_data, headlines, country_code)
                
                # Generate audio
                generate_audio(analysis)
                
                return {
                    'headlines': headlines,
                    'trends_data': trends_data,
                    'analysis': analysis
                }
            
        return None

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print("\nUsage: python test_trends.py")
        print("\nExposes the gap between official narratives and everyday reality")
    else:
        fetch_trends("IL")  # Default to Israel
