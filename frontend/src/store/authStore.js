import { create } from 'zustand';
import { getToken } from '../lib/auth';

export const useAuthStore = create((set) => ({
  token: getToken(),
  user: null,
  setToken: (token) => set({ token }),
  setUser: (user) => set({ user }),
  clearAuth: () => set({ token: null, user: null }),
}));
