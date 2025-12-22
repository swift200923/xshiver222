const { chromium } = require('playwright');
const fs = require('fs');

async function scrapeVideos() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1366, height: 768 }
  });
  
  // REPLACE WITH YOUR SHADY SITE'S LISTING PAGE
  const targetUrl = 'https://your-shady-site.com/videos'; 
  const page = await context.newPage();
  
  // Wait for Cloudflare/ads to settle (key for shady sites)
  await page.goto(targetUrl, { waitUntil: 'networkidle' });
  await page.waitForTimeout(5000); // Let JS challenges complete
  
  // Click away any overlay ads (common on shady sites)
  await page.evaluate(() => {
    document.querySelectorAll('iframe, .popup, .overlay, .ad').forEach(el => el.remove());
  });
  
  // Find video cards → click to get embed
  const videos = await page.evaluate(() => {
    const items = Array.from(document.querySelectorAll('a[href*="/watch"], a[href*="/video"], .video-item'));
    return items.slice(0, 10).map(async (item, i) => {
      const href = item.href;
      const title = item.querySelector('h3, h2, .title')?.textContent?.trim() || 'Unknown';
      const thumb = item.querySelector('img')?.src || '';
      
      // Open detail page in new tab for embed
      window.open(href, '_blank');
      return { title, thumb, embed: href, id: i }; // Update embed selector below
    });
  });
  
  await browser.close();
  
  // Load existing, dedupe, save
  let existing = [];
  try { existing = JSON.parse(fs.readFileSync('data/videos.json', 'utf8')); } catch {}
  const uniqueVideos = videos.filter(v => 
    !existing.some(e => e.embed === v.embed)
  );
  
  fs.writeFileSync('data/videos.json', JSON.stringify([...existing, ...uniqueVideos], null, 2));
  console.log(`Added ${uniqueVideos.length} new videos`);
}

scrapeVideos();
