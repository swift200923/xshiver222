#!/usr/bin/env python3
"""
Viralkand scraper - Gets thumbnails + direct MP4 URLs
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import re
import time
import os

LISTING_PAGES = [
    "https://viralkand.com/"
]

def get_post_urls(listing_url):
    """Get all post URLs from listing page."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        
        print(f"\n📄 {listing_url}")
        resp = requests.get(listing_url, headers=headers, timeout=30)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "html.parser")
        post_urls = []
        
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "viralkand.com" in href and all(skip not in href for skip in ["/page/", "/category/", "/tag/", "/author/"]):
                if href.endswith("/") and href not in post_urls:
                    post_urls.append(href)
        
        print(f"   Found {len(post_urls)} posts")
        return post_urls
        
    except Exception as e:
        print(f"   Error: {e}")
        return []


def scrape_video(post_url):
    """Extract video data from post."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://viralkand.com",
        }
        
        print(f"  🔍 {post_url}")
        resp = requests.get(post_url, headers=headers, timeout=30)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Get title
        title = "Video"
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"][:100]
        
        # Get thumbnail
        thumbnail = ""
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            thumbnail = og_image["content"]
        
        # Get MP4 URL - Strategy 1: video tag
        embed_url = None
        video_tag = soup.find("video")
        if video_tag:
            source = video_tag.find("source")
            if source and source.get("src"):
                embed_url = source["src"]
        
        # Strategy 2: iframe
        if not embed_url:
            for iframe in soup.find_all("iframe"):
                src = iframe.get("src")
                if src and not any(ad in src.lower() for ad in ["doubleclick", "googlesyndication"]):
                    embed_url = src if src.startswith("http") else ("https:" + src if src.startswith("//") else "")
                    break
        
        if not embed_url:
            print(f"     ❌ No video")
            return None
        
        # Generate ID
        slug_match = re.search(r"/([^/]+)/$", post_url)
        video_id = slug_match.group(1) if slug_match else f"vid-{abs(hash(post_url)) % 100000}"
        
        print(f"     ✅ {title[:40]}")
        
        return {
            "id": f"vid-{video_id[:50]}",
            "title": title,
            "description": "Viral video from viralkand.com",
            "category": "Viral",
            "duration": "00:00",
            "embedUrl": embed_url,
            "thumbnailUrl": thumbnail,
            "tags": ["viralkand", "viral"],
            "uploadedAt": datetime.now(timezone.utc).isoformat(),
            "views": 0
        }
        
    except Exception as e:
        print(f"     ❌ {e}")
        return None


def main():
    print("=" * 70)
    print("🚀 VIRALKAND SCRAPER")
    print("=" * 70)
    
    os.makedirs("data", exist_ok=True)
    
    # Collect post URLs
    all_urls = []
    for listing in LISTING_PAGES:
        urls = get_post_urls(listing)
        all_urls.extend(urls)
        time.sleep(2)
    
    all_urls = list(set(all_urls))
    print(f"\n📊 Total: {len(all_urls)} posts")
    
    # Scrape videos
    videos = []
    for i, url in enumerate(all_urls[:30], 1):
        print(f"\n[{i}/30]")
        video = scrape_video(url)
        if video:
            videos.append(video)
        time.sleep(1.5)
    
    # Remove duplicates
    seen = set()
    unique = []
    for v in videos:
        if v["embedUrl"] not in seen:
            seen.add(v["embedUrl"])
            unique.append(v)
    
    print("\n" + "=" * 70)
    print(f"✅ Scraped {len(unique)} videos")
    print("=" * 70)
    
    # Save
    with open("data/videos.json", "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)
    
    print("\n💾 Saved to data/videos.json")


if __name__ == "__main__":
    main()
