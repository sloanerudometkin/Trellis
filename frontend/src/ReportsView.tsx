import { useEffect, useState } from "react";
import { compareReports, getReports } from "./api/client";
import type { NumericDelta, ReportComparisonResponse, ReportResponse } from "./api/contracts";

const labels: Record<string, string> = {
  health_score: "Health Score", health_score_delta: "Health Score change since prior Report", aeo_completion_pct: "AEO completion", aeo_completion_delta: "AEO completion change since prior Report", technical_findings_resolved: "Technical findings resolved",
  technical_findings_open: "Technical findings open", content_published_count: "Cards published this period", sem_accepted_count: "SEM suggestions accepted",
  ad_groups_defined_count: "Starter ad groups", sem_cost_tier_low: "Accepted Low Cost Tier", sem_cost_tier_medium: "Accepted Medium Cost Tier",
  sem_cost_tier_high: "Accepted High Cost Tier", organizer_stage_backlog: "Backlog", organizer_stage_in_production: "In Production",
  organizer_stage_in_review: "In Review", organizer_stage_published: "Published",
};

function dateLabel(value: string) { return new Date(value).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" }); }
function deltaLabel(delta?: NumericDelta) {
  if (!delta) return "—";
  if (delta.absolute === null) return "—";
  const sign = delta.absolute > 0 ? "+" : "";
  return `${sign}${delta.absolute}${delta.percentage === null ? " (new from zero)" : ` (${sign}${delta.percentage.toFixed(1)}%)`}`;
}
function values(report: ReportResponse): Record<string, number | null> {
  return {
    health_score: report.health_score, health_score_delta: report.health_score_delta, aeo_completion_pct: report.aeo_completion_pct, aeo_completion_delta: report.aeo_completion_delta,
    technical_findings_resolved: report.technical_findings_resolved, technical_findings_open: report.technical_findings_open,
    content_published_count: report.content_published_count, sem_accepted_count: report.sem_accepted_count,
    ad_groups_defined_count: report.ad_groups_defined_count,
    ...Object.fromEntries(Object.entries(report.sem_cost_tier_breakdown).map(([key, value]) => [`sem_cost_tier_${key}`, value])),
    ...Object.fromEntries(Object.entries(report.organizer_stage_counts).map(([key, value]) => [`organizer_stage_${key}`, value])),
  };
}

function ReportDetail({ report }: { report: ReportResponse }) {
  const data = values(report);
  const group = (title: string, keys: string[]) => <section className="report-group" aria-label={`${title} KPIs`}><h3>{title}</h3><dl>{keys.map((key) => <div key={key}><dt>{labels[key]}</dt><dd>{data[key] ?? "—"}</dd></div>)}</dl></section>;
  return <div className="report-detail"><p className="report-summary" data-testid="current-report-summary">{report.summary_text}</p><p className="report-disclosure">{report.disclosure}</p><div className="report-groups">
    {group("Organic", ["health_score", "health_score_delta", "aeo_completion_pct", "aeo_completion_delta", "technical_findings_resolved", "technical_findings_open", "content_published_count"])}
    {group("Paid (heuristic)", ["sem_accepted_count", "sem_cost_tier_low", "sem_cost_tier_medium", "sem_cost_tier_high", "ad_groups_defined_count"])}
    {group("Pipeline", ["organizer_stage_backlog", "organizer_stage_in_production", "organizer_stage_in_review", "organizer_stage_published"])}
  </div><section className="report-group" aria-label="Top keyword candidates"><h3>Top keyword candidates</h3><p>{report.top_keywords.length ? report.top_keywords.join(", ") : "None captured"}</p></section></div>;
}

export function ReportsView({ websiteId, accessToken, refreshKey }: { websiteId: number; accessToken: string; refreshKey?: number }) {
  const [reports, setReports] = useState<ReportResponse[]>([]); const [openId, setOpenId] = useState<number | null>(null);
  const [beforeId, setBeforeId] = useState<number | null>(null); const [afterId, setAfterId] = useState<number | null>(null);
  const [comparison, setComparison] = useState<ReportComparisonResponse | null>(null); const [error, setError] = useState<string | null>(null);
  useEffect(() => { void getReports(websiteId, accessToken).then((items) => { setReports(items); setOpenId((current) => current ?? items[0]?.id ?? null); setAfterId(items[0]?.id ?? null); setBeforeId(items[1]?.id ?? null); }).catch(() => setError("We couldn’t load Report history.")); }, [websiteId, accessToken, refreshKey]);
  async function runComparison() { if (!beforeId || !afterId || beforeId === afterId) return; setError(null); try { setComparison(await compareReports(websiteId, beforeId, afterId, accessToken)); } catch { setError("We couldn’t compare those Reports."); } }
  if (error && reports.length === 0) return <div className="error-box" role="alert">{error}</div>;
  if (reports.length === 0) return <section className="empty-state"><h2 className="font-display text-2xl">No Reports yet</h2><p>Complete an analysis to save your first KPI snapshot.</p></section>;
  const open = reports.find((item) => item.id === openId) ?? reports[0];
  return <section className="reports-view" aria-label="Report history"><div className="report-history"><h2>Report history</h2>{reports.map((report) => <button key={report.id} onClick={() => { setOpenId(report.id); setComparison(null); }} aria-pressed={open.id === report.id}><strong>{dateLabel(report.generated_at)}</strong><span>{report.summary_text}</span></button>)}</div>
    <ReportDetail report={open} />
    <section className="report-compare" aria-label="Compare Reports"><h2>Compare two Reports</h2><div className="compare-controls"><label>Earlier Report<select aria-label="Earlier Report" value={beforeId ?? ""} onChange={(e) => setBeforeId(Number(e.target.value))}>{reports.map((report) => <option key={report.id} value={report.id}>{dateLabel(report.generated_at)}</option>)}</select></label><label>Later Report<select aria-label="Later Report" value={afterId ?? ""} onChange={(e) => setAfterId(Number(e.target.value))}>{reports.map((report) => <option key={report.id} value={report.id}>{dateLabel(report.generated_at)}</option>)}</select></label><button className="primary-button sm:w-auto" disabled={!beforeId || !afterId || beforeId === afterId} onClick={runComparison}>Compare Reports</button></div>{error && <div className="error-box" role="alert">{error}</div>}
      {comparison && <div className="comparison-table" role="region" aria-label="Report comparison"><table><thead><tr><th>KPI</th><th>{dateLabel(comparison.before.generated_at)}</th><th>{dateLabel(comparison.after.generated_at)}</th><th>Change</th></tr></thead><tbody>{Object.keys(labels).map((key) => <tr key={key}><th>{labels[key]}</th><td>{values(comparison.before)[key] ?? "—"}</td><td>{values(comparison.after)[key] ?? "—"}</td><td>{deltaLabel(comparison.deltas[key] as NumericDelta)}</td></tr>)}</tbody></table><p><strong>Keyword changes:</strong> +{(comparison.deltas.top_keywords as {added:string[]}).added.join(", ") || "none"}; removed {(comparison.deltas.top_keywords as {removed:string[]}).removed.join(", ") || "none"}</p></div>}
    </section></section>;
}
