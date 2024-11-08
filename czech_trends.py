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
import feedparser
import random
import tempfile
import shutil

# Load environment variables
load_dotenv()

# Initialize clients
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Suppress warnings
warnings.filterwarnings('ignore', category=FutureWarning)

# Country configuration
COUNTRY_CONFIG = {
    'code': 'CZ',
    'name': 'Czech Republic',
    'lang_code': 'cs'  # Czech language code
}

# Czech news RSS feeds
CZECH_RSS_FEEDS = [
    'https://servis.idnes.cz/rss.aspx?c=zpravodaj',  # iDNES.cz news
    'https://www.novinky.cz/rss',  # Novinky.cz
    'https://www.seznamzpravy.cz/rss'  # Seznam Zprávy
]

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
        # Using a Czech voice ID for Czech language
        url = "https://api.elevenlabs.io/v1/text-to-speech/ThT5KcBeYPX3keUQqHPh"  # Czech voice
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": os.getenv('ELEVENLABS_API_KEY')
        }
        
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",  # Using multilingual model for Czech
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

def get_czech_news():
    """Get current headlines from Czech RSS feeds"""
    try:
        print("\nFetching Czech news...")
        
        # Get unique headlines and translate them
        seen = set()
        unique_headlines = []
        translator = GoogleTranslator(source='cs', target='en')
        
        for feed_url in CZECH_RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:3]:  # Get top 3 from each feed
                    title = entry.title
                    if title and title not in seen:
                        seen.add(title)
                        try:
                            translated = translator.translate(title)
                            unique_headlines.append(f"{title} ({translated})")
                        except:
                            unique_headlines.append(title)
                        if len(unique_headlines) >= 5:
                            break
                if len(unique_headlines) >= 5:
                    break
            except Exception as e:
                print(f"Error fetching from {feed_url}: {str(e)}")
                continue
        
        print(f"Found {len(unique_headlines)} unique headlines")
        return unique_headlines
    except Exception as e:
        print(f"Error fetching Czech news: {str(e)}")
        return []

def translate_text(text, from_lang='auto'):
    """Translate text to English if it's not in English"""
    try:
        # Skip translation if the text is mostly ASCII (likely English)
        if all(ord(char) < 128 for char in text.replace(' ', '')):
            return text
        
        translator = GoogleTranslator(source=from_lang, target='en')
        translated = translator.translate(text)
        return f"{text} ({translated})" if translated != text else text
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return text

def get_trending_searches():
    """Get trending searches from Google Trends using SerpApi"""
    try:
        print("\nFetching trending searches...")
        
        # SerpApi parameters
        params = {
            'api_key': os.getenv('SERPAPI_KEY'),
            'engine': 'google_trends_trending_now',
            'geo': COUNTRY_CONFIG['code'],
            'hours': '24',  # Last 24 hours
            'hl': COUNTRY_CONFIG['lang_code']
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
                # Get title and translate
                title = trend.get('query', '')
                if title:
                    # Translate title
                    translated_title = translate_text(title, from_lang=COUNTRY_CONFIG['lang_code'])
                    
                    # Get related searches from the trend breakdown
                    related_searches = []
                    for related in trend.get('trend_breakdown', []):
                        if related != title:  # Don't show the same term
                            translated_related = translate_text(related, from_lang=COUNTRY_CONFIG['lang_code'])
                            related_searches.append(translated_related)
                    
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

def translate_to_czech(text):
    """Translate analysis to Czech"""
    try:
        translator = GoogleTranslator(source='en', target='cs')
        return translator.translate(text)
    except Exception as e:
        print(f"Error translating to Czech: {str(e)}")
        return text

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
        # Generate analysis in English
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": JOURNALIST_PERSONA},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=500
        )
        english_analysis = response.choices[0].message.content
        
        # Translate to Czech
        czech_analysis = translate_to_czech(english_analysis)
        
        return czech_analysis
    except Exception as e:
        print(f"Error generating analysis: {str(e)}")
        return f"Error generating analysis: {str(e)}"

def fetch_trends():
    """Fetch trends and news, then generate analysis"""
    try:
        print(f"\n{'='*50}")
        print(f"GOOGLE TRENDS - CZECH REPUBLIC")
        print(f"{'='*50}\n")

        # Get current Czech news
        headlines = get_czech_news()
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
        print("\nUsage: python czech_trends.py")
        print("\nShows trending searches with breakdowns in Czech Republic")
        print("Live trends: trends.google.com/trends/trendingsearches/daily?geo=CZ")
    else:
        fetch_trends()
