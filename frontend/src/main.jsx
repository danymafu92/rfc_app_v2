// Entry point for the React application. Renders the top-level <App /> and
// Entry point for the React application. Renders the top-level <App /> and
// imports global styles. Vite handles hot-reload in development.
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom' // 👈 ADD this import
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter> {/* 👈 WRAP <App /> with <BrowserRouter> */}
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)