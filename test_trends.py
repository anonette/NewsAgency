from pytrends.request import TrendReq
import sys
import time
from datetime import datetime
from deep_translator import GoogleTranslator
import warnings
import requests
import json

# Suppress pandas warnings
warnings.filterwarnings('ignore', category=FutureWarning)

# Country code mappings
COUNTRY_CODES = {
    'IL': 'israel'  # For trending searches we need the full name
}

# News sources to filter out
NEWS_SOURCES = {
    'cnn', 'bbc', 'fox news', 'nyt', 'new york times',
    'reuters', 'associated press', 'ap news'
}

def is_news_source(text):
    """Check if the term is a news source"""
    return any(source in text.lower() for source in NEWS_SOURCES)

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

def fetch_trends(country_code="IL"):
    """Fetch trending searches excluding news sources"""
    try:
        print(f"\n{'='*50}")
        print(f"GOOGLE TRENDS - ISRAEL")
        print(f"{'='*50}\n")

        print("🔥 TRENDING SEARCHES WITH BREAKDOWNS")
        print("-" * 50)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Last updated: {current_time}")
        print(f"Source: trends.google.com/trends/trendingsearches/daily?geo={country_code}\n")

        # Initialize pytrends
        pytrends = TrendReq(hl='en-US', tz=210)
        
        # Get trending searches using country name
        trending_searches = pytrends.trending_searches(pn=COUNTRY_CODES[country_code])
        
        if not trending_searches.empty:
            trend_number = 1
            for trend in trending_searches.values:
                keyword = trend[0]
                # Skip news sources
                if not is_news_source(keyword):
                    title = translate_text(keyword)
                    print(f"\n{trend_number}. {title}")
                    
                    # Get and show related searches from suggestions
                    suggestions = get_suggestions(keyword)
                    if suggestions:
                        print("   Related Searches:")
                        for suggestion in suggestions:
                            if suggestion != keyword:  # Don't show the same term
                                suggestion_text = translate_text(suggestion)
                                print(f"   - {suggestion_text}")
                    
                    trend_number += 1
                    if trend_number > 20:  # Show top 20 non-news-source trends
                        break
                    
                    time.sleep(0.5)  # Avoid rate limiting
        else:
            print("No trending searches found")
            print("\nView live trends at:")
            print(f"trends.google.com/trends/trendingsearches/daily?geo={country_code}")

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        print("\nView live trends at:")
        print(f"trends.google.com/trends/trendingsearches/daily?geo={country_code}")

def print_usage():
    """Print script usage instructions"""
    print("\nUsage:")
    print("python test_trends.py")
    print("\nShows trending searches with breakdowns in Israel")
    print("Live trends: trends.google.com/trends/trendingsearches/daily?geo=IL")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print_usage()
    else:
        fetch_trends()
