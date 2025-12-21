"use client";

import { useMemo, useState } from "react";
import Header from "@/components/Header";
import CategoryPills from "@/components/CategoryPills";
import VideoCard from "@/components/VideoCard";
import type { Video } from "@/components/types";
import videosData from "@/data/videos.json";

const allVideos = videosData as Video[];
const VIDEOS_PER_PAGE = 12;

export default function Page() {
  const [query, setQuery] = useState("");
  const [activeCategory, setActiveCategory] = useState<string>("All");
  const [currentPage, setCurrentPage] = useState(1);

  const categories = useMemo(
    () => Array.from(new Set(allVideos.map(v => v.category))).sort(),
    []
  );

  const filteredVideos = useMemo(() => {
    const q = query.trim().toLowerCase();
    let videos: Video[] = allVideos;

    if (activeCategory === "Top Viewed") {
      videos = [...videos].sort((a, b) => (b.views ?? 0) - (a.views ?? 0));
    } else if (activeCategory === "Latest") {
      videos = [...videos].reverse();
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

  useMemo(() => {
    setCurrentPage(1);
  }, [query, activeCategory]);

  const totalPages = Math.ceil(filteredVideos.length / VIDEOS_PER_PAGE);
  const paginatedVideos = filteredVideos.slice(
    (currentPage - 1) * VIDEOS_PER_PAGE,
    currentPage * VIDEOS_PER_PAGE
  );

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
          
          <div className="grid grid-cols-2 gap-3 md:gap-4">
            {paginatedVideos.map(video => (
              <a key={video.id} href={`/video/${video.id}`}>
                <VideoCard video={video} />
              </a>
            ))}
            {filteredVideos.length === 0 && (
              <p className="col-span-2 text-center text-sm text-slate-400 py-8">
                Nothing matches your filters yet.
              </p>
            )}
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 pt-4">
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-xs md:text-sm text-slate-300 hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition"
              >
                ← Prev
              </button>
              
              <span className="text-xs md:text-sm text-slate-400 px-2">
                {currentPage} / {totalPages}
              </span>
              
              <button
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-xs md:text-sm text-slate-300 hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition"
              >
                Next →
              </button>
            </div>
          )}
        </section>
      </main>

      <footer className="border-t border-slate-800 bg-slate-950/90 mt-auto">
        <div className="mx-auto flex max-w-6xl flex-col gap-6 px-4 py-8">
          <div className="grid grid-cols-2 gap-6 md:grid-cols-4">
            <div className="flex flex-col gap-2">
              <h3 className="text-sm font-semibold text-slate-300">Company</h3>
              <a href="#about" className="text-xs text-slate-400 hover:text-cyan-400 transition">About Us</a>
              <a href="#contact" className="text-xs text-slate-400 hover:text-cyan-400 transition">Contact</a>
            </div>
            
            <div className="flex flex-col gap-2">
              <h3 className="text-sm font-semibold text-slate-300">Support</h3>
              <a href="#removal" className="text-xs text-slate-400 hover:text-cyan-400 transition">Video Removal</a>
              <a href="#dmca" className="text-xs text-slate-400 hover:text-cyan-400 transition">DMCA</a>
            </div>
            
            <div className="flex flex-col gap-2">
              <h3 className="text-sm font-semibold text-slate-300">Legal</h3>
              <a href="#privacy" className="text-xs text-slate-400 hover:text-cyan-400 transition">Privacy Policy</a>
              <a href="#terms" className="text-xs text-slate-400 hover:text-cyan-400 transition">Terms of Service</a>
            </div>
            
            <div className="flex flex-col gap-2">
              <h3 className="text-sm font-semibold text-slate-300">Follow Us</h3>
              <div className="flex gap-3">
                <a href="https://instagram.com" target="_blank" rel="noreferrer" className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-purple-500 via-pink-500 to-orange-400 text-white hover:scale-110 transition-transform">
                  <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
                </a>
              </div>
            </div>
          </div>
          <div className="border-t border-slate-800 pt-6">
            <p className="text-center text-xs text-slate-500">© 2025 Xshiver. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
