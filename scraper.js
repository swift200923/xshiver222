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

  // kill overlays/ads
  await page.evaluate(() => {
    document
      .querySelectorAll(
        'iframe, .ad, .ads, .popup, .overlay, .modal, [class*="ad-"], [id*="ad-"]'
      )
      .forEach((el) => el.remove());
  });

  const videos = await page.evaluate(() => {
    // fsiblog: each video is an <article> with a link+thumb+title
    const cards = document.querySelectorAll('article');

    const out = [];
    cards.forEach((card, index) => {
      const link = card.querySelector('a');
      if (!link) return;

      const href = link.href || link.getAttribute('href') || '';
      const titleEl =
        card.querySelector('h2, h3, .entry-title, .title') ||
        link.querySelector('h2, h3');
      const title =
        titleEl?.textContent?.trim().replace(/\s+/g, ' ') || 'No Title';

      const imgEl = card.querySelector('img');
      const thumb = imgEl?.src || imgEl?.getAttribute('data-src') || '';

      // fsiblog uses MMSBaba embeds on detail page,
      // but for now we just store the post URL as embed target
      const embed = href;

      if (href) {
        out.push({
          id: `fsi_${Date.now()}_${index}`,
          title: title.slice(0, 120),
          thumbnail: thumb,
          embed,
          url: href,
        });
      }
    });

    // return up to 20 videos from this page
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
