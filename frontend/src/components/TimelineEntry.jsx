import { formatDateTime, timeAgo } from '../utils/time';

export default function TimelineEntry({ item, latest }) {
  return (
    <div className="relative flex gap-3">
      <div className="flex w-4 flex-col items-center">
        <span className={`h-2.5 w-2.5 rounded-full ${latest ? 'bg-indigo-500' : 'border border-gray-300 bg-white'}`} />
        <span className="mt-1 h-full w-px bg-gray-200" />
      </div>
      <div className="pb-4">
        <p className="text-xs text-gray-400">
          {formatDateTime(item.created_at)} ({timeAgo(item.created_at)})
        </p>
        <div className="mt-1 rounded-lg border border-gray-200 bg-white p-3">
          <p className="text-sm text-gray-700">{item.note}</p>
          {item.follow_up_at && (
            <span className="mt-2 inline-flex rounded-full bg-amber-50 px-2 py-0.5 text-xs text-amber-700">
              📅 {formatDateTime(item.follow_up_at)}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
