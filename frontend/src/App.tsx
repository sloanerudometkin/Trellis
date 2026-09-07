import { FormEvent, useEffect, useState } from "react";

import { ApiRequestError, createWebsite, decideSuggestion, getAnalysis, getOrganizerItems, retryAnalysis, startAnalysis, updateOrganizerItem, updateSuggestionStage } from "./api/client";
import type { AnalysisRunResponse, AnalysisStatus, DismissReason, OrganizerItemResponse, OrganizerStage, SuggestionResponse, WebsiteResponse } from "./api/contracts";
import { RecommendationView } from "./RecommendationView";
import { OrganizerView } from "./OrganizerView";
import { TechnicalAuditView } from "./TechnicalAuditView";
import { SemView } from "./SemView";
import { HealthScoreCard } from "./HealthScoreCard";
import { ReportsView } from "./ReportsView";

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
  const [analysis, setAnalysis] = useState<AnalysisRunResponse | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [organizerItems, setOrganizerItems] = useState<OrganizerItemResponse[]>([]);
  const [organizerLoading, setOrganizerLoading] = useState(false);
  const [organizerError, setOrganizerError] = useState<string | null>(null);
  const accessToken = window.localStorage.getItem("trellis_access_token") ?? "";

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
    try {
      setAnalysis(await startAnalysis(website.id, accessToken));
    } catch {
      setAnalysisError("We couldn't start the analysis. Please try again.");
    }
  }

  async function retryFailedAnalysis() {
    if (!analysis) return;
    setAnalysisError(null);
    try {
      setAnalysis(await retryAnalysis(analysis.id, accessToken));
    } catch {
      setAnalysisError("We couldn't retry the analysis. Please try again.");
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
    catch { setOrganizerError("We couldn’t load your Organizer. Please try again."); }
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

  const progressMessages: Record<AnalysisStatus, string> = {
    queued: "Your analysis is queued and will begin shortly.",
    scraping: "Reading the public pages Trellis is allowed to visit…",
    analyzing: "Finding meaningful keywords and filtering repeated boilerplate…",
    generating: "Preparing your analysis results…",
    completed: "Analysis complete.",
    failed: analysis?.error_message ?? "The analysis could not be completed.",
  };
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
          {activeView === "Overview" ? (
            <section className="empty-state" aria-labelledby="analysis-title">
              <p className="font-mono text-xs uppercase tracking-[0.16em] text-moss">Website analysis</p>
              <h2 id="analysis-title" className="mt-3 font-display text-2xl">{analysis?.status === "completed" ? "Your first results are ready." : "Turn your website into a starting strategy."}</h2>
              {!analysis && <p className="mt-3 max-w-xl leading-7 text-ink/65">Trellis will safely read up to 15 public pages and identify the language your website emphasizes.</p>}
              {analysis && <p className="mt-3 max-w-xl leading-7 text-ink/70" role={analysis.status === "failed" ? "alert" : "status"} aria-live="polite">{progressMessages[analysis.status]}</p>}
              {analysisError && <div className="error-box" role="alert">{analysisError}</div>}
              {!analysis && <button className="primary-button sm:w-auto" onClick={beginAnalysis}>Analyze website</button>}
              {analysis?.status === "failed" && <button className="primary-button sm:w-auto" onClick={retryFailedAnalysis}>Retry analysis</button>}
              {analysis?.status === "completed" && (
                <div className="mt-7" data-testid="analysis-results">
                  {typeof analysis.health_score === "number" && <HealthScoreCard score={analysis.health_score} delta={analysis.health_score_delta ?? null} history={analysis.health_score_history ?? []} disclosure={analysis.health_score_disclosure} />}
                  <p className="text-sm font-semibold">{analysis.pages_scanned_count} {analysis.pages_scanned_count === 1 ? "page" : "pages"} analyzed</p>
                  <h3 className="mt-5 font-display text-xl">Top keywords</h3>
                  <ul className="mt-3 flex flex-wrap gap-2">{analysis.keywords.slice(0, 10).map((keyword) => <li className="rounded-full border border-moss/20 bg-white px-3 py-1.5 text-sm" key={keyword.phrase}>{keyword.phrase} <span className="text-ink/45">×{keyword.frequency}</span></li>)}</ul>
                  <button className="secondary-button mt-6 sm:w-auto" onClick={beginAnalysis}>Rescan website</button>
                </div>
              )}
            </section>
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
          ) : (
            <section className="empty-state" aria-labelledby="view-state-title"><p className="font-mono text-xs uppercase tracking-[0.16em] text-moss">Workspace ready</p><h2 id="view-state-title" className="mt-3 font-display text-2xl">{activeView} data will appear as later MVP features are completed.</h2></section>
          )}
        </main>
      </div>
    </div>
  );
}

export default function App() {
  const [website, setWebsite] = useState<WebsiteResponse | null>(null);
  return website ? <Workspace website={website} /> : <AddWebsiteForm onCreated={setWebsite} />;
}
