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
    // fsiblog: each video is an <article class="post">
    const cards = document.querySelectorAll('article.post');

    const out = [];
    cards.forEach((card, index) => {
      const link = card.querySelector('a');
      if (!link) return;

      const href = link.href || link.getAttribute('href') || '';

      // title usually in h2.entry-title > a
      const titleEl =
        card.querySelector('h2.entry-title a') ||
        card.querySelector('h2.entry-title') ||
        card.querySelector('h2, h3');
      const rawTitle = titleEl?.textContent || '';
      const title = rawTitle.trim().replace(/\s+/g, ' ');

      // thumbnail from <img> (data-src or src)
      const imgEl = card.querySelector('img') || link.querySelector('img');
      const thumb =
        imgEl?.getAttribute('data-src') ||
        imgEl?.src ||
        '';

      // For now use post URL as embed target
      const embed = href;

      if (href) {
        out.push({
          id: `fsi_${Date.now()}_${index}`,
          title: title || 'Untitled',
          thumbnail: thumb,
          embed,
          url: href,
        });
      }
    });

    // limit per page
    return out.slice(0, 20);
  });

  await browser.close();
  console.log(`Found ${videos.length} videos on ${targetUrl}`);
  return videos;
}

async function main() {
  const targetUrls = [
    'https://www.fsiblog5.com/',
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

  // dedupe by embed/url
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
