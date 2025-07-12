import React, { useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'

import { useThemeStore } from './stores/themeStore'
import { useAuthStore } from './stores/authStore'

import Layout from './components/Layout'
import Login from './modules/auth/Login'
import Dashboard from './modules/dashboard/Dashboard'
import Chat from './modules/chat/Chat'
import Voice from './modules/voice/Voice'
import Vision from './modules/vision/Vision'
import Settings from './modules/settings/Settings'
import LoadingScreen from './components/LoadingScreen'

function App() {
  const { theme, initializeTheme } = useThemeStore()
  const { isAuthenticated, isLoading, checkAuth } = useAuthStore()

  useEffect(() => {
    initializeTheme()
    checkAuth()
  }, [initializeTheme, checkAuth])

  if (isLoading) {
    return <LoadingScreen />
  }

  return (
    <div className={`min-h-screen theme-${theme}`}>
      <AnimatePresence mode="wait">
        {!isAuthenticated ? (
          <motion.div
            key="login"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Login />
          </motion.div>
        ) : (
          <motion.div
            key="app"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Layout>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/chat" element={<Chat />} />
                <Route path="/voice" element={<Voice />} />
                <Route path="/vision" element={<Vision />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </Layout>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default App