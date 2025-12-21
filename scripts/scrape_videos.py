import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import re
import time

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
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://google.com",
        }
        
        print(f"Fetching listing: {listing_url}")
        resp = requests.get(listing_url, headers=headers, timeout=30)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # WordPress typically uses <article> tags or post links
        # Look for links to post pages
        for link in soup.find_all("a", href=True):
            href = link["href"]
            
            # Filter: only viralkand.com posts (not category/tag/page links)
            if "viralkand.com" in href and all(skip not in href for skip in ["/page/", "/category/", "/tag/", "/author/"]):
                if href.endswith("/") and href not in post_urls:
                    post_urls.append(href)
        
        print(f"  Found {len(post_urls)} post links")
        return post_urls
        
    except Exception as e:
        print(f"Error fetching {listing_url}: {e}")
        return []

def extract_video_from_post(post_url):
    """Extract video embed from a single post page."""
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://viralkand.com",
        }
        
        print(f"  Scraping: {post_url}")
        resp = requests.get(post_url, headers=headers, timeout=30)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Extract title from og:title meta tag
        title = "Untitled Video"
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"][:100]
        
        # Extract thumbnail from og:image
        thumbnail = "https://via.placeholder.com/480x360.png?text=Video"
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            thumbnail = og_image["content"]
        
        # Find video embed - look for iframe or video tag
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
        
        # Strategy 2: Look for HTML5 video tag
        if not embed_url:
            video_tag = soup.find("video")
            if video_tag:
                source = video_tag.find("source")
                if source and source.get("src"):
                    embed_url = source["src"]
        
        if not embed_url:
            print(f"    No video found on {post_url}")
            return None
        
        # Generate video ID from URL slug
        slug_match = re.search(r"/([^/]+)/$", post_url)
        video_id = slug_match.group(1) if slug_match else f"vid-{abs(hash(post_url)) % 100000}"
        
        return {
            "id": f"vid-{video_id[:50]}",
            "title": title,
            "description": f"Viral video from viralkand.com",
            "category": "Viral",
            "duration": "00:00",
            "embedUrl": embed_url,
            "thumbnailUrl": thumbnail,
            "tags": ["viralkand", "viral"],
            "uploadedAt": datetime.now(timezone.utc).isoformat(),
            "views": 0
        }
        
    except Exception as e:
        print(f"    Error on {post_url}: {e}")
        return None

def scrape_all():
    """Main scraper."""
    all_videos = []
    
    # Step 1: Collect post URLs
    all_post_urls = []
    for listing_url in LISTING_PAGES:
        urls = get_video_post_urls(listing_url)
        all_post_urls.extend(urls)
        time.sleep(2)
    
    all_post_urls = list(set(all_post_urls))
    print(f"\nTotal posts to scrape: {len(all_post_urls)}")
    
    # Step 2: Extract video from each post (limit to 30 per run)
    for post_url in all_post_urls[:30]:
        video = extract_video_from_post(post_url)
        if video:
            all_videos.append(video)
        time.sleep(1.5)
    
    # Remove duplicates
    seen = set()
    unique_videos = []
    for v in all_videos:
        if v["embedUrl"] not in seen:
            seen.add(v["embedUrl"])
            unique_videos.append(v)
    
    print(f"\nTotal unique videos: {len(unique_videos)}")
    
    # Save
    with open("data/videos.json", "w", encoding="utf-8") as f:
        json.dump(unique_videos, f, ensure_ascii=False, indent=2)
    
    print("✓ Saved to data/videos.json")

if __name__ == "__main__":
    scrape_all()
