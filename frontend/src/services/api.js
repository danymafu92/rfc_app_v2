import axios from 'axios'
import { supabase } from './supabase'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Attach the Supabase session access token to every outgoing request.
// The frontend reads the current session and adds `Authorization: Bearer <token>`
// when available. This protects backend endpoints with Supabase-issued tokens.
api.interceptors.request.use(async (config) => {
  try {
    // Attempt to get the current Supabase session
    const { data } = await supabase.auth.getSession()
    const session = data?.session;
    
    // Attach the access token if a valid session exists
    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`
    } else {
      // Clear any previous Authorization header if no session is found
      delete config.headers.Authorization;
    }
  } catch (error) {
    // Log error but allow request to continue without token, as failure 
    // to get a session should not halt the entire application flow.
    console.error("Failed to inject Supabase auth token into API request:", error);
  }
  return config
})

// Convenience wrappers around backend API endpoints. Use these from React
// components to keep network code centralized and the rest of the app testable.
export const getLocations = () => api.get('/locations/')

export const getLocationParameters = (locationId) => api.get(`/locations/${locationId}/parameters/`)

export const getUserPreferences = () => api.get('/user-preferences/')

export const updateUserPreferences = (data) => api.post('/user-preferences/', data)

export const getRainfallPredictions = (params) => api.get('/rainfall-predictions/', { params })

export const predictRainfall = (locationId) => api.post('/rainfall-predictions/predict/', { location_id: locationId })

export const getFloodingPredictions = (params) => api.get('/flooding-predictions/', { params })

export const predictFlooding = (data) => api.post('/flooding-predictions/predict/', data)

export const getCyclonePredictions = (params) => api.get('/cyclone-predictions/', { params })

export const predictCyclone = (data) => api.post('/cyclone-predictions/predict/', data)

export const getWeatherData = (params) => api.get('/weather-data/', { params })

export const fetchWeatherData = (data) => api.post('/weather-data/fetch/', data)

export default api
