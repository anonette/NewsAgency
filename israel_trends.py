from pytrends.request import TrendReq
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
import random

# Load environment variables
load_dotenv()

# Initialize clients
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))

# Suppress pandas warnings
warnings.filterwarnings('ignore', category=FutureWarning)

# Country configuration
COUNTRY_CONFIG = {
    'code': 'IL',
    'name': 'israel',  # lowercase for pytrends
    'news_query': 'Israel OR Israeli',
    'lang_code': 'iw'  # Hebrew language code for Google Translate
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
            # Create country-specific directory in archive
            country_dir = os.path.join('archive', COUNTRY_CONFIG['code'])
            os.makedirs(country_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_file = os.path.join(country_dir, f"IL_{timestamp}_analysis.mp3")
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
    """Get current top headlines about Israel"""
    try:
        print("\nFetching current news...")
        # Try top headlines first for most recent news
        headlines = newsapi.get_top_headlines(
            q=COUNTRY_CONFIG['news_query'],
            language='en'
        )
        
        # Get unique headlines
        seen = set()
        unique_headlines = []
        
        # Process top headlines first
        for article in headlines.get('articles', []):
            title = article.get('title', '')
            if title and title not in seen and not any(source.lower() in title.lower() for source in NEWS_SOURCES):
                seen.add(title)
                unique_headlines.append(title)
                if len(unique_headlines) >= 5:
                    break
        
        # If we don't have enough headlines, try everything endpoint
        if len(unique_headlines) < 5:
            print("Getting more headlines from everything endpoint...")
            headlines = newsapi.get_everything(
                q=COUNTRY_CONFIG['news_query'],
                language='en',
                sort_by='publishedAt',  # Get most recent first
                page_size=20  # Limit to 20 results
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
        url = "http://suggestqueries.google.com/complete/search"
        params = {
            "client": "firefox",  # Use Firefox client for JSON response
            "q": keyword,
            "hl": "en"  # Language
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/94.0'
        }
        
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = json.loads(response.text)
            if len(data) > 1 and isinstance(data[1], list):
                return data[1][:5]  # Return top 5 suggestions
    except:
        pass
    return []

def find_surprising_trends(trends_data, headlines):
    """Select random surprising trends that contrast with headlines"""
    if not trends_data:
        return []
    
    # Get indices of all non-news trends
    valid_indices = []
    for i, trend in enumerate(trends_data):
        # Check if trend title appears in any headline
        is_news_related = any(trend['title'].lower() in headline.lower() or headline.lower() in trend['title'].lower() for headline in headlines)
        if not is_news_related:
            valid_indices.append(i)
    
    # Randomly select up to 5 indices
    if valid_indices:
        num_trends = min(5, len(valid_indices))
        return random.sample(valid_indices, num_trends)
    
    return list(range(min(5, len(trends_data))))  # Fallback to first 5 if no valid trends found

def generate_analysis(trends_data, headlines):
    """Generate analysis contrasting trends with news"""
    context = {
        'trends': [{'title': t['title'], 'related': t['related']} for t in trends_data],
        'headlines': headlines
    }

    prompt = f"""Analyze these search trends and headlines from {COUNTRY_CONFIG['name'].title()}, using the search patterns as a window into the collective psyche:

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
        print(f"GOOGLE TRENDS - ISRAEL")
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
        print(f"Source: trends.google.com/trends/trendingsearches/daily?geo={COUNTRY_CONFIG['code']}\n")

        # Initialize pytrends
        pytrends = TrendReq(hl='en-US', tz=210)
        
        # Get trending searches using country name
        trending_searches = pytrends.trending_searches(pn=COUNTRY_CONFIG['name'])
        all_trends_data = []
        
        if not trending_searches.empty:
            trend_number = 1
            for trend in trending_searches.values:
                keyword = trend[0]
                # Skip news sources
                if not is_news_source(keyword):
                    title = translate_text(keyword)
                    
                    # Get related searches
                    suggestions = get_suggestions(keyword)
                    translated_suggestions = []
                    if suggestions:
                        for suggestion in suggestions:
                            if suggestion != keyword:  # Don't show the same term
                                suggestion_text = translate_text(suggestion)
                                translated_suggestions.append(suggestion_text)
                    
                    all_trends_data.append({
                        'title': title,
                        'related': translated_suggestions
                    })
                    
                    if len(all_trends_data) >= 20:  # Get top 20 trends for analysis
                        break
                    
                    time.sleep(0.5)  # Avoid rate limiting

            if all_trends_data and headlines:
                # Find surprising trends
                surprising_indices = find_surprising_trends(all_trends_data, headlines)
                trends_data = [all_trends_data[i] for i in surprising_indices]
                
                # Print selected trends
                for i, trend in enumerate(trends_data, 1):
                    print(f"\n{i}. {trend['title']}")
                    if trend['related']:
                        print("   Related Searches:")
                        for related in trend['related']:
                            print(f"   - {related}")
                
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
            elif all_trends_data:
                print("\nNo news headlines found to compare with trends")
            else:
                print("No trending searches found")
                print("\nView live trends at:")
                print(f"trends.google.com/trends/trendingsearches/daily?geo={COUNTRY_CONFIG['code']}")

        return None

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        print("\nView live trends at:")
        print(f"trends.google.com/trends/trendingsearches/daily?geo={COUNTRY_CONFIG['code']}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print("\nUsage: python israel_trends.py")
        print("\nShows trending searches with breakdowns in Israel")
        print("Live trends: trends.google.com/trends/trendingsearches/daily?geo=IL")
    else:
        fetch_trends()
