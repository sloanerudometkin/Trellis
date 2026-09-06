import type { AnalysisRunResponse, SuggestionResponse } from "./api/contracts";

type RecommendationKind = "aeo" | "seo_content";

const labels = {
  aeo: { eyebrow: "AEO checklist", empty: "No AEO actions were found for this analysis." },
  seo_content: { eyebrow: "SEO/content plan", empty: "No SEO/content actions were found for this analysis." },
};

function displayStage(stage: string) {
  return stage.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function RecommendationCard({ suggestion, checklist }: { suggestion: SuggestionResponse; checklist: boolean }) {
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
      {suggestion.affected_page_url && <p className="mt-4 break-all text-sm text-ink/60"><span className="font-semibold">Page:</span> {suggestion.affected_page_url}</p>}
      {suggestion.starter_outline && (
        <section className="mt-5" aria-label="Starter outline">
          <h3 className="font-display text-xl">Starter outline</h3>
          <ol className="mt-2 list-decimal space-y-2 pl-5 text-ink/75">{suggestion.starter_outline.map((item) => <li key={item}>{item}</li>)}</ol>
        </section>
      )}
      {suggestion.target_keywords.length > 0 && (
        <section className="mt-5" aria-label="Target keywords">
          <h3 className="font-display text-xl">Target keywords</h3>
          <ul className="mt-2 space-y-2">{suggestion.target_keywords.map((keyword) => (
            <li className="keyword-row" key={keyword.phrase}><span>{keyword.phrase}</span><span className="font-semibold text-moss">Use about {keyword.recommended_usage_count}×</span></li>
          ))}</ul>
        </section>
      )}
    </article>
  );
}

export function RecommendationView({ analysis, kind, requestError }: { analysis: AnalysisRunResponse | null; kind: RecommendationKind; requestError?: string | null }) {
  const copy = labels[kind];
  if (requestError) return <section className="empty-state" role="alert"><p className="eyebrow">Couldn’t load recommendations</p><h2 className="mt-3 font-display text-2xl">{requestError}</h2><p className="mt-3 text-ink/65">Return to Overview and try the analysis again.</p></section>;
  if (!analysis) return <section className="empty-state"><p className="eyebrow">Analysis needed</p><h2 className="mt-3 font-display text-2xl">Run your first website analysis from Overview.</h2><p className="mt-3 text-ink/65">Your persisted recommendations will appear here when it completes.</p></section>;
  if (["queued", "scraping", "analyzing", "generating"].includes(analysis.status)) return <section className="empty-state" role="status" aria-live="polite"><p className="eyebrow">Preparing your action plan</p><h2 className="mt-3 font-display text-2xl">Your analysis is still in progress.</h2><p className="mt-3 text-ink/65">This view will update automatically when your recommendations are ready.</p></section>;
  if (analysis.status === "failed") return <section className="empty-state" role="alert"><p className="eyebrow">Analysis incomplete</p><h2 className="mt-3 font-display text-2xl">We couldn’t finish your action plan.</h2><p className="mt-3 text-ink/65">{analysis.error_message ?? "Return to Overview to retry the analysis."}</p></section>;

  const suggestions = analysis.suggestions.filter((suggestion) => suggestion.category === kind);
  if (suggestions.length === 0) return <section className="empty-state"><p className="eyebrow">{copy.eyebrow}</p><h2 className="mt-3 font-display text-2xl">{copy.empty}</h2><p className="mt-3 text-ink/65">Your completed analysis is saved; run another analysis later to check again.</p></section>;
  return <section className="mt-7" aria-label={copy.eyebrow}><p className="mb-5 max-w-2xl text-ink/65">These site-specific actions are saved with this analysis, so you can return to them anytime.</p><div className="grid gap-5">{suggestions.map((suggestion) => <RecommendationCard key={suggestion.id} suggestion={suggestion} checklist={kind === "aeo"} />)}</div></section>;
}
