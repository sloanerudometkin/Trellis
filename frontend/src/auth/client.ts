import { createClient, type Session } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL?.trim() ?? "";
const supabasePublishableKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY?.trim() ?? "";

const testAuthBypassEnabled = import.meta.env.MODE === "test" || (
  import.meta.env.DEV && import.meta.env.VITE_E2E_AUTH_BYPASS === "true"
);

export function getTestAccessToken(): string | null {
  return testAuthBypassEnabled ? window.localStorage.getItem("trellis_access_token") : null;
}

export const isAuthConfigured = Boolean(
  supabaseUrl &&
  supabasePublishableKey &&
  !supabaseUrl.includes("your-project-id") &&
  !supabasePublishableKey.includes("replace-me"),
);

const supabase = isAuthConfigured
  ? createClient(supabaseUrl, supabasePublishableKey, {
      auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true },
    })
  : null;

export async function getCurrentSession(): Promise<Session | null> {
  // Automated tests can cross the auth boundary without contacting Supabase.
  // Vite replaces DEV with false in production, so the browser-test bypass cannot ship enabled.
  const testAccessToken = getTestAccessToken();
  if (testAccessToken) return { access_token: testAccessToken } as Session;
  if (!supabase) return null;
  const { data, error } = await supabase.auth.getSession();
  if (error) throw error;
  return data.session;
}

export function onAuthStateChange(callback: (session: Session | null) => void): () => void {
  if (!supabase) return () => undefined;
  const { data } = supabase.auth.onAuthStateChange((_event, session) => callback(session));
  return () => data.subscription.unsubscribe();
}

export async function signInWithPassword(email: string, password: string): Promise<void> {
  if (!supabase) throw new Error("Supabase is not configured.");
  const { error } = await supabase.auth.signInWithPassword({ email, password });
  if (error) throw error;
}

export async function signUpWithPassword(name: string, email: string, password: string): Promise<{ confirmationRequired: boolean }> {
  if (!supabase) throw new Error("Supabase is not configured.");
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: { data: { name }, emailRedirectTo: window.location.origin },
  });
  if (error) throw error;
  return { confirmationRequired: !data.session };
}

export async function signOut(): Promise<void> {
  if (!supabase) return;
  const { error } = await supabase.auth.signOut();
  if (error) throw error;
}
