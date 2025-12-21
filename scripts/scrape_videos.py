#!/usr/bin/env python3
"""
Viralkand.com video scraper - extracts direct MP4 links
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import re
import time
import os

# Target listing pages to scrape
LISTING_PAGES = [
    "https://viralkand.com",
]

def get_video_post_urls(listing_url):
    """Get all post URLs from a listing page."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        
        print(f"\n📄 Fetching: {listing_url}")
        resp = requests.get(listing_url, headers=headers, timeout=30)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "html.parser")
        post_urls = []
        
        # Look for post links (skip category/tag/page links)
        for link in soup.find_all("a", href=True):
            href = link["href"]
            # Only viralkand.com posts
            if "viralkand.com" in href and all(skip not in href for skip in ["/page/", "/category/", "/tag/", "/author/"]):
                if href.endswith("/") and href not in post_urls:
                    post_urls.append(href)
        
        print(f"   Found {len(post_urls)} post links")
        return post_urls
        
    except Exception as e:
        print(f"   Error: {e}")
        return []


def extract_video_from_post(post_url):
    """Extract video data from a post page."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://viralkand.com",
        }
        
        print(f"  🔍 {post_url}")
        resp = requests.get(post_url, headers=headers, timeout=30)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Extract title
        title = "Untitled Video"
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"][:100]
        
        # Extract thumbnail
        thumbnail = ""
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            thumbnail = og_image["content"]
        
        # Find video embed
        embed_url = None
        
        # Strategy 1: Look for iframe
        for iframe in soup.find_all("iframe"):
            src = iframe.get("src")
            if not src:
                continue
            # Skip ads
            if any(ad in src.lower() for ad in ["doubleclick", "googlesyndication", "adserver", "ads"]):
                continue
            embed_url = src if src.startswith("http") else ("https:" + src if src.startswith("//") else "")
            break
        
        # Strategy 2: Look for HTML5 video tag (direct MP4)
        if not embed_url:
            video_tag = soup.find("video")
            if video_tag:
                source = video_tag.find("source")
                if source and source.get("src"):
                    embed_url = source["src"]
        
        if not embed_url:
            print(f"     ❌ No video found")
            return None
        
        # Generate ID from URL slug
        slug_match = re.search(r"/([^/]+)/$", post_url)
        video_id = slug_match.group(1) if slug_match else f"vid-{abs(hash(post_url)) % 100000}"
        
        print(f"     ✅ {title[:50]}")
        
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
        print(f"     ❌ Error: {e}")
        return None


def scrape_all():
    """Main scraper function."""
    print("=" * 70)
    print("🚀 VIRALKAND SCRAPER STARTING")
    print("=" * 70)
    
    os.makedirs("data", exist_ok=True)
    
    all_videos = []
    
    # Step 1: Collect all post URLs
    all_post_urls = []
    for listing_url in LISTING_PAGES:
        urls = get_video_post_urls(listing_url)
        all_post_urls.extend(urls)
        time.sleep(2)  # Be polite
    
    all_post_urls = list(set(all_post_urls))  # Remove duplicates
    print(f"\n📊 Total posts found: {len(all_post_urls)}")
    
    # Step 2: Extract videos from each post (limit 30 per run)
    for i, post_url in enumerate(all_post_urls[:30], 1):
        print(f"\n[{i}/30]")
        video = extract_video_from_post(post_url)
        if video:
            all_videos.append(video)
        time.sleep(1.5)  # Be polite
    
    # Remove duplicate embeds
    seen = set()
    unique_videos = []
    for v in all_videos:
        if v["embedUrl"] not in seen:
            seen.add(v["embedUrl"])
            unique_videos.append(v)
    
    print("\n" + "=" * 70)
    print(f"✅ SUCCESS!")
    print(f"   Scraped: {len(unique_videos)} unique videos")
    print("=" * 70)
    
    # Save to JSON
    with open("data/videos.json", "w", encoding="utf-8") as f:
        json.dump(unique_videos, f, ensure_ascii=False, indent=2)
    
    print("\n💾 Saved to data/videos.json")


if __name__ == "__main__":
    scrape_all()
