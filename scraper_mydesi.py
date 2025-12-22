# scraper_mydesi.py - 2-STEP SCRAPING
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import os

def get_video_posts(page_num):
    """Step 1: Get post URLs"""
    if page_num == 1:
        url = "https://mydesi.click/"
    else:
        url = f"https://mydesi.click/page/{page_num}/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 403:
            print(f"  ⚠️ 403 blocked - switching to ScraperAPI")
            # Use ScraperAPI as fallback
            api_key = '512bf9b26d582f99b50ae92297c7fb7b'
            api_url = f"http://api.scraperapi.com?api_key={api_key}&url={url}"
            response = requests.get(api_url, timeout=60)
        
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        posts = []
        
        items = soup.select('article') or soup.select('div.post')
        
        for item in items:
            link = item.find('a', href=True)
            if not link:
                continue
            
            href = link.get('href', '').strip()
            if not href or '/tag/' in href or '/category/' in href:
                continue
            
            if not href.startswith('http'):
                href = 'https://mydesi.click' + href
            
            title_el = item.find('h2') or item.find('h3')
            title = title_el.get_text(strip=True) if title_el else 'Video'
            
            img = item.find('img')
            thumb = img.get('src', '') if img else ''
            
            posts.append({'url': href, 'title': title, 'thumb': thumb})
        
        print(f"  Found {len(posts)} posts")
        return posts
        
    except Exception as e:
        print(f"  Error: {e}")
        return []

def extract_video_url(post_url):
    """Step 2: Extract video embed"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    try:
        response = requests.get(post_url, headers=headers, timeout=30)
        if response.status_code == 403:
            # Use ScraperAPI
            api_key = '512bf9b26d582f99b50ae92297c7fb7b'
            api_url = f"http://api.scraperapi.com?api_key={api_key}&url={post_url}"
            response = requests.get(api_url, timeout=60)
        
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try iframe
        iframe = soup.find('iframe', src=True)
        if iframe:
            src = iframe.get('src')
            if src and 'http' in src and 'ad' not in src.lower():
                return src
        
        # Try video tag
        video = soup.find('video')
        if video:
            source = video.find('source', src=True)
            if source:
                return source.get('src')
        
        return post_url
        
    except:
        return None

def scrape_mydesi(page_num):
    posts = get_video_posts(page_num)
    videos = []
    
    for idx, post in enumerate(posts[:10]):
        print(f"    Processing {idx+1}/{len(posts[:10])}: {post['title'][:40]}")
        embed_url = extract_video_url(post['url'])
        
        if not embed_url:
            continue
        
        video_id = f"md-{abs(hash(embed_url)) % 1000000}"
        videos.append({
            'id': video_id,
            'title': post['title'][:150],
            'description': 'Video from mydesi.click',
            'category': 'Desi',
            'duration': '00:00',
            'embedUrl': embed_url,
            'thumbnailUrl': post['thumb'],
            'tags': ['mydesi'],
            'uploadedAt': datetime.utcnow().isoformat() + 'Z',
            'views': 0
        })
        time.sleep(1)
    
    return videos

def main():
    all_videos = []
    
    print("🔍 Starting MyDesi scraper...")
    for page in range(1, 3):
        print(f"\n📄 Page {page}")
        videos = scrape_mydesi(page)
        all_videos.extend(videos)
        print(f"  ✅ Extracted {len(videos)} videos")
        time.sleep(2)
    
    try:
        with open('data/videos.json', 'r') as f:
            existing = json.load(f)
    except:
        existing = []
    
    existing_urls = {v.get('embedUrl') for v in existing}
    new_videos = [v for v in all_videos if v['embedUrl'] not in existing_urls]
    combined = existing + new_videos
    
    os.makedirs('data', exist_ok=True)
    with open('data/videos.json', 'w') as f:
        json.dump(combined, f, indent=2)
    
    print(f"\n✅ Total: {len(new_videos)} new, {len(combined)} total")

if __name__ == '__main__':
    main()
