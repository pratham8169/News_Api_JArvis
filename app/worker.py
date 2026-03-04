from celery import Celery
from celery.schedules import crontab
from datetime import datetime

from app.config import get_settings
from app.logger import setup_logger
from app.database import SessionLocal
from app.models import NewsArticle
from app.services.news_api import fetch_latest_news

logger = setup_logger("celery_worker")
settings = get_settings()

celery_app = Celery(
    "news_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Schedule the task to run every minute
celery_app.conf.beat_schedule = {
    "fetch-news-every-minute": {
        "task": "app.worker.task_fetch_and_store_news",
        "schedule": crontab(minute="*"),  # Every minute
    }
}


@celery_app.task
def task_fetch_and_store_news():
    """
    Task to fetch latest news and store it in the database.
    """
    logger.info("Starting background task: fetch and store news.")
    articles = fetch_latest_news()

    if not articles:
        logger.warning("No articles fetched or an error occurred.")
        return "No articles fetched."

    db = SessionLocal()
    try:
        new_count = 0
        for item in articles:
            # Check if article already exists by URL
            exists = (
                db.query(NewsArticle).filter(NewsArticle.url == item.get("url")).first()
            )
            if not exists:

                # Parse published_at
                published_at_str = item.get("publishedAt")
                published_at = datetime.utcnow()
                if published_at_str:
                    try:
                        published_at = datetime.strptime(
                            published_at_str, "%Y-%m-%dT%H:%M:%SZ"
                        )
                    except ValueError:
                        pass

                article = NewsArticle(
                    source_name=item.get("source", {}).get("name"),
                    author=item.get("author"),
                    title=item.get("title"),
                    description=item.get("description"),
                    url=item.get("url"),
                    published_at=published_at,
                    published_date=published_at.date(),
                    content=item.get("content"),
                )
                db.add(article)
                new_count += 1

        db.commit()
        logger.info(f"Successfully stored {new_count} new articles.")
        return f"Stored {new_count} new articles."
    except Exception as e:
        db.rollback()
        logger.error(f"Database error while saving articles: {str(e)}")
        return "Database error."
    finally:
        db.close()
