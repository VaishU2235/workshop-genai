import { useEffect, useState } from 'react'
import { UserAuth } from './components/UserAuth'
import { LogoutButton } from './components/LogoutButton'
import { Toaster } from '@/components/ui/toaster'
import './App.css'
import Dashboard from './components/Dashboard'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false)

  useEffect(() => {
    // Check if token exists in localStorage
    const token = localStorage.getItem('token')
    setIsAuthenticated(!!token)
  }, [])

  if (!isAuthenticated) {
    return (
      <>
        <UserAuth onAuthSuccess={() => setIsAuthenticated(true)} />
        <Toaster />
      </>
    )
  }

  return (
    <>
      <div className="min-h-screen">
        {/* Header */}
        <header className="border-b">
          <div className="container mx-auto px-4 py-3 flex justify-between items-center">
            <h1 className="text-xl font-semibold">GenAI Workshop</h1>
            <LogoutButton onLogout={() => setIsAuthenticated(false)} />
          </div>
        </header>

        {/* Main Content */}
        <main>
          <Dashboard />
        </main>
      </div>
      <Toaster />
    </>
  )
}

export default App
