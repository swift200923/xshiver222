"use client";

import { useMemo, useState } from "react";
import Header from "@/components/Header";
import CategoryPills from "@/components/CategoryPills";
import VideoCard from "@/components/VideoCard";
import type { Video } from "@/components/types";
import videosData from "@/data/videos.json";

const allVideos = videosData as Video[];

export default function Page() {
  const [query, setQuery] = useState("");
  const [activeCategory, setActiveCategory] = useState<string>("All");

  const categories = useMemo(
    () => Array.from(new Set(allVideos.map(v => v.category))).sort(),
    []
  );

  const filteredVideos = useMemo(() => {
    const q = query.trim().toLowerCase();

    let videos: Video[] = allVideos;

    // Handle special filters
    if (activeCategory === "Top Viewed") {
      videos = [...videos].sort(
        (a, b) => (b.views ?? 0) - (a.views ?? 0)
      );
    } else if (activeCategory === "Latest") {
      videos = [...videos].sort(
        (a, b) =>
          new Date(b.uploadedAt).getTime() - new Date(a.uploadedAt).getTime()
      );
    } else if (activeCategory === "Instagram Viral") {
      videos = videos.filter(v =>
        v.tags?.some(t => t.toLowerCase().includes("instagram"))
      );
    } else if (activeCategory !== "All") {
      videos = videos.filter(v => v.category === activeCategory);
    }

    return videos.filter(video => {
      if (!q) return true;
      return (
        video.title.toLowerCase().includes(q) ||
        video.description.toLowerCase().includes(q) ||
        video.tags?.some(t => t.toLowerCase().includes(q))
      );
    });
  }, [query, activeCategory]);

  return (
    <div className="flex min-h-screen flex-col">
      <Header query={query} onQueryChange={setQuery} />

      <main className="mx-auto flex w-full max-w-6xl flex-1 flex-col gap-6 px-4 py-6">
        <section className="flex flex-col gap-2">
          <h1 className="text-2xl font-semibold tracking-tight">
            Chill, curated, no spam.
          </h1>
          <p className="text-sm text-slate-400">
            Browse Xshiver picks across Top Viewed, Latest drops, and Instagram
            Viral. No Telegram or Terabox garbage links – just clean embeds.
          </p>
        </section>

        <section className="flex flex-col gap-4">
          <CategoryPills
            categories={categories}
            active={activeCategory}
            onChange={setActiveCategory}
          />
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {filteredVideos.map(video => (
              <a key={video.id} href={`/video/${video.id}`}>
                <VideoCard video={video} />
              </a>
            ))}
            {filteredVideos.length === 0 && (
              <p className="col-span-full text-sm text-slate-400">
                Nothing matches your filters yet.
              </p>
            )}
          </div>
        </section>
      </main>

      <footer className="border-t border-slate-800 bg-slate-950/90">
        <div className="mx-auto flex max-w-6xl flex-col gap-4 px-4 py-5 text-xs text-slate-400 md:flex-row md:items-center md:justify-between">
          <div className="flex flex-wrap gap-3">
            <a id="about" href="#about" className="hover:text-cyan-400">
              About us
            </a>
            <a id="contact" href="#contact" className="hover:text-cyan-400">
              Contact us
            </a>
            <a id="removal" href="#removal" className="hover:text-cyan-400">
              Video removal
            </a>
            <a
              id="instagram"
              href="https://instagram.com"
              target="_blank"
              rel="noreferrer"
              className="hover:text-cyan-400"
            >
              Instagram
            </a>
          </div>
          <p className="text-[11px] text-slate-500">
            Xshiver only surfaces official embeds. No Telegram / Terabox links,
            no shady redirects.
          </p>
        </div>
      </footer>
    </div>
  );
}
