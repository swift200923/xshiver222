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
  await page.goto(targetUrl, { waitUntil: 'networkidle' });
  await page.waitForTimeout(5000);

  // remove shady overlays/ads
  await page.evaluate(() => {
    document
      .querySelectorAll(
        'iframe, .ad, .ads, .popup, .overlay, .modal, [class*="ad-"], [id*="ad-"]'
      )
      .forEach((el) => el.remove());
  });

  const videos = await page.evaluate(() => {
    const cards = document.querySelectorAll(
      'a[href*="/watch"], a[href*="/video"], a[href*="/play"], .video-item, article, .post'
    );

    const out = [];
    cards.forEach((card, index) => {
      const href = card.href || card.getAttribute('href') || '';
      const title =
        card.querySelector('h1,h2,h3,h4,.title')?.textContent?.trim() ||
        'No Title';

      const imgEl =
        card.querySelector('img') ||
        document.querySelector('meta[property="og:image"]');
      const thumb = imgEl?.src || imgEl?.content || '';

      // priority 1: iframe on card
      let embed = '';
      const iframe = card.querySelector(
        'iframe[src*="embed"], iframe[src*="player"], iframe[src*="video"]'
      );
      if (iframe) embed = iframe.src;

      // priority 2: detail page URL if no iframe
      if (!embed) embed = href;

      if (href) {
        out.push({
          id: `v_${Date.now()}_${index}`,
          title: title.slice(0, 120),
          thumbnail: thumb,
          embed,
          url: href,
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
    'https://www.fsiblog.cc/page/2/',
    'https://www.fsiblog.cc/page/3/',
    'https://www.fsiblog.cc/page/4/',
    'https://www.fsiblog.cc/page/5/',
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

  const combined = [...existing];
  allNew.forEach((v) => {
    if (!combined.some((e) => e.embed === v.embed || e.url === v.url)) {
      combined.push(v);
    }
  });

  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(combined, null, 2), 'utf8');
  console.log('Wrote', combined.length, 'videos to data/videos.json');
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
