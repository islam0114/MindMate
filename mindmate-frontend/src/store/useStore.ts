// src/store/useStore.ts
import { create } from 'zustand';

interface UserState {
  userId: number | null;
  username: string;
  isLoggedIn: boolean;
  setLogin: (id: number, name: string) => void;
  setLogout: () => void;
}

export const useStore = create<UserState>((set) => ({
  userId: null,
  username: "صديقي",
  isLoggedIn: false,
  setLogin: (id, name) => set({ userId: id, username: name, isLoggedIn: true }),
  setLogout: () => set({ userId: null, username: "صديقي", isLoggedIn: false }),
}));