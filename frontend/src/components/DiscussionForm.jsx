import { Loader2 } from 'lucide-react';
import { useState } from 'react';

export default function DiscussionForm({ onSubmit, submitting }) {
  const [note, setNote] = useState('');
  const [followUpEnabled, setFollowUpEnabled] = useState(false);
  const [followDate, setFollowDate] = useState('');
  const [followTime, setFollowTime] = useState('');

  const canSubmit = note.trim().length > 0;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!canSubmit) return;
    const follow_up_at =
      followUpEnabled && followDate && followTime ? new Date(`${followDate}T${followTime}`).toISOString() : null;
    onSubmit({ note: note.trim(), follow_up_at });
    setNote('');
    setFollowUpEnabled(false);
    setFollowDate('');
    setFollowTime('');
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-gray-100 bg-gray-50 p-6">
      <textarea
        value={note}
        onChange={(e) => setNote(e.target.value)}
        placeholder="Log a new discussion..."
        className="h-20 w-full resize-none rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-900 placeholder:text-gray-400 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/20 focus-visible:border-indigo-500"
      />
      <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <input id="follow-up" type="checkbox" checked={followUpEnabled} onChange={(e) => setFollowUpEnabled(e.target.checked)} />
          <label htmlFor="follow-up">Set Follow-up</label>
          {followUpEnabled && (
            <>
              <input type="date" value={followDate} onChange={(e) => setFollowDate(e.target.value)} className="h-9 rounded border border-gray-200 px-2 text-sm" />
              <input type="time" value={followTime} onChange={(e) => setFollowTime(e.target.value)} className="h-9 rounded border border-gray-200 px-2 text-sm" />
            </>
          )}
        </div>
        <button
          type="submit"
          disabled={!canSubmit || submitting}
          className="inline-flex h-10 min-w-24 items-center justify-center rounded-lg bg-indigo-600 px-4 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-70"
        >
          {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Save Note'}
        </button>
      </div>
    </form>
  );
}
