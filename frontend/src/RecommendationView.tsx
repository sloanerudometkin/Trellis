import { useState } from "react";
import type { AnalysisRunResponse, DismissReason, OrganizerStage, SuggestionResponse } from "./api/contracts";

type RecommendationKind = "aeo" | "seo_content" | "sem";

const labels = {
  aeo: { eyebrow: "AEO checklist", empty: "No AEO actions were found for this analysis." },
  seo_content: { eyebrow: "SEO/content plan", empty: "No SEO/content actions were found for this analysis." },
  sem: { eyebrow: "SEM strategy", empty: "No SEM keyword candidates were found for this analysis." },
};

function displayStage(stage: string) {
  return stage.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

const dismissReasons: { value: DismissReason; label: string }[] = [
  { value: "not_relevant", label: "Not relevant" },
  { value: "too_much_work", label: "Too much work right now" },
  { value: "already_doing_this", label: "Already doing this" },
  { value: "other", label: "Another reason" },
];
const stages: { value: OrganizerStage; label: string }[] = [
  { value: "backlog", label: "Backlog" }, { value: "in_production", label: "In Production" },
  { value: "in_review", label: "In Review" }, { value: "published", label: "Published" },
];

function RecommendationCard({ suggestion, checklist, onDecision, onStageChange }: { suggestion: SuggestionResponse; checklist: boolean; onDecision?: (suggestion: SuggestionResponse, status: "accepted" | "dismissed", reason?: DismissReason) => Promise<void>; onStageChange?: (suggestion: SuggestionResponse, stage: OrganizerStage) => Promise<void> }) {
  const [choosingReason, setChoosingReason] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  async function act(action: () => Promise<void>) { setBusy(true); setError(null); try { await action(); setChoosingReason(false); } catch { setError("We couldn’t update this recommendation. Please try again."); } finally { setBusy(false); } }
  return (
    <article className="recommendation-card" data-testid="recommendation-card">
      <div className="flex flex-wrap items-center gap-2">
        {checklist && <span className="check-marker" aria-hidden="true" />}
        <span className={`badge priority-${suggestion.priority}`}>{suggestion.priority} priority</span>
        <span className="badge stage-badge">{displayStage(suggestion.stage)}</span>
      </div>
      <h2 className="mt-4 font-display text-2xl">{suggestion.title}</h2>
      <p className="mt-2 leading-7 text-ink/75">{suggestion.description}</p>
      <div className="rationale-box">
        <h3 className="text-sm font-semibold">Why this matters</h3>
        <p className="mt-1 leading-6 text-ink/70">{suggestion.rationale}</p>
      </div>
      {suggestion.affected_page_url && <p className="mt-4 break-all text-sm text-ink/70"><span className="font-semibold">Page:</span> {suggestion.affected_page_url}</p>}
      {suggestion.starter_outline && (
        <section className="mt-5" aria-label="Starter outline">
          <h3 className="font-display text-xl">Starter outline</h3>
          <ol className="mt-2 list-decimal space-y-2 pl-5 text-ink/75">{suggestion.starter_outline.map((item) => <li key={item}>{item}</li>)}</ol>
        </section>
      )}
      {suggestion.category === "seo_content" && suggestion.target_keywords.length > 0 && (
        <section className="mt-5" aria-label="Target keywords">
          <h3 className="font-display text-xl">Target keywords</h3>
          <ul className="mt-2 space-y-2">{suggestion.target_keywords.map((keyword) => (
            <li className="keyword-row" key={keyword.phrase}><span>{keyword.phrase}</span><span className="font-semibold text-moss">Use about {keyword.recommended_usage_count}×</span></li>
          ))}</ul>
        </section>
      )}
      {suggestion.category === "sem" && <section className="sem-details" aria-label={`Ad group details for ${suggestion.title}`}>
        <div className="flex flex-wrap gap-2">
          <span className="badge cost-tier-badge">Cost Tier: {displayStage(suggestion.cost_tier ?? "unknown")} · heuristic estimate</span>
          {suggestion.cheaper_alternative_to_id && <span className="badge alternative-badge">Cheaper alternative</span>}
        </div>
        <p className="mt-2 text-xs text-ink/70">{suggestion.cost_tier_disclosure}</p>
        {suggestion.sem_keyword && <p className="mt-4"><span className="font-semibold">Keyword:</span> {suggestion.sem_keyword}</p>}
        <dl className="mt-4 grid gap-4 sm:grid-cols-2">
          <div><dt>Ad group</dt><dd>{suggestion.ad_group_label}</dd></div>
          <div><dt>Ad angle</dt><dd>{suggestion.ad_copy_angle}</dd></div>
          <div><dt>Landing page</dt><dd>{suggestion.landing_page_match}</dd></div>
          <div><dt>Targeting</dt><dd>{suggestion.targeting_notes}</dd></div>
        </dl>
        <div className="mt-4"><h3 className="text-sm font-semibold">Starter negative keywords</h3><div className="mt-2 flex flex-wrap gap-2">{suggestion.negative_keywords?.map((keyword) => <span className="negative-chip" key={keyword}>{keyword}</span>)}</div></div>
      </section>}
      <div className="action-row">
        {suggestion.status !== "accepted" && <button className="primary-button action-button" disabled={busy} onClick={() => onDecision && act(() => onDecision(suggestion, "accepted"))}>Accept</button>}
        {suggestion.status !== "dismissed" && <button className="secondary-button" disabled={busy} onClick={() => setChoosingReason(true)}>Dismiss</button>}
        {suggestion.status === "accepted" && <label className="stage-control">Stage<select aria-label={`Stage for ${suggestion.title}`} value={suggestion.stage} disabled={busy} onChange={(event) => onStageChange && act(() => onStageChange(suggestion, event.target.value as OrganizerStage))}>{stages.map((stage) => <option key={stage.value} value={stage.value}>{stage.label}</option>)}</select></label>}
      </div>
      {choosingReason && <div className="reason-picker" role="group" aria-label={`Dismiss reason for ${suggestion.title}`}><p className="text-sm font-semibold">Why are you dismissing this?</p><div className="mt-3 flex flex-wrap gap-2">{dismissReasons.map((reason) => <button className="reason-button" disabled={busy} key={reason.value} onClick={() => onDecision && act(() => onDecision(suggestion, "dismissed", reason.value))}>{reason.label}</button>)}</div></div>}
      {suggestion.status === "dismissed" && <p className="mt-5 text-sm text-ink/70">Dismissed: {displayStage(suggestion.dismiss_reason ?? "other")}</p>}
      {error && <div className="error-box" role="alert">{error}</div>}
    </article>
  );
}

export function RecommendationView({ analysis, kind, requestError, onDecision, onStageChange }: { analysis: AnalysisRunResponse | null; kind: RecommendationKind; requestError?: string | null; onDecision?: (suggestion: SuggestionResponse, status: "accepted" | "dismissed", reason?: DismissReason) => Promise<void>; onStageChange?: (suggestion: SuggestionResponse, stage: OrganizerStage) => Promise<void> }) {
  const copy = labels[kind];
  if (requestError) return <section className="empty-state" role="alert"><p className="eyebrow">Couldn’t load recommendations</p><h2 className="mt-3 font-display text-2xl">{requestError}</h2><p className="mt-3 text-ink/70">Return to Overview and try the analysis again.</p></section>;
  if (!analysis) return <section className="empty-state"><p className="eyebrow">Analysis needed</p><h2 className="mt-3 font-display text-2xl">Run your first website analysis from Overview.</h2><p className="mt-3 text-ink/70">Your persisted recommendations will appear here when it completes.</p></section>;
  if (["queued", "scraping", "analyzing", "generating"].includes(analysis.status)) return <section className="empty-state" role="status" aria-live="polite"><p className="eyebrow">Preparing your action plan</p><h2 className="mt-3 font-display text-2xl">Your analysis is still in progress.</h2><p className="mt-3 text-ink/70">This view will update automatically when your recommendations are ready.</p></section>;
  if (analysis.status === "failed") return <section className="empty-state" role="alert"><p className="eyebrow">Analysis incomplete</p><h2 className="mt-3 font-display text-2xl">We couldn’t finish your action plan.</h2><p className="mt-3 text-ink/70">{analysis.error_message ?? "Return to Overview to retry the analysis."}</p></section>;

  const suggestions = analysis.suggestions.filter((suggestion) => suggestion.category === kind);
  if (suggestions.length === 0) return <section className="empty-state"><p className="eyebrow">{copy.eyebrow}</p><h2 className="mt-3 font-display text-2xl">{copy.empty}</h2><p className="mt-3 text-ink/70">Your completed analysis is saved; run another analysis later to check again.</p></section>;
  return <section className="mt-7" aria-label={copy.eyebrow}><p className="mb-5 max-w-2xl text-ink/70">These site-specific actions are saved with this analysis, so you can return to them anytime.</p><div className="grid gap-5">{suggestions.map((suggestion) => <RecommendationCard key={suggestion.id} suggestion={suggestion} checklist={kind === "aeo"} onDecision={onDecision} onStageChange={onStageChange} />)}</div></section>;
}
