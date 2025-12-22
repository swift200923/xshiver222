// scraper.js — Cloudflare-safe extractor
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const URLS = [
  "https://viralkand.com/page/1/",
  "https://viralkand.com/page/2/",
  "https://www.fsiblog.cc/page/2/",
];

const OUT = path.join(__dirname, "data", "videos.json");

async function run() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent:
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
  });

  let results = [];

  for (const url of URLS) {
    const page = await context.newPage();
    console.log("Opening:", url);

    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 60000 });
    await page.waitForTimeout(8000);

    // ⬇️ scroll to trigger lazy loading
    await page.evaluate(() => {
      window.scrollTo(0, document.body.scrollHeight);
    });
    await page.waitForTimeout(4000);

    // ⬇️ extract from inline JSON / scripts
    const data = await page.evaluate(() => {
      const items = [];
      const scripts = Array.from(document.querySelectorAll("script"));

      for (const s of scripts) {
        const t = s.textContent || "";
        if (t.includes(".mp4") && t.includes("http")) {
          const mp4s = t.match(/https?:\/\/[^"' ]+\.mp4/g) || [];
          const imgs = t.match(/https?:\/\/[^"' ]+\.(jpg|jpeg|png)/g) || [];

          mp4s.forEach((mp4, i) => {
            items.push({
              embedUrl: mp4,
              thumbnailUrl: imgs[i] || "",
            });
          });
        }
      }
      return items;
    });

    const host = new URL(url).hostname.replace("www.", "");

    data.forEach((v, i) => {
      results.push({
        id: `vid-${host}-${Date.now()}-${i}`,
        title: `Viral video from ${host}`,
        description: `Auto scraped from ${host}`,
        category: "Viral",
        duration: "00:00",
        embedUrl: v.embedUrl,
        thumbnailUrl: v.thumbnailUrl,
        tags: [host, "viral"],
        uploadedAt: new Date().toISOString(),
        views: 0,
      });
    });

    console.log(`Extracted ${data.length} videos from ${url}`);
    await page.close();
  }

  await browser.close();

  let existing = [];
  try {
    existing = JSON.parse(fs.readFileSync(OUT, "utf8"));
  } catch {}

  const map = new Map();
  [...existing, ...results].forEach((v) => map.set(v.embedUrl, v));

  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, JSON.stringify([...map.values()], null, 2));

  console.log("Wrote", map.size, "videos");
}

run().catch(console.error);
