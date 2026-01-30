from textblob import TextBlob
from datetime import datetime
from utils.helpers.logger.logger import get_logger

logger = get_logger(__name__)

class RedditSentimentScraper:
    SUBREDDITS = [
        'wallstreetbets',
        'stocks',
        'investing',
        'options',
        'CryptoCurrency'
    ]
    
    def __init__(self, client_id: str, client_secret: str):
        import praw
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent='FinanceHub/1.0 (your-email@domain.com)'
        )
    
    def get_stock_sentiment(self, ticker: str) -> Dict:
        sentiment_scores = []
        
        for sub in self.SUBREDDITS:
            subreddit = self.reddit.subreddit(sub)
            
            for post in subreddit.search(ticker, limit=100):
                title_sentiment = TextBlob(post.title).sentiment.polarity
                sentiment_scores.append({
                    'source': f'r/{sub}',
                    'type': 'post',
                    'sentiment': title_sentiment,
                    'upvotes': post.ups,
                    'timestamp': datetime.fromtimestamp(post.created_utc)
                })
        
        if not sentiment_scores:
            return {'ticker': ticker, 'sentiment': 0, 'posts': 0}
        
        avg_sentiment = sum(s['sentiment'] for s in sentiment_scores) / len(sentiment_scores)
        positive_count = sum(1 for s in sentiment_scores if s['sentiment'] > 0)
        negative_count = sum(1 for s in sentiment_scores if s['sentiment'] < 0)
        
        return {
            'ticker': ticker,
            'sentiment': avg_sentiment,
            'posts': len(sentiment_scores),
            'positive': positive_count,
            'negative': negative_count,
            'ratio': positive_count / (positive_count + negative_count) if (positive_count + negative_count) > 0 else 0
        }
