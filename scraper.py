import requests
from bs4 import BeautifulSoup
from datetime import datetime
from newspaper import Article as NewsArticle

def fetch_daily_articles(year, month, day):
    """
    Fetches article hyperlinks from The Hindu's RSS feeds.
    We use RSS to bypass the 403 Forbidden blocks on their main archive pages.
    """
    selected_date_str = f"{year}-{month:02d}-{day:02d}"
    
    rss_feeds = [
        {'url': 'https://www.thehindu.com/news/national/feeder/default.rss', 'category': 'National'},
        {'url': 'https://www.thehindu.com/opinion/editorial/feeder/default.rss', 'category': 'Editorial'},
        {'url': 'https://www.thehindu.com/news/international/feeder/default.rss', 'category': 'International'},
        {'url': 'https://www.thehindu.com/sci-tech/feeder/default.rss', 'category': 'Sci-Tech'}
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    
    articles = []
    
    try:
        for feed in rss_feeds:
            response = requests.get(feed['url'], headers=headers, timeout=10)
            if response.status_code != 200:
                continue
                
            # Parse XML robustly with BeautifulSoup to avoid 'invalid token' crashes on malformed feeds
            soup = BeautifulSoup(response.content, 'xml')
            
            items = soup.find_all('item')
            for item in items:
                title = item.title.text if item.title else "Untitled"
                link = item.link.text if item.link else ""
                
                # Check pubDate
                pub_date_tag = item.find('pubDate')
                pubDate = pub_date_tag.text if pub_date_tag else ""
                
                articles.append({
                    'title': title.strip(),
                    'url': link.strip(),
                    'category': feed['category'],
                    'pubDate': pubDate
                })
                
        if not articles:
            return {'success': False, 'error': f"Failed to fetch articles. No items found in RSS feeds."}
            
        return {'success': True, 'articles': articles[:40]} # Limit to 40 for UI
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def extract_article_content(url):
    """
    Uses newspaper3k to extract the main content of an article efficiently.
    """
    try:
        article = NewsArticle(url)
        article.download()
        article.parse()
        
        title = article.title
        text = article.text
        top_image = article.top_image
        
        if not text or len(text) < 100:
            return {'success': False, 'error': "Article is too short or is behind a paywall."}
            
        return {'success': True, 'title': title, 'text': text, 'image_url': top_image}
    except Exception as e:
        return {'success': False, 'error': f"Failed to parse article: {str(e)}"}
