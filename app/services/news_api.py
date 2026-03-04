import requests
from datetime import datetime
from app.config import get_settings
from app.logger import setup_logger

logger = setup_logger("news_api_service")
settings = get_settings()

BASE_URL = "https://newsapi.org/v2/top-headlines"


def fetch_latest_news(country: str = "us"):
    """
    Fetches the latest top headlines from News API.
    """
    if not settings.NEWS_API_KEY:
        logger.error("NEWS_API_KEY is not set in environment or config.")
        return []

    params = {"country": country, "apiKey": settings.NEWS_API_KEY}

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        if data.get("status") == "ok":
            logger.info(f"Successfully fetched {data.get('totalResults', 0)} articles.")
            return data.get("articles", [])
        else:
            logger.error(f"News API returned error: {data}")
            return []

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch news from API: {str(e)}")
        return []
