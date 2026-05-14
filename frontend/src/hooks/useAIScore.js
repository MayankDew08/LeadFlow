import { useMutation } from '@tanstack/react-query';
import api from '../lib/api';
import { useAIStore } from '../store/aiStore';

export const useAIScore = () => {
  const getCachedScore = useAIStore((state) => state.getCachedScore);
  const setScore = useAIStore((state) => state.setScore);

  return useMutation({
    mutationFn: async (leadId) => {
      const cached = getCachedScore(leadId);
      if (cached) return { ...cached, fromCache: true };
      const data = await api.post('/ai/score-lead', { lead_id: leadId }).then((r) => r.data);
      setScore(leadId, data);
      return { ...data, fromCache: false };
    },
  });
};
