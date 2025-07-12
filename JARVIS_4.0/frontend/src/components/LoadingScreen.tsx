import React from 'react'
import { motion } from 'framer-motion'

interface LoadingScreenProps {
  message?: string
}

const LoadingScreen: React.FC<LoadingScreenProps> = ({ 
  message = "Initializing JARVIS 4.0..." 
}) => {
  return (
    <div className="min-h-screen bg-jarvis-darker flex items-center justify-center">
      <div className="text-center">
        {/* JARVIS Logo/Animation */}
        <motion.div
          className="relative w-32 h-32 mx-auto mb-8"
          initial={{ scale: 0.5, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.8 }}
        >
          {/* Outer ring */}
          <motion.div
            className="absolute inset-0 border-2 border-jarvis-blue rounded-full"
            animate={{ rotate: 360 }}
            transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
          />
          
          {/* Inner ring */}
          <motion.div
            className="absolute inset-4 border-2 border-jarvis-cyan rounded-full"
            animate={{ rotate: -360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          />
          
          {/* Center core */}
          <motion.div
            className="absolute inset-8 bg-gradient-to-r from-jarvis-blue to-jarvis-cyan rounded-full"
            animate={{ 
              scale: [1, 1.2, 1],
              opacity: [0.7, 1, 0.7]
            }}
            transition={{ duration: 2, repeat: Infinity }}
          />
          
          {/* JARVIS Text */}
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-white font-mono text-sm font-bold">J.A.R.V.I.S</span>
          </div>
        </motion.div>

        {/* Loading Message */}
        <motion.h2
          className="text-2xl font-semibold text-white mb-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.6 }}
        >
          {message}
        </motion.h2>

        {/* Loading Dots */}
        <motion.div
          className="flex justify-center space-x-2"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1, duration: 0.6 }}
        >
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className="w-3 h-3 bg-jarvis-blue rounded-full"
              animate={{
                scale: [1, 1.5, 1],
                opacity: [0.5, 1, 0.5],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                delay: i * 0.2,
              }}
            />
          ))}
        </motion.div>

        {/* Tagline */}
        <motion.p
          className="text-white/60 mt-6 font-mono text-sm"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5, duration: 0.6 }}
        >
          "Sometimes you gotta run before you can walk"
        </motion.p>
      </div>
    </div>
  )
}

export default LoadingScreen