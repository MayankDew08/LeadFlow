import { MessageSquare } from 'lucide-react';
import TimelineEntry from './TimelineEntry';
import { TimelineSkeletons } from './LoadingSkeletons';

export default function Timeline({ discussions, loading }) {
  return (
    <div className="flex-1 overflow-y-auto p-6">
      <div className="mb-3 flex items-center justify-between">
        <p className="text-xs font-semibold uppercase tracking-wider text-gray-400">Discussion Timeline</p>
        <p className="text-xs text-gray-400">{discussions?.length || 0} discussions</p>
      </div>
      {loading ? (
        <TimelineSkeletons />
      ) : discussions?.length ? (
        <div>
          {discussions.map((d, idx) => (
            <TimelineEntry key={d.id} item={d} latest={idx === 0} />
          ))}
        </div>
      ) : (
        <div className="flex min-h-40 flex-col items-center justify-center text-center">
          <MessageSquare className="h-9 w-9 text-gray-300" />
          <p className="mt-2 text-sm font-medium text-gray-500">No discussions yet</p>
          <p className="text-sm text-gray-400">Add your first note below</p>
        </div>
      )}
    </div>
  );
}
