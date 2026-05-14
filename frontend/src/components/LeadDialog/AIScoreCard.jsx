import { AlertCircle, Loader2, RefreshCw } from 'lucide-react';

const SCORE_META = {
  Hot: {
    emoji: '🔥',
    label: 'Hot Lead',
    meaning: 'High priority — engage today',
    bgClass: 'bg-orange-50',
    borderClass: 'border-orange-200',
    textClass: 'text-orange-900',
    accentClass: 'text-orange-700',
    iconBgClass: 'bg-orange-100',
    action: 'Call or email this lead today. They\'re showing strong buying signals.',
  },
  Warm: {
    emoji: '🌤️',
    label: 'Warm Lead',
    meaning: 'Active — nurture this week',
    bgClass: 'bg-amber-50',
    borderClass: 'border-amber-200',
    textClass: 'text-amber-900',
    accentClass: 'text-amber-700',
    iconBgClass: 'bg-amber-100',
    action: 'Schedule a follow-up within the week. Continue building the relationship.',
  },
  Cold: {
    emoji: '🧊',
    label: 'Cold Lead',
    meaning: 'Low engagement — re-engage or deprioritize',
    bgClass: 'bg-slate-50',
    borderClass: 'border-slate-200',
    textClass: 'text-slate-900',
    accentClass: 'text-slate-700',
    iconBgClass: 'bg-slate-100',
    action: 'Try a re-engagement message or move focus to higher-priority leads.',
  },
};

export default function AIScoreCard({ data, loading, onRefresh }) {
  if (data?.ai_available === false) {
    return (
      <div className="mt-3 rounded-lg border border-gray-200 bg-gray-50 p-4">
        <p className="flex items-center gap-2 text-sm text-gray-500">
          <AlertCircle className="h-4 w-4" />
          Lead scoring temporarily unavailable
        </p>
      </div>
    );
  }

  const meta = SCORE_META[data?.score] || SCORE_META.Warm;

  return (
    <div className={`mt-3 rounded-lg border p-4 ${meta.bgClass} ${meta.borderClass}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className={`h-10 w-10 rounded-full text-lg flex items-center justify-center ${meta.iconBgClass}`}>
            {meta.emoji}
          </div>
          <div>
            <div className={`text-sm font-semibold ${meta.textClass}`}>{meta.label}</div>
            <div className={`text-xs ${meta.accentClass}`}>{meta.meaning}</div>
          </div>
        </div>
        <button type="button" aria-label="Refresh score" onClick={onRefresh} className="rounded p-1 hover:bg-white/50" disabled={loading}>
          {loading ? <Loader2 className="h-4 w-4 animate-spin text-gray-400" /> : <RefreshCw className="h-4 w-4 text-gray-400" />}
        </button>
      </div>

      <div className={`mt-3 border-t border-current/10 pt-3 ${meta.textClass}`}>
        <p className={`mb-1 text-xs font-semibold uppercase tracking-wider ${meta.accentClass}`}>Why this score</p>
        <p className="text-sm leading-relaxed">{data?.reason}</p>
      </div>

      <div className={`mt-3 ${meta.textClass}`}>
        <p className={`mb-1 text-xs font-semibold uppercase tracking-wider ${meta.accentClass}`}>Recommended action</p>
        <p className="text-sm leading-relaxed">{meta.action}</p>
      </div>
    </div>
  );
}
