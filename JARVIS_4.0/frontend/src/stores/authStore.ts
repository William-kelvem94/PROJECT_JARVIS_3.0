import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import axios from 'axios'

interface User {
  username: string
  email?: string
}

interface AuthStore {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  checkAuth: () => void
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: true,

      login: async (username: string, password: string) => {
        try {
          set({ isLoading: true })
          
          const response = await axios.post('/api/auth/login', {
            username,
            password,
          })

          const { access_token } = response.data
          
          // Set auth header for future requests
          axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
          
          // Get user info
          const userResponse = await axios.get('/api/auth/me')
          
          set({
            token: access_token,
            user: userResponse.data,
            isAuthenticated: true,
            isLoading: false,
          })
        } catch (error) {
          set({ isLoading: false })
          throw error
        }
      },

      logout: () => {
        delete axios.defaults.headers.common['Authorization']
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        })
      },

      checkAuth: () => {
        const { token } = get()
        if (token) {
          axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
          // Verify token is still valid
          axios.get('/api/auth/verify')
            .then(() => {
              set({ isAuthenticated: true, isLoading: false })
            })
            .catch(() => {
              get().logout()
            })
        } else {
          set({ isLoading: false })
        }
      },
    }),
    {
      name: 'jarvis-auth',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({ 
        token: state.token,
        user: state.user 
      }),
    }
  )
)