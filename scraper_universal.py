# scraper_universal.py - EXTRACT VIDEO PLAYERS ONLY
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import os
import re

SITES = {
    'fsiblog5': {
        'base': 'https://www.fsiblog5.com',
        'pages': ['https://www.fsiblog5.com/', 'https://www.fsiblog5.com/page/2/'],
        'selector': 'article.post',
    },
    'viralkand': {
        'base': 'https://viralkand.com',
        'pages': ['https://viralkand.com/', 'https://viralkand.com/page/2/'],
        'selector': 'article.post',
    },
}

# Video player domains to extract
VIDEO_DOMAINS = [
    'streamtape', 'dood', 'mixdrop', 'streamlare', 'vidoza',
    'upstream', 'voe', 'filemoon', 'fembed', 'streamsb',
    'videovard', 'streamwish', 'mp4upload', 'sendvid'
]

# Ad domains to reject
AD_DOMAINS = [
    'doubleclick', 'googlesyndication', 'ads', 'adserver', 'banner',
    'popup', 'track', 'analytics', 'pixel', 'affiliate', 'promo'
]

def get_posts(url, selector):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        cards = soup.select(selector) or soup.find_all('article')
        
        posts = []
        for card in cards:
            link = card.find('a', href=True)
            if not link:
                continue
            
            href = link.get('href', '').strip()
            if not href or '/tag/' in href or '/category/' in href:
                continue
            
            title = link.get('title', '').strip()
            if not title:
                h_tag = card.find(['h1', 'h2', 'h3'])
                if h_tag:
                    title = h_tag.get_text(strip=True)
            
            title = title.replace('\n', ' ').strip()[:150]
            
            img = card.find('img')
            thumb = ''
            if img:
                thumb = img.get('data-src', '') or img.get('src', '')
            
            if href and title and len(title) > 3:
                posts.append({'url': href, 'title': title, 'thumb': thumb})
        
        return posts
    except:
        return []

def extract_video_player(post_url, base):
    """Extract ONLY the video player URL from post page"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': base
    }
    
    try:
        response = requests.get(post_url, headers=headers, timeout=30)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        html_content = str(response.content)
        
        # Method 1: Find iframe with video player
        iframes = soup.find_all('iframe', src=True)
        
        for iframe in iframes:
            src = iframe.get('src', '').strip()
            
            if not src or not src.startswith('http'):
                continue
            
            # Skip ads
            if any(ad in src.lower() for ad in AD_DOMAINS):
                continue
            
            # Accept known video players
            if any(vd in src.lower() for vd in VIDEO_DOMAINS):
                return src
        
        # Method 2: Search HTML source for video URLs
        video_patterns = [
            r'https?://(?:' + '|'.join(VIDEO_DOMAINS) + r')[^\s"\'<>]+',
            r'"file"\s*:\s*"([^"]+\.m3u8[^"]*)"',
            r'"file"\s*:\s*"([^"]+\.mp4[^"]*)"'
        ]
        
        for pattern in video_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                url = matches[0] if isinstance(matches[0], str) else matches[0]
                if url.startswith('http'):
                    return url
        
        return None
        
    except:
        return None

def scrape_site(name, config):
    print(f"\n{'='*50}")
    print(f"🌐 {name.upper()}")
    print(f"{'='*50}")
    
    all_videos = []
    
    for page_url in config['pages']:
        print(f"\n📄 {page_url}")
        posts = get_posts(page_url, config['selector'])
        print(f"   {len(posts)} posts found")
        
        for idx, post in enumerate(posts[:5]):  # Limit 5 per page
            print(f"   {idx+1}/5: {post['title'][:40]}...")
            
            if not post['url'].startswith('http'):
                post['url'] = config['base'] + post['url']
            
            # EXTRACT REAL VIDEO PLAYER
            player_url = extract_video_player(post['url'], config['base'])
            
            if not player_url:
                print(f"      ❌ No player found")
                continue
            
            print(f"      ✅ Player: {player_url[:50]}...")
            
            video_id = f"{name}-{abs(hash(player_url)) % 1000000}"
            
            all_videos.append({
                'id': video_id,
                'title': post['title'],
                'description': f'Video from {name}',
                'category': name.capitalize(),
                'duration': '00:00',
                'embedUrl': player_url,  # NOW THIS IS THE PLAYER, NOT PAGE
                'thumbnailUrl': post['thumb'],
                'tags': [name],
                'uploadedAt': datetime.utcnow().isoformat() + 'Z',
                'views': 0
            })
            
            time.sleep(1.5)
        
        time.sleep(2)
    
    print(f"✅ {name}: {len(all_videos)} video players extracted")
    return all_videos

def main():
    print("🚀 UNIVERSAL SCRAPER - VIDEO PLAYERS ONLY")
    
    all_videos = []
    
    for name, config in SITES.items():
        try:
            videos = scrape_site(name, config)
            all_videos.extend(videos)
        except Exception as e:
            print(f"❌ {name} failed: {e}")
    
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
    
    print(f"\n✅ Total new players: {len(new_videos)}")
    print(f"✅ Total videos: {len(combined)}")

if __name__ == '__main__':
    main()
