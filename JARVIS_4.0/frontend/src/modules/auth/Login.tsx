import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { useForm } from 'react-hook-form'
import { Eye, EyeOff, Shield, Cpu } from 'lucide-react'
import toast from 'react-hot-toast'

import { useAuthStore } from '../../stores/authStore'

interface LoginForm {
  username: string
  password: string
}

const Login: React.FC = () => {
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const { login } = useAuthStore()

  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>()

  const onSubmit = async (data: LoginForm) => {
    setIsLoading(true)
    try {
      await login(data.username, data.password)
      toast.success('Welcome back to JARVIS 4.0!')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Login failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-jarvis-darker flex items-center justify-center p-4">
      {/* Background Effects */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-jarvis-blue/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-jarvis-cyan/10 rounded-full blur-3xl" />
      </div>

      <motion.div
        className="relative z-10 w-full max-w-md"
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        {/* Header */}
        <div className="text-center mb-8">
          <motion.div
            className="inline-flex items-center justify-center w-20 h-20 rounded-full glass mb-4"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.3, duration: 0.5 }}
          >
            <Shield className="w-10 h-10 text-jarvis-blue" />
          </motion.div>
          
          <motion.h1
            className="text-3xl font-bold text-gradient mb-2"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5, duration: 0.6 }}
          >
            JARVIS 4.0
          </motion.h1>
          
          <motion.p
            className="text-white/60"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7, duration: 0.6 }}
          >
            Next Generation AI Assistant
          </motion.p>
        </div>

        {/* Login Form */}
        <motion.form
          onSubmit={handleSubmit(onSubmit)}
          className="glass glass-hover rounded-2xl p-8 space-y-6"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4, duration: 0.6 }}
        >
          {/* Username Field */}
          <div>
            <label className="block text-sm font-medium text-white/80 mb-2">
              Username
            </label>
            <input
              {...register('username', { required: 'Username is required' })}
              type="text"
              className="input-glass"
              placeholder="Enter your username"
              autoComplete="username"
            />
            {errors.username && (
              <p className="text-red-400 text-sm mt-1">{errors.username.message}</p>
            )}
          </div>

          {/* Password Field */}
          <div>
            <label className="block text-sm font-medium text-white/80 mb-2">
              Password
            </label>
            <div className="relative">
              <input
                {...register('password', { required: 'Password is required' })}
                type={showPassword ? 'text' : 'password'}
                className="input-glass pr-12"
                placeholder="Enter your password"
                autoComplete="current-password"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-white/60 hover:text-white"
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
            {errors.password && (
              <p className="text-red-400 text-sm mt-1">{errors.password.message}</p>
            )}
          </div>

          {/* Login Button */}
          <motion.button
            type="submit"
            disabled={isLoading}
            className="btn-primary w-full flex items-center justify-center space-x-2"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {isLoading ? (
              <>
                <Cpu className="w-5 h-5 animate-spin" />
                <span>Authenticating...</span>
              </>
            ) : (
              <>
                <Shield className="w-5 h-5" />
                <span>Access JARVIS</span>
              </>
            )}
          </motion.button>

          {/* Default Credentials Info */}
          <motion.div
            className="text-center p-4 rounded-xl bg-white/5 border border-white/10"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1, duration: 0.6 }}
          >
            <p className="text-white/60 text-sm mb-2">Default credentials:</p>
            <p className="text-white/80 text-sm font-mono">
              Username: <span className="text-jarvis-blue">admin</span><br />
              Password: <span className="text-jarvis-blue">jarvis123</span>
            </p>
          </motion.div>
        </motion.form>

        {/* Footer */}
        <motion.div
          className="text-center mt-8 text-white/40 text-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2, duration: 0.6 }}
        >
          <p>"I am JARVIS, and I'm here to help you reach your full potential."</p>
        </motion.div>
      </motion.div>
    </div>
  )
}

export default Login