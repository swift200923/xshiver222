import fs from "fs";
import path from "path";
import { chromium } from "playwright";

/* ===================== CONFIG ===================== */

const BASE = "https://desimyhub.net";
const PAGES = [
  `${BASE}/latest/`,
  `${BASE}/latest/page/2/`,
];

/* Blocked ad / junk domains */
const BLOCKED_SRC = [
  "ads",
  "doubleclick",
  "googlesyndication",
  "afcdn",
  "pop",
  "traffic",
];

/* ===================== FILE ===================== */

const DATA_PATH = path.resolve("data/videos.json");

/* ===================== HELPERS ===================== */

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

function isBlocked(url = "") {
  return BLOCKED_SRC.some(b => url.toLowerCase().includes(b));
}

/* ===================== MAIN ===================== */

async function run() {
  console.log("▶ Scraper started");

  const existing = loadExisting();
  const seen = new Set(existing.map(v => v.embedUrl));
  const results = [...existing];

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent:
      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
  });

  const page = await context.newPage();

  /* 🚫 BLOCK ADS / TRACKERS */
  await page.route("**/*", route => {
    const url = route.request().url();
    if (BLOCKED_SRC.some(b => url.includes(b))) {
      return route.abort();
    }
    route.continue();
  });

  for (const url of PAGES) {
    console.log("📄 Listing:", url);

    await page.goto(url, {
      waitUntil: "domcontentloaded",
      timeout: 30000,
    });

    await page.waitForTimeout(2000);

    /* UNIVERSAL CARD SELECTOR */
    let cards = await page.$$("a.video");
    if (!cards.length) cards = await page.$$("article a[href]");
    if (!cards.length) cards = await page.$$(".post a[href]");
    if (!cards.length) cards = await page.$$("a[href]");

    console.log(`Found ${cards.length} cards`);

    for (const card of cards) {
      try {
        const href = await card.getAttribute("href");
        if (!href || href.startsWith("#")) continue;

        const postUrl = href.startsWith("http") ? href : BASE + href;

        /* TITLE */
        const title =
          (await card.$eval("h1", el => el.textContent.trim()).catch(() => null)) ||
          (await card.$eval("h2", el => el.textContent.trim()).catch(() => null)) ||
          (await card.$eval("h3", el => el.textContent.trim()).catch(() => null)) ||
          (await card.getAttribute("title")) ||
          "Video";

        /* THUMB */
        const thumbnail =
          (await card.$eval("img", el => el.src).catch(() => "")) || "";

        /* DURATION */
        const duration =
          (await card
            .$eval(".time, .clock, .duration", el => el.textContent.trim())
            .catch(() => "00:00")) || "00:00";

        /* OPEN POST PAGE */
        const post = await context.newPage();

        await post.route("**/*", route => {
          const url = route.request().url();
          if (BLOCKED_SRC.some(b => url.includes(b))) {
            return route.abort();
          }
          route.continue();
        });

        await post.goto(postUrl, {
          waitUntil: "domcontentloaded",
          timeout: 30000,
        });

        await post.waitForTimeout(2000);

        /* EMBED EXTRACTION */
        let embedUrl = null;

        const iframeUrls = await post.$$eval("iframe", els =>
          els.map(el => el.src).filter(Boolean)
        );

        embedUrl = iframeUrls.find(src => !isBlocked(src)) || null;

        if (!embedUrl) {
          const videoUrls = await post.$$eval("video source", els =>
            els.map(el => el.src).filter(Boolean)
          );
          embedUrl = videoUrls.find(src => !isBlocked(src)) || null;
        }

        await post.close();

        if (!embedUrl || seen.has(embedUrl)) continue;

        results.push({
          id: makeId(embedUrl),
          title,
          description: `Video from ${new URL(BASE).hostname}`,
          category: "Viral",
          duration,
          embedUrl,
          thumbnailUrl: thumbnail,
          tags: [new URL(BASE).hostname],
          uploadedAt: new Date().toISOString(),
          views: 0,
        });

        seen.add(embedUrl);
        console.log("➕ Added:", title.slice(0, 60));
      } catch (err) {
        console.log("⚠️ Skipped one card");
        continue;
      }
    }
  }

  await browser.close();
  save(results);

  console.log(`✅ Done. Total videos: ${results.length}`);
}

/* ⏱ HARD SAFETY EXIT */
setTimeout(() => {
  console.error("⏱ Forced exit to prevent hang");
  process.exit(0);
}, 4 * 60 * 1000);

run();
