#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
import os
import hashlib

BASE_URL = "https://viralkand.com"

def clean_title(title):
    title = title.replace("Viral video from viralkand.com", "")
    title = title.replace("- viralkand.com", "")
    title = title.replace("viralkand.com", "")
    return title.strip().strip("-").strip()

def main():
    print("=" * 60)
    print("SCRAPING VIRALKAND.COM")
    print("=" * 60)
    
    os.makedirs("data", exist_ok=True)
    
    # Load existing
    if os.path.exists("data/videos.json"):
        with open("data/videos.json", 'r') as f:
            videos = json.load(f)
        print(f"Loaded {len(videos)} existing videos")
    else:
        videos = []
        print("Starting fresh")
    
    existing_ids = {v['id'] for v in videos}
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    new_count = 0
    
    try:
        print(f"\nFetching: {BASE_URL}")
        response = requests.get(BASE_URL, headers=headers, timeout=15)
        print(f"Status: {response.status_code}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find video links
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if '/2024/' in href or '/2025/' in href:
                url = href if href.startswith('http') else BASE_URL + href
                if url not in links and BASE_URL in url:
                    links.append(url)
        
        print(f"Found {len(links)} video URLs\n")
        
        # Scrape each video
        for i, link in enumerate(links[:10], 1):
            try:
                print(f"[{i}/10] {link}")
                
                vid_id = "vid-" + hashlib.md5(link.encode()).hexdigest()[:10]
                
                if vid_id in existing_ids:
                    print("  ⏭️  Already exists\n")
                    continue
                
                r = requests.get(link, headers=headers, timeout=15)
                s = BeautifulSoup(r.content, 'html.parser')
                
                # Title
                h1 = s.find('h1')
                if h1:
                    title = clean_title(h1.get_text())
                else:
                    title_tag = s.find('title')
                    title = clean_title(title_tag.get_text()) if title_tag else "Video"
                
                print(f"  Title: {title[:50]}")
                
                # Iframe
                iframe = s.find('iframe')
                if not iframe:
                    print("  ❌ No iframe\n")
                    continue
                
                embed = iframe.get('src', '')
                if not embed:
                    print("  ❌ No embed URL\n")
                    continue
                
                if embed.startswith('//'):
                    embed = 'https:' + embed
                
                print(f"  Embed: {embed[:50]}...")
                
                # Thumbnail
                thumbnail = ""
                og_img = s.find('meta', property='og:image')
                if og_img:
                    thumbnail = og_img.get('content', '')
                
                # Category
                category = "Viral"
                cat = s.find('a', rel='category')
                if cat:
                    category = cat.get_text().strip()
                
                # Add
                videos.append({
                    "id": vid_id,
                    "title": title,
                    "description": title,
                    "thumbnailUrl": thumbnail,
                    "embedUrl": embed,
                    "category": category,
                    "duration": "10:00",
                    "tags": [category.lower()]
                })
                
                existing_ids.add(vid_id)
                new_count += 1
                
                print(f"  ✅ ADDED! Total new: {new_count}\n")
                
            except Exception as e:
                print(f"  ❌ Error: {e}\n")
                continue
        
        # Save
        if new_count > 0:
            with open("data/videos.json", 'w', encoding='utf-8') as f:
                json.dump(videos, f, indent=2, ensure_ascii=False)
            
            print("=" * 60)
            print(f"✅ SUCCESS - Scraped {new_count} new videos")
            print(f"Total videos: {len(videos)}")
            print("=" * 60)
        else:
            print("=" * 60)
            print("⚠️  No new videos found")
            print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
