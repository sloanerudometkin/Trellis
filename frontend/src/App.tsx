import { FormEvent, useState } from "react";

import { ApiRequestError, createWebsite } from "./api/client";
import type { WebsiteResponse } from "./api/contracts";

const views = ["Overview", "AEO", "SEO/Content", "SEM", "Reports", "Organizer"] as const;
type View = (typeof views)[number];

function AddWebsiteForm({ onCreated }: { onCreated: (website: WebsiteResponse) => void }) {
  const [url, setUrl] = useState("");
  const [businessName, setBusinessName] = useState("");
  const [businessContext, setBusinessContext] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    const trimmedUrl = url.trim();
    if (!trimmedUrl || /\s/.test(trimmedUrl)) {
      setError("Enter a valid website URL, such as example.com.");
      return;
    }
    const accessToken = window.localStorage.getItem("trellis_access_token");
    if (!accessToken) {
      setError("Your session has expired. Sign in again before adding a website.");
      return;
    }
    setSubmitting(true);
    try {
      const created = await createWebsite({
        url: trimmedUrl,
        business_name: businessName.trim(),
        ...(businessContext.trim() ? { business_context: businessContext.trim() } : {}),
      }, accessToken);
      onCreated(created);
    } catch (caught) {
      if (caught instanceof ApiRequestError && caught.code === "conflict") {
        setError("That website is already in your Trellis account.");
      } else if (caught instanceof ApiRequestError && caught.code === "invalid_url") {
        setError(caught.message);
      } else {
        setError("We couldn't create your workspace. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen px-5 py-12 sm:px-8">
      <section className="mx-auto grid max-w-5xl gap-10 lg:grid-cols-[1fr_1.05fr] lg:items-center">
        <div>
          <p className="eyebrow">Your strategy starts here</p>
          <h1 className="mt-3 max-w-xl font-display text-5xl leading-tight text-ink sm:text-6xl">Grow paid and organic search in one place.</h1>
          <p className="mt-5 max-w-lg text-lg leading-8 text-ink/70">Add your website to create its private Trellis workspace. You can add context now to make future recommendations more relevant.</p>
        </div>
        <form className="panel" onSubmit={handleSubmit} noValidate aria-busy={submitting}>
          <h2 className="font-display text-3xl">Add a website</h2>
          <p className="mt-2 text-sm leading-6 text-ink/65">We’ll save the workspace first. Analysis comes next.</p>
          <label className="field-label" htmlFor="website-url">Website URL</label>
          <input id="website-url" type="text" inputMode="url" autoComplete="url" placeholder="example.com" value={url} onChange={(event) => setUrl(event.target.value)} disabled={submitting} required />
          <label className="field-label" htmlFor="business-name">Business or organization name</label>
          <input id="business-name" type="text" autoComplete="organization" placeholder="Community Garden Network" value={businessName} onChange={(event) => setBusinessName(event.target.value)} disabled={submitting} required />
          <label className="field-label" htmlFor="business-context">Business context <span className="font-normal text-ink/50">(optional)</span></label>
          <textarea id="business-context" rows={4} maxLength={5000} placeholder="Who you serve, what you offer, and your search goals" value={businessContext} onChange={(event) => setBusinessContext(event.target.value)} disabled={submitting} />
          {error && <div className="error-box" role="alert">{error}</div>}
          <button className="primary-button" type="submit" disabled={submitting || !url.trim() || !businessName.trim()}>{submitting ? "Creating workspace…" : "Create workspace"}</button>
        </form>
      </section>
    </main>
  );
}

function Workspace({ website }: { website: WebsiteResponse }) {
  const [activeView, setActiveView] = useState<View>("Overview");
  return (
    <div className="min-h-screen bg-[#f3efe3]">
      <header className="border-b border-moss/15 bg-paper px-5 py-4 sm:px-8">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4">
          <div><p className="font-display text-2xl text-moss">Trellis</p><p className="mt-1 text-xs text-ink/55">Paid + organic search workspace</p></div>
          <div className="min-w-0 text-right"><p className="truncate font-semibold">{website.business_name}</p><p className="truncate text-sm text-ink/55">{website.url}</p></div>
        </div>
      </header>
      <div className="mx-auto grid max-w-7xl md:grid-cols-[220px_1fr]">
        <nav className="border-b border-moss/15 bg-paper p-4 md:min-h-[calc(100vh-81px)] md:border-b-0 md:border-r" aria-label="Workspace views">
          <ul className="flex gap-2 overflow-x-auto md:flex-col">{views.map((view) => <li key={view}><button className={`nav-button ${activeView === view ? "nav-button-active" : ""}`} onClick={() => setActiveView(view)} aria-current={activeView === view ? "page" : undefined}>{view}</button></li>)}</ul>
        </nav>
        <main className="p-5 sm:p-8 lg:p-12">
          <p className="eyebrow">{website.business_name}</p><h1 className="mt-2 font-display text-4xl">{activeView}</h1>
          <section className="empty-state" aria-labelledby="view-state-title"><p className="font-mono text-xs uppercase tracking-[0.16em] text-moss">Workspace ready</p><h2 id="view-state-title" className="mt-3 font-display text-2xl">{activeView} data will appear after analysis.</h2><p className="mt-3 max-w-xl leading-7 text-ink/65">Your website was saved securely. The next MVP step will analyze it and fill this view with site-specific guidance.</p></section>
        </main>
      </div>
    </div>
  );
}

export default function App() {
  const [website, setWebsite] = useState<WebsiteResponse | null>(null);
  return website ? <Workspace website={website} /> : <AddWebsiteForm onCreated={setWebsite} />;
}
