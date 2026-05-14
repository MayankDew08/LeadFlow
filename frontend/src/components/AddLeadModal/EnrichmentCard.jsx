import { AnimatePresence, motion } from 'framer-motion';
import { AlertCircle, Building2, Calendar, Check, Globe, MapPin, Users, X } from 'lucide-react';

const sourceLabel = (source) => {
  if (source === 'gemini') return '⚡ Live';
  return '🔍 Web';
};

export default function EnrichmentCard({ data, open, onClose }) {
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
          <div className="mb-3 flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <p className="text-xs font-semibold uppercase tracking-wider text-indigo-700">✨ Company Intelligence</p>
              <span className="rounded bg-indigo-100 px-1.5 py-0.5 text-[10px] font-medium text-indigo-700">{sourceLabel(data?.source)}</span>
            </div>
            <button type="button" onClick={onClose} aria-label="Close intelligence" className="rounded p-1 text-indigo-600 hover:bg-indigo-100">
              <X className="h-4 w-4" />
            </button>
          </div>

          {data?.ai_available === false ? (
            <div className="flex items-center gap-2 text-sm italic text-gray-500">
              <AlertCircle className="h-4 w-4" />
              Enrichment temporarily unavailable. You can still add this lead manually.
            </div>
          ) : (
            <>
              {data?.description && <p className="mb-3 text-sm leading-relaxed text-gray-700">{data.description}</p>}
              <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                {data?.industry && <p className="flex items-start gap-1.5 text-xs"><Building2 className="mt-0.5 h-3.5 w-3.5 text-indigo-600" /><span className="text-gray-500">Industry:</span><span className="font-medium text-gray-800">{data.industry}</span></p>}
                {data?.size && <p className="flex items-start gap-1.5 text-xs"><Users className="mt-0.5 h-3.5 w-3.5 text-indigo-600" /><span className="text-gray-500">Size:</span><span className="font-medium text-gray-800">{data.size}</span></p>}
                {data?.headquarters && <p className="flex items-start gap-1.5 text-xs"><MapPin className="mt-0.5 h-3.5 w-3.5 text-indigo-600" /><span className="text-gray-500">HQ:</span><span className="font-medium text-gray-800">{data.headquarters}</span></p>}
                {data?.website && <p className="flex items-start gap-1.5 text-xs"><Globe className="mt-0.5 h-3.5 w-3.5 text-indigo-600" /><span className="text-gray-500">Web:</span><span className="font-medium text-gray-800">{data.website.replace(/^https?:\/\//, '')}</span></p>}
                {data?.founded && <p className="flex items-start gap-1.5 text-xs"><Calendar className="mt-0.5 h-3.5 w-3.5 text-indigo-600" /><span className="text-gray-500">Founded:</span><span className="font-medium text-gray-800">{data.founded}</span></p>}
              </div>

              {data?.recent_news && (
                <div className="mt-3 rounded-lg border border-indigo-100 bg-white p-3">
                  <p className="mb-1 text-xs font-semibold text-indigo-700">📰 Recent</p>
                  <p className="text-xs text-gray-700">{data.recent_news}</p>
                </div>
              )}

              {Array.isArray(data?.potential_pain_points) && data.potential_pain_points.length > 0 && (
                <div className="mt-3">
                  <p className="mb-1 text-xs font-semibold text-indigo-700">🎯 Sales Angles</p>
                  <div className="space-y-1">
                    {data.potential_pain_points.map((item, index) => (
                      <p key={`${item}-${index}`} className="flex items-start gap-1.5 text-xs text-gray-700"><Check className="mt-0.5 h-3 w-3 text-indigo-500" />{item}</p>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
