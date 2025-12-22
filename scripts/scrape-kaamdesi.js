import fs from "fs";
import path from "path";
import fetch from "node-fetch";
import * as cheerio from "cheerio";

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

async function fetchHTML(url) {
  const res = await fetch(url, {
    headers: {
      "User-Agent": "Mozilla/5.0",
      "Referer": "https://google.com",
    },
  });
  return res.text();
}

async function scrapePost(postUrl) {
  const html = await fetchHTML(postUrl);
  const $ = cheerio.load(html);

  let embedUrl = "";

  $("iframe").each((_, el) => {
    const src = $(el).attr("src");
    if (src && !src.includes("ads")) {
      embedUrl = src.startsWith("//") ? "https:" + src : src;
      return false;
    }
  });

  if (!embedUrl) {
    $("video source").each((_, el) => {
      const src = $(el).attr("src");
      if (src) {
        embedUrl = src;
        return false;
      }
    });
  }

  return embedUrl || null;
}

async function run() {
  console.log("🔍 Scraping kaamdesi.com");

  const existing = loadExisting();
  const seen = new Set(existing.map(v => v.embedUrl));
  const results = [...existing];

  for (const page of PAGES) {
    console.log("📄 Listing:", page);

    const html = await fetchHTML(page);
    const $ = cheerio.load(html);

    const cards = $("a.video");

    console.log(`Found ${cards.length} cards`);

    for (let i = 0; i < cards.length; i++) {
      const el = cards.eq(i);

      const href = el.attr("href");
      if (!href) continue;

      const postUrl = href.startsWith("http") ? href : BASE + href;

      const title =
        el.find(".vtitle").text().trim() ||
        el.attr("title") ||
        "Kaamdesi Video";

      const thumbnail = el.find("img").attr("src") || "";

      const duration = el.find(".time.clock").text().trim() || "00:00";

      const embedUrl = await scrapePost(postUrl);
      if (!embedUrl || seen.has(embedUrl)) continue;

      const video = {
        id: makeId(embedUrl),
        title,
        description: `Video from kaamdesi.com`,
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
    }
  }

  save(results);
  console.log(`✅ Done. Total videos: ${results.length}`);
}

run();
