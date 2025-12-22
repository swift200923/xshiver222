# scraper_desibf.py - EXTRACT REAL VIDEO PLAYER ONLY
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import os
import re

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

def extract_video_player(post_url):
    """Extract ONLY the video player iframe URL, not the post page"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://desibf.com/'
    }
    
    try:
        response = requests.get(post_url, headers=headers, timeout=30)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        html_content = str(response.content)
        
        # Method 1: Find iframe with video player domains
        iframes = soup.find_all('iframe')
        
        video_domains = [
            'streamtape', 'dood', 'mixdrop', 'streamlare', 
            'vidoza', 'upstream', 'voe', 'filemoon', 'fembed',
            'streamsb', 'videovard', 'streamwish'
        ]
        
        for iframe in iframes:
            src = iframe.get('src', '').strip()
            
            if not src or not src.startswith('http'):
                continue
            
            # Skip ads
            ad_keywords = ['doubleclick', 'googlesyndication', 'ads', 'adserver', 'banner']
            if any(ad in src.lower() for ad in ad_keywords):
                continue
            
            # Accept video players
            if any(vd in src.lower() for vd in video_domains):
                print(f"      ✅ Found player: {src[:50]}...")
                return src
        
        # Method 2: Search for video URLs in page source
        video_patterns = [
            r'https?://[^"\']*(?:streamtape|dood|mixdrop|streamlare|vidoza|upstream|voe|filemoon)[^"\']*',
            r'"file":"([^"]+\.m3u8[^"]*)"',
            r'"file":"([^"]+\.mp4[^"]*)"'
        ]
        
        for pattern in video_patterns:
            matches = re.findall(pattern, html_content)
            if matches:
                url = matches[0] if isinstance(matches[0], str) else matches[0]
                if url.startswith('http'):
                    print(f"      ✅ Found embed: {url[:50]}...")
                    return url
        
        print(f"      ❌ No video player found")
        return None
        
    except Exception as e:
        print(f"      ❌ Error: {e}")
        return None

def main():
    print("🔍 Scraping DESIBF.COM - VIDEO PLAYERS ONLY")
    
    all_videos = []
    
    # Scrape 3 pages (approx 30 videos)
    for page in range(1, 4):
        print(f"\n📄 Page {page}")
        posts = get_posts(page)
        
        for idx, post in enumerate(posts[:10]):
            print(f"   {idx+1}/10: {post['title'][:45]}...")
            
            # THIS IS THE KEY FIX - extract real video player
            player_url = extract_video_player(post['url'])
            
            if not player_url:
                continue
            
            video_id = f"desibf-{abs(hash(player_url)) % 1000000}"
            
            all_videos.append({
                'id': video_id,
                'title': post['title'],
                'description': 'Desi BF video',
                'category': 'Desi',
                'duration': '00:00',
                'embedUrl': player_url,  # Now this is the PLAYER, not the page
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
    
    # Dedupe by embedUrl
    existing_urls = {v.get('embedUrl') for v in existing}
    new_videos = [v for v in all_videos if v['embedUrl'] not in existing_urls]
    
    combined = existing + new_videos
    
    # Save
    os.makedirs('data', exist_ok=True)
    with open('data/videos.json', 'w') as f:
        json.dump(combined, f, indent=2)
    
    print(f"\n✅ Scraped: {len(new_videos)} new video players")
    print(f"✅ Total: {len(combined)}")

if __name__ == '__main__':
    main()
