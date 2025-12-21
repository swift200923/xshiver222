 "use client";

import type { Video } from "./types";

type Props = {
  video: Video | null;
  onClose: () => void;
};

export default function VideoDetail({ video, onClose }: Props) {
  if (!video) return null;

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/70 px-4">
      <div className="relative w-full max-w-4xl overflow-hidden rounded-2xl border border-slate-700 bg-slate-950 shadow-xl">
        <button
          type="button"
          onClick={onClose}
          className="absolute right-3 top-3 rounded-full bg-black/60 px-3 py-1 text-xs text-slate-200 hover:bg-black/80"
        >
          Close
        </button>
        <div className="aspect-video w-full bg-black">
          <iframe
            src={video.embedUrl}
            title={video.title}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowFullScreen
            className="h-full w-full"
          />
        </div>
        <div className="space-y-2 px-4 py-3">
          <h2 className="text-lg font-semibold">{video.title}</h2>
          <p className="text-sm text-slate-300">{video.description}</p>
          <div className="flex flex-wrap gap-2 text-xs text-slate-400">
            <span className="rounded-full bg-slate-800 px-2 py-0.5">
              {video.category}
            </span>
            {video.tags?.map(tag => (
              <span
                key={tag}
                className="rounded-full bg-slate-800 px-2 py-0.5"
              >
                #{tag}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
