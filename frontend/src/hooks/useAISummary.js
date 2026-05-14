import { useMutation } from '@tanstack/react-query';
import api from '../lib/api';

export const useAISummary = () => {
  return useMutation({
    mutationFn: (leadId) => api.post('/ai/summarize', { lead_id: leadId }).then((r) => r.data),
  });
};
