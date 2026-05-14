import { AnimatePresence, motion } from 'framer-motion';
import { Bot, Loader2, Mail, X } from 'lucide-react';
import { useState } from 'react';
import { useAIScore } from '../../hooks/useAIScore';
import { useAISummary } from '../../hooks/useAISummary';
import { useCreateDiscussion, useDiscussions } from '../../hooks/useDiscussions';
import { useUpdateLead } from '../../hooks/useLeads';
import { useAIStore } from '../../store/aiStore';
import Timeline from '../Timeline';
import AIScoreCard from './AIScoreCard';
import AISummaryCard from './AISummaryCard';
import DiscussionForm from './DiscussionForm';
import EmailGeneratorModal from './EmailGeneratorModal';

const statuses = ['New', 'Contacted', 'Qualified', 'Proposal Sent', 'Won', 'Lost'];

export default function LeadDialog({ lead, open, onClose }) {
  const [showSummary, setShowSummary] = useState(false);
  const [emailOpen, setEmailOpen] = useState(false);
  const { summaries, scores, setSummary, clearCacheForLead } = useAIStore();
  const { data, isLoading } = useDiscussions(lead?.id);
  const createDiscussion = useCreateDiscussion(lead?.id);
  const updateLead = useUpdateLead();
  const summaryMutation = useAISummary();
  const scoreMutation = useAIScore();

  if (!lead) return null;

  const currentSummary = summaries[lead.id];
  const currentScore = scores[lead.id];

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
              <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
                <select
                  value={lead.status}
                  onChange={(e) => updateLead.mutate({ leadId: lead.id, payload: { status: e.target.value } })}
                  className="h-10 rounded-lg border border-gray-200 px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/20"
                >
                  {statuses.map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
                <div className="flex flex-wrap items-center gap-2">
                  <button type="button" onClick={() => summaryMutation.mutate(lead.id, { onSuccess: (result) => { setSummary(lead.id, result); setShowSummary(true); } })} disabled={summaryMutation.isPending} className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-50 px-3 py-1.5 text-sm font-medium text-indigo-700 hover:bg-indigo-100 disabled:cursor-not-allowed disabled:opacity-60">
                    {summaryMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Bot className="h-4 w-4" />}
                    AI Summary
                  </button>
                  <button type="button" onClick={() => setEmailOpen(true)} className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-50 px-3 py-1.5 text-sm font-medium text-indigo-700 hover:bg-indigo-100">
                    <Mail className="h-4 w-4" />Generate Email
                  </button>
                </div>
              </div>
              {summaryMutation.isError && <p role="alert" className="mt-3 rounded-lg border border-red-100 bg-red-50 p-2 text-sm text-red-700">{summaryMutation.error?.response?.data?.detail || 'AI feature temporarily unavailable'}</p>}
              <AISummaryCard open={showSummary && !!currentSummary} summary={currentSummary} onClose={() => setShowSummary(false)} />
              <AnimatePresence>
                {currentScore ? (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.25 }}
                  >
                    <AIScoreCard
                      data={currentScore}
                      loading={scoreMutation.isPending}
                      onRefresh={() => {
                        clearCacheForLead(lead.id);
                        scoreMutation.mutate(lead.id);
                      }}
                    />
                  </motion.div>
                ) : (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.25 }}
                    className="mt-3"
                  >
                    <button
                      type="button"
                      onClick={() => scoreMutation.mutate(lead.id)}
                      disabled={scoreMutation.isPending}
                      className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-50 px-3 py-1.5 text-sm font-medium text-indigo-700 hover:bg-indigo-100 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {scoreMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                      📊 Score this lead
                    </button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
            <Timeline discussions={data?.discussions || []} loading={isLoading} />
            <DiscussionForm onSubmit={(payload) => createDiscussion.mutate(payload)} submitting={createDiscussion.isPending} />
          </motion.div>
          <EmailGeneratorModal open={emailOpen} onClose={() => setEmailOpen(false)} lead={lead} />
        </motion.div>
      )}
    </AnimatePresence>
  );
}
