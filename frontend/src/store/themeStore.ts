import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface ThemeState {
  color: string;
  setColor: (color: string) => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      color: '#dc2626',
      setColor: (color) => {
        document.documentElement.style.setProperty('--theme-color', color);
        set({ color });
      },
    }),
    { name: 'flowserve-theme' }
  )
);
