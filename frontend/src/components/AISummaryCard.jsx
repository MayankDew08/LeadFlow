import { motion } from 'framer-motion';

export default function AISummaryCard({ summary }) {
  if (!summary) return null;
  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      exit={{ opacity: 0, height: 0 }}
      transition={{ duration: 0.2, ease: 'easeOut' }}
      className="rounded-lg border border-indigo-100 bg-indigo-50/50 p-4"
    >
      <p className="text-xs text-indigo-600">📋 AI Brief</p>
      <p className="mt-2 text-sm text-gray-700">Situation: {summary.situation}</p>
      <p className="mt-2 text-sm text-gray-700">Concerns: {summary.concerns}</p>
      <p className="mt-2 text-sm text-gray-700">Next Action: {summary.next_action}</p>
    </motion.div>
  );
}
