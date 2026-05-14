import { AnimatePresence, motion } from 'framer-motion';
import { AlertCircle, X } from 'lucide-react';

export default function AISummaryCard({ open, summary, onClose }) {
  return (
    <AnimatePresence>
      {open && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.25 }}
          className="mt-3 rounded-lg border border-indigo-100 bg-indigo-50/50 p-4"
        >
          <div className="mb-3 flex items-center justify-between">
            <p className="text-xs font-semibold uppercase tracking-wider text-indigo-700">📋 AI Brief</p>
            <button type="button" onClick={onClose} className="rounded p-1 text-indigo-600 hover:bg-indigo-100" aria-label="Close AI brief">
              <X className="h-4 w-4" />
            </button>
          </div>

          {summary?.ai_available === false ? (
            <p className="flex items-center gap-2 text-sm text-gray-500"><AlertCircle className="h-4 w-4" />AI summary temporarily unavailable</p>
          ) : (
            <div className="space-y-3">
              <div>
                <p className="mb-1 text-xs font-medium uppercase text-indigo-600">Situation</p>
                <p className="text-sm text-gray-700">{summary?.situation}</p>
              </div>
              {Array.isArray(summary?.concerns) && summary.concerns.length > 0 && (
                <div>
                  <p className="mb-1 text-xs font-medium uppercase text-indigo-600">Concerns</p>
                  <div className="space-y-1">
                    {summary.concerns.map((concern, index) => (
                      <p key={`${concern}-${index}`} className="text-sm text-gray-700">• {concern}</p>
                    ))}
                  </div>
                </div>
              )}
              <div>
                <p className="mb-1 text-xs font-medium uppercase text-indigo-600">Recommended Next Action</p>
                <p className="rounded border border-indigo-100 bg-white p-2.5 text-sm font-medium text-gray-800">{summary?.next_action}</p>
              </div>
            </div>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
