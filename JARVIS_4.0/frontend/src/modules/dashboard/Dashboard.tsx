import React from 'react'

const Dashboard: React.FC = () => {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-gradient mb-8">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="card-glass">
          <h3 className="text-xl font-semibold mb-4">System Status</h3>
          <p className="text-white/60">All systems operational</p>
        </div>
        <div className="card-glass">
          <h3 className="text-xl font-semibold mb-4">AI Models</h3>
          <p className="text-white/60">Local LLM ready</p>
        </div>
        <div className="card-glass">
          <h3 className="text-xl font-semibold mb-4">Voice Assistant</h3>
          <p className="text-white/60">Whisper initialized</p>
        </div>
      </div>
    </div>
  )
}

export default Dashboard