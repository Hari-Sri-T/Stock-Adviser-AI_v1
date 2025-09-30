import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

def get_company_news(query="GOOG", limit=5):
    """
    Fetches latest news articles using a specific query string (e.g., symbol or full company name).
    """
    if not NEWS_API_KEY:
        print("Warning: NEWS_API_KEY is not set. News fetching will be skipped.")
        return []

    # Add quotes around the query for better multi-word search results
    url = f"https://newsapi.org/v2/everything?q=\"{query}\"&sortBy=publishedAt&language=en&apiKey={NEWS_API_KEY}"
    
    try:
        resp = requests.get(url).json()
        if resp.get("status") != "ok":
            print(f"Error from NewsAPI: {resp.get('message')}")
            return []
    except Exception as e:
        print(f"An exception occurred while fetching news: {e}")
        return []

    articles = []
    for a in resp.get("articles", []):
        if len(articles) >= limit:
            break
        if a.get("title") and a.get("description"):
            articles.append({
                "title": a.get("title"),
                "description": a.get("description"),
                "url": a.get("url", "")
            })
            
    print(f"Fetched {len(articles)} articles from NewsAPI for query: \"{query}\"")
    return articles