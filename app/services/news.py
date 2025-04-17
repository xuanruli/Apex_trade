import os
import requests

NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

def get_recent_stock_news(count=3):
    """
    Fetches recent general stock/market news from NewsAPI.
    If an article has an unusable 'urlToImage' (e.g., a favicon),
    we'll replace it with '/static/default-news.jpg'.
    """
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "stocks",
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": count,
        "apiKey": NEWS_API_KEY
    }

    fallback_image = "/static/default-news.jpg"

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        articles = data.get("articles", [])

        formatted_articles = []
        for article in articles:
            # Use 'or fallback_image' to handle None or empty strings
            url_to_image = article.get("urlToImage") or fallback_image

            # If it's obviously a small icon or favicon, replace with fallback.
            if any(x in (url_to_image or "").lower() for x in ["favicon", "16x16", "32x32", "64x64", "icon"]):
                url_to_image = fallback_image

            formatted_articles.append({
                "title": article.get("title", "No Title"),
                "description": article.get("description", "No Description"),
                "url": article.get("url", "#"),
                "image_url": url_to_image
            })

        return formatted_articles

    except Exception as e:
        print(f"Error fetching news: {e}")
        return []
