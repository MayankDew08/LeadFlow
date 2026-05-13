import { create } from 'zustand';

export const useAIStore = create((set) => ({
  scores: {},
  summaries: {},
  setScore: (leadId, data) => set((state) => ({ scores: { ...state.scores, [leadId]: data } })),
  setSummary: (leadId, data) => set((state) => ({ summaries: { ...state.summaries, [leadId]: data } })),
}));
