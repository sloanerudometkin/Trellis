import { RecommendationView } from "./RecommendationView";
import type { AnalysisRunResponse, DismissReason, OrganizerStage, SuggestionResponse } from "./api/contracts";

export function SemView({ analysis, requestError, onDecision, onStageChange }: { analysis: AnalysisRunResponse | null; requestError?: string | null; onDecision: (suggestion: SuggestionResponse, status: "accepted" | "dismissed", reason?: DismissReason) => Promise<void>; onStageChange: (suggestion: SuggestionResponse, stage: OrganizerStage) => Promise<void> }) {
  return <>
    {analysis?.status === "completed" && <section className="sem-summary" aria-label="SEM summary">
      <div><p className="eyebrow">Cost-conscious paid-search plan</p><h2 className="mt-2 font-display text-2xl">{analysis.sem_summary.candidate_count} keyword candidates · {analysis.sem_summary.accepted_count} accepted</h2><p className="mt-2 text-ink/70">Estimated range: {analysis.sem_summary.estimated_cost_range ?? "No Cost Tiers available"}</p></div>
      <div className="disclosure-box"><p className="font-semibold">Cost Tier disclosure</p><p className="mt-1">{analysis.sem_summary.cost_tier_disclosure}</p><p className="mt-3 font-semibold">{analysis.sem_summary.campaign_boundary}</p></div>
    </section>}
    <RecommendationView analysis={analysis} kind="sem" requestError={requestError} onDecision={onDecision} onStageChange={onStageChange} />
  </>;
}
