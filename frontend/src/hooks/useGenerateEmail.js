import { useMutation } from '@tanstack/react-query';
import api from '../lib/api';

export const useGenerateEmail = () => {
  return useMutation({
    mutationFn: ({ leadId, purpose, tone, context }) => api.post('/ai/generate-email', {
      lead_id: leadId,
      purpose,
      tone,
      context,
    }).then((r) => r.data),
  });
};
