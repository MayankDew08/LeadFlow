import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import api from '../lib/api';
import { useAIStore } from '../store/aiStore';

export function useDiscussions(leadId) {
  return useQuery({
    queryKey: ['discussions', leadId],
    enabled: Boolean(leadId),
    queryFn: async () => (await api.get(`/leads/${leadId}/discussions`)).data,
    staleTime: 30000,
  });
}

export function useCreateDiscussion(leadId) {
  const qc = useQueryClient();
  const clearCacheForLead = useAIStore((state) => state.clearCacheForLead);
  return useMutation({
    mutationFn: (payload) => api.post(`/leads/${leadId}/discussions`, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['discussions', leadId] });
      qc.invalidateQueries({ queryKey: ['leads'] });
      clearCacheForLead(leadId);
    },
  });
}
