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
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
import random
import tempfile
import shutil
from urllib.parse import urlencode

# Load environment variables
load_dotenv()

# Initialize clients
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Suppress warnings
warnings.filterwarnings('ignore', category=FutureWarning)

# Country configuration
COUNTRY_CONFIG = {
    'code': 'IL',
    'name': 'israel',  # lowercase for trends
    'news_query': 'Israel OR Israeli',
    'lang_code': 'he'  # Hebrew language code for NewsData.io
}

# News sources to filter out
NEWS_SOURCES = {
    'cnn', 'bbc', 'fox news', 'nyt', 'new york times',
    'reuters', 'associated press', 'ap news'
}

JOURNALIST_PERSONA = """You're a journalist with the biting wit of Christopher Hitchens, tasked with analyzing the collective psyche through search trends. Your unique talent lies in using these digital footprints—what people search for in private—to expose the raw, unfiltered reality beneath official narratives.

Your job is to decode these search patterns like a psychological X-ray, revealing the true preoccupations, fears, and absurdities that occupy people's minds while the state trumpets its grand narratives. Use dark humor and sharp insight to contrast the public face of events with the private thoughts revealed through search trends, showing how these digital confessions often tell a more honest story than any official report."""

def ensure_directory_exists(directory):
    """Ensure directory exists, create if it doesn't"""
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory {directory}: {str(e)}")
        return False

def save_analysis_log(headlines, trends_data, analysis, timestamp):
    """Save analysis log to text archive using atomic write"""
    temp_file = None
    try:
        # Ensure directory exists
        archive_dir = os.path.join('archive', 'text_archive', COUNTRY_CONFIG['code'])
        if not ensure_directory_exists(archive_dir):
            print("Failed to create archive directory")
            return False
            
        # Prepare log data
        log_data = {
            'timestamp': timestamp,
            'country': COUNTRY_CONFIG['name'],
            'headlines': headlines,
            'trends': trends_data,
            'analysis': analysis
        }
        
        # Create final filename
        final_path = os.path.join(archive_dir, f"{COUNTRY_CONFIG['code']}_{timestamp}_log.json")
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
        
        try:
            # Write to temporary file
            json.dump(log_data, temp_file, ensure_ascii=False, indent=2)
            temp_file.flush()
            os.fsync(temp_file.fileno())
            
            # Close the file handle explicitly
            temp_file.close()
            
            # Move temporary file to final location
            shutil.move(temp_file.name, final_path)
            
            print(f"Analysis log saved as: {final_path}")
            return True
            
        except Exception as e:
            print(f"Error writing to temporary file: {str(e)}")
            return False
            
    except Exception as e:
        print(f"Error saving analysis log: {str(e)}")
        return False
        
    finally:
        # Clean up temporary file if it exists and hasn't been moved
        if temp_file is not None:
            try:
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
            except Exception as e:
                print(f"Error cleaning up temporary file: {str(e)}")

def generate_audio(text, timestamp):
    """Generate audio using ElevenLabs text-to-speech"""
    temp_file = None
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
            if not ensure_directory_exists(country_dir):
                print("Failed to create country directory for audio")
                return False
            
            # Use the same timestamp as JSON file
            audio_file = os.path.join(country_dir, f"{COUNTRY_CONFIG['code']}_{timestamp}_analysis.mp3")
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, mode='wb')
            
            try:
                # Write to temporary file
                temp_file.write(response.content)
                temp_file.flush()
                os.fsync(temp_file.fileno())
                
                # Close the file handle explicitly
                temp_file.close()
                
                # Move temporary file to final location
                shutil.move(temp_file.name, audio_file)
                
                print(f"Audio saved as: {audio_file}")
                return True
                
            except Exception as e:
                print(f"Error writing audio to temporary file: {str(e)}")
                return False
                
        else:
            print(f"Error: API request failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error with text-to-speech: {str(e)}")
        return False
        
    finally:
        # Clean up temporary file if it exists and hasn't been moved
        if temp_file is not None:
            try:
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
            except Exception as e:
                print(f"Error cleaning up temporary file: {str(e)}")

def is_news_source(text):
    """Check if the term is a news source"""
    return any(source.lower() in text.lower() for source in NEWS_SOURCES)

def translate_text(text, from_lang='auto'):
    """Translate text to English if it's not in English"""
    try:
        # Skip translation if the text is mostly ASCII (likely English)
        if all(ord(char) < 128 for char in text.replace(' ', '')):
            return text
        
        # Use 'iw' for Hebrew instead of 'he'
        if from_lang == 'he':
            from_lang = 'iw'
        
        translator = GoogleTranslator(source=from_lang, target='en')
        translated = translator.translate(text)
        return f"{text} ({translated})" if translated != text else text
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return text

def get_current_news():
    """Get current news from Israeli sources using NewsData.io API"""
    try:
        print("\nFetching current news...")
        
        # NewsData.io API endpoint and parameters
        base_url = "https://newsdata.io/api/1/news"
        params = {
            'apikey': os.getenv('NEWSDATA_API_KEY'),
            'country': 'il',  # Israel (lowercase)
            'language': 'he',  # Hebrew
            'category': 'top'  # Top news only
        }
        
        # Build URL with properly encoded parameters
        url = f"{base_url}?{urlencode(params)}"
        
        # Request headers
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print("Fetching Israeli news from NewsData.io...")
        print(f"Request URL: {url}")
        
        # Make request with extended timeout
        response = requests.get(url, headers=headers, timeout=30)
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        
        try:
            data = response.json()
            print(f"Raw response: {json.dumps(data, indent=2)}")
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON response: {str(e)}")
            print(f"Raw response text: {response.text}")
            data = {}
        
        # Process articles
        seen = set()
        unique_headlines = []
        
        if response.status_code == 200 and data.get('status') == 'success':
            for article in data.get('results', []):
                title = article.get('title', '')
                if title and title not in seen and not is_news_source(title):
                    # Translate Hebrew headlines to English using 'iw' for Hebrew
                    translated_title = translate_text(title, from_lang='iw')
                    seen.add(title)
                    unique_headlines.append(translated_title)
                    if len(unique_headlines) >= 5:
                        break
        else:
            print(f"API request failed or returned no data. Status: {response.status_code}")
            if data:
                print(f"API response message: {data.get('message', 'No message provided')}")
        
        print(f"\nFound {len(unique_headlines)} unique headlines")
        if unique_headlines:
            print("Headlines found:")
            for headline in unique_headlines:
                print(f"- {headline}")
        else:
            print("No headlines found. Using fallback headlines...")
            # Provide some fallback headlines if API fails
            unique_headlines = [
                "Israel-Hamas War Continues Into Fourth Month",
                "Economic Challenges Mount Amid Regional Tensions",
                "Government Debates New Security Measures",
                "Tech Sector Shows Resilience Despite Conflict",
                "International Community Calls for Peace Talks"
            ]
        
        return unique_headlines
    except requests.exceptions.RequestException as e:
        print(f"Network error fetching news: {str(e)}")
        return []
    except Exception as e:
        print(f"Error fetching news: {str(e)}")
        return []

def get_trending_searches():
    """Get trending searches from Google Trends using SerpApi"""
    try:
        print("\nFetching trending searches...")
        
        # SerpApi parameters
        params = {
            'api_key': os.getenv('SERPAPI_KEY'),
            'engine': 'google_trends_trending_now',
            'geo': 'IL',  # Israel
            'hours': '48',  # Last 48 hours
            'hl': 'iw'  # Hebrew language
        }
        
        # Make request to SerpApi
        response = requests.get('https://serpapi.com/search.json', params=params)
        print(f"Response status code: {response.status_code}")
        
        data = response.json()
        print(f"Raw response: {data}")
        
        # Process trending searches
        all_trends_data = []
        
        if response.status_code == 200 and 'trending_searches' in data:
            trending_searches = data['trending_searches']
            for trend in trending_searches:
                # Skip news sources
                title = trend.get('query', '')
                if title and not is_news_source(title):
                    # Skip translation if the text is mostly ASCII (likely English)
                    if all(ord(char) < 128 for char in title.replace(' ', '')):
                        translated_title = title
                    else:
                        # Translate title
                        try:
                            translator = GoogleTranslator(source='iw', target='en')
                            translated = translator.translate(title)
                            translated_title = f"{title} ({translated})" if translated != title else title
                        except Exception as e:
                            print(f"Translation error for title: {str(e)}")
                            translated_title = title
                    
                    # Get related searches from the trend breakdown
                    related_searches = []
                    for related in trend.get('trend_breakdown', []):
                        if related != title:  # Don't show the same term
                            # Skip translation if the text is mostly ASCII (likely English)
                            if all(ord(char) < 128 for char in related.replace(' ', '')):
                                related_text = related
                            else:
                                # Translate related search
                                try:
                                    translator = GoogleTranslator(source='iw', target='en')
                                    translated = translator.translate(related)
                                    related_text = f"{related} ({translated})" if translated != related else related
                                except Exception as e:
                                    print(f"Translation error for related: {str(e)}")
                                    related_text = related
                            related_searches.append(related_text)
                    
                    all_trends_data.append({
                        'title': translated_title,
                        'related': related_searches[:5]  # Limit to top 5 related searches
                    })
                    
                    if len(all_trends_data) >= 20:  # Get top 20 trends for analysis
                        break
            
            print(f"\nFound {len(all_trends_data)} trending searches")
            if all_trends_data:
                print("Trending searches found:")
                for trend in all_trends_data:
                    print(f"- {trend['title']}")
                    if trend['related']:
                        print("  Related searches:")
                        for related in trend['related']:
                            print(f"  - {related}")
        
        return all_trends_data
    except Exception as e:
        print(f"Error fetching trending searches: {str(e)}")
        return []

def find_surprising_trends(trends_data, headlines):
    """Select trends, prioritizing non-news trends but ensuring we get 5 total"""
    if not trends_data:
        return []
    
    # Get indices of all trends, separating news and non-news
    non_news_indices = []
    news_indices = []
    
    for i, trend in enumerate(trends_data):
        # Check if trend title appears in any headline
        is_news_related = any(trend['title'].lower() in headline.lower() or headline.lower() in trend['title'].lower() for headline in headlines)
        if is_news_related:
            news_indices.append(i)
        else:
            non_news_indices.append(i)
    
    # Randomly select up to 5 trends, prioritizing non-news trends
    selected_indices = []
    
    # First, add non-news trends
    if non_news_indices:
        num_non_news = min(5, len(non_news_indices))
        selected_indices.extend(random.sample(non_news_indices, num_non_news))
    
    # If we need more trends to reach 5, add news-related trends
    remaining_slots = 5 - len(selected_indices)
    if remaining_slots > 0 and news_indices:
        num_news = min(remaining_slots, len(news_indices))
        selected_indices.extend(random.sample(news_indices, num_news))
    
    # If we still don't have 5 trends, add any remaining trends
    remaining_slots = 5 - len(selected_indices)
    if remaining_slots > 0:
        all_indices = list(range(len(trends_data)))
        unused_indices = [i for i in all_indices if i not in selected_indices]
        if unused_indices:
            num_additional = min(remaining_slots, len(unused_indices))
            selected_indices.extend(random.sample(unused_indices, num_additional))
    
    return sorted(selected_indices)  # Return indices in original order

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
        print(f"Error generating analysis: {str(e)}")
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

        try:
            # Get trending searches
            all_trends_data = get_trending_searches()
            
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
                
                # Generate timestamp once for both files
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Save JSON log first
                print("\n📝 Saving analysis log...")
                if save_analysis_log(headlines, trends_data, analysis, timestamp):
                    # Only generate audio if JSON save was successful
                    print("\n🔊 Generating audio version...")
                    generate_audio(analysis, timestamp)
                else:
                    print("Skipping audio generation due to JSON save failure")
                
                return {
                    'headlines': headlines,
                    'trends_data': trends_data,
                    'analysis': analysis
                }
            elif all_trends_data:
                print("\nNo news headlines found to compare with trends")
            else:
                print("No trending searches found")
                
        except Exception as e:
            print(f"Error processing trends: {str(e)}")
        
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
