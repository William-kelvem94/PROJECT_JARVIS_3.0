import React from 'react'

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="min-h-screen bg-jarvis-darker">
      <div className="flex">
        {/* Sidebar placeholder */}
        <div className="w-64 sidebar-glass h-screen">
          <div className="p-6">
            <h2 className="text-xl font-bold text-gradient">JARVIS 4.0</h2>
          </div>
        </div>
        
        {/* Main content */}
        <div className="flex-1">
          {children}
        </div>
      </div>
    </div>
  )
}

export default Layout