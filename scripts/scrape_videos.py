#!/usr/bin/env python3
"""
COMPLETE VIRALKAND SCRAPER - NO FALLBACK, REAL SCRAPING ONLY
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import re
import time
import os

# Target pages - homepage and category pages
LISTING_PAGES = [
    "https://viralkand.com/",
    "https://viralkand.com/page/2/",
    "https://viralkand.com/page/3/",
]

def get_video_post_urls(listing_url):
    """Extract all video post URLs from a listing page."""
    post_urls = []
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        
        print(f"\n📄 Fetching listing: {listing_url}")
        response = requests.get(listing_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Find all links with year patterns (WordPress style)
        for link in soup.find_all("a", href=True):
            href = link["href"]
            # Match URLs like /2024/12/video-title/ or /2025/01/video-title/
            if re.search(r"/\d{4}/\d{2}/", href):
                if href.startswith("http"):
                    full_url = href
                elif href.startswith("/"):
                    full_url = "https://viralkand.com" + href
                else:
                    full_url = "https://viralkand.com/" + href
                
                if full_url not in post_urls:
                    post_urls.append(full_url)
        
        print(f"   Found {len(post_urls)} video URLs")
        return post_urls
        
    except Exception as e:
        print(f"   ❌ Error fetching listing: {e}")
        return []


def clean_title(title):
    """Remove site name and unwanted text from titles."""
    unwanted = [
        "Viral video from viralkand.com",
        "- viralkand.com",
        "viralkand.com",
        "| viralkand",
    ]
    
    for phrase in unwanted:
        title = title.replace(phrase, "")
    
    # Clean whitespace
    title = re.sub(r"\s+", " ", title).strip()
    title = title.strip("-").strip("|").strip()
    
    return title if title else "Untitled Video"


def scrape_video_data(video_url):
    """Scrape data from a single video page."""
    try:
        print(f"\n🔍 Scraping: {video_url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(video_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Extract title
        title = "Untitled"
        h1_tag = soup.find("h1")
        if h1_tag:
            title = clean_title(h1_tag.get_text())
        else:
            title_tag = soup.find("title")
            if title_tag:
                title = clean_title(title_tag.get_text())
        
        print(f"   Title: {title[:60]}")
        
        # Extract iframe embed URL
        iframe = soup.find("iframe")
        if not iframe or not iframe.get("src"):
            print(f"   ❌ No iframe found, skipping")
            return None
        
        embed_url = iframe["src"]
        
        # Fix protocol
        if embed_url.startswith("//"):
            embed_url = "https:" + embed_url
        
        print(f"   Embed: {embed_url[:60]}...")
        
        # Extract thumbnail
        thumbnail_url = ""
        og_image = soup.find("meta", property="og:image")
        if og_image:
            thumbnail_url = og_image.get("content", "")
        
        if not thumbnail_url:
            twitter_image = soup.find("meta", attrs={"name": "twitter:image"})
            if twitter_image:
                thumbnail_url = twitter_image.get("content", "")
        
        # Extract category
        category = "Viral"
        category_link = soup.find("a", rel="category")
        if category_link:
            category = category_link.get_text().strip()
        
        # Generate unique ID
        video_id = "vid-" + str(abs(hash(video_url)))[:12]
        
        video_data = {
            "id": video_id,
            "title": title,
            "description": title,
            "thumbnailUrl": thumbnail_url,
            "embedUrl": embed_url,
            "category": category,
            "duration": "10:00",
            "tags": [category.lower()],
        }
        
        print(f"   ✅ Successfully scraped!")
        return video_data
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def main():
    print("=" * 70)
    print("🚀 VIRALKAND SCRAPER - STARTING")
    print("=" * 70)
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Load existing videos
    videos_file = "data/videos.json"
    existing_videos = []
    existing_ids = set()
    
    if os.path.exists(videos_file):
        try:
            with open(videos_file, "r", encoding="utf-8") as f:
                existing_videos = json.load(f)
                existing_ids = {v["id"] for v in existing_videos}
            print(f"📚 Loaded {len(existing_videos)} existing videos")
        except Exception as e:
            print(f"⚠️  Error loading existing videos: {e}")
            existing_videos = []
    else:
        print("📝 No existing videos found, starting fresh")
    
    # Collect all video URLs from listing pages
    all_video_urls = []
    for listing_page in LISTING_PAGES:
        urls = get_video_post_urls(listing_page)
        all_video_urls.extend(urls)
        time.sleep(2)  # Be polite
    
    # Remove duplicates
    all_video_urls = list(set(all_video_urls))
    print(f"\n📊 Total unique video URLs found: {len(all_video_urls)}")
    
    if len(all_video_urls) == 0:
        print("\n❌ CRITICAL: No video URLs found!")
        print("The site structure may have changed or is blocking scraping.")
        return 1
    
    # Scrape each video
    new_videos_count = 0
    max_new_videos = 15
    
    for video_url in all_video_urls:
        if new_videos_count >= max_new_videos:
            print(f"\n✋ Reached limit of {max_new_videos} new videos")
            break
        
        # Generate ID to check if exists
        temp_id = "vid-" + str(abs(hash(video_url)))[:12]
        if temp_id in existing_ids:
            print(f"\n⏭️  Skipping (already exists): {video_url}")
            continue
        
        video_data = scrape_video_data(video_url)
        
        if video_data:
            existing_videos.append(video_data)
            existing_ids.add(video_data["id"])
            new_videos_count += 1
            print(f"   📈 New videos added: {new_videos_count}/{max_new_videos}")
        
        time.sleep(2)  # Be polite
    
    # Save videos
    if new_videos_count > 0:
        with open(videos_file, "w", encoding="utf-8") as f:
            json.dump(existing_videos, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 70)
        print(f"✅ SUCCESS!")
        print(f"   New videos scraped: {new_videos_count}")
        print(f"   Total videos: {len(existing_videos)}")
        print(f"   Saved to: {videos_file}")
        print("=" * 70)
        return 0
    else:
        print("\n" + "=" * 70)
        print("⚠️  NO NEW VIDEOS ADDED")
        print("All found videos already exist in database")
        print("=" * 70)
        return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
