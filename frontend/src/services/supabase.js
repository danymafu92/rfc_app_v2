// Minimal Supabase client wrapper used by the frontend.
//
// - Reads Vite env vars `VITE_SUPABASE_URL` and `VITE_SUPABASE_KEY`.
// - Exposes small helpers used by UI components (signIn, signOut, getSession).
//
// The axios `api` layer uses `supabase.auth.getSession()` to attach the
// current access token to backend requests. Keep this file small and side-
// effect free so it's easy to mock in tests.
import { createClient } from '@supabase/supabase-js'

// FIX: Added VITE_ prefix to read the exposed variables
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseKey)

export const signIn = async (email, password) => {
// ... (rest of the file is unchanged)
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  })
  return { data, error }
}

export const signUp = async (email, password) => {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
  })
  return { data, error }
}

export const signOut = async () => {
  const { error } = await supabase.auth.signOut()
  return { error }
}

export const getCurrentUser = async () => {
  const { data: { user }, error } = await supabase.auth.getUser()
  return { user, error }
}

export const getSession = async () => {
  const { data: { session }, error } = await supabase.auth.getSession()
  return { session, error }
}
