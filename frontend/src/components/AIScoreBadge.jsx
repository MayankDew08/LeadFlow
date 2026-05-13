const config = {
  Hot: { label: '🔥 Hot', cls: 'bg-orange-50 text-orange-700 border-orange-200' },
  Warm: { label: '🌤️ Warm', cls: 'bg-amber-50 text-amber-700 border-amber-200' },
  Cold: { label: '🧊 Cold', cls: 'bg-slate-100 text-slate-600 border-slate-200' },
};

export default function AIScoreBadge({ score = 'Warm' }) {
  const item = config[score] || config.Warm;
  return <span className={`rounded-full border px-2.5 py-0.5 text-xs font-medium ${item.cls}`}>{item.label}</span>;
}
