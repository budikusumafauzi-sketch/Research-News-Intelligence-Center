import feedparser
import logging

logger = logging.getLogger(__name__)

class RSSParser:
    @staticmethod
    def parse_feed(url):
        """
        Fetches and parses an RSS feed using feedparser.
        Returns a structured list of articles.
        """
        try:
            # feedparser handles malformed XML securely
            feed = feedparser.parse(url)
            
            if feed.bozo and hasattr(feed, 'bozo_exception'):
                logger.warning(f"Malformed feed warning at {url}: {feed.bozo_exception}")
            
            articles = []
            for entry in feed.entries:
                articles.append({
                    'title': entry.get('title', 'Untitled'),
                    'original_url': entry.get('link', ''),
                    'content_raw': entry.get('description', '') or entry.get('summary', ''),
                    'published_at': entry.get('published_parsed', None)
                })
            return articles
        except Exception as e:
            logger.error(f"Failed to parse RSS feed {url}: {e}")
            return []
