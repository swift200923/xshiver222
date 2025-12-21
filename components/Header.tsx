"use client";

import { useState } from "react";
import SearchBar from "@/components/SearchBar";

type HeaderProps = {
  query: string;
  onQueryChange: (value: string) => void; 
};

export default function Header({ query, onQueryChange }: HeaderProps) {
  const [showSearch, setShowSearch] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <>
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setSidebarOpen(true)}
              className="mr-2 rounded-md border border-slate-700 bg-slate-900 px-2 py-1 text-xs text-slate-300 hover:bg-slate-800"
            >
              ☰
            </button>
            <div className="h-7 w-7 rounded-lg bg-gradient-to-br from-cyan-400 to-violet-500" />
            <span className="text-base font-semibold tracking-tight">
              Xshiver
            </span>
          </div>

          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setShowSearch(prev => !prev)}
              className="flex items-center gap-1 rounded-full border border-slate-700 bg-slate-900 px-3 py-1 text-xs text-slate-300 hover:bg-slate-800"
            >
              <span className="text-sm">🔍</span>
              <span className="hidden sm:inline">Search</span>
            </button>
          </div>
        </div>

        {showSearch && (
          <div className="border-t border-slate-800 bg-slate-950/95">
            <div className="mx-auto max-w-6xl px-4 py-3">
              <SearchBar value={query} onChange={onQueryChange} />
            </div>
          </div>
        )}
      </header>

      {/* Sidebar */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 flex">
          <div
            className="flex-1 bg-black/60"
            onClick={() => setSidebarOpen(false)}
          />
          <aside className="w-64 border-l border-slate-800 bg-slate-950 p-4 text-sm text-slate-200">
            <button
              type="button"
              onClick={() => setSidebarOpen(false)}
              className="mb-4 rounded-md bg-slate-900 px-2 py-1 text-xs text-slate-300 hover:bg-slate-800"
            >
              Close
            </button>
            <nav className="space-y-3">
              <a href="#about" className="block hover:text-cyan-400">
                About us
              </a>
              <a href="#contact" className="block hover:text-cyan-400">
                Contact us
              </a>
              <a href="#removal" className="block hover:text-cyan-400">
                Video removal
              </a>
              <a href="#instagram" className="block hover:text-cyan-400">
                Instagram
              </a>
            </nav>
          </aside>
        </div>
      )}
    </>
  );
}
