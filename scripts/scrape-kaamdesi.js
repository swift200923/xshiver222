import fs from "fs";
import path from "path";
import { chromium } from "playwright";

const BASE = "https://kaamdesi.com";
const PAGES = [
  `${BASE}/`,
  `${BASE}/page/2/`,
];

const DATA_PATH = path.resolve("data/videos.json");

function loadExisting() {
  try {
    return JSON.parse(fs.readFileSync(DATA_PATH, "utf8"));
  } catch {
    return [];
  }
}

function save(videos) {
  fs.writeFileSync(DATA_PATH, JSON.stringify(videos, null, 2));
}

function makeId(str) {
  return "vid-" + Buffer.from(str).toString("base64").slice(0, 32);
}

async function run() {
  console.log("🔍 Scraping kaamdesi.com (Playwright)");

  const existing = loadExisting();
  const seen = new Set(existing.map(v => v.embedUrl));
  const results = [...existing];

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({
    userAgent:
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
  });

  for (const url of PAGES) {
    console.log("📄 Opening:", url);
    await page.goto(url, { waitUntil: "networkidle", timeout: 60000 });
    await page.waitForTimeout(3000);

    const cards = await page.$$("a.video");
    console.log(`Found ${cards.length} cards`);

    for (const card of cards) {
      try {
        const href = await card.getAttribute("href");
        if (!href) continue;

        const postUrl = href.startsWith("http") ? href : BASE + href;

        const title =
          (await card.$eval(".vtitle", el => el.textContent?.trim()).catch(() => null)) ||
          (await card.getAttribute("title")) ||
          "Kaamdesi Video";

        const thumbnail =
          (await card.$eval("img", el => el.src).catch(() => "")) || "";

        const duration =
          (await card.$eval(".time.clock", el => el.textContent?.trim()).catch(() => "00:00")) ||
          "00:00";

        // open post page
        const post = await browser.newPage();
        await post.goto(postUrl, { waitUntil: "networkidle", timeout: 60000 });
        await post.waitForTimeout(2000);

        let embedUrl =
          (await post.$eval("iframe", el => el.src).catch(() => null)) ||
          (await post.$eval("video source", el => el.src).catch(() => null));

        await post.close();

        if (!embedUrl || seen.has(embedUrl)) continue;

        const video = {
          id: makeId(embedUrl),
          title,
          description: "Video from kaamdesi.com",
          category: "Viral",
          duration,
          embedUrl,
          thumbnailUrl: thumbnail,
          tags: ["kaamdesi"],
          uploadedAt: new Date().toISOString(),
          views: 0,
        };

        results.push(video);
        seen.add(embedUrl);
        console.log("➕ Added:", title.slice(0, 50));
      } catch {
        continue;
      }
    }
  }

  await browser.close();
  save(results);

  console.log(`✅ Done. Total videos: ${results.length}`);
}

run();
