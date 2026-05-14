import StatusBadge from './StatusBadge';
import AIScoreBadge from './AIScoreBadge';
import { formatDateTime, isOverdue, isToday, timeAgo } from '../utils/time';
import { useAIStore } from '../store/aiStore';

export default function LeadCard({ lead, onClick, aiScore = 'Warm' }) {
  const cachedScore = useAIStore((state) => state.scores[lead.id]?.score);
  const overdue = isOverdue(lead.follow_up_at);
  const today = isToday(lead.follow_up_at);

  const leftBorder = overdue
    ? 'border-l-red-500 bg-red-50/50'
    : today
      ? 'border-l-amber-400 bg-amber-50/30'
      : 'border-l-transparent bg-white';

  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-full rounded-lg border border-l-4 border-gray-200 p-4 text-left transition-all duration-150 hover:border-gray-300 hover:shadow-sm ${leftBorder}`}
    >
      <div className="mb-2 flex items-start justify-between gap-3">
        <p className="text-sm font-semibold text-gray-900">{lead.name}</p>
        <div className="flex items-center gap-2">
          <StatusBadge status={lead.status} />
          <AIScoreBadge score={cachedScore || aiScore} />
        </div>
      </div>
      <p className="text-sm text-gray-500">{lead.company || 'No company'}</p>
      <div className="mt-2 flex items-center justify-between gap-2">
        <p className="truncate text-sm text-gray-500">{lead.last_discussion?.note || 'No discussions yet'}</p>
        <p className="text-xs text-gray-400">{lead.last_discussion?.created_at ? timeAgo(lead.last_discussion.created_at) : '—'}</p>
      </div>
      {lead.follow_up_at && (
        <p className={`mt-2 text-xs ${overdue ? 'font-medium text-red-600' : today ? 'text-amber-600' : 'text-amber-600'}`}>
          📅 Follow-up: {formatDateTime(lead.follow_up_at)}
        </p>
      )}
    </button>
  );
}
