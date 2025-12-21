import { notFound } from "next/navigation";
import type { Metadata } from "next";
import VideoCard from "@/components/VideoCard";
import type { Video } from "@/components/types";
import videosData from "@/data/videos.json";

const allVideos = videosData as Video[];

type Props = {
  params: Promise<{ id: string }>;
};

export function generateStaticParams() {
  return allVideos.map(video => ({
    id: video.id
  }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const video = allVideos.find(v => v.id === id);
  if (!video) return { title: "Video not found – Xshiver" };
  return {
    title: `${video.title} – Xshiver`,
    description: video.description
  };
}

export default async function VideoPage({ params }: Props) {
  const { id } = await params;
  const video = allVideos.find(v => v.id === id);

  if (!video) {
    notFound();
  }

  const recommendations = allVideos
    .filter(v => v.id !== video.id && v.category === video.category)
    .slice(0, 6);

  return (
    <div className="flex min-h-screen flex-col">
      {/* Static header for video pages */}
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
          <a href="/" className="flex items-center gap-2">
            <div className="h-7 w-7 rounded-lg bg-gradient-to-br from-cyan-400 to-violet-500" />
            <span className="text-base font-semibold tracking-tight">
              Xshiver
            </span>
          </a>
          <a
            href="/"
            className="rounded-full border border-slate-700 bg-slate-900 px-3 py-1 text-xs text-slate-300 hover:bg-slate-800"
          >
            ← Back to home
          </a>
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-6xl flex-1 flex-col gap-6 px-4 py-6">
        <section className="grid gap-6 lg:grid-cols-[2fr,1.2fr]">
          {/* Main video */}
          <div className="space-y-3">
            <div className="aspect-video w-full rounded-2xl border border-slate-800 bg-black">
              <iframe
                src={video.embedUrl}
                title={video.title}
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                allowFullScreen
                className="h-full w-full rounded-2xl"
              />
            </div>
            <h1 className="text-xl font-semibold">{video.title}</h1>
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

          {/* Recommendations */}
          <aside className="space-y-3">
            <h2 className="text-sm font-semibold text-slate-200">
              More from Xshiver
            </h2>
            <div className="grid gap-3">
              {recommendations.length === 0 && (
                <p className="text-xs text-slate-500">
                  No more videos in this category yet.
                </p>
              )}
              {recommendations.map(v => (
                <a key={v.id} href={`/video/${v.id}`} className="block">
                  <VideoCard video={v} />
                </a>
              ))}
            </div>
          </aside>
        </section>
      </main>
    </div>
  );
}
