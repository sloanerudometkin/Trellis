# Proposed Spec Addition: Reporting & Analytics Feature

*Drafted for review against `_Trellis_Updated_specification_document_v2-1.md` (v2.1, Sep 1, 2026). Nothing in the actual spec has been changed yet — this is the proposal, in the same format as `trellis_sem_proposal.md`. Once you sign off, I'll fold the approved parts into the real spec doc, the data model doc, and the decision log.*

---

## 0. Quick concepts, since this is new territory

A few terms this feature introduces, in plain language, before the requirements use them:

- **KPI (Key Performance Indicator)** — a metric someone has decided actually matters for judging whether things are going well, as opposed to a metric that's just easy to measure. Part of what you're asking for is Trellis picking these *for* the user, so a beginner marketer never has to guess which numbers are the important ones.
- **Snapshot** — a saved copy of a value at a point in time, frozen even if the thing it measures keeps changing later. Trellis already does this for Health Score (`AnalysisRun.health_score`, DR-1) — this proposal does the same thing for a whole report, so a report from January still reads exactly as it did in January even if, say, the Health Score formula gets tuned in March.
- **GA4 (Google Analytics 4)** — Google's current free web-analytics product; it's the thing that tells a site owner how many people visited, where they came from, and (if set up) whether they converted (bought something, filled out a form, etc.). This is the "Google Analytics" your old job's spreadsheet was pulling from.
- **Google Analytics Data API** — the free, official API that lets software (like Trellis) read a user's own GA4 numbers programmatically, instead of a person logging into GA4 and copying numbers into a spreadsheet by hand. Same shape as the Search Console and Google Ads APIs already in the spec: the user connects their own account via OAuth (a "sign in with Google and approve access" flow), no cost, no credit card.
- **Attribution** — figuring out *which* channel (organic search, paid search, direct visit, etc.) gets credit for a visit or a sale. Your screenshot's "SEM Attributed" vs "GA4 Total Sales" columns are attribution: how much of total sales did paid search specifically drive.
- **ROI (Return on Investment)** — value gotten back ÷ money spent. Your screenshot's "Monthly ROI" column.
- **MoM (Month-over-Month)** — comparing this month's numbers to last month's, the most common way marketers show whether something is trending up or down.

---

## 1. Why this is currently missing, and the two-phase shape I'm proposing

Right now, the spec computes plenty of the *ingredients* of a report — Health Score (FR-11), AEO/SEO/SEM suggestion status, technical audit findings, Organizer pipeline stage — but nothing ever bundles them into something a user can name, save, revisit, and compare. That's exactly the gap you described: today, "seeing progress over time" only exists as the Health Score trend line (FR-1.2/FR-11.3), and there's no equivalent of the monthly-spreadsheet report your old job relied on.

There's a real fork in the road here, the same one FR-14/FR-15 already hit with SEM Cost Tier vs. real Google Ads numbers:

**Layer 1 — reporting built entirely from data Trellis already has.** Every AnalysisRun already produces a Health Score, suggestion counts, AEO completion, technical findings, and (once accepted) SEM keyword/ad-group data. Turning that into a saved, comparable report is pure aggregation of existing data — no new external account, no new OAuth, no new cost or schedule risk. This is genuinely buildable in the MVP, which is what you asked for.

**Layer 2 — real analytics numbers**, the kind your screenshot shows: actual site traffic, actual ad spend, actual sales, real ROI. Trellis doesn't currently talk to GA4 or pull real ad spend at all (FR-15's Google Ads connection gets CPC/search-volume estimates, not actual spend or sales). Getting the *real* version of your example report requires a new integration — the Google Analytics Data API — and it's per-user OAuth, exactly like Search Console (FR-8) and Google Ads (FR-15). Both of those were pushed to Phase 2 for onboarding-friction and schedule reasons, not cost.

**What I'm proposing:**
- **FR-16 (MVP):** Trellis automatically generates and saves a Report every time an analysis runs, built from predefined KPIs Trellis already computes, with month-over-month and last-analysis-vs-current comparison built in. This is the part of "analytics" that can genuinely ship in the MVP, and it's what makes "no more spreadsheets" true for the organic + heuristic-SEM side of the plan.
- **FR-17 (Phase 2):** Once the user optionally connects GA4 (and, if also connected, real Google Ads spend from FR-15), the Report is enriched with real traffic, conversions, revenue, and true ROI — closing the gap to your old-job example exactly.

This means Trellis really does stop being "insight only" and start replacing the spreadsheet, in the MVP, for everything it already knows — and the report only grows more powerful as GA4/Ads get connected, rather than the whole reporting feature waiting on those integrations to exist at all.

*If you'd rather pull GA4 into the MVP anyway (it's still $0, just adds an OAuth flow and per-user setup dependency to the Phase 1 timeline, same trade-off FR-7/FR-8/FR-15 already made the other way), say so in the open questions at the end and I'll rewrite this as one FR instead of two.*

---

## 2. Proposed changes to Section 1 (Introduction)

**1.3 Product Scope — add to "In scope":**
> - Automatic, saved Reports generated from every analysis run, built from a predefined set of organic and paid KPIs so the user never has to decide which metrics matter — plus month-over-month and last-analysis-vs-current comparison, so the user never has to rebuild this in a spreadsheet. (See FR-16; Phase 2 optionally enriches reports with real Google Analytics 4 traffic/conversion data via FR-17.)

**1.4 Definitions, Acronyms, and Abbreviations — add:**
> - **KPI** — Key Performance Indicator; a metric selected as meaningful for judging progress, as opposed to any metric that happens to be easy to measure.
> - **Report** — a saved, timestamped snapshot of a website's predefined KPIs at the time of one analysis run, kept so it reads the same later even if scoring formulas change (FR-16).
> - **GA4** — Google Analytics 4; Google's free web-analytics product, the data source for real traffic/conversion numbers in FR-17.
> - **Google Analytics Data API** — Google's free API for programmatically reading a user's own GA4 data; the data source for FR-17.
> - **ROI** — Return on Investment; value returned divided by amount spent, surfaced once real spend (FR-15) and real attributed revenue (FR-17) are both connected.

---

## 3. Proposed changes to Section 2 (Overall Description)

**2.2 Product Functions (Summary) — add:**
> 7. Automatically generates a saved Report after every analysis, built from a predefined KPI set spanning organic and paid performance, and lets the user compare any two reports (e.g., this month vs. last month, or last analysis vs. current) — so tracking progress over time never requires a separate spreadsheet or a trip to Google Analytics.

**2.3.3 End-user objectives — add:**
> see performance summarized the same way every time, without having to decide which numbers matter or rebuild a monthly report by hand in a spreadsheet; compare this period to last period at a glance.

**2.7 Competitive Landscape — add a closing line:**
> Reporting is the other place this landscape asks a solo/nonprofit marketer to leave the tool: even AEO-native and SEO-incumbent platforms typically export data for the user to report on elsewhere, or gate a real reporting layer behind a higher tier. A predefined-KPI report generated automatically from the same $0 workspace — with no separate reporting product, and no need to touch Excel or Google Analytics directly for the data Trellis already has — extends this product's "strategy + execution workspace, not an insights dashboard" positioning (2.1) one step further: through to reporting, not just planning.

---

## 4. New requirement: FR-16 — Analysis Reports & KPI Comparison (MVP)

*Turns data Trellis already computes into a saved, comparable Report — no new external dependency, no new account connection, buildable entirely within the existing MVP scope.*

- **FR-16.1** The system shall automatically generate one Report immediately after each AnalysisRun completes (FR-5.2), without requiring any user action.
- **FR-16.2** Each Report shall be built from a **predefined KPI set** (not user-configurable in MVP, so a marketer never has to decide which metrics matter) spanning:
  - *Organic:* Health Score and its change since the prior report (FR-11); AEO checklist completion % and its change (FR-2); technical audit findings resolved vs. still open (FR-6); count of content items reaching Published this period (FR-4); top keyword/content-gap candidates by trend score (FR-3.1).
  - *Paid (heuristic, MVP):* count of SEM suggestions accepted; breakdown of accepted keywords by Cost Tier (Low/Medium/High, FR-14.1); number of starter ad groups defined (FR-14.5).
  - *Pipeline:* Organizer cards by stage, and cards that moved to Published this period (FR-4).
- **FR-16.3** Each Report shall store its KPI values as a **snapshot** at generation time, so a saved report's numbers remain fixed even if the underlying scoring logic (e.g., the Health Score formula, FR-11) is later changed — the same principle already applied to `AnalysisRun.health_score` (DR-1).
- **FR-16.4** The system shall provide a Report History view per website, listing every past Report by date, from which any report can be reopened in full.
- **FR-16.5** The system shall let the user select any two Reports for the same website and view them side by side with a computed delta (absolute and %, where applicable) for every KPI in FR-16.2 — supporting both the common cases (most recent vs. previous report, i.e. "since last scan"; and same-period-last-month) and an arbitrary pair the user picks.
- **FR-16.6** Each Report shall lead with a short plain-language summary of what changed, in the same "here's what matters first" pattern already used for the technical audit (FR-5.6) and the since-last-scan delta (FR-1.2) — e.g., "Health Score up 7 points, 3 tasks published, 2 new keyword opportunities."
- **FR-16.7** The system shall NOT require the user to leave Trellis (e.g., to Excel or Google Analytics) to view, save, or compare any KPI covered by FR-16.2 — that data lives, is computed, and is retained entirely inside Trellis.

*Rationale:* every KPI here is already produced somewhere else in the spec (FR-2 through FR-6, FR-11, FR-14); FR-16 is a persistence and presentation layer on top of existing computation, not new analysis logic — so it carries none of the schedule/onboarding risk that a new external integration would.

---

## 5. New requirement: FR-17 — Real Analytics Enrichment via Google Analytics 4 (Phase 2)

*Upgrades FR-16's Reports with real traffic, conversion, and revenue data once the user opts in — same $0-but-per-user-OAuth shape as FR-7, FR-8, and FR-15.*

- **FR-17.1** The system shall let the user connect their own GA4 property via OAuth. Creating and using GA4 is free and requires no credit card.
- **FR-17.2** Once connected, the system shall call the free Google Analytics Data API to retrieve, per reporting period: sessions, new vs. returning users, and (where the user has configured GA4 conversions/goals) conversion count and any tracked revenue.
- **FR-17.3** Where the site also has real ad spend data (FR-15, Google Ads connected), the system shall compute and display a real ROI figure (GA4-attributed conversions or revenue ÷ actual ad spend) alongside the existing heuristic Cost Tier view, clearly distinguishing "estimate" fields from "real" fields at all times (extending the FR-14.9 disclosure pattern).
- **FR-17.4** The system shall add real GA4 metrics as additional KPI rows in the FR-16 Report and its comparison view, rather than a separate report — so a user with GA4 connected sees one enriched report, not two.
- **FR-17.5** The system shall clearly label any KPI in FR-17.2/17.3 as sourced from the user's own GA4 account, and shall never modify or write to the user's GA4 property — read-only, exactly as FR-8 reads Search Console without writing to it.
- **Dependency note:** unlike FR-15's Google Ads API, the Google Analytics Data API does not require a separate developer-side app review — only the per-user OAuth connection (FR-17.1) — so FR-17 has less setup risk than FR-15, though it still depends on the user already having GA4 installed on their site, which Trellis cannot do for them.

*Optional Phase-2 extension worth flagging now:* FR-8 (Search Console, Phase 2) already reads the user's Search Console data for backlinks; Search Console also has a free Performance report (clicks, impressions, average position, click-through rate) that isn't currently used anywhere in the spec. Pulling that into the same Report would round out FR-17 with real organic-search performance, not just paid — I'd suggest folding this in as FR-17.6 if you want organic analytics to reach the same "real data" bar as paid. Flagging it rather than assuming, since it's scope you didn't ask for explicitly.

---

## 6. Data model changes

**New entity: `Report` (MVP)** — one-to-one with `AnalysisRun`, snapshotting the KPIs in FR-16.2 at generation time.

| Field | Type | Notes |
|---|---|---|
| `id` | PK | |
| `website_id` | FK → Website | |
| `analysis_run_id` | FK → AnalysisRun, unique | one Report per AnalysisRun (FR-16.1) |
| `generated_at` | timestamp | |
| `health_score`, `health_score_delta` | int | snapshot + change since prior Report (FR-16.2, FR-16.3) |
| `aeo_completion_pct`, `aeo_completion_delta` | decimal | " |
| `technical_findings_resolved`, `technical_findings_open` | int | " |
| `content_published_count` | int | this period (FR-4) |
| `top_keywords` | text[] or JSON | top trend-score candidates this period (FR-3.1) |
| `sem_accepted_count` | int | " |
| `sem_cost_tier_breakdown` | JSON (`{low, medium, high}` counts) | " |
| `ad_groups_defined_count` | int | " |
| `organizer_stage_counts` | JSON | cards per stage at time of report |
| `summary_text` | text | plain-language lead-in (FR-16.6) |
| `ga4_sessions`, `ga4_new_users`, `ga4_returning_users`, `ga4_conversions`, `ga4_revenue` | nullable | populated once FR-17 is connected |
| `real_ad_spend`, `real_roi_pct` | decimal, nullable | populated once FR-15 + FR-17 are both connected (FR-17.3) |

**New field on `Website`:** `ga4_connected` (boolean) — mirrors the existing `gbp_connected` / `search_console_connected` / (proposed) `google_ads_connected` pattern; gates FR-17.

**Comparison (FR-16.5)** is proposed as a computed operation over two `Report` rows (pick any two, diff every field) rather than a new stored entity — nothing about "a comparison" needs to be persisted on its own; it's always derivable from two existing Reports.

---

## 7. UI / navigation changes

**FR-1.3** — add a sixth workspace tab: **Overview, AEO, SEO/Content, SEM, Reports, Organizer.**

**4.1 User Interfaces — add:**
> **Reports section:** a list of past Reports (newest first) with the FR-16.6 one-line summary shown per row; opening one shows the full KPI breakdown grouped Organic / Paid / Pipeline, matching the section layout used elsewhere. A "Compare" control lets the user pick any two reports (defaulting to "most recent vs. previous") and see every KPI side by side with its delta, using the same up/down indicator style as the Health Score trend (FR-11.3). Once FR-17 is connected, a GA4 row group appears with real traffic/conversion figures, and a real-ROI figure replaces the heuristic Cost Tier summary wherever both FR-15 and FR-17 are connected — with "estimate" vs. "real" labeled per FR-14.9/FR-17.5's disclosure pattern throughout.

Sample microcopy, in the Identity Guide's Direct / Plain / Unhurried voice (matching the tone already used for FR-14's SEM microcopy in the SEM proposal):
> - "Since your last scan: Health Score up 7, 3 tasks published, 2 new keyword ideas."
> - "This report is a snapshot — even if we improve how we score things later, this number stays what it was in January."
> - "Connect Google Analytics to see real visits and conversions here instead of estimates."

---

## 8. External interfaces (4.3) — new row

| Interface | Direction | Purpose | Auth | Notes |
|---|---|---|---|---|
| Google Analytics Data API (GA4) | Outbound | Real sessions, users, conversions, revenue for Report enrichment (FR-17.2) | Per-user OAuth | Free tier; generous free quota; no developer-side app review required (unlike Google Ads API) |

---

## 9. Schedule impact (5.2)

- **Phase 1 (MVP):** add a **"Reports & KPI comparison"** milestone (~1.5–2 weeks) — Report generation on every AnalysisRun, Report History view, Compare view, predefined-KPI aggregation logic. Same honest framing as the SEM addition: this is new scope on top of the current ~18-week MVP estimate, so either the timeline extends by ~1.5–2 weeks, or FR-16 trades priority against something else already in Phase 1 — worth deciding explicitly.
- **Phase 2 (Grow):** add FR-17 (GA4 integration) to the existing Phase 2 description, alongside FR-7, FR-8, FR-10, FR-15 — natural to build right after FR-15 (Google Ads), since FR-17.3's real ROI figure depends on both being connected.

---

## 10. Risks (5.3) — additions

- **Predefined-KPI set is a product judgment call, not a technical one** — same category of open question already flagged for Health Score weighting (FR-11) and SEM Cost Tier (FR-14); should be sanity-checked with a real marketer before being treated as the definitive "what matters" list.
- **GA4 connection requires the user to already have GA4 installed on their site** — Trellis can't do this step for them; same onboarding-friction category as Search Console verification and GBP listing ownership, already logged in 5.3.
- **Report snapshot immutability vs. scoring changes** — once Health Score's weighting formula (still unvalidated per FR-11) is tuned, old Reports and the live Health Score will intentionally disagree on "what a 68 meant" for older data; this needs a one-line disclosure in the UI so it doesn't read as a bug.

---

## 11. Proposed decision log entry (Appendix A)

> **[date] (Reporting & Analytics feature proposal):** added automatic, saved Reports as a new MVP feature (FR-16) — every AnalysisRun generates a Report snapshotting a predefined KPI set (Health Score, AEO completion, technical findings, content published, SEM acceptance/cost-tier mix, Organizer pipeline counts), with a Report History view and a Compare view (any two reports, full KPI deltas), built entirely from data the spec already computes at $0. Real Google Analytics 4 traffic/conversion/revenue data, plus a real-ROI figure once combined with FR-15's real ad spend, proposed as a Phase 2 upgrade (FR-17) via per-user GA4 OAuth, mirroring the FR-7/FR-8/FR-15 pattern. Added new `Report` entity (one-to-one with `AnalysisRun`) and `Website.ga4_connected`; added a sixth Reports workspace tab (FR-1.3).

---

## 12. Open questions for you

1. **Does the FR-16 (MVP, existing data) / FR-17 (Phase 2, real GA4 data) split work,** or do you want GA4 pulled into the MVP anyway since it's still $0 — just with an added OAuth flow and a dependency on the user already having GA4 set up?
2. **Should the Search Console Performance report (clicks/impressions/position/CTR) get folded into FR-17 as real organic-search analytics** (I sketched this as an optional FR-17.6), so both the organic and paid sides of the report reach "real data" in Phase 2 together — or should that wait for a later pass?
3. **Is the predefined KPI list in FR-16.2 the right one to lock in for MVP,** or are there specific numbers from your old reporting process (beyond what's already covered) you'd want guaranteed a place in every report from day one?
4. **Report export** — your old workflow lived partly in Excel; is an in-app Report History + Compare view enough for MVP, or do you want a CSV/PDF export of a Report as part of this same feature rather than a later add-on? (Print-to-PDF from the browser is $0 either way; a dedicated CSV export is a small additional build, not a cost question.)

Once you weigh in, I'll write the approved version into `_Trellis_Updated_specification_document_v2-1.md` and `claude/Trellis_Data_Model.md` directly and update the decision log — same as the SEM feature did.
