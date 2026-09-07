import type { TechnicalAuditResponse } from "./api/contracts";

const labels: Record<string, string> = {
  crawl_error: "Crawl error", robots_invalid: "robots.txt", sitemap_invalid: "sitemap.xml",
  missing_title: "Missing title", title_length: "Page title", missing_meta_description: "Meta description",
  missing_h1: "Missing H1", multiple_h1: "Multiple H1 headings", heading_order: "Heading structure",
  missing_image_alt: "Image alt text", thin_content: "Thin content", duplicate_content: "Duplicate content",
  near_duplicate_content: "Near-duplicate content", pagespeed_unavailable: "PageSpeed unavailable",
  mobile_performance: "Mobile performance", largest_contentful_paint: "Largest Contentful Paint",
  cumulative_layout_shift: "Cumulative Layout Shift", interaction_to_next_paint: "Interaction to Next Paint",
};

export function TechnicalAuditView({ audit }: { audit: TechnicalAuditResponse }) {
  return <section className="mt-10" aria-labelledby="technical-audit-title">
    <p className="eyebrow">Technical SEO audit</p>
    <h2 id="technical-audit-title" className="mt-2 font-display text-3xl">Prioritized fix list</h2>
    <div className="rationale-box" data-testid="fix-first-summary"><h3 className="text-sm font-semibold">Here’s what I’d fix first and why</h3><p className="mt-2 leading-7 text-ink/75">{audit.summary}</p></div>
    {audit.findings.length ? <ol className="mt-5 grid gap-3">{audit.findings.map((finding) => <li className="technical-finding" key={finding.id}><div className="flex flex-wrap items-center gap-2"><span className={`badge severity-${finding.severity}`}>{finding.severity}</span><h3 className="font-semibold">{labels[finding.finding_type] ?? finding.finding_type.replaceAll("_", " ")}</h3></div><p className="mt-2 leading-6 text-ink/70">{finding.explanation}</p>{finding.affected_page_url && <p className="mt-2 break-all text-xs text-ink/50">Page: {finding.affected_page_url}</p>}{finding.related_page_url && <p className="mt-1 break-all text-xs text-ink/50">Related page: {finding.related_page_url}</p>}</li>)}</ol> : <p className="mt-5 text-ink/65">No technical findings were recorded for this analysis.</p>}
  </section>;
}
