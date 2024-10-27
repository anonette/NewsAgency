import json
import requests
from bs4 import BeautifulSoup

url = "https://trends.google.com/trending?geo=IR&&hours=24"
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

trends_data = []
trends = soup.find_all('your-target-element')  # Replace 'your-target-element' with actual HTML tag/class

for trend in trends:
    trend_info = {
        'title': trend.text,  # Adjust based on actual HTML structure
        'timestamp': 'time-info'  # Adjust based on actual HTML structure
    }
    trends_data.append(trend_info)

# Save as JSON
with open('trends_data.json', 'w') as json_file:
    json.dump(trends_data, json_file, indent=4)
