import { AnimatePresence, motion } from 'framer-motion';
import { Loader2, Sparkles, X } from 'lucide-react';
import { useState } from 'react';
import { useEnrichCompany } from '../../hooks/useEnrichCompany';
import EnrichmentCard from './EnrichmentCard';

export default function AddLeadModal({ open, onClose, onSubmit, submitting }) {
  const [name, setName] = useState('');
  const [company, setCompany] = useState('');
  const [phone, setPhone] = useState('');
  const [touched, setTouched] = useState(false);
  const [showEnrichment, setShowEnrichment] = useState(false);
  const enrichCompany = useEnrichCompany();
  const invalid = touched && !name.trim();

  const submit = (e) => {
    e.preventDefault();
    setTouched(true);
    if (!name.trim()) return;
    onSubmit({ name: name.trim(), company: company.trim() || null, phone: phone.trim() || null, status: 'New' });
    setName('');
    setCompany('');
    setPhone('');
    setTouched(false);
    setShowEnrichment(false);
  };

  return (
    <AnimatePresence>
      {open && (
        <motion.div className="fixed inset-0 z-50 bg-black/40 p-4 backdrop-blur-sm" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
          <motion.form
            role="dialog"
            aria-modal="true"
            onSubmit={submit}
            className="mx-auto mt-8 w-full max-w-md rounded-xl border border-gray-200 bg-white p-6 shadow-xl"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 8 }}
            transition={{ duration: 0.2 }}
          >
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">Add New Lead</h2>
              <button type="button" onClick={onClose} aria-label="Close" className="rounded p-1 text-gray-500 hover:bg-gray-100">
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="mt-6 space-y-4">
              <div>
                <label htmlFor="name" className="text-sm font-medium text-gray-700">Full Name *</label>
                <input id="name" value={name} onBlur={() => setTouched(true)} onChange={(e) => setName(e.target.value)} className={`mt-1 h-10 w-full rounded-lg border px-3 text-sm ${invalid ? 'border-red-400' : 'border-gray-200'} focus-visible:border-indigo-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/20`} placeholder="e.g., John Doe" />
                {invalid && <p className="mt-1 text-xs text-red-500">Name is required</p>}
              </div>
              <div>
                <label htmlFor="company" className="text-sm font-medium text-gray-700">Company (Optional)</label>
                <div className="relative mt-1">
                  <input id="company" value={company} onChange={(e) => setCompany(e.target.value)} className="h-10 w-full rounded-lg border border-gray-200 px-3 pr-24 text-sm focus-visible:border-indigo-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/20" placeholder="e.g., Stark Industries" />
                  {company.trim().length >= 2 && (
                    <button
                      type="button"
                      onClick={() => {
                        enrichCompany.mutate(company.trim(), {
                          onSuccess: () => setShowEnrichment(true),
                        });
                      }}
                      disabled={enrichCompany.isPending}
                      className="absolute right-1.5 top-1/2 inline-flex -translate-y-1/2 items-center gap-1 rounded-full bg-indigo-50 px-2.5 py-1 text-xs font-medium text-indigo-700 hover:bg-indigo-100 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {enrichCompany.isPending ? <Loader2 className="h-3 w-3 animate-spin" /> : <Sparkles className="h-3 w-3" />}
                      {enrichCompany.isPending ? 'Researching...' : 'Enrich'}
                    </button>
                  )}
                </div>
                {enrichCompany.isError && (
                  <p role="alert" className="mt-2 rounded-lg border border-red-100 bg-red-50 p-2 text-xs text-red-700">
                    {enrichCompany.error?.response?.data?.detail || 'AI feature temporarily unavailable'}
                  </p>
                )}
                <EnrichmentCard open={showEnrichment && !!enrichCompany.data} data={enrichCompany.data} onClose={() => setShowEnrichment(false)} />
              </div>
              <div>
                <label htmlFor="phone" className="text-sm font-medium text-gray-700">Phone (Optional)</label>
                <input id="phone" value={phone} onChange={(e) => setPhone(e.target.value)} className="mt-1 h-10 w-full rounded-lg border border-gray-200 px-3 text-sm focus-visible:border-indigo-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/20" placeholder="e.g., 555-0123" />
              </div>
            </div>
            <div className="mt-6 flex justify-end gap-3 border-t border-gray-100 pt-4">
              <button type="button" onClick={onClose} className="h-9 rounded-lg px-4 text-sm text-gray-600 hover:bg-gray-100">Cancel</button>
              <button type="submit" disabled={submitting} className="inline-flex h-10 min-w-24 items-center justify-center rounded-lg bg-indigo-600 px-4 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-80">
                {submitting ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Save Lead'}
              </button>
            </div>
          </motion.form>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
