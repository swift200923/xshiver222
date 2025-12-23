import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

def scrape_desibf(max_pages=5):
    base_url = "https://desibf.com/page/{}"
    all_videos = []
    
    for page in range(1, max_pages + 1):
        url = base_url.format(page)
        print(f'Page {page}...')
        try:
            response = requests.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all('article') or soup.find_all('div', class_='post')
            
            for article in articles:
                try:
                    title_elem = article.find('h2') or article.find('h3') or article.find('a')
                    title = title_elem.get_text(strip=True) if title_elem else 'Untitled'
                    link_elem = article.find('a', href=True)
                    link = link_elem['href'] if link_elem else ''
                    img_elem = article.find('img', src=True)
                    thumbnail = img_elem['src'] if img_elem else ''
                    video_id = f'desibf-{link.split("/")[-2] if "/" in link else title.lower().replace(" ", "-")}'
                    
                    all_videos.append({
                        'id': video_id,
                        'title': title,
                        'description': 'Video from desibf',
                        'category': 'Desibf',
                        'duration': '00:00',
                        'embedUrl': link,
                        'thumbnailUrl': thumbnail,
                        'tags': ['desibf', 'desi', 'video'],
                        'uploadedAt': datetime.now().isoformat() + 'Z',
                        'views': 0
                    })
                except: pass
            time.sleep(2)
        except Exception as e: print(f'Error: {e}')
    
    all_videos.reverse()
    return all_videos

if __name__ == '__main__':
    videos = scrape_desibf(5)
    with open('data/videos.json', 'w', encoding='utf-8') as f:
        json.dump(videos, f, indent=2, ensure_ascii=False)
    print(f'Done! {len(videos)} videos saved')
