import { AnimatePresence, motion } from 'framer-motion';
import { AlertCircle, Check, Copy, ExternalLink, Loader2, Mail, Sparkles, X } from 'lucide-react';
import { useState } from 'react';
import { useGenerateEmail } from '../../hooks/useGenerateEmail';

const tones = ['professional', 'friendly', 'concise', 'persuasive'];
const purposes = ['introduction', 'follow-up', 'proposal', 'check-in', 'thank-you', 'custom'];

/**
 * Normalizes email body text to ensure line breaks render correctly.
 * Handles all common escape patterns:
 *   - Literal "\n" strings (most common issue)
 *   - Double-escaped "\\n"
 *   - Carriage returns "\r\n"
 *   - Already-normalized real newlines
 */
const normalizeEmailBody = (raw) => {
  if (!raw || typeof raw !== 'string') return '';

  return raw
    .replace(/\\r\\n/g, '\n')
    .replace(/\\n/g, '\n')
    .replace(/\\\\n/g, '\n')
    .replace(/\r\n/g, '\n')
    .replace(/\r/g, '\n')
    .trim();
};

export default function EmailGeneratorModal({ open, onClose, lead }) {
  const [purpose, setPurpose] = useState('follow-up');
  const [tone, setTone] = useState('professional');
  const [context, setContext] = useState('');
  const [copiedSubject, setCopiedSubject] = useState(false);
  const [copiedBody, setCopiedBody] = useState(false);
  const [copiedAll, setCopiedAll] = useState(false);
  const generateEmail = useGenerateEmail();
  const generated = generateEmail.data;
  const formattedBody = generated ? normalizeEmailBody(generated.body) : '';

  const copy = async (value, kind) => {
    await navigator.clipboard.writeText(value);
    if (kind === 'subject') setCopiedSubject(true);
    if (kind === 'body') setCopiedBody(true);
    if (kind === 'all') setCopiedAll(true);
    setTimeout(() => {
      setCopiedSubject(false);
      setCopiedBody(false);
      setCopiedAll(false);
    }, 2000);
  };

  const openInMail = () => {
    const to = lead?.email ? encodeURIComponent(lead.email) : '';
    const subject = encodeURIComponent(generated?.subject || '');
    const body = encodeURIComponent(formattedBody);
    window.location.href = `mailto:${to}?subject=${subject}&body=${body}`;
  };

  return (
    <AnimatePresence>
      {open && (
        <motion.div className="fixed inset-0 z-[60] bg-black/40 backdrop-blur-sm" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={onClose}>
          <motion.div
            role="dialog"
            aria-modal="true"
            aria-labelledby="email-generator-title"
            className="mx-auto mt-8 flex max-h-[90vh] w-[calc(100%-2rem)] max-w-2xl flex-col overflow-hidden rounded-xl border border-gray-200 bg-white shadow-xl"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25 }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="border-b border-gray-100 px-6 py-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 id="email-generator-title" className="flex items-center gap-2 text-lg font-semibold text-gray-900"><Mail className="h-5 w-5 text-indigo-600" />Generate Email</h3>
                  <p className="text-sm text-gray-500">To {lead?.name}{lead?.company ? ` · ${lead.company}` : ''}</p>
                </div>
                <button type="button" onClick={onClose} className="rounded p-1 text-gray-500 hover:bg-gray-100"><X className="h-4 w-4" /></button>
              </div>
            </div>

            <div className="flex-1 space-y-4 overflow-y-auto px-6 py-5">
              <div>
                <label htmlFor="purpose" className="mb-1.5 block text-sm font-medium text-gray-700">Purpose</label>
                <select id="purpose" value={purpose} onChange={(e) => setPurpose(e.target.value)} className="h-10 w-full rounded-lg border border-gray-200 bg-white px-3 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20">
                  {purposes.map((item) => <option key={item} value={item}>{item}</option>)}
                </select>
              </div>

              <div>
                <p className="mb-1.5 text-sm font-medium text-gray-700">Tone</p>
                <div className="flex flex-wrap gap-2">
                  {tones.map((item) => (
                    <button key={item} type="button" onClick={() => setTone(item)} className={tone === item ? 'rounded-full bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white' : 'rounded-full bg-gray-100 px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-200'}>
                      {item.charAt(0).toUpperCase() + item.slice(1)}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label htmlFor="context" className="mb-1.5 block text-sm font-medium text-gray-700">Context (optional)</label>
                <textarea id="context" rows={3} value={context} onChange={(e) => setContext(e.target.value)} placeholder="e.g., They asked about pricing tiers last week..." className="w-full resize-none rounded-lg border border-gray-200 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/20" />
              </div>

              <button
                type="button"
                onClick={() => generateEmail.mutate({ leadId: lead.id, purpose, tone, context })}
                disabled={generateEmail.isPending}
                className="inline-flex h-10 w-full items-center justify-center gap-1.5 rounded-lg bg-indigo-600 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {generateEmail.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
                {generateEmail.isPending ? 'Generating...' : generated ? '✨ Regenerate' : '✨ Generate Email'}
              </button>

              {generateEmail.isError && (
                <div role="alert" className="flex items-center gap-2 rounded-lg border border-red-100 bg-red-50 p-3 text-sm text-red-700">
                  <AlertCircle className="h-4 w-4 text-red-500" />
                  {generateEmail.error?.response?.data?.detail || 'AI feature temporarily unavailable'}
                </div>
              )}

              <AnimatePresence>
                {generated && (
                  <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} transition={{ duration: 0.25 }} className="border-t border-gray-100 pt-4">
                    <span className="rounded bg-indigo-50 px-1.5 py-0.5 text-[10px] text-indigo-600">via {generated.source || 'ai'}</span>
                    <div className="mt-3 space-y-3">
                      <div>
                        <div className="mb-1 flex items-center justify-between">
                          <p className="text-xs font-semibold text-gray-500">SUBJECT</p>
                          <button type="button" onClick={() => copy(generated.subject, 'subject')} className="inline-flex items-center gap-1 text-xs text-indigo-600">{copiedSubject ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}{copiedSubject ? 'Copied' : 'Copy'}</button>
                        </div>
                        <p className="rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm font-medium">{generated.subject}</p>
                      </div>
                      <div>
                        <div className="mb-1 flex items-center justify-between">
                          <p className="text-xs font-semibold text-gray-500">BODY</p>
                          <button type="button" onClick={() => copy(formattedBody, 'body')} className="inline-flex items-center gap-1 text-xs text-indigo-600">{copiedBody ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}{copiedBody ? 'Copied' : 'Copy'}</button>
                        </div>
                        <p className="rounded-lg border border-gray-200 bg-gray-50 px-3 py-3 text-sm text-gray-800 leading-relaxed whitespace-pre-wrap font-normal">{formattedBody}</p>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {generated && (
              <div className="flex items-center justify-end gap-2 border-t border-gray-100 bg-gray-50 px-6 py-4">
                <button type="button" onClick={() => copy(`Subject: ${generated.subject}\n\n${formattedBody}`, 'all')} className="h-9 rounded-lg border border-gray-200 bg-white px-4 text-sm font-medium hover:border-gray-300 hover:bg-gray-50">
                  {copiedAll ? 'Copied' : 'Copy All'}
                </button>
                <button type="button" onClick={openInMail} className="inline-flex h-9 items-center gap-1.5 rounded-lg bg-indigo-600 px-4 text-sm font-medium text-white hover:bg-indigo-700">
                  <ExternalLink className="h-4 w-4" />Open in Mail
                </button>
              </div>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
