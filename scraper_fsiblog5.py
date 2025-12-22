# scraper_fsiblog5.py - FSIBlog5 Scraper
import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import time
import os

SCRAPER_API_KEY = '512bf9b26d582f99b50ae92297c7fb7b'

def scrape_fsiblog5(page_num):
    """Scrape fsiblog5.com"""
    
    if page_num == 1:
        url = "https://www.fsiblog5.com/"
    else:
        url = f"https://www.fsiblog5.com/page/{page_num}/"
    
    api_url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={url}"
    
    try:
        print(f"Fetching page {page_num}...")
        response = requests.get(api_url, timeout=60)
        
        if response.status_code != 200:
            print(f"  Failed: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        videos = []
        
        # FSIBlog5 uses <article class="post">
        articles = soup.find_all('article', class_='post')
        print(f"  Found {len(articles)} articles")
        
        for article in articles:
            link = article.find('a')
            if not link:
                continue
            
            href = link.get('href', '').strip()
            if not href or '/tag/' in href or '/category/' in href:
                continue
            
            # Title from h2.entry-title
            title_el = article.find('h2', class_='entry-title') or article.find('h2')
            title = title_el.get_text(strip=True) if title_el else ''
            
            if not title:
                continue
            
            title = title.replace('\n', ' ').strip()
            
            # Thumbnail
            img = article.find('img')
            thumb = ''
            if img:
                thumb = img.get('src', '') or img.get('data-src', '')
            
            if href and title:
                video_id = href.rstrip('/').split('/')[-1]
                videos.append({
                    'id': f'vid-{video_id}',
                    'title': title[:150],
                    'description': 'Video from fsiblog5',
                    'category': 'FSI',
                    'duration': '00:00',
                    'embedUrl': href,
                    'thumbnailUrl': thumb,
                    'tags': ['fsiblog5', 'desi'],
                    'uploadedAt': datetime.utcnow().isoformat() + 'Z',
                    'views': 0
                })
        
        print(f"  ✅ Extracted {len(videos)} videos")
        return videos
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return []

def main():
    all_videos = []
    
    for page in range(1, 6):
        videos = scrape_fsiblog5(page)
        all_videos.extend(videos)
        time.sleep(2)
    
    try:
        with open('data/videos.json', 'r') as f:
            existing = json.load(f)
    except:
        existing = []
    
    existing_ids = {v['id'] for v in existing}
    new_videos = [v for v in all_videos if v['id'] not in existing_ids]
    
    combined = existing + new_videos
    
    os.makedirs('data', exist_ok=True)
    with open('data/videos.json', 'w') as f:
        json.dump(combined, f, indent=2)
    
    print(f"\n✅ Scraped {len(new_videos)} new videos from 5 pages")
    print(f"✅ Total videos: {len(combined)}")

if __name__ == '__main__':
    main()
