import { create } from "zustand";

/**
 * Lightweight notification state for the bell icon badge.
 * The full notification list is fetched via React Query, not stored here.
 */
const useNotificationStore = create((set) => ({
  unreadCount: 0,

  setUnreadCount: (count) => set({ unreadCount: count }),

  increment: () => set((s) => ({ unreadCount: s.unreadCount + 1 })),

  decrement: () =>
    set((s) => ({ unreadCount: Math.max(0, s.unreadCount - 1) })),

  reset: () => set({ unreadCount: 0 }),
}));

export default useNotificationStore;
