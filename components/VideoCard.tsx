"use client"; 

import type { Video } from "./types";

type Props = {
  video: Video;
};

export default function VideoCard({ video }: Props) {
  return (
    <div className="group flex w-full flex-col overflow-hidden rounded-xl border border-slate-800 bg-slate-900/60 text-left shadow-sm transition hover:border-cyan-500/70 hover:bg-slate-900 cursor-pointer">
      <div className="relative aspect-video w-full overflow-hidden">
        <img
          src={video.thumbnailUrl}
          alt={video.title}
          className="h-full w-full object-cover transition-transform group-hover:scale-105"
        />
        <span className="absolute bottom-2 right-2 rounded bg-black/70 px-2 py-0.5 text-xs text-slate-50">
          {video.duration}
        </span>
      </div>
      <div className="flex flex-1 flex-col gap-1 px-3 py-3">
        <span className="line-clamp-2 text-sm font-medium text-slate-50">
          {video.title}
        </span>
        <span className="text-xs text-cyan-400">{video.category}</span>
        <span className="line-clamp-2 text-xs text-slate-400">
          {video.description}
        </span>
      </div>
    </div>
  );
}
