import requests
from config import NEWS_API_KEY

def get_company_news(symbol="GOOG", limit=5):
    """
    Fetches latest news articles about a company using NewsAPI.
    Returns a list of dicts with {title, description, url}.
    """
    url = f"https://newsapi.org/v2/everything?q={symbol}&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    resp = requests.get(url).json()

    articles = []
    for a in resp.get("articles", [])[:limit]:
        articles.append({
            "title": a.get("title", ""),
            "description": a.get("description") or "",
            "url": a.get("url", "")
        })

    return articles
