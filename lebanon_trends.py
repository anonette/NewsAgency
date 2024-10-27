import sys
import time
from datetime import datetime, timedelta, timezone
from deep_translator import GoogleTranslator
import warnings
import requests
import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from newsapi import NewsApiClient
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

# Load environment variables
load_dotenv()

# Initialize clients
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))

# Suppress pandas warnings
warnings.filterwarnings('ignore', category=FutureWarning)

# Country configuration
COUNTRY_CONFIG = {
    'code': 'LB',
    'name': 'Lebanon',
    'news_query': 'Lebanon OR Lebanese OR Beirut OR Hezbollah',  # Added more terms to get more results
    'lang_code': 'ar'  # Arabic language code for Google Translate
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
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_file = f"LE_{timestamp}_analysis.mp3"
            with open(audio_file, "wb") as f:
                f.write(response.content)
            print(f"Audio saved as: {audio_file}")
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

def get_current_news():
    """Get current top headlines about Lebanon"""
    try:
        print("\nFetching current news...")
        # Get date range for last 7 days to ensure we get enough results
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # Search for country-related news
        headlines = newsapi.get_everything(
            q=COUNTRY_CONFIG['news_query'],
            language='en',
            sort_by='relevancy',
            from_param=start_date.strftime('%Y-%m-%d'),
            to=end_date.strftime('%Y-%m-%d')
        )
        
        # Get unique headlines
        seen = set()
        unique_headlines = []
        for article in headlines.get('articles', []):
            title = article.get('title', '')
            if title and title not in seen and not any(source.lower() in title.lower() for source in NEWS_SOURCES):
                seen.add(title)
                unique_headlines.append(title)
                if len(unique_headlines) >= 5:
                    break
        
        if not unique_headlines:
            print("No news found in everything, trying top headlines...")
            headlines = newsapi.get_top_headlines(
                q=COUNTRY_CONFIG['news_query'],
                language='en'
            )
            
            for article in headlines.get('articles', []):
                title = article.get('title', '')
                if title and title not in seen and not any(source.lower() in title.lower() for source in NEWS_SOURCES):
                    seen.add(title)
                    unique_headlines.append(title)
                    if len(unique_headlines) >= 5:
                        break
        
        print(f"Found {len(unique_headlines)} unique headlines")
        return unique_headlines
    except Exception as e:
        print(f"Error fetching news: {str(e)}")
        return []

def translate_text(text):
    """Translate text to English if it's not in English"""
    try:
        # Skip translation if the text is mostly ASCII (likely English)
        if all(ord(char) < 128 for char in text.replace(' ', '')):
            return text
        
        translator = GoogleTranslator(source='auto', target='en')
        translated = translator.translate(text)
        return f"{text} ({translated})" if translated != text else text
    except:
        return text

def get_suggestions(keyword):
    """Get Google's search suggestions for a keyword"""
    try:
        # Try Arabic suggestions first
        url = "http://suggestqueries.google.com/complete/search"
        params = {
            "client": "firefox",
            "q": keyword,
            "hl": COUNTRY_CONFIG['lang_code']
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/94.0'
        }
        
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = json.loads(response.text)
            if len(data) > 1 and isinstance(data[1], list):
                suggestions = data[1][:5]
                if suggestions:
                    return suggestions
        
        # Fallback to English suggestions
        params['hl'] = 'en'
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = json.loads(response.text)
            if len(data) > 1 and isinstance(data[1], list):
                return data[1][:5]
    except:
        pass
    return []

def get_trending_searches():
    """Get trending searches from Google Trends RSS feed"""
    try:
        print("Fetching trends from RSS feed...")
        url = f"https://trends.google.com/trending/rss?geo={COUNTRY_CONFIG['code']}"
        print(f"URL: {url}")
        response = requests.get(url)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            trends = []
            cutoff_time = datetime.now(timezone.utc) - timedelta(days=1)
            
            for item in root.findall('.//item'):
                title = item.find('title').text
                if title:
                    trends.append(title)
            
            print(f"Found {len(trends)} trends")
            return trends[:5]  # Return top 5 trends
        return []
    except Exception as e:
        print(f"Error fetching trends: {str(e)}")
        return []

def generate_analysis(trends_data, headlines):
    """Generate analysis contrasting trends with news"""
    context = {
        'trends': [{'title': t['title'], 'related': t['related']} for t in trends_data],
        'headlines': headlines
    }

    prompt = f"""Analyze these search trends and headlines from {COUNTRY_CONFIG['name']}, using the search patterns as a window into the collective psyche:

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
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating analysis: {str(e)}"

def fetch_trends():
    """Fetch trends and news, then generate analysis"""
    try:
        print(f"\n{'='*50}")
        print(f"GOOGLE TRENDS - LEBANON")
        print(f"{'='*50}\n")

        # Get current news first
        headlines = get_current_news()
        if headlines:
            print("\n📰 CURRENT NEWS")
            print("-" * 50)
            for i, headline in enumerate(headlines, 1):
                print(f"{i}. {headline}")
            print()

        print("🔥 TRENDING SEARCHES WITH BREAKDOWNS")
        print("-" * 50)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Last updated: {current_time}")
        print(f"Source: trends.google.com/trending/rss?geo={COUNTRY_CONFIG['code']}\n")

        # Get trending searches from RSS feed
        trending_searches = get_trending_searches()
        trends_data = []
        
        if trending_searches:
            trend_number = 1
            for keyword in trending_searches:
                # Skip news sources
                if not is_news_source(keyword):
                    title = translate_text(keyword)
                    print(f"\n{trend_number}. {title}")
                    
                    # Get and show related searches from suggestions
                    suggestions = get_suggestions(keyword)
                    if suggestions:
                        print("   Related Searches:")
                        translated_suggestions = []
                        for suggestion in suggestions:
                            if suggestion != keyword:  # Don't show the same term
                                suggestion_text = translate_text(suggestion)
                                print(f"   - {suggestion_text}")
                                translated_suggestions.append(suggestion_text)
                        
                        trends_data.append({
                            'title': title,
                            'related': translated_suggestions
                        })
                    
                    trend_number += 1
                    if trend_number > 5:  # Show top 5 non-news-source trends
                        break
                    
                    time.sleep(0.5)  # Avoid rate limiting

            if trends_data and headlines:
                # Generate analysis comparing trends with news
                print("\n✒️ ANALYSIS")
                print("-" * 50)
                analysis = generate_analysis(trends_data, headlines)
                print(analysis)
                
                # Generate audio version
                print("\n🔊 Generating audio version...")
                generate_audio(analysis)
                
                return {
                    'headlines': headlines,
                    'trends_data': trends_data,
                    'analysis': analysis
                }
            elif trends_data:
                print("\nNo news headlines found to compare with trends")
            else:
                print("No trending searches found")
                print("\nView live trends at:")
                print(f"trends.google.com/trending/rss?geo={COUNTRY_CONFIG['code']}")

        return None

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        print("\nView live trends at:")
        print(f"trends.google.com/trending/rss?geo={COUNTRY_CONFIG['code']}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print("\nUsage: python lebanon_trends.py")
        print("\nShows trending searches with breakdowns in Lebanon")
        print("Live trends: trends.google.com/trending/rss?geo=LB")
    else:
        fetch_trends()
