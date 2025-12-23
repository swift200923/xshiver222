import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import time
import os
import git

# ALL SITES CONFIG
SITES = {
    'desikahani2': {
        'pages': ['https://www.desikahani2.net/videos/', 'https://www.desikahani2.net/videos/?page=2'],
        'card_selector': 'div.item, article, .post, div[class*="video"]'
    },
    'fsiblog5': {
        'pages': ['https://www.fsiblog5.com/', 'https://www.fsiblog5.com/page/2/'],
        'card_selector': 'article.post, article, .post'
    },
    'viralkand': {
        'pages': ['https://viralkand.com/', 'https://viralkand.com/page/2/'],
        'card_selector': 'article.post, article, .post'
    },
    'desibf': {
        'pages': ['https://desibf.com/', 'https://desibf.com/page/2/'],
        'card_selector': 'article, .post, div[class*="video"]'
    },
    'kamababa': {
        'pages': ['https://www.kamababa.desi/', 'https://www.kamababa.desi/page/2/'],
        'card_selector': 'article, .post, div[class*="video"]'
    }
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_video_links(page_url, site_name):
    """Get video post links from listing page"""
    try:
        print(f"📄 Scraping listing: {page_url}")
        response = requests.get(page_url, headers=HEADERS, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        links = []
        site_config = SITES[site_name]
        
        # Try multiple selectors
        for selector in site_config['card_selector'].split(', '):
            cards = soup.select(selector.strip())
            print(f"  '{selector.strip()}': {len(cards)} cards")
            
            for card in cards[:10]:  # Max 10 per selector
                link = card.find('a', href=True)
                if link:
                    href = link.get('href', '').strip()
                    if href and not href.startswith('#') and 'page' not in href:
                        links.append(href)
                        if len(links) >= 15:  # Max 15 per page
                            break
            if len(links) >= 15:
                break
                
        print(f"  → Found {len(links)} video links")
        return list(set(links))[:15]  # Dedupe
        
    except Exception as e:
        print(f"❌ Listing error: {e}")
        return []

def extract_video_embed(video_url):
    """Visit video page → extract REAL player iframe/video src"""
    try:
        print(f"  🎥 Visiting: {video_url}")
        response = requests.get(video_url, headers=HEADERS, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Priority 1: Find iframe src with video domains
        iframes = soup.find_all('iframe', src=True)
        for iframe in iframes:
            src = iframe.get('src', '')
            if any(domain in src.lower() for domain in ['embed', 'player', 'video', 'mp4']):
                if not any(ad in src.lower() for ad in ['ads', 'googleads', 'doubleclick']):
                    print(f"    ✅ Found embed: {src[:80]}...")
                    return src
        
        # Priority 2: Direct video URLs
        video_sources = soup.find_all('source', src=True) + soup.find_all('video', src=True)
        for source in video_sources:
            src = source.get('src', '')
            if src.endswith('.mp4') or 'video' in src:
                print(f"    ✅ Found direct video: {src[:80]}...")
                return src
        
        # Priority 3: Return video page URL
        print(f"    ⚠️ Using page URL as embed")
        return video_url
        
    except Exception as e:
        print(f"    ❌ Video page error: {e}")
        return video_url

def scrape_site(site_name):
    """Scrape entire site"""
    print(f"\n🚀 SCRAPING {site_name.upper()}")
    all_videos = []
    
    site_config = SITES[site_name]
    for page_url in site_config['pages']:
        video_links = get_video_links(page_url, site_name)
        
        for video_url in video_links:
            embed_url = extract_video_embed(video_url)
            
            # Extract title/thumbnail from video page
            try:
                response = requests.get(video_url, headers=HEADERS, timeout=20)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                title = (soup.find('h1') or soup.find('title') or soup.find('h2'))
                title = title.get_text(strip=True)[:150] if title else f"{site_name} Video"
                
                img = soup.find('meta', property='og:image') or soup.find('img')
                thumb = img.get('content') if img and img.get('content') else img.get('src') if img else ''
                
            except:
                title = f"{site_name} Video"
                thumb = ''
            
            video_id = re.sub(r'[^a-z0-9-]', '-', title.lower())[:40]
            all_videos.append({
                'id': f"{site_name}-{video_id}",
                'title': title,
                'description': f"Video from {site_name}",
                'category': site_name.capitalize(),
                'duration': '00:00',
                'embedUrl': embed_url,
                'thumbnailUrl': thumb,
                'tags': [site_name, 'desi', 'video'],
                'uploadedAt': datetime.utcnow().isoformat() + 'Z',
                'views': 0
            })
            
            time.sleep(1)  # Polite delay
        
        time.sleep(2)
    
    print(f"✅ {site_name}: {len(all_videos)} videos")
    return all_videos

def save_and_push():
    os.makedirs('data', exist_ok=True)
    
    # Load existing
    try:
        with open('data/videos.json', 'r') as f:
            existing = json.load(f)
    except:
        existing = []
    
    all_new_videos = []
    
    # Scrape ALL sites
    for site_name in SITES.keys():
        new_videos = scrape_site(site_name)
        all_new_videos.extend(new_videos)
        time.sleep(3)
    
    # Dedupe
    existing_ids = {v['id'] for v in existing}
    unique_new = [v for v in all_new_videos if v['id'] not in existing_ids]
    combined = existing + unique_new
    
    # Save
    with open('data/videos.json', 'w') as f:
        json.dump(combined, f, indent=2)
    
    print(f"\n🎉 TOTAL: {len(unique_new)} NEW videos")
    print(f"🎉 GRAND TOTAL: {len(combined)} videos")
    
    # Git push
    repo = git.Repo('.')
    repo.git.config('user.name', 'swift200923')
    repo.git.config('user.email', 'swift200923@gmail.com')
    
    repo.index.add(['data/videos.json'])
    if repo.index.diff('HEAD'):
        repo.index.commit("update all sites videos [skip ci]")
        repo.git.push('origin', 'main')
        print("✅ PUSHED TO GITHUB!")
    else:
        print("No new changes")

if __name__ == '__main__':
    save_and_push()
