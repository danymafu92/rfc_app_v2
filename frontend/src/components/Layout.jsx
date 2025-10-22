// App layout component: navigation bar, sign-out action and content outlet.
// Links use client-side routing; sign-out delegates to `services/supabase.js`.
import { Outlet, Link, useNavigate } from 'react-router-dom'
import { signOut } from '../services/supabase'
import './Layout.css'

function Layout() {
  const navigate = useNavigate()

  const handleSignOut = async () => {
    await signOut()
    navigate('/login')
  }

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="navbar-brand">
          <h1>Weather Prediction Platform</h1>
        </div>
        <div className="navbar-links">
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/cyclone">Cyclone Predictions</Link>
          <Link to="/flooding">Flooding Predictions</Link>
          <Link to="/rainfall">Rainfall Data</Link>
        </div>
        <button className="btn-signout" onClick={handleSignOut}>
          Sign Out
        </button>
      </nav>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}

export default Layout
