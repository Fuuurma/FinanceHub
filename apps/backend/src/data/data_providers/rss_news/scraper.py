import feedparser
from typing import List, Dict
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)

class RSSNewsScraper:
    SOURCES = {
        'CNBC': 'https://www.cnbc.com/id/10000664/device/rss/rss.html',
        'Reuters': 'https://www.reutersagency.com/feed/',
        'MarketWatch': 'https://www.marketwatch.com/rss/topstories',
        'Bloomberg': 'https://feeds.bloomberg.com/markets/news.rss',
        'SeekingAlpha': 'https://seekingalpha.com/feed.xml',
        'Benzinga': 'https://www.benzinga.com/feed'
    }
    
    def get_news(self, source: str = 'CNBC', limit: int = 20) -> List[Dict]:
        if source not in self.SOURCES:
            logger.error(f"Unknown news source: {source}")
            return []
        
        try:
            feed = feedparser.parse(self.SOURCES[source])
            articles = []
            
            for entry in feed.entries[:limit]:
                articles.append({
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.get('published'),
                    'summary': entry.get('summary', ''),
                    'source': source
                })
            
            logger.info(f"Retrieved {len(articles)} articles from {source}")
            return articles
        except (ValueError, KeyError, TypeError, NetworkError, TimeoutException, DatabaseError) as e:
            logger.error(f"Error fetching RSS feed from {source}: {str(e)}")
            return []
    
    def get_all_news(self, limit_per_source: int = 10) -> List[Dict]:
        all_articles = []
        for source in self.SOURCES:
            articles = self.get_news(source, limit_per_source)
            all_articles.extend(articles)
        return all_articles
