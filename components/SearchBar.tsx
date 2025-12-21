"use client";

type Props = {
  value: string;
  onChange: (value: string) => void;
};

export default function SearchBar({ value, onChange }: Props) { 
  return (
    <div className="w-full">
      <input
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder="Search videos..."
        className="w-full rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-sm text-slate-50 placeholder:text-slate-500 focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500"
      />
    </div>
  );
}
