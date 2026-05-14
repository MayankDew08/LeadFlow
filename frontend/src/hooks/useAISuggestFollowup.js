import { useMutation } from '@tanstack/react-query';
import api from '../lib/api';

export const useAISuggestFollowup = () => {
  return useMutation({
    mutationFn: (note) => api.post('/ai/suggest-followup', { note }).then((r) => r.data),
  });
};
