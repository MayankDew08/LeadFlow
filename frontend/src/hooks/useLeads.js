import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import api from '../lib/api';

export function useLeads({ status, search }) {
  return useQuery({
    queryKey: ['leads', { status, search }],
    queryFn: async () => {
      const params = {};
      if (status && status !== 'All') params.status = status;
      if (search) params.search = search;
      const res = await api.get('/leads', { params });
      return res.data;
    },
    staleTime: 30000,
  });
}

export function useTodayFollowUps() {
  return useQuery({
    queryKey: ['leads', { follow_up_today: true }],
    queryFn: async () => (await api.get('/leads', { params: { follow_up_today: true } })).data,
    staleTime: 30000,
  });
}

export function useCreateLead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload) => api.post('/leads', payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['leads'] }),
  });
}

export function useUpdateLead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ leadId, payload }) => api.patch(`/leads/${leadId}`, payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['leads'] }),
  });
}
