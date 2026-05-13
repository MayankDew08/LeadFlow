import { AnimatePresence, motion } from 'framer-motion';
import { Sparkles, X } from 'lucide-react';
import { useState } from 'react';
import { useAIStore } from '../store/aiStore';
import { useCreateDiscussion, useDiscussions } from '../hooks/useDiscussions';
import { useUpdateLead } from '../hooks/useLeads';
import AISummaryCard from './AISummaryCard';
import DiscussionForm from './DiscussionForm';
import Timeline from './Timeline';

const statuses = ['New', 'Contacted', 'Qualified', 'Proposal Sent', 'Won', 'Lost'];

export default function LeadDialog({ lead, open, onClose }) {
  const [showSummary, setShowSummary] = useState(false);
  const { summaries, setSummary } = useAIStore();
  const { data, isLoading } = useDiscussions(lead?.id);
  const createDiscussion = useCreateDiscussion(lead?.id);
  const updateLead = useUpdateLead();

  const generateSummary = () => {
    const fallback = {
      situation: 'Client is evaluating options and reviewing scope.',
      concerns: 'Pricing and timeline constraints.',
      next_action: 'Schedule follow-up call with a tailored demo.',
    };
    setSummary(lead.id, fallback);
    setShowSummary(true);
  };

  if (!lead) return null;

  return (
    <AnimatePresence>
      {open && (
        <motion.div className="fixed inset-0 z-50 bg-black/40 p-4 backdrop-blur-sm" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={onClose}>
          <motion.div
            role="dialog"
            aria-modal="true"
            aria-labelledby="lead-dialog-title"
            className="mx-auto my-8 flex max-h-[85vh] w-full max-w-2xl flex-col overflow-hidden rounded-xl border border-gray-200 bg-white shadow-xl"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 8 }}
            transition={{ duration: 0.25 }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="border-b border-gray-100 p-6">
              <div className="flex items-center justify-between">
                <h2 id="lead-dialog-title" className="text-lg font-semibold text-gray-900">{lead.name} · {lead.company || 'No company'}</h2>
                <button type="button" onClick={onClose} className="rounded p-1 text-gray-500 hover:bg-gray-100"><X className="h-4 w-4" /></button>
              </div>
              <p className="mt-1 text-sm text-gray-500">{lead.phone || 'No phone number'}</p>
              <div className="mt-3 flex items-center justify-between gap-3">
                <select
                  value={lead.status}
                  onChange={(e) => updateLead.mutate({ leadId: lead.id, payload: { status: e.target.value } })}
                  className="h-10 rounded-lg border border-gray-200 px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/20"
                >
                  {statuses.map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
                <button type="button" onClick={generateSummary} className="inline-flex h-9 items-center gap-1 rounded-lg px-3 text-sm text-indigo-600 hover:bg-indigo-50">
                  <Sparkles className="h-4 w-4" /> AI Summary
                </button>
              </div>
              {showSummary && <div className="mt-3"><AISummaryCard summary={summaries[lead.id]} /></div>}
            </div>
            <Timeline discussions={data?.discussions || []} loading={isLoading} />
            <DiscussionForm onSubmit={(payload) => createDiscussion.mutate(payload)} submitting={createDiscussion.isPending} />
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
