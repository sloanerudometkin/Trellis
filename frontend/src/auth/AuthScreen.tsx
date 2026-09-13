import { FormEvent, useState } from "react";

type AuthScreenProps = {
  configured: boolean;
  onSignIn: (email: string, password: string) => Promise<void>;
  onSignUp: (name: string, email: string, password: string) => Promise<{ confirmationRequired: boolean }>;
};

function friendlyAuthError(error: unknown): string {
  const message = error instanceof Error ? error.message.toLowerCase() : "";
  if (message.includes("email not confirmed")) return "Confirm your email address before signing in.";
  if (message.includes("invalid login") || message.includes("credentials")) return "Check your email and password, then try again.";
  if (message.includes("already registered")) return "An account already exists for this email. Try signing in.";
  if (message.includes("password")) return "Use a password with at least 8 characters.";
  return "We couldn’t complete that request. Please try again.";
}

export function AuthScreen({ configured, onSignIn, onSignUp }: AuthScreenProps) {
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setNotice(null);
    setBusy(true);
    try {
      if (mode === "signin") {
        await onSignIn(email.trim(), password);
      } else {
        const result = await onSignUp(name.trim(), email.trim(), password);
        if (result.confirmationRequired) setNotice("Check your email to confirm your account, then return here to sign in.");
      }
    } catch (caught) {
      setError(friendlyAuthError(caught));
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="auth-shell">
      <section className="auth-intro">
        <p className="eyebrow">Welcome to Trellis</p>
        <h1>Turn search insights into a plan you can finish.</h1>
        <p>Sign in to keep every website, recommendation, Organizer task, and Report private to your account.</p>
      </section>
      <section className="panel auth-panel" aria-labelledby="auth-heading">
        <p className="font-display text-2xl text-moss">Trellis</p>
        <h2 id="auth-heading" className="mt-4 font-display text-3xl">{mode === "signin" ? "Sign in" : "Create your account"}</h2>
        <p className="mt-2 text-sm leading-6 text-ink/70">{mode === "signin" ? "Continue to your paid and organic search workspace." : "Start building your first website workspace."}</p>
        {!configured && <div className="error-box" role="alert">Trellis needs its Supabase connection before accounts can be used. Add the frontend project URL and publishable key to <code>frontend/.env</code>, then restart the site.</div>}
        <form onSubmit={submit}>
          {mode === "signup" && <><label className="field-label" htmlFor="auth-name">Name</label><input id="auth-name" autoComplete="name" value={name} onChange={(event) => setName(event.target.value)} required /></>}
          <label className="field-label" htmlFor="auth-email">Email address</label>
          <input id="auth-email" type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
          <label className="field-label" htmlFor="auth-password">Password</label>
          <input id="auth-password" type="password" autoComplete={mode === "signin" ? "current-password" : "new-password"} minLength={8} value={password} onChange={(event) => setPassword(event.target.value)} required />
          {error && <div className="error-box" role="alert">{error}</div>}
          {notice && <div className="notice-box" role="status">{notice}</div>}
          <button className="primary-button" type="submit" disabled={!configured || busy}>{busy ? "Please wait…" : mode === "signin" ? "Sign in" : "Create my account"}</button>
        </form>
        <button className="auth-switch" type="button" onClick={() => { setMode(mode === "signin" ? "signup" : "signin"); setError(null); setNotice(null); }}>
          {mode === "signin" ? "Create account" : "Already have an account? Sign in"}
        </button>
      </section>
    </main>
  );
}
