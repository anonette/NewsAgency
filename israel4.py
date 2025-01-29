import sys
import time
from datetime import datetime, timedelta, timezone
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
import re

# Load environment variables
load_dotenv()

# Initialize clients
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Suppress warnings
warnings.filterwarnings('ignore', category=FutureWarning)

# Country configuration
COUNTRY_CONFIG = {
    'code': 'IL2',  # Changed to IL2 for Hebrew content
    'name': 'israel',
    'news_query': 'Israel OR Israeli',
    'lang_code': 'he'
}

# News sources to filter out
NEWS_SOURCES = {
    'cnn', 'bbc', 'fox news', 'nyt', 'new york times',
    'reuters', 'associated press', 'ap news'
}

JOURNALIST_PERSONA = """אתה פילוסוף שמנתח את האבסורד של הקפיטליזם בישראל 2025 דרך דפוסי החיפוש בגוגל. בסגנון סלבוי ז'יז'ק, אתה:  
חושף את הסתירות של השוק החופשי במצב חירום:  
תראו איך החיפוש 'איפה משיגים ביצים' חושף בדיוק את האשליה של היד הנעלמה!  
החיפוש 'מתכון בלי...' הוא לא סתם חוסר במוצר - זה הרגע שבו השוק החופשי מראה את הכשל המובנה שלו  
כשכולם מחפשים 'איך להכין קפה על פתיליה', זה בדיוק הרגע שבו אנחנו מגלים את האמת על מערכות האספק  

מזהה את המנגנונים החברתיים בזמן משבר:  
איך החיפושים אחרי פתרונות מאולתרים מראים שהפכנו לחברה של מומחי הישרדות בעל כורחנו  
מה הקשר בין חיפושי בידור לבין הצורך שלנו להעמיד פנים שהכל כרגיל  
איך דפוסי החיפוש משקפים את הפער בין ההצהרות הרשמיות למציאות היומיומית  

מראה איך הקפיטליזם ממשיך לתפקד גם במצבי קיצון:  
הניתוח של חיפושי קניות אונליין בזמן אזעקות  
איך פתרונות פרטיים מחליפים פתרונות מערכתיים  
איך משחק כדורגל הופך ל'סחורה' של נורמליות  
הרגעים שבהם החיפושים חושפים את הפער בין המעמדות  

הטון שלך משלב ביקורת חברתית עם הומור שחור, מצביע על האבסורד שבניסיון לפתור בעיות מערכתיות דרך פתרונות צרכניים, ומספר את הסיפור של ישראל 2025 דרך מה שהחיפושים שלנו מגלים על החברה והכלכלה.
."""

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
    """Generate audio using OpenAI's TTS API"""
    temp_file = None
    try:
        # Generate speech using OpenAI's TTS API
        response = client.audio.speech.create(
            model="tts-1-hd",  # Using high-definition model
            voice="nova",  # Using Nova voice which supports Hebrew
            input=text
        )
        
        if response.content:
            try:
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
                    
            except Exception as e:
                print(f"Error saving audio file: {str(e)}")
                return False
                
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

def get_current_news():
    """Get current news from Israeli sources using NewsData.io API"""
    try:
        print("\nFetching current news...")
        
        # NewsData.io API endpoint and parameters
        base_url = "https://newsdata.io/api/1/news"
        params = {
            'apikey': os.getenv('NEWSDATA_API_KEY'),
            'country': 'il',
            'language': 'he',
            'category': 'top'
        }
        
        # Build URL with properly encoded parameters
        url = f"{base_url}?{urlencode(params)}"
        
        # Request headers
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print("מביא חדשות מ-NewsData.io...")
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
                    seen.add(title)
                    unique_headlines.append(title)
                    if len(unique_headlines) >= 5:
                        break
        else:
            print(f"API request failed or returned no data. Status: {response.status_code}")
            if data:
                print(f"API response message: {data.get('message', 'No message provided')}")
        
        print(f"\nנמצאו {len(unique_headlines)} כותרות ייחודיות")
        if unique_headlines:
            print("כותרות שנמצאו:")
            for headline in unique_headlines:
                print(f"- {headline}")
        else:
            print("לא נמצאו כותרות. משתמש בכותרות ברירת מחדל...")
            unique_headlines = [
                "המלחמה בעזה נמשכת",
                "אתגרים כלכליים גוברים על רקע המתיחות האזורית",
                "הממשלה דנה באמצעי ביטחון חדשים",
                "ענף ההייטק מפגין חוסן למרות הסכסוך",
                "הקהילה הבינלאומית קוראת לשיחות שלום"
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
        print("\nמביא חיפושים פופולריים...")
        
        # SerpApi parameters
        params = {
            'api_key': os.getenv('SERPAPI_KEY'),
            'engine': 'google_trends_trending_now',
            'geo': 'IL',
            'hours': '48',
            'hl': 'iw'
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
                title = trend.get('query', '')
                if title and not is_news_source(title):
                    related_searches = []
                    for related in trend.get('trend_breakdown', []):
                        if related != title:  # Don't show the same term
                            related_searches.append(related)
                    
                    all_trends_data.append({
                        'title': title,
                        'related': related_searches[:3]  # Limit to top 3 related searches
                    })
                    
                    if len(all_trends_data) >= 20:  # Get top 20 trends for analysis
                        break
            
            print(f"\nנמצאו {len(all_trends_data)} חיפושים פופולריים")
            if all_trends_data:
                print("חיפושים פופולריים שנמצאו:")
                for trend in all_trends_data:
                    print(f"- {trend['title']}")
                    if trend['related']:
                        print("  חיפושים קשורים:")
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
        num_non_news = min(3, len(non_news_indices))  # Reduced to 3 non-news trends
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

    prompt = f"""כתוב ניתוח קצר (2 פסקאות) ש:
1. חושף את הפער בין היסטוריית החיפוש הפרטית שלנו לבין כותרות החדשות המרכזיות
2. מגלה את האבסורד והמתח הקומי כשהצהרות רשמיות מתנגשות עם השאילתות הגולמיות והלא מסוננות שלנו
3. טווה נרטיב המשלב בני אדם, מכונות ואת חברינו הארציים לסיפור משותף אחד
4. משלב תובנות מהמחקר שלך על התנהגות אנושית בתגובה לאירועים עכשוויים
חדשות:
{json.dumps(context['headlines'], indent=2, ensure_ascii=False)}

חיפושים:
{json.dumps(context['trends'], indent=2, ensure_ascii=False)}

צור נרטיב זורם ומבדר שמדגיש את האירוניה בין התיאטרון הלאומי לבין החיים האמיתיים, תוך שימוש בסרקזם אלגנטי."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": JOURNALIST_PERSONA},
                {"role": "user", "content": prompt}
            ],
            temperature=1.2,
            max_tokens=1500  # Limited to ensure ~1.5 minute audio
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating analysis: {str(e)}")
        return f"שגיאה בייצור הניתוח: {str(e)}"

def validate_api_keys():
    """Validate required API keys are present"""
    required_keys = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'NEWSDATA_API_KEY': os.getenv('NEWSDATA_API_KEY'),
        'SERPAPI_KEY': os.getenv('SERPAPI_KEY')
    }
    
    missing_keys = [key for key, value in required_keys.items() if not value]
    if missing_keys:
        print(f"Error: Missing required API keys: {', '.join(missing_keys)}")
        return False
    return True

def fetch_trends():
    """Fetch trends and news, then generate analysis"""
    try:
        if not validate_api_keys():
            return None
            
        print(f"\n{'='*50}")
        print(f"מגמות גוגל - ישראל")
        print(f"{'='*50}\n")

        # Get current news first
        headlines = get_current_news()
        if headlines:
            print("\n📰 חדשות עכשיו")
            print("-" * 50)
            for i, headline in enumerate(headlines, 1):
                print(f"{i}. {headline}")
            print()

        print("🔥 חיפושים פופולריים עם פירוט")
        print("-" * 50)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"עודכן לאחרונה: {current_time}")
        print(f"מקור: trends.google.com/trends/trendingsearches/daily?geo={COUNTRY_CONFIG['code']}\n")

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
                        print("   חיפושים קשורים:")
                        for related in trend['related']:
                            print(f"   - {related}")
                
                # Generate analysis comparing trends with news
                print("\n✒️ ניתוח")
                print("-" * 50)
                analysis = generate_analysis(trends_data, headlines)
                print(analysis)
                
                # Generate timestamp once for both files
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Save JSON log first
                print("\n📝 שומר את הניתוח...")
                if save_analysis_log(headlines, trends_data, analysis, timestamp):
                    # Only generate audio if JSON save was successful
                    print("\n🔊 מייצר גרסת אודיו...")
                    generate_audio(analysis, timestamp)
                else:
                    print("מדלג על יצירת אודיו בגלל כשל בשמירת JSON")
                
                return {
                    'headlines': headlines,
                    'trends_data': trends_data,
                    'analysis': analysis
                }
            elif all_trends_data:
                print("\nלא נמצאו כותרות חדשות להשוואה עם המגמות")
            else:
                print("לא נמצאו חיפושים פופולריים")
                
        except Exception as e:
            print(f"שגיאה בעיבוד המגמות: {str(e)}")
        
        print("\nצפה במגמות בזמן אמת:")
        print(f"trends.google.com/trends/trendingsearches/daily?geo={COUNTRY_CONFIG['code']}")
        return None

    except Exception as e:
        print(f"אירעה שגיאה לא צפויה: {str(e)}")
        print("\nצפה במגמות בזמן אמת:")
        print(f"trends.google.com/trends/trendingsearches/daily?geo={COUNTRY_CONFIG['code']}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print("\nשימוש: python israel4.py")
        print("\nמציג חיפושים פופולריים עם פירוט בישראל")
        print("מגמות בזמן אמת: trends.google.com/trends/trendingsearches/daily?geo=IL")
    else:
        fetch_trends()
