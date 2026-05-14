import { Loader2, Sparkles } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useAISuggestFollowup } from '../../hooks/useAISuggestFollowup';

export default function DiscussionForm({ onSubmit, submitting }) {
  const [note, setNote] = useState('');
  const [followUpEnabled, setFollowUpEnabled] = useState(false);
  const [followDate, setFollowDate] = useState('');
  const [followTime, setFollowTime] = useState('');
  const [suggestReady, setSuggestReady] = useState(false);
  const [suggestHint, setSuggestHint] = useState('');
  const suggestFollowup = useAISuggestFollowup();
  const canSubmit = note.trim().length > 0;
  const wordCount = note.trim().split(/\s+/).filter(Boolean).length;

  useEffect(() => {
    setSuggestReady(false);
    if (wordCount < 2) return;
    const timer = setTimeout(() => setSuggestReady(true), 500);
    return () => clearTimeout(timer);
  }, [wordCount, note]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!canSubmit) return;
    const followUpAt = followUpEnabled && followDate && followTime ? new Date(`${followDate}T${followTime}`).toISOString() : null;
    onSubmit({ note: note.trim(), follow_up_at: followUpAt });
    setNote('');
    setFollowUpEnabled(false);
    setFollowDate('');
    setFollowTime('');
    setSuggestHint('');
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-gray-100 bg-gray-50 p-6">
      <textarea
        value={note}
        onChange={(e) => setNote(e.target.value)}
        placeholder="Log a new discussion..."
        className="h-20 w-full resize-none rounded-lg border border-gray-200 px-3 py-2 text-sm text-gray-900 placeholder:text-gray-400 focus-visible:border-indigo-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/20"
      />
      <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2 text-sm text-gray-600">
          <input id="follow-up" type="checkbox" checked={followUpEnabled} onChange={(e) => setFollowUpEnabled(e.target.checked)} />
          <label htmlFor="follow-up">Set Follow-up</label>
          {followUpEnabled && (
            <>
              <input type="date" value={followDate} onChange={(e) => setFollowDate(e.target.value)} className="h-9 rounded border border-gray-200 px-2 text-sm" />
              <input type="time" value={followTime} onChange={(e) => setFollowTime(e.target.value)} className="h-9 rounded border border-gray-200 px-2 text-sm" />
            </>
          )}
          {wordCount >= 2 && (
            <button
              type="button"
              onClick={() => {
                suggestFollowup.mutate(note.trim(), {
                  onSuccess: (data) => {
                    if (data.follow_up_iso) {
                      const dt = new Date(data.follow_up_iso);
                      setFollowUpEnabled(true);
                      setFollowDate(dt.toISOString().slice(0, 10));
                      setFollowTime(dt.toTimeString().slice(0, 5));
                      setSuggestHint(`💡 ${data.reasoning}`);
                    } else {
                      setSuggestHint('💡 No specific timing detected');
                    }
                  },
                });
              }}
              disabled={!suggestReady || suggestFollowup.isPending}
              className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-50 px-3 py-1.5 text-sm font-medium text-indigo-700 transition-colors hover:bg-indigo-100 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {suggestFollowup.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
              Suggest follow-up
            </button>
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
      {suggestHint && <p className={`mt-2 text-xs italic ${suggestHint.includes('No specific') ? 'text-gray-500' : 'text-indigo-600'}`}>{suggestHint}</p>}
      {suggestFollowup.isError && <p role="alert" className="mt-2 text-xs text-red-700">{suggestFollowup.error?.response?.data?.detail || 'AI feature temporarily unavailable'}</p>}
    </form>
  );
}
