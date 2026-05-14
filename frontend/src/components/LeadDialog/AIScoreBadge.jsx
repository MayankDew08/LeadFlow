import { Loader2, TrendingUp } from 'lucide-react';

const config = {
  Hot: { label: '🔥 Hot', cls: 'bg-orange-50 text-orange-700 border-orange-200' },
  Warm: { label: '🌤️ Warm', cls: 'bg-amber-50 text-amber-700 border-amber-200' },
  Cold: { label: '🧊 Cold', cls: 'bg-slate-100 text-slate-600 border-slate-200' },
};

export default function AIScoreBadge({ score, reason, loading, onClick }) {
  if (!score) {
    return (
      <button
        type="button"
        onClick={onClick}
        disabled={loading}
        className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-50 px-3 py-1.5 text-sm font-medium text-indigo-700 transition-colors hover:bg-indigo-100 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <TrendingUp className="h-4 w-4" />}
        {loading ? 'Scoring...' : 'Score Lead'}
      </button>
    );
  }

  const item = config[score] || config.Warm;

  return (
    <button
      type="button"
      onClick={onClick}
      title={reason || ''}
      disabled={loading}
      className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium disabled:opacity-60 ${item.cls}`}
    >
      {loading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : null}
      {item.label}
    </button>
  );
}
