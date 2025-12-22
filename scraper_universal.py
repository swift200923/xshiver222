# scraper_universal.py - WITH AD FILTERING
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import os

SITES = {
    'desikahani2': {
        'base': 'https://www.desikahani2.net',
        'pages': ['https://www.desikahani2.net/videos/'],
        'selector': 'div.item',
    },
    'viralkand': {
        'base': 'https://viralkand.com',
        'pages': ['https://viralkand.com/'],
        'selector': 'article.post',
    },
    'fsiblog5': {
        'base': 'https://www.fsiblog5.com',
        'pages': ['https://www.fsiblog5.com/'],
        'selector': 'article.post',
    },
}

# Ad domains to reject
AD_DOMAINS = [
    'doubleclick', 'googlesyndication', 'ads', 'adserver', 'banner',
    'popup', 'track', 'analytics', 'pixel', 'affiliate', 'promo',
    'sync', 'tag', 'impression', 'adnxs', 'adsystem', 'adform'
]

# Video player domains to accept
VIDEO_DOMAINS = [
    'streamtape', 'dood', 'mixdrop', 'streamlare', 'vidoza',
    'upstream', 'voe', 'filemoon', 'fembed', 'streamsb'
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

def extract_video(post_url, base):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Referer': base}
    
    try:
        response = requests.get(post_url, headers=headers, timeout=30)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find iframes
        iframes = soup.find_all('iframe', src=True)
        
        for iframe in iframes:
            src = iframe.get('src', '').strip()
            
            if not src or not src.startswith('http'):
                continue
            
            # Reject ads
            if any(ad in src.lower() for ad in AD_DOMAINS):
                continue
            
            # Accept known video players
            if any(vd in src.lower() for vd in VIDEO_DOMAINS):
                return src
        
        # Fallback
        return post_url
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
        print(f"   {len(posts)} posts")
        
        for idx, post in enumerate(posts[:5]):  # Limit 5 per page
            print(f"   {idx+1}/5: {post['title'][:40]}...")
            
            if not post['url'].startswith('http'):
                post['url'] = config['base'] + post['url']
            
            embed = extract_video(post['url'], config['base'])
            
            if not embed:
                continue
            
            video_id = f"{name}-{abs(hash(embed)) % 1000000}"
            
            all_videos.append({
                'id': video_id,
                'title': post['title'],
                'description': f'Video from {name}',
                'category': name.capitalize(),
                'duration': '00:00',
                'embedUrl': embed,
                'thumbnailUrl': post['thumb'],
                'tags': [name],
                'uploadedAt': datetime.utcnow().isoformat() + 'Z',
                'views': 0
            })
            
            time.sleep(1)
        
        time.sleep(2)
    
    print(f"✅ {name}: {len(all_videos)} videos")
    return all_videos

def main():
    print("🚀 UNIVERSAL SCRAPER (AD-FILTERED)")
    
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
    
    print(f"\n✅ Total new: {len(new_videos)}")
    print(f"✅ Total: {len(combined)}")

if __name__ == '__main__':
    main()
