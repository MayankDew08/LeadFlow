import { create } from 'zustand';

export const useAIStore = create((set, get) => ({
  scores: {},
  summaries: {},

  setScore: (leadId, data) => set((state) => ({
    scores: {
      ...state.scores,
      [leadId]: { ...data, fetchedAt: Date.now() },
    },
  })),

  setSummary: (leadId, data) => set((state) => ({
    summaries: {
      ...state.summaries,
      [leadId]: { ...data, fetchedAt: Date.now() },
    },
  })),

  getCachedScore: (leadId) => {
    const cached = get().scores[leadId];
    if (!cached) return null;
    const fiveMinutes = 5 * 60 * 1000;
    if (Date.now() - cached.fetchedAt > fiveMinutes) return null;
    return cached;
  },

  clearCacheForLead: (leadId) => set((state) => {
    const newScores = { ...state.scores };
    const newSummaries = { ...state.summaries };
    delete newScores[leadId];
    delete newSummaries[leadId];
    return { scores: newScores, summaries: newSummaries };
  }),
}));
