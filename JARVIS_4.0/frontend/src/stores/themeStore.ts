import { create } from 'zustand'
import { subscribeWithSelector, persist, createJSONStorage } from 'zustand/middleware'

export type Theme = 'dark' | 'light' | 'neon' | 'matrix'

interface ThemeStore {
  theme: Theme
  setTheme: (theme: Theme) => void
  initializeTheme: () => void
}

export const useThemeStore = create<ThemeStore>()(
  persist(
    (set, get) => ({
      theme: 'dark',
      
      setTheme: (theme: Theme) => {
        set({ theme })
        document.documentElement.className = `theme-${theme}`
      },
      
      initializeTheme: () => {
        const { theme } = get()
        document.documentElement.className = `theme-${theme}`
      },
    }),
    {
      name: 'jarvis-theme',
      storage: createJSONStorage(() => localStorage),
    }
  )
)