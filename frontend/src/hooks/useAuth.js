import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import api from '../lib/api';
import { clearToken, isAuthenticated, setToken } from '../lib/auth';
import { useAuthStore } from '../store/authStore';

export function useAuth() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { setToken: setTokenState, setUser, clearAuth, user } = useAuthStore();

  const meQuery = useQuery({
    queryKey: ['auth', 'me'],
    queryFn: async () => (await api.get('/auth/me')).data,
    enabled: isAuthenticated(),
    staleTime: 30000,
  });

  const login = useMutation({
    mutationFn: async ({ email, password }) => {
      const payload = new URLSearchParams({ username: email, password });
      const response = await api.post('/auth/login', payload, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      return response.data;
    },
    onSuccess: async (data) => {
      setToken(data.access_token);
      setTokenState(data.access_token);
      const me = await api.get('/auth/me');
      setUser(me.data);
      navigate('/', { replace: true });
    },
  });

  const signup = useMutation({
    mutationFn: async ({ name, email, password }) => {
      await api.post('/auth/register', { name, email, password });
      const payload = new URLSearchParams({ username: email, password });
      const loginRes = await api.post('/auth/login', payload, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      return loginRes.data;
    },
    onSuccess: async (data) => {
      setToken(data.access_token);
      setTokenState(data.access_token);
      const me = await api.get('/auth/me');
      setUser(me.data);
      navigate('/', { replace: true });
    },
  });

  const logout = () => {
    clearToken();
    clearAuth();
    queryClient.clear();
    navigate('/login', { replace: true });
  };

  return {
    login,
    signup,
    logout,
    user: meQuery.data || user,
    isAuthenticated: isAuthenticated(),
  };
}
