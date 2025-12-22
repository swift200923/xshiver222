import fs from "fs";
import path from "path";
import fetch from "node-fetch";
import * as cheerio from "cheerio";

const BASE = "https://kaamdesi.com";
const LISTING_PAGES = [
  `${BASE}/`,
  `${BASE}/page/2/`
];

const DATA_PATH = path.resolve("data/videos.json");

function loadExisting() {
  try {
    return JSON.parse(fs.readFileSync(DATA_PATH, "utf-8"));
  } catch {
    return [];
  }
}

function saveAll(videos) {
  fs.writeFileSync(DATA_PATH, JSON.stringify(videos, null, 2));
}

function uidFromUrl(url) {
  return "vid-" + Buffer.from(url).toString("base64").slice(0, 20);
}

async function fetchHTML(url) {
  const res = await fetch(url, {
    headers: {
      "User-Agent": "Mozilla/5.0",
      "Referer": "https://google.com"
    }
  });
  return res.text();
}

async function scrapePost(postUrl) {
  const html = await fetchHTML(postUrl);
  const $ = cheerio.load(html);

  const title =
    $('meta[property="og:title"]').attr("content") ||
    $("h1").first().text().trim() ||
    "Untitled Video";

  const thumbnail =
    $('meta[property="og:image"]').attr("content") ||
    "";

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

  if (!embedUrl) return null;

  return {
    id: uidFromUrl(embedUrl),
    title,
    description: `Video from kaamdesi.com`,
    category: "Viral",
    duration: "00:00",
    embedUrl,
    thumbnailUrl: thumbnail,
    tags: ["kaamdesi", "viral"],
    uploadedAt: new Date().toISOString(),
    views: 0
  };
}

async function run() {
  console.log("🔍 Scraping kaamdesi.com");

  const existing = loadExisting();
  const seen = new Set(existing.map(v => v.embedUrl));
  const results = [...existing];

  for (const page of LISTING_PAGES) {
    console.log("📄 Listing:", page);
    const html = await fetchHTML(page);
    const $ = cheerio.load(html);

    const links = new Set();

    $("a[href]").each((_, el) => {
      const href = $(el).attr("href");
      if (href && href.includes("kaamdesi.com") && !href.includes("/page/")) {
        links.add(href.endsWith("/") ? href : href + "/");
      }
    });

    for (const link of Array.from(links).slice(0, 20)) {
      try {
        const video = await scrapePost(link);
        if (video && !seen.has(video.embedUrl)) {
          results.push(video);
          seen.add(video.embedUrl);
          console.log("➕ Added:", video.title.slice(0, 40));
        }
      } catch {
        continue;
      }
    }
  }

  saveAll(results);
  console.log(`✅ Done. Total videos: ${results.length}`);
}

run();
