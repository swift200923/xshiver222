# scraper.py
import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import time

def scrape_viralkand(page_num):
    url = f"https://viralkand.com/page/{page_num}/" if page_num > 1 else "https://viralkand.com/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"Failed to fetch {url}: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        videos = []
        
        # Find all article posts
        articles = soup.find_all('article', class_='post')
        print(f"Found {len(articles)} articles on page {page_num}")
        
        for article in articles:
            link = article.find('a')
            if not link:
                continue
                
            href = link.get('href', '')
            
            # Get title
            title_tag = article.find('h2', class_='entry-title')
            if title_tag:
                title = title_tag.get_text(strip=True)
                title = re.sub(r'Viral video from viralkand\.com', '', title).strip()
            else:
                continue
            
            # Get thumbnail
            img = article.find('img')
            thumb = img['src'] if img and 'src' in img.attrs else ''
            
            # Get category
            cat_link = article.find('a', rel='category')
            category = cat_link.get_text(strip=True) if cat_link else 'Viral'
            
            if href and title:
                video_id = href.rstrip('/').split('/')[-1]
                videos.append({
                    'id': f'vid-{video_id}',
                    'title': title[:150],
                    'description': 'Viral video from viralkand.com',
                    'category': category,
                    'duration': '00:00',
                    'embedUrl': href,
                    'thumbnailUrl': thumb,
                    'tags': ['viralkand', 'viral'],
                    'uploadedAt': datetime.utcnow().isoformat() + 'Z',
                    'views': 0
                })
        
        return videos
        
    except Exception as e:
        print(f"Error scraping page {page_num}: {e}")
        return []

def main():
    all_videos = []
    
    # Scrape 10 pages
    for page in range(1, 11):
        print(f"\nScraping page {page}...")
        videos = scrape_viralkand(page)
        all_videos.extend(videos)
        time.sleep(2)  # Delay between requests
    
    # Load existing
    try:
        with open('data/videos.json', 'r') as f:
            existing = json.load(f)
    except:
        existing = []
    
    # Dedupe
    existing_ids = {v['id'] for v in existing}
    new_videos = [v for v in all_videos if v['id'] not in existing_ids]
    
    combined = existing + new_videos
    
    # Save
    import os
    os.makedirs('data', exist_ok=True)
    with open('data/videos.json', 'w') as f:
        json.dump(combined, f, indent=2)
    
    print(f"\n✅ Scraped {len(new_videos)} new videos from 10 pages")
    print(f"✅ Total videos: {len(combined)}")

if __name__ == '__main__':
    main()
