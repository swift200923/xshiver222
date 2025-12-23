# scraper_fsiblog.py - FSIBLOG.CC: scrape posts, extract clean iframe players
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import os
import re

BASE = "https://www.fsiblog.cc"
LIST_PAGES = [
    "https://www.fsiblog.cc/",
    "https://www.fsiblog.cc/page/2/",
    "https://www.fsiblog.cc/page/3/",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# Known video hosts used by fsiblog posts (mmsbaba + others).[web:53][web:59]
VIDEO_HOSTS = [
    "mmsbaba.co",
    "streamtape", "dood", "mixdrop", "streamlare", "vidoza",
    "upstream", "voe", "filemoon", "fembed", "streamsb",
    "videovard", "streamwish", "mp4upload", "sendvid",
]

# Ad / tracking domains to skip
AD_KEYWORDS = [
    "doubleclick", "googlesyndication", "adservice", "adsystem",
    "adserver", "banner", "track", "analytics", "pixel", "popunder",
]


def get_posts(list_url: str):
    """Go to fsiblog.cc listing page and collect post URLs + meta."""
    try:
        r = requests.get(list_url, headers=HEADERS, timeout=30)
        if r.status_code != 200:
            print(f"  Failed listing {list_url}: {r.status_code}")
            return []

        soup = BeautifulSoup(r.content, "html.parser")
        posts = []

        # fsiblog listing pages use <article> per post.[web:41][web:66]
        for art in soup.find_all("article"):
            a = art.find("a", href=True)
            if not a:
                continue

            href = a["href"].strip()
            if not href.startswith("http"):
                href = BASE.rstrip("/") + href

            # skip taxonomy pages
            if any(x in href for x in ["/tag/", "/category/"]):
                continue

            # title
            h = art.find(["h1", "h2", "h3"])
            title = (h.get_text(strip=True) if h else a.get("title") or "Video").strip()
            title = title.replace("\n", " ")[:150]

            # thumbnail
            img = art.find("img")
            thumb = ""
            if img:
                thumb = img.get("data-src") or img.get("src") or ""

            if href and title and len(title) > 3:
                posts.append({"url": href, "title": title, "thumb": thumb})

        print(f"  {list_url} -> {len(posts)} posts")
        return posts

    except Exception as e:
        print(f"  Error listing {list_url}: {e}")
        return []


def extract_clean_iframe(post_url: str):
    """
    Go to a single fsiblog post, find the real video iframe, and
    return a cleaned iframe URL that bypasses page ads.
    """
    try:
        r = requests.get(post_url, headers=HEADERS, timeout=30)
        if r.status_code != 200:
            print(f"    Post failed {r.status_code}")
            return None

        html = r.text
        soup = BeautifulSoup(html, "html.parser")

        # 1) Look for iframe elements
        for iframe in soup.find_all("iframe", src=True):
            src = iframe["src"].strip()

            if not src.startswith("http"):
                continue

            # skip obvious ad / tracking iframes
            if any(k in src.lower() for k in AD_KEYWORDS):
                continue

            # accept known video hosts
            if any(h in src.lower() for h in VIDEO_HOSTS):
                return src

        # 2) Fallback: search raw HTML for video host URLs
        pattern = r'https?://[^"\']+(?:' + "|".join(VIDEO_HOSTS) + r')[^"\']*'
        matches = re.findall(pattern, html, flags=re.IGNORECASE)
        for url in matches:
            if any(k in url.lower() for k in AD_KEYWORDS):
                continue
            return url

        print("    ❌ no player iframe found")
        return None

    except Exception as e:
        print(f"    Error post {post_url}: {e}")
        return None


def main():
    print("🔍 Scraping FSIBLOG.CC (clean iframes)")

    scraped = []

    for list_url in LIST_PAGES:
        print(f"\n📄 Listing: {list_url}")
        posts = get_posts(list_url)

        # Limit per page so you do not explode JSON
        for idx, post in enumerate(posts[:10]):
            print(f"   {idx+1}/{len(posts)}: {post['title'][:60]}")
            iframe_url = extract_clean_iframe(post["url"])
            if not iframe_url:
                continue

            print(f"      ✅ iframe: {iframe_url[:80]}")

            vid_hash = abs(hash(iframe_url)) % 1_000_000
            v = {
                "id": f"fsiblog-{vid_hash}",
                "title": post["title"],
                "description": "FSIBlog video",
                "category": "FSIBlog",
                "duration": "00:00",
                "embedUrl": iframe_url,          # this goes straight into your <iframe src=...>
                "thumbnailUrl": post["thumb"],
                "tags": ["fsiblog", "desi"],
                "uploadedAt": datetime.utcnow().isoformat() + "Z",
                "views": 0,
            }
            scraped.append(v)
            time.sleep(1)

        time.sleep(2)

    # merge with existing videos.json
    try:
        with open("data/videos.json", "r") as f:
            existing = json.load(f)
    except Exception:
        existing = []

    existing_urls = {v.get("embedUrl") for v in existing}
    new_items = [v for v in scraped if v["embedUrl"] not in existing_urls]

    combined = existing + new_items
    os.makedirs("data", exist_ok=True)
    with open("data/videos.json", "w") as f:
        json.dump(combined, f, indent=2)

    print(f"\n✅ New videos: {len(new_items)}")
    print(f"✅ Total videos: {len(combined)}")


if __name__ == "__main__":
    main()
