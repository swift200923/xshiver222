const { chromium } = require('playwright');
const fs = require('fs');

async function scrapeVideos() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    viewport: { width: 1366, height: 768 }
  });
  
  const targetUrl = 'https://viralkand.com/'; // CHANGE THIS
  const page = await context.newPage();
  
  await page.goto(targetUrl, { waitUntil: 'networkidle' });
  await page.waitForTimeout(5000);
  
  // Kill ALL shady ads first
  await page.evaluate(() => {
    document.querySelectorAll('iframe, .ad, .popup, .overlay, .modal, [class*="ad-"]').forEach(el => el.remove());
  });
  
  const videos = await page.evaluate(() => {
    const results = [];
    const cards = document.querySelectorAll('a[href*="/watch"], a[href*="/video"], a[href*="/play"], .video-item, article, .post');
    
    cards.forEach((card, index) => {
      const href = card.href || card.getAttribute('href');
      const title = card.querySelector('h1,h2,h3,h4,.title')?.textContent?.trim() || 'No Title';
      const thumb = card.querySelector('img')?.src || 
                   document.querySelector('meta[property="og:image"]')?.content || '';
      
      // PRIORITY 1: Direct embed iframe on listing page
      let embed = '';
      const iframes = card.querySelectorAll('iframe[src*="embed"], iframe[src*="player"]');
      if (iframes.length) {
        embed = iframes[0].src;
      }
      
      // PRIORITY 2: Detail page URL (for sites without direct embeds)
      if (!embed) {
        embed = href;
      }
      
      results.push({
        title: title.slice(0, 100),
        thumbnail: thumb,
        embed: embed,
        url: href,
        id: `v${Date.now()}${index}`
      });
    });
    
    return results.slice(0, 15);
  });
  
  await browser.close();
  
  // Dedupe + save
  let existing = [];
  try { existing = JSON.parse(fs.readFileSync('data/videos.json', 'utf8')); } catch (e) {}
  const newVideos = videos.filter(v => 
    !existing.some(e => e.embed === v.embed || e.url === v.url)
  );
  
  fs.writeFileSync('data/videos.json', JSON.stringify([...existing, ...newVideos], null, 2));
  console.log(`✅ Found ${videos.length} videos, added ${newVideos.length} new ones`);
  console.log('Sample:', JSON.stringify(newVideos.slice(0,2), null, 2));
}

scrapeVideos();
