import hashlib
import logging
from datetime import datetime
from time import mktime
from extensions import db
from models.content import News
from models.source import Source
from scraper.rss_parser import RSSParser

logger = logging.getLogger(__name__)

class NewsService:
    @staticmethod
    def generate_content_hash(title, content):
        """Generate SHA-256 hash to prevent duplicate insertions."""
        safe_title = title or ""
        safe_content = content or ""
        return hashlib.sha256(f"{safe_title}{safe_content}".encode('utf-8')).hexdigest()

    @staticmethod
    def fetch_latest_news():
        """Triggered by APScheduler to pull all RSS feeds."""
        logger.info("Starting scheduled RSS fetch for all sources.")
        sources = Source.query.filter_by(source_type='rss').all()
        
        total_saved = 0
        for source in sources:
            articles = RSSParser.parse_feed(source.base_url)
            saved_count = 0
            
            for article in articles:
                if NewsService.save_news(source.id, article):
                    saved_count += 1
            
            source.last_scraped_at = datetime.utcnow()
            total_saved += saved_count
            logger.info(f"Fetched and saved {saved_count} new articles from {source.name}.")
            
        db.session.commit()
        logger.info(f"RSS fetch complete. {total_saved} total articles saved.")

    @staticmethod
    def is_valid_article(article_data):
        """Filters out low-value commercial and promotional content based on title analysis."""
        title = article_data.get('title', '').lower()
        
        blocked_keywords = [
            "coupon", "promo code", "discount code", "discounts",
            "deals", "sale", "save up to", "% off", "exclusive offer"
        ]
        
        import re
        for keyword in blocked_keywords:
            # For phrases or symbols, use direct substring check
            if " " in keyword or "%" in keyword:
                if keyword in title:
                    logger.info("Article filtered: promotional content detected.")
                    return False
            else:
                # For single words (like 'sale', 'deals'), use regex word boundaries 
                # to prevent false positives like 'Salesforce' or 'Wholesale'
                if re.search(rf'\b{keyword}\b', title):
                    logger.info("Article filtered: promotional content detected.")
                    return False
                    
        logger.info("Article accepted: technology intelligence content.")
        return True

    @staticmethod
    def save_news(source_id, article_data):
        """Saves a single news article ensuring no duplicates and high intelligence value."""
        
        # 1. Quality Filter (Reject low-value commercial content FIRST)
        if not NewsService.is_valid_article(article_data):
            return False

        url = article_data.get('original_url')
        if not url:
            return False

        # 2. URL Uniqueness Check
        if News.query.filter_by(original_url=url).first():
            return False

        title = article_data.get('title', 'Untitled')
        content_raw = article_data.get('content_raw', '')
        
        # 3. Content Hash Uniqueness Check
        content_hash = NewsService.generate_content_hash(title, content_raw)
        if News.query.filter_by(content_hash=content_hash).first():
            return False

        pub_parsed = article_data.get('published_at')
        if pub_parsed:
            published_date = datetime.fromtimestamp(mktime(pub_parsed))
        else:
            published_date = datetime.utcnow()

        news = News(
            source_id=source_id,
            title=title,
            content_raw=content_raw,
            original_url=url,
            published_at=published_date,
            content_hash=content_hash
        )
        db.session.add(news)
        return True

    @staticmethod
    def update_existing_news(existing_news, new_data):
        """Update an existing news article (stub for future expansions)."""
        pass

    @staticmethod
    def get_trending_news(limit=5):
        """Placeholder for actual trending logic (will use Analytics module later)."""
        return News.query.filter_by(is_deleted=False).order_by(News.published_at.desc()).limit(limit).all()

    @staticmethod
    def get_latest_news(limit=10):
        """Retrieve the most recently published articles."""
        return News.query.filter_by(is_deleted=False).order_by(News.published_at.desc()).limit(limit).all()
        
    @staticmethod
    def get_news_by_id(news_id):
        """Fetch a specific news item by its UUID."""
        return News.query.filter_by(id=news_id, is_deleted=False).first()
