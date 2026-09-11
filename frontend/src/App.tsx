import { FormEvent, useEffect, useState } from "react";

import { ApiRequestError, createWebsite, decideSuggestion, getAnalysis, getOrganizerItems, getReports, retryAnalysis, startAnalysis, updateOrganizerItem, updateSuggestionStage } from "./api/client";
import type { AnalysisRunResponse, DismissReason, OrganizerItemResponse, OrganizerStage, ReportResponse, SuggestionResponse, WebsiteResponse } from "./api/contracts";
import { RecommendationView } from "./RecommendationView";
import { OrganizerView } from "./OrganizerView";
import { TechnicalAuditView } from "./TechnicalAuditView";
import { SemView } from "./SemView";
import { ReportsView } from "./ReportsView";
import { OverviewView } from "./OverviewView";
import { AuthScreen } from "./auth/AuthScreen";
import { getCurrentSession, getTestAccessToken, isAuthConfigured, onAuthStateChange, signInWithPassword, signOut, signUpWithPassword } from "./auth/client";

const views = ["Overview", "AEO", "SEO/Content", "SEM", "Reports", "Organizer"] as const;
type View = (typeof views)[number];

function requestErrorMessage(caught: unknown, fallback: string) {
  return caught instanceof ApiRequestError && caught.code === "unauthorized" ? "Your session has expired. Sign in again." : fallback;
}

function AddWebsiteForm({ accessToken, onCreated }: { accessToken: string; onCreated: (website: WebsiteResponse) => void }) {
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
          <p className="mt-2 text-sm leading-6 text-ink/70">We’ll save the workspace first. Analysis comes next.</p>
          <label className="field-label" htmlFor="website-url">Website URL</label>
          <input id="website-url" type="text" inputMode="url" autoComplete="url" placeholder="example.com" value={url} onChange={(event) => setUrl(event.target.value)} disabled={submitting} required />
          <label className="field-label" htmlFor="business-name">Business or organization name</label>
          <input id="business-name" type="text" autoComplete="organization" placeholder="Community Garden Network" value={businessName} onChange={(event) => setBusinessName(event.target.value)} disabled={submitting} required />
          <label className="field-label" htmlFor="business-context">Business context <span className="font-normal text-ink/70">(optional)</span></label>
          <textarea id="business-context" rows={4} maxLength={5000} placeholder="Who you serve, what you offer, and your search goals" value={businessContext} onChange={(event) => setBusinessContext(event.target.value)} disabled={submitting} />
          {error && <div className="error-box" role="alert">{error}</div>}
          <button className="primary-button" type="submit" disabled={submitting || !url.trim() || !businessName.trim()}>{submitting ? "Creating workspace…" : "Create workspace"}</button>
        </form>
      </section>
    </main>
  );
}

function Workspace({ website, accessToken, onSignOut }: { website: WebsiteResponse; accessToken: string; onSignOut: () => Promise<void> }) {
  const [activeView, setActiveView] = useState<View>("Overview");
  const [analysis, setAnalysis] = useState<AnalysisRunResponse | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [analysisStarting, setAnalysisStarting] = useState(false);
  const [organizerItems, setOrganizerItems] = useState<OrganizerItemResponse[]>([]);
  const [organizerLoading, setOrganizerLoading] = useState(false);
  const [organizerError, setOrganizerError] = useState<string | null>(null);
  const [latestReport, setLatestReport] = useState<ReportResponse | null>(null);
  const [reportLoading, setReportLoading] = useState(false);
  useEffect(() => {
    if (!analysis || analysis.status === "completed" || analysis.status === "failed") return;
    const timer = window.setTimeout(async () => {
      try {
        setAnalysis(await getAnalysis(analysis.id, accessToken));
      } catch {
        setAnalysisError("We lost contact with the analysis. Please try again.");
      }
    }, 750);
    return () => window.clearTimeout(timer);
  }, [analysis, accessToken]);

  async function beginAnalysis() {
    setAnalysisError(null);
    setAnalysisStarting(true);
    try {
      setAnalysis(await startAnalysis(website.id, accessToken));
    } catch (caught) {
      setAnalysisError(requestErrorMessage(caught, "We couldn't start the analysis. Please try again."));
    } finally { setAnalysisStarting(false); }
  }

  async function retryFailedAnalysis() {
    if (!analysis) return;
    setAnalysisError(null);
    try {
      setAnalysis(await retryAnalysis(analysis.id, accessToken));
    } catch (caught) {
      setAnalysisError(requestErrorMessage(caught, "We couldn't retry the analysis. Please try again."));
    }
  }

  function replaceSuggestion(updated: SuggestionResponse) {
    setAnalysis((current) => {
      if (!current) return current;
      const suggestions = current.suggestions.map((item) => item.id === updated.id ? updated : item);
      return {
        ...current,
        suggestions,
        sem_summary: {
          ...current.sem_summary,
          accepted_count: suggestions.filter((item) => item.category === "sem" && item.status === "accepted").length,
        },
      };
    });
  }

  async function refreshOrganizer() {
    setOrganizerLoading(true); setOrganizerError(null);
    try { setOrganizerItems(await getOrganizerItems(website.id, accessToken)); }
    catch (caught) { setOrganizerError(requestErrorMessage(caught, "We couldn’t load your Organizer. Please try again.")); }
    finally { setOrganizerLoading(false); }
  }

  async function handleDecision(suggestion: SuggestionResponse, status: "accepted" | "dismissed", reason?: DismissReason) {
    replaceSuggestion(await decideSuggestion(suggestion.id, status, accessToken, reason));
    await refreshOrganizer();
  }

  async function handleSuggestionStage(suggestion: SuggestionResponse, stage: OrganizerStage) {
    replaceSuggestion(await updateSuggestionStage(suggestion.id, stage, accessToken));
    setOrganizerItems((items) => items.map((item) => item.suggestion_id === suggestion.id ? { ...item, stage } : item));
  }

  async function handleOrganizerStage(item: OrganizerItemResponse, stage: OrganizerStage) {
    const updated = await updateOrganizerItem(item.id, stage, accessToken);
    setOrganizerItems((items) => items.map((candidate) => candidate.id === updated.id ? updated : candidate));
    if (analysis && item.suggestion_id) setAnalysis(await getAnalysis(analysis.id, accessToken));
  }

  useEffect(() => { if (activeView === "Organizer") void refreshOrganizer(); }, [activeView]);
  useEffect(() => {
    if (analysis?.status !== "completed") return;
    setReportLoading(true);
    void getReports(website.id, accessToken).then((reports) => setLatestReport(reports[0] ?? null)).catch((caught) => {
      if (caught instanceof ApiRequestError && caught.code === "unauthorized") setAnalysisError("Your session has expired. Sign in again.");
    }).finally(() => setReportLoading(false));
  }, [analysis?.id, analysis?.status, website.id, accessToken]);

  function handleNavKey(event: React.KeyboardEvent<HTMLButtonElement>, index: number) {
    if (!["ArrowDown", "ArrowUp", "ArrowRight", "ArrowLeft", "Home", "End"].includes(event.key)) return;
    event.preventDefault();
    const next = event.key === "Home" ? 0 : event.key === "End" ? views.length - 1 : (index + (["ArrowDown", "ArrowRight"].includes(event.key) ? 1 : -1) + views.length) % views.length;
    setActiveView(views[next]);
    document.getElementById(`workspace-tab-${next}`)?.focus();
  }
  return (
    <div className="min-h-screen bg-[#f3efe3]"><a className="skip-link" href="#workspace-content">Skip to workspace content</a>
      <header className="border-b border-moss/15 bg-paper px-5 py-4 sm:px-8">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4">
          <div><p className="font-display text-2xl text-moss">Trellis</p><p className="mt-1 text-xs text-ink/70">Paid + organic search workspace</p></div>
          <div className="flex min-w-0 items-center gap-4"><div className="min-w-0 text-right"><p className="truncate font-semibold">{website.business_name}</p><p className="truncate text-sm text-ink/70">{website.url}</p></div><button className="header-button" type="button" onClick={() => void onSignOut()}>Sign out</button></div>
        </div>
      </header>
      <div className="mx-auto grid max-w-7xl md:grid-cols-[220px_1fr]">
        <nav className="min-w-0 overflow-hidden border-b border-moss/15 bg-paper p-4 md:min-h-[calc(100vh-81px)] md:border-b-0 md:border-r" aria-label="Workspace views">
          <ul className="flex gap-2 overflow-x-auto md:flex-col">{views.map((view, index) => <li key={view}><button id={`workspace-tab-${index}`} className={`nav-button ${activeView === view ? "nav-button-active" : ""}`} onClick={() => setActiveView(view)} onKeyDown={(event) => handleNavKey(event, index)} aria-current={activeView === view ? "page" : undefined}>{view}</button></li>)}</ul>
        </nav>
        <main id="workspace-content" tabIndex={-1} className="min-w-0 p-5 sm:p-8 lg:p-12">
          <p className="eyebrow">{website.business_name}</p><h1 className="mt-2 font-display text-4xl">{activeView}</h1>
          {activeView === "Overview" ? (
            <OverviewView analysis={analysis} latestReport={latestReport} reportLoading={reportLoading} analysisError={analysisError} onAnalyze={beginAnalysis} onRetry={retryFailedAnalysis} analysisStarting={analysisStarting} />
          ) : activeView === "AEO" ? (
            <RecommendationView analysis={analysis} kind="aeo" requestError={analysisError} onDecision={handleDecision} onStageChange={handleSuggestionStage} />
          ) : activeView === "SEO/Content" ? (
            <><RecommendationView analysis={analysis} kind="seo_content" requestError={analysisError} onDecision={handleDecision} onStageChange={handleSuggestionStage} />{analysis?.status === "completed" && <TechnicalAuditView audit={analysis.technical_audit} />}</>
          ) : activeView === "SEM" ? (
            <SemView analysis={analysis} requestError={analysisError} onDecision={handleDecision} onStageChange={handleSuggestionStage} />
          ) : activeView === "Organizer" ? (
            <OrganizerView items={organizerItems} loading={organizerLoading} error={organizerError} onStageChange={handleOrganizerStage} />
          ) : activeView === "Reports" ? (
            <ReportsView websiteId={website.id} accessToken={accessToken} refreshKey={analysis?.id} />
          ) : null}
        </main>
      </div>
    </div>
  );
}

export default function App() {
  const initialTestAccessToken = getTestAccessToken();
  const [website, setWebsite] = useState<WebsiteResponse | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(initialTestAccessToken);
  const [authLoading, setAuthLoading] = useState(!initialTestAccessToken);

  useEffect(() => {
    let active = true;
    void getCurrentSession().then((session) => {
      if (active) setAccessToken(session?.access_token ?? null);
    }).catch(() => {
      if (active) setAccessToken(null);
    }).finally(() => { if (active) setAuthLoading(false); });
    const unsubscribe = onAuthStateChange((session) => {
      setAccessToken(session?.access_token ?? null);
      setWebsite(null);
      setAuthLoading(false);
    });
    return () => { active = false; unsubscribe(); };
  }, []);

  async function handleSignOut() {
    await signOut();
    setAccessToken(null);
    setWebsite(null);
  }

  if (authLoading) return <main className="auth-loading" role="status">Opening your Trellis workspace…</main>;
  if (!accessToken) return <AuthScreen configured={isAuthConfigured} onSignIn={signInWithPassword} onSignUp={signUpWithPassword} />;
  return website ? <Workspace website={website} accessToken={accessToken} onSignOut={handleSignOut} /> : <AddWebsiteForm accessToken={accessToken} onCreated={setWebsite} />;
}
