# scraper_universal.py - Universal scraper for ALL sites
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import os
import re

# All sites to scrape
SITES = {
    'desikahani2': {
        'base': 'https://www.desikahani2.net',
        'pages': ['https://www.desikahani2.net/videos/', 'https://www.desikahani2.net/videos/?page=2'],
        'card_selector': 'div.item',
    },
    'viralkand': {
        'base': 'https://viralkand.com',
        'pages': ['https://viralkand.com/', 'https://viralkand.com/page/2/'],
        'card_selector': 'article.post',
    },
    'fsiblog5': {
        'base': 'https://www.fsiblog5.com',
        'pages': ['https://www.fsiblog5.com/', 'https://www.fsiblog5.com/page/2/'],
        'card_selector': 'article.post',
    },
    'mydesi': {
        'base': 'https://mydesi.click',
        'pages': ['https://mydesi.click/', 'https://mydesi.click/page/2/'],
        'card_selector': 'article',
    },
    'fsiblog': {
        'base': 'https://www.fsiblog.cc',
        'pages': ['https://www.fsiblog.cc/', 'https://www.fsiblog.cc/page/2/'],
        'card_selector': 'article',
    },
    'kamababa': {
        'base': 'https://www.kamababa.desi',
        'pages': ['https://www.kamababa.desi/', 'https://www.kamababa.desi/page/2/'],
        'card_selector': 'article',
    },
    'desibf': {
        'base': 'https://desibf.com',
        'pages': ['https://desibf.com/', 'https://desibf.com/page/2/'],
        'card_selector': 'article',
    },
}

def get_video_cards(page_url, selector):
    """Step 1: Get all video post URLs from a listing page"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    try:
        response = requests.get(page_url, headers=headers, timeout=30)
        if response.status_code != 200:
            print(f"    ⚠️ Failed {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        cards = soup.select(selector) or soup.find_all('article') or soup.select('div.post')
        
        posts = []
        for card in cards:
            link = card.find('a', href=True)
            if not link:
                continue
            
            href = link.get('href', '').strip()
            if not href or href.startswith('#') or '/tag/' in href or '/category/' in href:
                continue
            
            # Get title
            title = link.get('title', '').strip()
            if not title or len(title) < 3:
                h_tag = card.find(['h1', 'h2', 'h3'])
                if h_tag:
                    title = h_tag.get_text(strip=True)
            if not title or len(title) < 3:
                title = link.get_text(strip=True)
            
            title = title.replace('\n', ' ').strip()[:150]
            
            # Get thumbnail
            img = card.find('img')
            thumb = ''
            if img:
                thumb = img.get('data-src', '') or img.get('src', '') or img.get('data-original', '')
            
            if href and title and len(title) > 3:
                posts.append({'url': href, 'title': title, 'thumb': thumb})
        
        return posts
        
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return []

def extract_video_embed(post_url, base_url):
    """Step 2: Visit video post page and extract iframe/video src"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': base_url
    }
    
    try:
        response = requests.get(post_url, headers=headers, timeout=30)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try iframe first (most common for embeds)
        iframes = soup.find_all('iframe', src=True)
        for iframe in iframes:
            src = iframe.get('src', '').strip()
            # Skip ad iframes
            if src and 'http' in src and not any(x in src.lower() for x in ['ad', 'banner', 'popup', 'track', 'analytics']):
                return src
        
        # Try video tag
        video = soup.find('video')
        if video:
            source = video.find('source', src=True)
            if source:
                return source.get('src')
        
        # Fallback: return post URL itself
        return post_url
        
    except:
        return None

def scrape_site(site_name, site_config):
    """Scrape one site"""
    print(f"\n{'='*60}")
    print(f"🌐 Scraping: {site_name.upper()}")
    print(f"{'='*60}")
    
    all_videos = []
    
    for page_url in site_config['pages']:
        print(f"\n📄 {page_url}")
        posts = get_video_cards(page_url, site_config['card_selector'])
        print(f"   Found {len(posts)} posts")
        
        for idx, post in enumerate(posts[:10]):  # Limit 10 per page to avoid timeout
            print(f"   {idx+1}/10: {post['title'][:50]}...")
            
            # Make absolute URL
            if not post['url'].startswith('http'):
                post['url'] = site_config['base'] + post['url']
            
            # Extract video embed URL
            embed_url = extract_video_embed(post['url'], site_config['base'])
            
            if not embed_url:
                print(f"      ❌ No video URL")
                continue
            
            video_id = f"{site_name}-{abs(hash(embed_url)) % 1000000}"
            
            all_videos.append({
                'id': video_id,
                'title': post['title'],
                'description': f'Video from {site_name}',
                'category': site_name.capitalize(),
                'duration': '00:00',
                'embedUrl': embed_url,
                'thumbnailUrl': post['thumb'],
                'tags': [site_name],
                'uploadedAt': datetime.utcnow().isoformat() + 'Z',
                'views': 0
            })
            
            time.sleep(1)  # Polite delay
        
        time.sleep(2)  # Delay between pages
    
    print(f"\n✅ {site_name}: {len(all_videos)} videos scraped")
    return all_videos

def main():
    print("🚀 UNIVERSAL VIDEO SCRAPER STARTED")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_videos = []
    
    # Scrape each site
    for site_name, site_config in SITES.items():
        try:
            videos = scrape_site(site_name, site_config)
            all_videos.extend(videos)
        except Exception as e:
            print(f"❌ {site_name} failed: {e}")
            continue
    
    # Load existing videos
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
    
    print(f"\n{'='*60}")
    print(f"✅ SCRAPING COMPLETE")
    print(f"{'='*60}")
    print(f"📊 New videos: {len(new_videos)}")
    print(f"📊 Total videos: {len(combined)}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
