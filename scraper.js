// scraper.js (root)
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function scrapeSite(targetUrl) {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent:
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1366, height: 768 },
  });

  const page = await context.newPage();
  console.log('Opening', targetUrl);
  
  try {
    await page.goto(targetUrl, { waitUntil: 'networkidle', timeout: 30000 });
  } catch (e) {
    console.error('Failed to load', targetUrl, e.message);
    await browser.close();
    return [];
  }

  await page.waitForTimeout(5000);

  // remove ads/overlays
  await page.evaluate(() => {
    document
      .querySelectorAll(
        'iframe[src*="ads"], iframe[src*="ad"], .ad, .ads, .popup, .overlay, .modal, [class*="ad-"], [id*="ad-"]'
      )
      .forEach((el) => el.remove());
  });

  const videos = await page.evaluate(() => {
    const out = [];
    
    // Try multiple selectors for different site structures
    const cards = document.querySelectorAll(
      'article.post, article, .video-item, .post, a[href*="/video"], a[href*="/watch"]'
    );

    cards.forEach((card, index) => {
      // Get link
      const link = card.tagName === 'A' ? card : card.querySelector('a');
      if (!link) return;

      const href = link.href || link.getAttribute('href') || '';
      if (!href || href.includes('/tag/') || href.includes('/category/') || href.includes('/video-source/')) return;

      // Get title - try multiple selectors
      const titleEl =
        card.querySelector('h2.entry-title a') ||
        card.querySelector('h2.entry-title') ||
        card.querySelector('h1, h2, h3, h4') ||
        link.querySelector('h1, h2, h3, h4') ||
        card.querySelector('.title, .post-title');
      
      const rawTitle = titleEl?.textContent || titleEl?.innerText || '';
      const title = rawTitle.trim().replace(/\s+/g, ' ').replace(/Viral video from \w+\.com/gi, '');

      // Get thumbnail - try multiple sources
      const imgEl = 
        card.querySelector('img') || 
        link.querySelector('img');
      
      const thumb =
        imgEl?.getAttribute('data-src') ||
        imgEl?.getAttribute('data-lazy-src') ||
        imgEl?.src ||
        '';

      // Skip if it's a lazy-load placeholder SVG
      if (thumb.includes('data:image/svg') || !thumb) return;

      // Get category if available
      const categoryEl = card.querySelector('a[rel="category"], .cat-links a, .category a');
      const category = categoryEl?.textContent?.trim() || 'General';

      if (href && title) {
        out.push({
          id: `vid_${Date.now()}_${index}`,
          title: title.slice(0, 150),
          description: `Video from ${new URL(href).hostname}`,
          category: category,
          duration: '00:00',
          embedUrl: href,
          thumbnailUrl: thumb,
          tags: [new URL(href).hostname.replace('www.', '').split('.')[0]],
          uploadedAt: new Date().toISOString(),
          views: 0,
        });
      }
    });

    return out.slice(0, 20);
  });

  await browser.close();
  console.log(`Found ${videos.length} videos on ${targetUrl}`);
  return videos;
}

async function main() {
  const targetUrls = [
    // Add your target pages here
    'https://viralkand.com/page/2/',
    'https://www.fsiblog5.com/page/2/',
    // 'https://www.fsiblog5.com/page/3/',
  ];

  let allNew = [];
  for (const url of targetUrls) {
    try {
      const vids = await scrapeSite(url);
      allNew = allNew.concat(vids);
    } catch (e) {
      console.error('Error scraping', url, e);
    }
  }

  const filePath = path.join(__dirname, 'data', 'videos.json');
  let existing = [];
  try {
    existing = JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch {
    existing = [];
  }

  // Dedupe by embedUrl/url
  const combined = [...existing];
  allNew.forEach((v) => {
    if (!combined.some((e) => e.embedUrl === v.embedUrl || e.url === v.url || e.embedUrl === v.url)) {
      combined.push(v);
    }
  });

  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(combined, null, 2), 'utf8');
  console.log(`✅ Wrote ${combined.length} total videos (${allNew.length} new) to data/videos.json`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
