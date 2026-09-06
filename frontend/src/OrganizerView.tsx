import type { OrganizerItemResponse, OrganizerStage } from "./api/contracts";

const stages: { value: OrganizerStage; label: string }[] = [
  { value: "backlog", label: "Backlog" },
  { value: "in_production", label: "In Production" },
  { value: "in_review", label: "In Review" },
  { value: "published", label: "Published" },
];

function StageSelect({ item, onStageChange }: { item: OrganizerItemResponse; onStageChange: (item: OrganizerItemResponse, stage: OrganizerStage) => void }) {
  return <label className="stage-control">Stage<span className="sr-only"> for {item.title}</span><select aria-label={`Stage for ${item.title}`} value={item.stage} onChange={(event) => onStageChange(item, event.target.value as OrganizerStage)}>{stages.map((stage) => <option key={stage.value} value={stage.value}>{stage.label}</option>)}</select></label>;
}

function TaskCard({ item, onStageChange }: { item: OrganizerItemResponse; onStageChange: (item: OrganizerItemResponse, stage: OrganizerStage) => void }) {
  return <article className="organizer-card" data-testid={`organizer-item-${item.id}`}><p className="eyebrow">{item.item_type === "seo_content" ? "SEO/content" : item.item_type.toUpperCase()}</p><h3 className="mt-2 font-display text-xl">{item.title}</h3><StageSelect item={item} onStageChange={onStageChange} /></article>;
}

export function OrganizerView({ items, loading, error, onStageChange }: { items: OrganizerItemResponse[]; loading: boolean; error: string | null; onStageChange: (item: OrganizerItemResponse, stage: OrganizerStage) => void }) {
  if (loading) return <section className="empty-state" role="status">Loading your Organizer…</section>;
  if (error) return <section className="error-box" role="alert">{error}</section>;
  const aeoItems = items.filter((item) => item.item_type === "aeo");
  const seoItems = items.filter((item) => item.item_type !== "aeo");
  return <div className="mt-7 space-y-10">
    <section aria-labelledby="aeo-checklist-title"><h2 id="aeo-checklist-title" className="font-display text-2xl">AEO checklist</h2><div className="mt-4 grid gap-3">{aeoItems.length ? aeoItems.map((item) => <label className="checklist-task" key={item.id}><input type="checkbox" checked={item.stage === "published"} onChange={(event) => onStageChange(item, event.target.checked ? "published" : "backlog")} /><span>{item.title}</span><StageSelect item={item} onStageChange={onStageChange} /></label>) : <p className="text-ink/60">Accept an AEO recommendation to add it here.</p>}</div></section>
    <section aria-labelledby="seo-board-title"><h2 id="seo-board-title" className="font-display text-2xl">Combined SEO task view</h2><p className="mt-2 text-ink/60">SEO/content and paid-search tasks share one execution board.</p><div className="kanban-board mt-5">{stages.map((stage) => <section className="kanban-column" aria-label={stage.label} key={stage.value}><div className="flex items-center justify-between"><h3 className="font-semibold">{stage.label}</h3><span className="badge stage-badge">{seoItems.filter((item) => item.stage === stage.value).length}</span></div><div className="mt-4 grid gap-3">{seoItems.filter((item) => item.stage === stage.value).map((item) => <TaskCard key={item.id} item={item} onStageChange={onStageChange} />)}</div></section>)}</div></section>
  </div>;
}
