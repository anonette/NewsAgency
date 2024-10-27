import requests
from bs4 import BeautifulSoup

url = "https://trends.google.com/trending?geo=IR&&hours=24"
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Locate specific data fields (e.g., trending topics, timestamps)
trends = soup.find_all('your-target-element')  # Update with actual element

for trend in trends:
    print(trend.text)
