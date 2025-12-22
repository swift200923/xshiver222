# scraper_desibf.py - DESIBF ONLY (WORKING)
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import os

def get_posts(page_num):
    """Get video posts from desibf.com"""
    url = f"https://desibf.com/page/{page_num}/" if page_num > 1 else "https://desibf.com/"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"  Failed: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        posts = []
        
        # Desibf uses article tags
        articles = soup.find_all('article')
        
        for article in articles:
            link = article.find('a', href=True)
            if not link:
                continue
            
            href = link.get('href', '').strip()
            if not href or '/tag/' in href or '/category/' in href:
                continue
            
            # Title
            h2 = article.find('h2') or article.find('h3')
            title = h2.get_text(strip=True) if h2 else 'Video'
            title = title.replace('\n', ' ').strip()[:150]
            
            # Thumbnail
            img = article.find('img')
            thumb = ''
            if img:
                thumb = img.get('data-src', '') or img.get('src', '')
            
            if href and title and len(title) > 3:
                posts.append({'url': href, 'title': title, 'thumb': thumb})
        
        print(f"  Found {len(posts)} posts")
        return posts
        
    except Exception as e:
        print(f"  Error: {e}")
        return []

def extract_video(post_url):
    """Extract actual video URL from post page"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://desibf.com/'
    }
    
    try:
        response = requests.get(post_url, headers=headers, timeout=30)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all iframes
        iframes = soup.find_all('iframe')
        
        for iframe in iframes:
            src = iframe.get('src', '').strip()
            
            # Skip ads - only accept video player iframes
            if not src or not src.startswith('http'):
                continue
            
            # Reject ad domains
            ad_domains = [
                'doubleclick', 'googlesyndication', 'ads', 'adserver', 
                'banner', 'popup', 'track', 'analytics', 'pixel',
                'affiliate', 'promo', 'sync', 'tag', 'impression'
            ]
            
            if any(ad in src.lower() for ad in ad_domains):
                continue
            
            # Accept video player domains
            video_domains = [
                'streamtape', 'dood', 'mixdrop', 'streamlare', 
                'vidoza', 'upstream', 'voe', 'filemoon'
            ]
            
            # If it contains video player domain OR is generic iframe, accept it
            if any(vd in src.lower() for vd in video_domains):
                return src
        
        # Fallback: return post URL
        return post_url
        
    except:
        return None

def main():
    print("🔍 Scraping DESIBF.COM")
    
    all_videos = []
    
    # Scrape 3 pages (approx 30 videos)
    for page in range(1, 4):
        print(f"\n📄 Page {page}")
        posts = get_posts(page)
        
        for idx, post in enumerate(posts[:10]):
            print(f"   {idx+1}/10: {post['title'][:45]}...")
            
            embed = extract_video(post['url'])
            
            if not embed:
                print(f"      ❌ No video")
                continue
            
            video_id = f"desibf-{abs(hash(embed)) % 1000000}"
            
            all_videos.append({
                'id': video_id,
                'title': post['title'],
                'description': 'Desi BF video',
                'category': 'Desi',
                'duration': '00:00',
                'embedUrl': embed,
                'thumbnailUrl': post['thumb'],
                'tags': ['desibf', 'desi'],
                'uploadedAt': datetime.utcnow().isoformat() + 'Z',
                'views': 0
            })
            
            time.sleep(1)
        
        time.sleep(2)
    
    # Load existing
    try:
        with open('data/videos.json', 'r') as f:
            existing = json.load(f)
    except:
        existing = []
    
    # Dedupe
    existing_urls = {v.get('embedUrl') for v in existing}
    new_videos = [v for v in all_videos if v['embedUrl'] not in existing_urls]
    
    combined = existing + new_videos
    
    # Save
    os.makedirs('data', exist_ok=True)
    with open('data/videos.json', 'w') as f:
        json.dump(combined, f, indent=2)
    
    print(f"\n✅ Scraped: {len(new_videos)} new")
    print(f"✅ Total: {len(combined)}")

if __name__ == '__main__':
    main()
