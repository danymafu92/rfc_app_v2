// Top-level React router and session bootstrap.
// - Uses Supabase session to gate routes.
// - Routes mounted under `/` assume the backend API is proxied at `/api`.
import { Routes, Route, Navigate } from 'react-router-dom' // Removed 'BrowserRouter as Router'
import { useState, useEffect } from 'react'
import { supabase } from './services/supabase'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import CyclonePrediction from './pages/CyclonePrediction'
import FloodingPrediction from './pages/FloodingPrediction'
import RainfallData from './pages/RainfallData'
import Layout from './components/Layout'

function App() {
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let mounted = true

    // Initialize session state on mount
    const checkSession = async () => {
      try {
        const { data: { session }, error } = await supabase.auth.getSession()
        
        if (error) throw error

        if (mounted) {
          setSession(session)
        }
      } catch (err) {
        // Log error, but ensure UI still loads
        // eslint-disable-next-line no-console
        console.error('Failed to get Supabase session:', err)
        if (mounted) {
          setSession(null)
        }
      } finally {
        if (mounted) {
          setLoading(false)
        }
      }
    }
    
    checkSession() // Run the initial check

    // Subscribe to auth state changes
    const { data: listener } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        if (mounted) setSession(session)
      }
    )

    // Cleanup function
    return () => {
      mounted = false
      // Use the specific unsubscribe method returned by the listener object
      if (listener && typeof listener.unsubscribe === 'function') {
        listener.unsubscribe()
      }
    }
  }, []) // Empty dependency array means this runs once on mount

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <div>Loading...</div>
      </div>
    )
  }

  return (
    // REMOVED: <Router> tag as it is now in main.jsx
    <Routes>
      <Route
        path="/login"
        element={!session ? <Login /> : <Navigate to="/dashboard" />}
      />
      <Route
        path="/"
        element={session ? <Layout /> : <Navigate to="/login" />}
      >
        <Route index element={<Navigate to="/dashboard" />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="cyclone" element={<CyclonePrediction />} />
        <Route path="flooding" element={<FloodingPrediction />} />
        <Route path="rainfall" element={<RainfallData />} />
      </Route>
    </Routes>
    // REMOVED: </Router> tag
  )
}

export default App
