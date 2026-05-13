import { create } from 'zustand';

export const STATUS_TABS = ['All', 'New', 'Contacted', 'Qualified', 'Proposal Sent', 'Won', 'Lost'];

export const useFilterStore = create((set) => ({
  status: 'All',
  search: '',
  setStatus: (status) => set({ status }),
  setSearch: (search) => set({ search }),
}));
