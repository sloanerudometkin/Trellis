import type { AnalysisRunResponse, ReportResponse } from "./api/contracts";
import { HealthScoreCard } from "./HealthScoreCard";

const stageLabels: Record<string, string> = { backlog: "Backlog", in_production: "In Production", in_review: "In Review", published: "Published" };

export function OverviewView({ analysis, latestReport, reportLoading, analysisError, onAnalyze, onRetry, analysisStarting = false }: {
  analysis: AnalysisRunResponse | null; latestReport: ReportResponse | null; reportLoading: boolean; analysisError: string | null;
  onAnalyze: () => void; onRetry: () => void; analysisStarting?: boolean;
}) {
  const progressMessages = {
    queued: "Your analysis is queued and will begin shortly.", scraping: "Reading the public pages Trellis is allowed to visit…",
    analyzing: "Finding meaningful keywords and filtering repeated boilerplate…", generating: "Preparing your analysis results…",
    completed: "Analysis complete.", failed: analysis?.error_message ?? "The analysis could not be completed.",
  };
  if (!analysis) return <section className="empty-state" aria-labelledby="analysis-title" aria-busy={analysisStarting}><p className="eyebrow">Website analysis</p><h2 id="analysis-title" className="mt-3 font-display text-2xl">Turn your website into a starting strategy.</h2><p className="mt-3 max-w-xl leading-7 text-ink/65">Trellis will safely read up to 15 public pages, generate one connected paid-and-organic plan, and save a Report.</p>{analysisError && <div className="error-box" role="alert">{analysisError}</div>}<button className="primary-button sm:w-auto" disabled={analysisStarting} onClick={onAnalyze}>{analysisStarting ? "Starting analysis…" : "Analyze website"}</button></section>;
  if (analysis.status === "failed") return <section className="empty-state" aria-labelledby="analysis-title"><p className="eyebrow">Analysis needs attention</p><h2 id="analysis-title" className="mt-3 font-display text-2xl">We couldn’t finish this analysis.</h2><p className="mt-3" role="alert">{progressMessages.failed}</p>{analysisError && <div className="error-box" role="alert">{analysisError}</div>}<button className="primary-button sm:w-auto" onClick={onRetry}>Retry analysis</button></section>;
  if (analysis.status !== "completed") return <section className="empty-state" aria-busy="true"><p className="eyebrow">Website analysis</p><h2 className="mt-3 font-display text-2xl">Building your connected strategy…</h2><p className="mt-3" role="status" aria-live="polite">{progressMessages[analysis.status]}</p>{analysisError && <div className="error-box" role="alert">{analysisError}</div>}</section>;
  return <section className="mt-7" data-testid="analysis-results" aria-label="Overview summary">
    {analysis.error_message && <div className="partial-notice" role="status"><strong>Partial analysis:</strong> {analysis.error_message} Results from pages Trellis could read are still saved below.</div>}
    <div className="overview-callout"><div><p className="eyebrow">Last analysis</p><h2 className="mt-2 font-display text-2xl">{analysis.completed_at ? new Date(analysis.completed_at).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" }) : "Completed"}</h2><p className="mt-2 text-sm text-ink/65">{analysis.pages_scanned_count} {analysis.pages_scanned_count === 1 ? "page" : "pages"} analyzed</p></div><button className="secondary-button sm:w-auto" onClick={onAnalyze}>Rescan website</button></div>
    {typeof analysis.health_score === "number" && <HealthScoreCard score={analysis.health_score} delta={analysis.health_score_delta ?? null} history={analysis.health_score_history ?? []} disclosure={analysis.health_score_disclosure} />}
    {reportLoading ? <div className="summary-loading" role="status">Loading saved KPI summary…</div> : latestReport ? <div className="overview-grid">
      <article className="summary-card"><p className="eyebrow">AEO checklist</p><strong>{latestReport.aeo_completion_pct}% complete</strong><span>{latestReport.aeo_completion_delta === null ? "First Report" : `${latestReport.aeo_completion_delta > 0 ? "+" : ""}${latestReport.aeo_completion_delta} points since last Report`}</span></article>
      <article className="summary-card"><p className="eyebrow">Pipeline</p><strong>{Object.values(latestReport.organizer_stage_counts).reduce((sum, count) => sum + count, 0)} active cards</strong><span>{Object.entries(latestReport.organizer_stage_counts).map(([stage, count]) => `${stageLabels[stage]} ${count}`).join(" · ")}</span></article>
      <article className="summary-card"><p className="eyebrow">Paid strategy</p><strong>{latestReport.sem_accepted_count} SEM accepted</strong><span>{latestReport.ad_groups_defined_count} starter ad groups defined</span></article>
    </div> : <p className="summary-loading">The saved KPI summary is not available yet. Open Reports to retry.</p>}
    <section className="summary-card mt-5" aria-labelledby="overview-keywords"><p className="eyebrow">Organic opportunities</p><h3 id="overview-keywords" className="mt-2 font-display text-xl">Top keywords</h3>{analysis.keywords.length ? <ul className="mt-3 flex flex-wrap gap-2">{analysis.keywords.slice(0, 10).map((keyword) => <li className="rounded-full border border-moss/20 bg-white px-3 py-1.5 text-sm" key={keyword.phrase}>{keyword.phrase} <span className="text-ink/45">×{keyword.frequency}</span></li>)}</ul> : <p className="mt-2 text-ink/60">No keyword candidates were captured in this run.</p>}</section>
  </section>;
}
