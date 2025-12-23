# scraper_fsiblog.py - FSIBLOG.CC SCRAPER (MMSBABA EMBED)
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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

MMS_EMBED_TEMPLATE = "https://mmsbaba.co/embed.php?id={video_id}"  # from webmaster docs[web:33]


def get_posts(list_url: str):
    """Scrape listing page for post links, titles, thumbs."""
    try:
        r = requests.get(list_url, headers=HEADERS, timeout=30)
        if r.status_code != 200:
            print(f"  Failed listing {list_url}: {r.status_code}")
            return []

        soup = BeautifulSoup(r.content, "html.parser")
        posts = []

        # FSIBlog uses <article class="post"> on listing pages.[web:28][web:41]
        for art in soup.find_all("article"):
            a = art.find("a", href=True)
            if not a:
                continue

            href = a["href"].strip()
            if not href.startswith("http"):
                href = BASE.rstrip("/") + href

            # Skip non-post links
            if any(x in href for x in ["/tag/", "/category/", "/page/"]):
                continue

            # Title
            h = art.find(["h1", "h2", "h3"])
            title = (h.get_text(strip=True) if h else a.get("title") or "Video").strip()
            title = title.replace("\n", " ")[:150]

            # Thumbnail
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


def extract_video_id(post_url: str):
    """
    FSIBlog’s webmaster page shows the official embed format:
      <iframe src="https://mmsbaba.co/embed.php?id=VIDEO_ID">[web:33]
    Most posts include either that iframe or a link containing ?id=VIDEO_ID.
    """
    try:
        r = requests.get(post_url, headers=HEADERS, timeout=30)
        if r.status_code != 200:
            print(f"    Post failed {r.status_code}")
            return None

        html = r.text
        soup = BeautifulSoup(html, "html.parser")

        # 1) Direct iframe embed with mmsbaba.co
        for iframe in soup.find_all("iframe", src=True):
            src = iframe["src"].strip()
            if "mmsbaba.co" in src:
                m = re.search(r"id=([a-zA-Z0-9_-]+)", src)
                if m:
                    return m.group(1)

        # 2) Any link or script containing mmsbaba embed
        m = re.search(r"https?://mmsbaba\.co/embed\.php\?id=([a-zA-Z0-9_-]+)", html)
        if m:
            return m.group(1)

        # 3) Fallback: generic id=XYZ pattern used for video id
        m = re.search(r"id=([a-zA-Z0-9]{3,10})", html)
        if m:
            return m.group(1)

        print("    ❌ no VIDEO_ID found")
        return None

    except Exception as e:
        print(f"    Error post {post_url}: {e}")
        return None


def main():
    print("🔍 Scraping FSIBLOG.CC (MMSBABA embeds)")

    scraped = []

    for list_url in LIST_PAGES:
        print(f"\n📄 Listing: {list_url}")
        posts = get_posts(list_url)

        for idx, post in enumerate(posts[:10]):  # cap per page
            print(f"   {idx+1}/{len(posts)}: {post['title'][:60]}")

            vid_id = extract_video_id(post["url"])
            if not vid_id:
                continue

            embed_url = MMS_EMBED_TEMPLATE.format(video_id=vid_id)
            print(f"      ✅ {embed_url}")

            v = {
                "id": f"fsiblog-{vid_id}",
                "title": post["title"],
                "description": "FSIBlog video",
                "category": "FSIBlog",
                "duration": "00:00",
                "embedUrl": embed_url,
                "thumbnailUrl": post["thumb"],
                "tags": ["fsiblog", "desi"],
                "uploadedAt": datetime.utcnow().isoformat() + "Z",
                "views": 0,
            }
            scraped.append(v)
            time.sleep(1)

        time.sleep(2)

    # merge with existing JSON
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
