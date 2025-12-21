"use client";

type Props = {
  categories: string[];
  active: string;
  onChange: (cat: string) => void;
};
 
const STATIC_FILTERS = ["Top Viewed", "Latest", "Instagram Viral"];

export default function CategoryPills({ categories, active, onChange }: Props) {
  const dynamic = Array.from(new Set(categories)).sort();
  const all = ["All", ...STATIC_FILTERS, ...dynamic];

  return (
    <div className="flex flex-wrap gap-2">
      {all.map(cat => {
        const isActive = cat === active;
        return (
          <button
            key={cat}
            type="button"
            onClick={() => onChange(cat)}
            className={`rounded-full px-3 py-1 text-xs font-medium transition ${
              isActive
                ? "bg-cyan-500 text-slate-950"
                : "bg-slate-800 text-slate-300 hover:bg-slate-700"
            }`}
          >
            {cat}
          </button>
        );
      })}
    </div>
  );
}
