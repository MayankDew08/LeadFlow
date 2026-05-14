import { useMutation } from '@tanstack/react-query';
import api from '../lib/api';

export const useEnrichCompany = () => {
  return useMutation({
    mutationFn: (companyName) => api.post('/ai/enrich-company', { company_name: companyName }).then((r) => r.data),
  });
};
