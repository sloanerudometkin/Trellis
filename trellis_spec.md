**TRELLIS: AN SEO / AEO / SEM GROWTH STRATEGY PLATFORM**

Software Requirements Specification (v2.9 — September 4, 2026)

**Primary positioning:** Your paid and organic search growth strategy—all in one place.

**Plain-language definition:** Trellis is a website analysis and action-planning app for solo marketers and small teams that brings paid and organic search together: it analyzes a site for SEO, AEO, and SEM opportunities, turns the findings into one prioritized plan, tracks the work through completion, and measures progress across repeat analyses.

**Technical definition:** Trellis is an agentic-AI web application that helps digital marketing managers plan, prioritize, and organize a full organic-and-paid search growth strategy — SEO, Answer Engine Optimization (AEO), and SEM (paid search) — by packaging consultancy-style guidance into a repeatable workspace built entirely on free tiers and open-source software.

**Problem:** Digital marketers are often responsible for a complete SEO, AEO, and SEM strategy without a specialist team or the budget for ongoing consultancy support. Consultants and audit tools may provide useful recommendations, but execution, task tracking, and reporting are still left to the marketer across disconnected tools and spreadsheets.

**Product promise:** Trellis closes the gap between insight and execution by helping resource-limited marketers analyze their website, prioritize connected organic and paid opportunities, carry the right work through completion, and measure progress in one workspace.

**How it works:** The user submits a URL to create a website workspace, then can analyze and rescan the site whenever needed. Every run produces prioritized, consultancy-style SEO, AEO, content, technical, and SEM recommendations. The user accepts or dismisses each recommendation, turns accepted recommendations into tasks, tracks them through one Organizer (Kanban board), and receives an automatic Report that builds the website's progress history. The organic Health Score shows SEO/AEO momentum, while SEM remains visible through its own separate summary.

**Built to cost $0:** every component — frontend, backend, database, LLM, and hosting — runs on free tiers or open-source software, no credit card required anywhere in the stack (see Section 5 for the budget breakdown and Section 2.6 for free-tier limits). This describes the MVP's build-and-demo infrastructure, not a permanent customer-pricing guarantee at every future usage level.

**Product mottoes (guiding the functionality below):**
- *"The AEO/SEO/SEM consultant you can't afford, minus the invoice."*
- *"Your full organic-and-paid search growth strategy — from insight to execution."*
- *"Analyze whenever you need to. Every run strengthens one evolving strategy, plan, Organizer, and reporting history."*
- *"No more spreadsheets. One workspace, start to published."*

---

## 1. Introduction

### 1.1 Purpose
This document specifies the requirements for the Trellis SEO/AEO/SEM Growth Strategy Platform, a three-tier web application for Digital Marketing Managers — especially at small businesses and nonprofits — to plan, prioritize, and track a full organic (SEO/AEO) and paid (SEM) growth strategy. It is written to give Sloane (the sole developer), and any future contributor, reviewer, or evaluator (instructor, hiring manager, or investor), a single, unambiguous reference for what the system does, what it does not do, how it's built, and when each piece is expected to ship.

**North star:** Trellis makes a coordinated paid-and-organic search growth strategy accessible to marketers who lack specialist time, budget, or tools. It lets them analyze whenever needed, use every run to strengthen one evolving strategy, and keep planning, prioritization, execution, and measurement connected—without overstating its MVP estimates as live campaign or revenue data.

### 1.2 Intended Audience
- **Sloane (developer/product owner):** primary reference for scope, priority, and acceptance criteria while building.
- **Instructors / technical reviewers:** evidence of requirements discipline and system design for a capstone or portfolio review.
- **Prospective employers:** demonstration of end-to-end product thinking (problem framing → requirements → architecture → delivery plan).
- **Prospective investors / early users:** a clear, non-technical picture of scope and timeline sits in Sections 1–2 and 5; Sections 3–4 are the technical detail beneath it.

### 1.3 Product Scope

**In scope (this document covers):**
- A single-user (MVP) web app that can save multiple website workspaces but analyzes one website at a time. "Single-user" means the MVP has no shared teams, roles, or collaborative accounts. Within each website workspace, the user manages a full AEO/SEO/SEM growth strategy through to publication — organic (AEO/SEO) and paid (SEM) are both core, not an add-on to an SEO-only tool.
- An AI agent subsystem that scrapes a submitted URL and returns structured, prioritized, rationale-backed recommendations across organic and paid channels alike.
- A cost-conscious SEM (paid search) strategy layer: keyword and ad-group suggestions, placement/targeting guidance, and a Cost Tier estimate per keyword, generated from the same site analysis used for SEO/AEO — with an optional (Phase 2) upgrade to real Google Ads Keyword Planner data via the user's own free Google Ads account.
- A trackable Organizer (kanban) that carries every recommendation — AEO, SEO/content, and SEM alike — from suggestion to published/live.
- Automatic, saved Reports generated from every analysis run, built from a predefined set of organic and paid KPIs so the user never has to decide which metrics matter — plus month-over-month and last-analysis comparison, so the user never has to rebuild this in a spreadsheet. (See FR-9; Phase 2 optionally enriches reports with real Google Analytics 4 traffic/conversion data via FR-15.)
- Consultancy-style deliverables reworked to run at $0: technical SEO audit, local SEO/Google Business Profile checklist, backlink visibility (via Search Console), competitor benchmarking, and a manual-assisted AI-citation checklist.
- A single Health Score (0–100) summarizing a website's overall organic SEO/AEO progress and its trend over time (see FR-7 for why SEM is tracked as its own summary rather than blended into this score).

**Explicitly out of scope (for the phases defined here):**
- Fully automated, continuous polling of ChatGPT/Perplexity/other AI engines for citation tracking — no free or ToS-compliant way to do this at volume exists (see 2.7 Assumptions and Dependencies, and 5.3 Risks). A manual-assisted substitute is in scope instead (FR-12).
- A comprehensive third-party backlink index (Ahrefs/Moz/SEMrush-style) — backlink visibility is scoped to what Google Search Console already reports (FR-11).
- Paid crawler/audit tools, paid LLM tiers, paid hosting, or any component that requires a credit card, for as long as this remains a $0-to-build project (see 5.1 Budget).
- Native mobile apps; this is a responsive web application only.
- Multi-language / non-English content analysis (English-language websites only, all phases covered here).
- Creating, launching, or managing live ad campaigns, or moving/spending the user's money in any way — Trellis's SEM feature (FR-8/FR-14) produces a paid-search strategy the user manually implements in their own Google Ads account; it is not a bidding or campaign-management tool.

### 1.4 Definitions, Acronyms, and Abbreviations
- **SEO** — Search Engine Optimization; improving a site's visibility in traditional search engine results.
- **AEO** — Answer Engine Optimization; improving how a site is surfaced and cited by AI answer engines (ChatGPT, Perplexity, Google AI Overviews).
- **SEM** — Search Engine Marketing; paid placement in search results, priced per click (PPC), as distinct from the unpaid ("organic") SEO/AEO placement this product otherwise focuses on.
- **PPC** — Pay-Per-Click; the pricing model where an advertiser is charged only when their ad is clicked.
- **CPC** — Cost Per Click; what one ad click costs, set by keyword competitiveness and Quality Score.
- **Quality Score** — Google's 1–10 relevance rating (keyword ↔ ad ↔ landing page) that directly sets CPC.
- **Keyword Planner** — Google's free keyword research tool; its API (Google Ads API, Basic Access tier) is the data source for FR-14's real search-volume/CPC figures.
- **TF-IDF** — Term Frequency–Inverse Document Frequency; a statistical scoring method that weighs a word higher when it's frequent *within* one document but rare *across* a comparison set of other documents. Requires multiple documents to compute (unlike YAKE/RAKE, which score a single document alone); used in this product only where a natural multi-document comparison already exists — across a site's own pages (FR-3.5, FR-6.7) and across a site vs. its competitors (FR-16.3) — not for single-page keyword ranking.
- **Long-tail keyword** — a longer, more specific search phrase; generally lower CPC and lower competition than a short "head" term.
- **Negative keyword** — a term explicitly excluded from triggering an ad, to avoid paying for irrelevant clicks.
- **SERP** — Search Engine Results Page.
- **Schema markup** — structured data (schema.org vocabulary) embedded in a page's HTML to help search/answer engines understand its content.
- **GBP** — Google Business Profile (formerly Google My Business); the free local-business listing product.
- **NAP** — Name, Address, Phone number; consistency of these across the web is a local-SEO ranking signal.
- **RAG** — Retrieval-Augmented Generation; retrieving relevant reference text to ground an LLM's output.
- **Kanban** — a visual workflow board with columns representing stages of work (e.g., Backlog → In Production → In Review → Published).
- **Health Score** — this product's single 0–100 composite metric summarizing a website's overall organic SEO/AEO progress (FR-7); SEM has its own separate summary rather than being blended into this score.
- **KPI** — Key Performance Indicator; a metric selected as meaningful for judging progress, as opposed to any metric that happens to be easy to measure.
- **Report** — a saved, timestamped snapshot of a website's predefined KPIs at the time of one analysis run, kept so it reads the same later even if scoring formulas change (FR-9).
- **GA4** — Google Analytics 4; Google's free web-analytics product, the data source for real traffic/conversion numbers in FR-15.
- **Google Analytics Data API** — Google's free API for programmatically reading a user's own GA4 data; the data source for FR-15.
- **ROI** — Return on Investment; value returned divided by amount spent, surfaced once real spend (FR-14) and real attributed revenue (FR-15) are both connected.
- **LLM** — Large Language Model; here, Groq's hosted Llama 3.3 70B (primary) or Google Gemini free tier (backup).
- **MVP** — Minimum Viable Product; Phase 1 of this spec.

### 1.5 References
- `SEO_AEO_Platform_Spec.docx` — full formatted version with architecture diagram, ER diagram, sequence flow, and navigation map.
- `SEO_AEO_Platform_OnePager.pdf` — investor/employer-facing summary derived from this spec.
- Google PageSpeed Insights API documentation (technical audit, FR-6).
- Google Business Profile API documentation (local SEO, FR-10).
- Google Search Console API documentation (backlink visibility, FR-11).
- Groq API documentation and Google Gemini API documentation (LLM provider, FR-5).
- Google Ads API documentation, Keyword Planning overview and Access Levels reference (SEM keyword/CPC data, FR-14).
- Google Analytics Data API documentation (real analytics enrichment, FR-15).

---

## 2. Overall Description

### 2.1 Product Perspective
This is a new, standalone product — not an extension of an existing system. It is a three-tier web application (presentation / API+agent / data, detailed in 2.5) built entirely from free-tier and open-source components so it can be built and demonstrated at $0.

Most competing AEO tools (see 2.8) stop at insight: a citation score, a dashboard, a report. This product's differentiation is that it is a **strategy + execution workspace** — every recommendation follows a visible path from **audit → suggestion → task → published** and stays a living, trackable initiative rather than a one-time report. Combined with serving a persona (solo/nonprofit marketers, no team, no budget) that established competitors price above, this is the defensible edge — not the SEO+AEO combination itself, which is now table stakes in this market.

Trellis is deliberately a **paid-and-organic search growth product**, not an organic tool with an SEM feature attached. Organic strategy (AEO/SEO) and paid strategy (SEM) begin with the same website analysis and remain connected through one coordinated strategy, one prioritized plan, one Organizer, and one reporting system. They share a workflow without being misleadingly blended into one metric: the organic Health Score and the separate SEM summary preserve the different evidence each discipline requires.

**Defining product loop:** **Analyze → Recommend → Prioritize → Complete the work → Rescan → Measure progress.** Trellis's core promise depends on the whole loop: analysis produces guidance, accepted guidance becomes manageable work, and later scans and Reports show what changed.

**Promise and boundaries:**

| Trellis promises | Trellis does not promise |
|---|---|
| Consultancy-style guidance structured for a resource-limited marketer | Guaranteed equivalence to a human consultancy |
| Prioritized recommendations based on the submitted website | Guaranteed rankings, traffic, AI citations, or revenue |
| A workflow from recommendation through publication | Automatic implementation of changes on the user's website |
| Paid-search planning and clearly labeled cost guidance | Campaign creation, bidding, purchasing, or spending |
| Consistent progress reporting from data Trellis has computed | Real traffic, conversion, or ROI data in the MVP |
| Guided AEO improvements and, in Phase 2, manual citation checks | Continuous automated monitoring of AI answer engines |
| A $0-to-build MVP technology stack | Permanent free commercial operation at every usage level |

### 2.2 Product Functions (Summary)
At a high level, the system helps the user achieve four connected outcomes across paid and organic search:

1. **Understand where growth may come from.** The user adds a website and can run or rerun an analysis whenever needed. Each run examines the site's current content and technical condition, then returns connected, rationale-backed opportunities across AEO, SEO/content, technical health, and paid-search planning.
2. **Choose one practical strategy.** Trellis prioritizes organic and paid opportunities in one plan. The user sees why each recommendation matters, compares likely impact and clearly labeled SEM Cost Tiers, and accepts or dismisses each recommendation.
3. **Complete the work in one workflow.** Accepted organic and paid recommendations become Organizer tasks that move through a visible pipeline to Published or Live, keeping strategy and execution together instead of scattered across specialist tools and spreadsheets.
4. **Demonstrate progress in one reporting system.** Trellis tracks the organic Health Score and separate SEM summary, highlights what changed since the previous scan, automatically saves a Report after every analysis, and lets the user compare any two Reports. Real traffic, conversion, spend, revenue, and ROI require the Phase 2 integrations.

Later phases extend these outcomes with local visibility, backlinks Google already sees, guided AI-citation checks, real Google Ads keyword/CPC data, GA4 reporting enrichment, progress digests, and competitor benchmarking.

Full detail and acceptance-level requirements for each function are in Section 3.

### 2.3 User Classes and Characteristics

**2.3.1 Primary persona — "Priya."** Marketing Manager at a 12-person nonprofit. Owns marketing end-to-end — organic and paid alike; has no dedicated SEO/AEO/SEM specialist or specialist-tool budget; currently tracks content in scattered spreadsheets; is newly aware that AI answer engines are becoming a traffic source; and is unsure whether or where paid search would be worth the spend. Technical comfort: low-to-moderate — needs plain-language rationale, not raw data.

**2.3.2 Secondary persona — small agency account manager.** Manages multiple client sites; needs a consistent, repeatable audit-and-plan workflow she can run the same way across every client. Technical comfort: moderate; values consistency and speed over depth of customization.

**2.3.3 End-user objectives:**
- Know what to fix or create and why it matters.
- Receive an actionable starting plan from a URL in under five minutes.
- Decide which organic recommendations to pursue and which paid-search opportunities may fit the user's goals and budget.
- Keep strategy, decisions, and active work in one place per website.
- Track accepted AEO, SEO/content, and SEM work through completion.
- Revisit a website, discover what is new, and see progress since the prior scan.
- Review the same meaningful KPIs every time and compare periods without rebuilding a spreadsheet.

### 2.4 Core User Use Cases

The use cases below connect the product promise to the detailed, testable requirements in Section 3. They describe intended user outcomes; the referenced functional requirements remain authoritative for acceptance criteria and phase scope.

#### UC-1 — Create the first website action plan
- **User need:** "I know my website needs improvement, but I do not know what to do first."
- **Trigger:** The user submits a website URL and optional business context.
- **Trellis response:** Analyze the site and generate prioritized, site-specific SEO, AEO, technical, content, and SEM recommendations with plain-language rationales.
- **Visible outcome:** The user receives an actionable starting plan in under five minutes.
- **Related requirements:** FR-1, FR-3, FR-5, FR-6, FR-8, NFR-5.

#### UC-2 — Turn recommendations into a focused plan
- **User need:** "I have recommendations, but I need help deciding which ones to pursue."
- **Trigger:** The user reviews a recommendation.
- **Trellis response:** Explain why the recommendation matters and let the user accept or dismiss it.
- **Visible outcome:** Accepted recommendations enter the active plan; dismissed recommendations leave it and retain a simple reason for future quality improvement.
- **Related requirements:** FR-2, FR-3, FR-8, DR-3, DR-4.

#### UC-3 — Manage work through completion
- **User need:** "I need one place to manage my SEO, AEO, content, and SEM work."
- **Trigger:** The user accepts a recommendation.
- **Trellis response:** Create a corresponding Organizer task and keep its stage synchronized with the originating recommendation.
- **Visible outcome:** The user moves work from Backlog through Published without maintaining a separate spreadsheet.
- **Related requirements:** FR-2, FR-3, FR-4, FR-8.

#### UC-4 — Decide whether paid search is worth considering
- **User need:** "I do not understand Google Ads or know which keywords might fit my budget."
- **Trigger:** Trellis completes a website analysis.
- **Trellis response:** Generate starter ad groups, relative Cost Tiers, targeting guidance, negative keywords, landing-page matches, and lower-cost alternatives.
- **Visible outcome:** The user receives a clearly labeled planning aid to implement manually in Google Ads if they choose.
- **Boundary:** Trellis does not launch campaigns, guarantee bid prices, or spend money. Real search volume and CPC data require the Phase 2 Google Ads connection.
- **Related requirements:** FR-8; upgraded by FR-14 and FR-15.

#### UC-5 — Measure improvement over time
- **User need:** "I need to know whether the work is moving in the right direction."
- **Trigger:** The user rescans the website or opens Reports.
- **Trellis response:** Save a new KPI snapshot, update the organic Health Score trend, summarize what changed, and compare the new Report with an earlier one.
- **Visible outcome:** The user sees completed work, new opportunities, organic progress indicators, and clearly labeled SEM planning indicators. Real traffic, conversions, revenue, and ROI require the Phase 2 GA4 and Google Ads connections.
- **Related requirements:** FR-1, FR-7, FR-9, FR-14, FR-15.

### 2.5 Operating Environment
- **Client:** any modern desktop or mobile browser (responsive web app); no OS-specific requirement.
- **Frontend:** React + TypeScript (Vite), Tailwind + shadcn/ui, hosted on **Netlify's free tier** (chosen over Vercel Hobby, whose free plan is restricted to non-commercial use — Netlify's free plan permits the commercial use Trellis's monetization path (5.1) may eventually need, at the same $0 cost).
- **Backend:** Python + Flask + Gunicorn API server, hosted on **Render's free web-service tier only** (750 free instance-hours/month; sleeps after ~15 min idle — see 5.3 Risks). Fly.io and Railway were evaluated and removed from the committed stack: Fly.io now requires a credit card on file for all organizations, and Railway's terms beyond its one-time trial credit don't clearly guarantee a permanent no-card path — see 5.3 for sourcing.
- **AI agent orchestration:** plain Python functions calling each pipeline stage in order (scrape → analyze → audit → suggest → score → report), invoked from the Flask API. LangGraph is deliberately **not** used for the MVP — Trellis's pipeline is fixed and sequential, not a branching, tool-selecting agent, so an orchestration framework would add debugging surface and a learning curve without changing what the user experiences. LangGraph can be revisited if a future phase genuinely needs branching agent behavior.
- **Database:** PostgreSQL on **Supabase's free tier** (chosen over "Neon or Supabase" for the MVP so the project isn't left deciding between two providers mid-build; Supabase also bundles authentication and a browser-based data editor — see Authentication below). Free-tier projects pause after 7 days of inactivity but are not deleted; a paused project restores in one click for up to a year. pgvector can be added in Phase 2 for the best-practice knowledge base on the same free instance.
- **Database access:** SQLAlchemy (Python's standard tool for reading and writing database records as Python objects) with Alembic (tracks and applies database schema changes safely as the data model evolves).
- **Authentication:** Supabase Auth (issues and manages the JWT tokens NFR-1 requires) rather than a hand-built login system — removes an entire class of common beginner security mistakes (password hashing, token refresh/expiry) from the MVP build.
- **AI output validation:** Pydantic, implementing the JSON-schema validation FR-5.5 requires.
- **Deployment:** GitHub Actions (free tier) for CI, deploying directly from GitHub to Render and Netlify. Docker is **not** an MVP requirement — neither Render nor Netlify needs a Dockerfile to build from a repo, so containerization is dropped from the MVP to avoid an extra layer of concepts (images, containers, volumes) with no deployment benefit at this stage; it can be added later if hosting needs change.

Full software-interface detail (which external APIs each component talks to) is in Section 4.3.

### 2.6 Design and Implementation Constraints
- **Zero-cost constraint:** every component must run on a free tier or be open-source, with no credit card required anywhere in the stack, for as long as this is a personal/demo project (see 5.1 Budget for what changes if it becomes a paid product).
- **Free-tier rate limits govern design:** Groq's free tier for the Llama 3.3 70B model Trellis actually calls is **~1,000 requests/day (30 RPM, 6,000 TPM)** — a much tighter budget than earlier drafts of this spec assumed; the higher 14,400 req/day figure applies only to Groq's Llama Guard safety-classifier models, not the generation model FR-5.4 uses, and should not be relied on. Gemini's free tier remains ~1,500 req/day. Request queuing and caching are required, not optional (NFR-3), and the API layer must read and gracefully degrade on rate-limit responses rather than assume headroom.
- **Security constraints:** authentication via Supabase Auth (JWT-based under the hood); per-user data scoping enforced at the database level via Supabase row-level security (RLS), not just in application code; URL validation on every submitted website to block requests to private/internal network addresses (SSRF protection — a submitted URL could otherwise be used to probe Trellis's own infrastructure); `robots.txt` compliance with a clear, identifiable user agent; per-user and per-endpoint rate limiting; HTML sanitization of scraped content before storage or display; secrets management via environment variables, never committed (NFR-1).
- **Accessibility constraint:** WCAG 2.1 AA compliance is a requirement, not a stretch goal (NFR-4).
- **Solo-developer constraint:** all schedule estimates in Section 5 assume one part-time developer (Sloane, ~5–10 hrs/week), which shapes both scope sequencing and the decision to lean on managed free-tier services rather than self-hosting infrastructure.

### 2.7 Assumptions and Dependencies
- Groq and Google Gemini continue to offer no-credit-card free tiers at roughly current request-volume limits for the life of this project (see 2.6 for the corrected Groq figure); if either changes terms, FR-5 (AI Agent Subsystem) has a documented fallback (switch primary/backup roles, or add a third free provider).
- Google's PageSpeed Insights, Business Profile, and Search Console APIs remain free and available to individual developers; Search Console and GBP both require the *user* to verify ownership of their own site/listing, which is a real onboarding step, not just an API call (documented in 5.3 Risks).
- There is no free or ToS-compliant way to programmatically poll ChatGPT, Perplexity, or other AI engines at volume; FR-12 is deliberately designed as manual-assisted rather than fully automated for this reason.
- **pytrends was archived in April 2025 and is no longer reliable** — Google has changed the internal endpoints it relied on, and Google's own official Trends API remains in closed alpha. FR-3.1's keyword ranking and FR-8.1's SEM Cost Tier no longer depend on live trend data for the MVP; both rely on frequency and TF-IDF distinctiveness (FR-3.5) instead. Live trend-volatility data is deferred to a future phase, pending either the official API opening up or a deliberate, documented exception to the $0 constraint for a paid scraping service. HTTPX + BeautifulSoup is the default scraping stack for FR-5.2 (lightweight enough for Render's free-tier memory limit); Playwright is kept only as a fallback for JavaScript-rendered sites, since headless-browser scraping is too memory-heavy to run on every analysis by default.
- Render's free web-service tier (750 instance-hours/month) is assumed adequate for MVP traffic; cold starts after 15 minutes of inactivity are an accepted tradeoff, not a defect. Render is the single committed $0 host (see 2.5); it also offers no free background-worker product, which shapes FR-5.2/NFR-2's resumable, stage-tracked approach to long-running analyses.
- The Google Ads API's Basic Access tier (FR-14) remains free and includes Keyword Planner data (`KeywordPlanIdeaService`); Trellis's own one-time Basic Access review is assumed to complete in Google's stated ~5 business days, requested early in Phase 2 planning so it doesn't block FR-14 (documented in 5.3 Risks).
- The Google Analytics Data API (FR-15) remains free and requires no comparable developer-side app review, only each user's own OAuth connection; it's assumed to remain adequate for reading GA4 sessions, users, and conversion/revenue data at MVP-to-Phase-2 usage scale.

### 2.8 Competitive Landscape
The AEO tooling category is roughly two years old (Profound and Otterly.AI launched late 2023) and has grown crowded through 2026. Relevant categories:
- **AEO-native platforms** (Profound, Scrunch AI, Athena HQ, AirOps) — enterprise-priced ($2,000–$5,000+/month), built for brand-scale citation tracking, not this product's persona.
- **SEO incumbents with AEO bolted on** (Conductor, Semrush AI Toolkit, Surfer AI Tracker) — already combine SEO + AEO, which means "SEO and AEO in one place" alone is not a differentiator.
- **Self-serve entry-level AEO tools** (Otterly.AI, Peec AI, Geoptie) — closest price band, starting ~$79–199/month; still priced and positioned above this product's target persona (solo/nonprofit marketers, no team, no budget).

This product's differentiation is the combination of (a) $0-to-build / low-cost-to-run positioning aimed at an underserved persona, and (b) being a strategy + execution workspace, not an insights dashboard (see 2.1). None of the tools in this landscape — including the AEO-native and self-serve entry-level categories — bundle a cost-conscious SEM/paid-search plan into the same $0 workspace as the organic strategy. For a solo or nonprofit marketer weighing whether to ever pay for ads, and which ones, that's currently a third tool and a third bill. Folding it in (FR-8/FR-14) extends the same differentiation logic: not a new category, but full-stack coverage at a price point nobody else in this landscape offers.

Reporting is the other place this landscape asks a solo/nonprofit marketer to leave the tool: even AEO-native and SEO-incumbent platforms typically export data for the user to report on elsewhere, or gate a real reporting layer behind a higher tier. A predefined-KPI report generated automatically from the same $0 workspace — with no separate reporting product, and no need to touch Excel or Google Analytics directly for the data Trellis already has — extends this product's "strategy + execution workspace, not an insights dashboard" positioning (2.1) one step further: through to reporting, not just planning.

---

## 3. System Features and Requirements

Each feature below is tagged with its target phase (**MVP** = Phase 1, **P2** = Phase 2, **P3** = Phase 3) and stated as testable "shall" requirements with a requirement ID for traceability. Requirement IDs were reassigned on Sep 1, 2026 so MVP requirements are numbered first, followed by Phase 2, then Phase 3 — the list below is simultaneously in strict ascending numeric order (FR-1 through FR-17) *and* grouped by phase, with no exceptions: **FR-1–FR-9 are MVP, FR-10–FR-15 are Phase 2, FR-16–FR-17 are Phase 3.** If you're cross-referencing an older version of this spec, the data model doc, or another project doc that still uses a pre-reassignment ID, see the old-ID → new-ID mapping table in the final entry of the decision log (Appendix A). Rationale is included where it clarifies *why* a requirement exists, since several of these trade off against the $0 constraint.

### FR-1 — Website Workspace (MVP)
Per-site home for the AEO plan, SEO/content plan, SEM plan, Reports, and Organizer.
- **FR-1.1** The system shall let a user add a website (by URL) and create a dedicated workspace for it.
- **FR-1.2** The workspace overview shall display: date of the last analysis run, top keywords, AEO checklist completion %, Organizer pipeline counts, current Health Score, and the Health Score's change since the last scan.
- **FR-1.3** The workspace shall provide navigation to six views: Overview, AEO, SEO/Content, SEM, Reports, and Organizer (see 4.1 for the navigation map).

### FR-2 — AEO Section (MVP)
Trackable checklist covering identity signals, schema.org structured data, direct-answer formatting, FAQ/Q&A coverage, and citation-worthiness signals.
- **FR-2.1** The system shall present AEO recommendations as a trackable checklist scoped to the analyzed site.
- **FR-2.2** Each AEO recommendation shall display a one-sentence rationale (why it matters for *this* site — see FR-5.3) and a priority badge.
- **FR-2.3** Each AEO recommendation shall display a stage tag (Suggested → Backlog → In Production → In Review → Published). Before acceptance, the tag is computed as Suggested; after acceptance, it displays the stage of the corresponding Organizer item (see FR-4.3).
- **FR-2.4** The user shall be able to Accept or Dismiss each recommendation; dismissing shall prompt a one-tap reason (see DR-3).

### FR-3 — SEO/Content Marketing Section (MVP)
Word-frequency ("wordcloud") analysis, keyword candidates, and content-gap suggestions.
- **FR-3.1** The system shall analyze scraped site content for word frequency and rank keyword and keyword-phrase candidates (unigrams through trigrams, e.g. single words like 'marketing' as well as multi-word long-tail phrases like 'content marketing strategy') by frequency and TF-IDF distinctiveness (FR-3.5). Live external search-trend data is not part of MVP ranking (see 2.7 — pytrends is no longer reliable); a real trend-volatility signal is a candidate Phase 2 enhancement.
- **FR-3.2** The system shall generate content-gap suggestions, each including a starter outline (section headings), target keyword(s), and a recommended usage count per keyword.
- **FR-3.3** Each content suggestion shall carry a rationale, priority, and stage tag (as FR-2.2/2.3).
- **FR-3.4** The user shall be able to add any suggestion to the content plan with one click, which creates a corresponding Organizer card (FR-4).
- **FR-3.5** When a site's scrape covers multiple pages, the system shall compute a TF-IDF score for each candidate keyword/phrase across those pages before the FR-3.1 ranking step, and shall down-weight or exclude candidates that score nearly uniformly across all pages (i.e., boilerplate such as navigation menus, footers, and cookie banners) rather than letting them dilute the keyword/content-gap results with content that isn't distinctive to any page.
- *Rationale (FR-3.5):* TF-IDF is only meaningful across multiple documents, so it's applied here as a same-site, page-vs-page filtering pass — not as a replacement for FR-3.1's YAKE/RAKE-based ranking, which correctly rewards a term for recurring across a site's real content. Filtering out boilerplate first keeps that recurrence signal genuine instead of being swamped by templated text every page shares. No new external dependency: implemented with scikit-learn's `TfidfVectorizer` (open-source, self-hosted), added to the existing scrape/keyword pipeline (4.3).

### FR-4 — Organizer (MVP)
Kanban board and checklist tracking every recommendation to completion.
- **FR-4.1** The system shall provide a kanban board with columns Backlog / In Production / In Review / Published for content items.
- **FR-4.2** The system shall provide a separate AEO task checklist and a combined SEO task view.
- **FR-4.3** Every card and checklist item's stage shall be visible from both the Organizer and its originating suggestion in the AEO/SEO/SEM sections. `OrganizerItem.stage` is the single stored source of truth, so changing the task in either interface updates the same record rather than synchronizing duplicate stage fields.

### FR-5 — AI Agent Subsystem (MVP)
Python agent that turns a URL into structured recommendations.
- **FR-5.1** The system shall accept a URL and optional business context as input to the AI agent.
- **FR-5.2** The agent shall orchestrate, in order: scrape → word-frequency/keyword analysis (including the FR-3.5 TF-IDF boilerplate filter, when multiple pages were scraped) → best-practice retrieval → technical audit (FR-6) → generate suggestions (single structured-output LLM call) → compute Health Score (FR-7) → generate Report (FR-9) → persist results. Because Render's free tier has no background-worker product (2.7), this pipeline runs as ordinary Python functions (2.5) and shall update `AnalysisRun.status` (queued/scraping/analyzing/generating/completed/failed — already modeled in the data model) after each stage completes, so a failed or interrupted run can resume from its last completed stage instead of restarting, and the frontend can poll for progress (see NFR-2).
- **FR-5.3** Every generated `Suggestion` shall include a one-sentence rationale explaining why the recommendation matters for the specific analyzed site.
- **FR-5.4** The agent shall call a free-tier LLM (Groq Llama 3.3 70B primary, Google Gemini free tier backup) for the suggestion-generation step only.
- **FR-5.5** LLM output shall be validated against a JSON schema, with one automatic retry on validation failure, to mitigate free-model schema drift.
- **FR-5.6** The technical-audit output (FR-6) shall lead with a short plain-language summary ("here's what I'd fix first and why") ahead of itemized findings.

### FR-6 — Technical SEO Audit (MVP)
- **FR-6.1** The system shall retrieve Core Web Vitals and a mobile-usability score via Google's free PageSpeed Insights API.
- **FR-6.2** The system shall detect crawl errors (404/500) using the existing scraper.
- **FR-6.3** The system shall validate sitemap.xml and robots.txt presence and correctness.
- **FR-6.4** The system shall audit meta titles, meta descriptions, header structure, and image alt-text.
- **FR-6.5** The system shall flag duplicate or thin content, reusing the word-frequency analysis from FR-3.1.
- **FR-6.6** The system shall roll all findings into a single prioritized fix list per FR-5.6.
- **FR-6.7** In addition to FR-6.5's exact-repetition signal, the system shall compute pairwise TF-IDF cosine similarity across a site's scraped pages (reusing the FR-3.5 TF-IDF pass) and flag page pairs above a similarity threshold as likely near-duplicate content, since two pages can share the same distinctive vocabulary without being textually identical.
- *Rationale:* provides a consultancy-style technical audit with no paid crawler tool, per the $0 constraint (2.6). FR-6.7 adds a near-duplicate signal that plain word-frequency comparison (FR-6.5) cannot catch on its own, at no new cost (same TF-IDF pass as FR-3.5).

### FR-7 — Health Score (MVP)
- **FR-7.1** The system shall compute a single 0–100 Health Score per website as a weighted blend of: AEO checklist completion %, technical audit findings resolved %, keyword/content-gap coverage, and (once available) the AI-citation check-log rate (FR-12.3).
- **FR-7.2** A Health Score snapshot shall be stored on every `AnalysisRun` (DR-1).
- **FR-7.3** The Website Overview shall display both the current Health Score and its trend as a line chart across scans.
- *Open question (carried into 5.3 Risks):* the weighting formula is a product judgment call, not a technical one, and should be validated with real users before being treated as authoritative. The Health Score is scoped to organic SEO/AEO performance; SEM (FR-8/FR-14) is intentionally tracked as its own summary (FR-8.8) rather than blended into this score, since paid and organic are different disciplines with different success signals.

### FR-8 — SEM Keyword & Ad Strategy (MVP)
Generates a cost-conscious paid-search plan using only data the system already collects — no new account connection, no external cost, no waiting on any third-party review.
- **FR-8.1** The system shall generate SEM keyword candidates from the same keyword/content analysis already produced for organic SEO (FR-3.1), each tagged with a relative **Cost Tier** (Low / Medium / High) inferred from: keyword length (long-tail vs. short "head" term) and presence of commercial-intent modifiers (e.g., "buy," "near me," "best," "pricing," "vs"). The MVP does not use a live trend-volatility signal as a competition proxy, since pytrends is no longer reliable (2.7); real search-volume/CPC data replaces this heuristic once FR-14 (Phase 2) is connected.
- **FR-8.2** The system shall prioritize long-tail, high-commercial-intent, lower-Cost-Tier keywords over expensive head terms in its default suggestion ranking, consistent with the cost-efficiency goal.
- **FR-8.3** For each higher-Cost-Tier keyword candidate, the system shall suggest 2–4 long-tail sibling variants targeting similar intent at a presumed lower Cost Tier, so the user always sees a cheaper alternative next to the expensive option, not just the expensive option alone.
- **FR-8.4** The system shall recommend, in plain language, where each ad should be targeted: Search vs. Display network, relevant audience/topic targeting, and — for a local business (detected from FR-1's `business_context`) — a suggested geographic radius.
- **FR-8.5** The system shall group keyword candidates into 2–4 tightly-themed starter ad groups, each with a suggested headline/description angle, and explain in the rationale that tight theming is what keeps Quality Score up and CPC down (not a separate, unexplained best practice).
- **FR-8.6** The system shall match each ad group to the existing scraped page (or an FR-3.2 content-gap suggestion, if no matching page exists yet) it should link to, so ad-to-landing-page relevance — a direct Quality Score input — is addressed by default rather than left to the user to figure out.
- **FR-8.7** The system shall suggest a starter negative-keyword list per ad group, drawn from off-topic terms surfaced by the existing word-frequency analysis (FR-3.1) and common irrelevant-intent modifiers (e.g., "free," "jobs," "DIY," "how to" — where these don't match the site's actual offering), to reduce wasted spend from day one.
- **FR-8.8** Each SEM suggestion shall carry the same rationale, priority badge, stage tag, and Accept/Dismiss pattern as AEO/SEO suggestions (FR-2.2–2.4, FR-5.3); accepting one shall create a corresponding Organizer card (FR-4), so an SEM item moves through the same Suggested → Backlog → In Production → In Review → Published pipeline as everything else. The SEM section's overview shall display its own small summary (accepted keyword count and estimated cost range) rather than folding into the single Health Score (FR-7).
- **FR-8.9** The system shall clearly and persistently label Cost Tier as a **heuristic estimate**, not a guaranteed or real Google Ads bid price, everywhere it's displayed, until FR-14 is connected.
- **FR-8.10** The system shall NOT create, launch, or manage live ad campaigns, and shall NOT move or spend the user's money in any way — FR-8 produces a strategy the user manually implements in their own Google Ads account, exactly as FR-11 reads Search Console data without ever modifying the user's site. This boundary matters both for scope (a real ad-buying/bidding engine is a much larger, higher-stakes build) and so the product is never mistaken for a financial tool making spending decisions on the user's behalf.
- *Rationale:* every sub-requirement here reuses infrastructure the spec already commits to (FR-3's scraping/keyword pipeline, FR-5's LLM call) — no new external dependency, so this is buildable within the $0 constraint and doesn't introduce new schedule risk from third-party account linking.

### FR-9 — Analysis Reports & KPI Comparison (MVP)
Turns data Trellis already computes into a saved, comparable Report — no new external dependency, no new account connection, buildable entirely within the existing MVP scope.
- **FR-9.1** The system shall automatically generate one Report immediately after each AnalysisRun completes (FR-5.2), without requiring any user action.
- **FR-9.2** Each Report shall be built from a **predefined KPI set** (not user-configurable in MVP, so a marketer never has to decide which metrics matter) spanning:
  - *Organic:* Health Score and its change since the prior report (FR-7); AEO checklist completion % and its change (FR-2); technical audit findings resolved vs. still open (FR-6); count of content items reaching Published this period (FR-4); top keyword/content-gap candidates by the MVP's frequency and TF-IDF ranking (FR-3.1).
  - *Paid (heuristic, MVP):* count of SEM suggestions accepted; breakdown of accepted keywords by Cost Tier (Low/Medium/High, FR-8.1); number of starter ad groups defined (FR-8.5).
  - *Pipeline:* Organizer cards by stage, and cards that moved to Published this period (FR-4).
- **FR-9.3** Each Report shall store its KPI values as a **snapshot** at generation time, so a saved report's numbers remain fixed even if the underlying scoring logic (e.g., the Health Score formula, FR-7) is later changed — the same principle already applied to `AnalysisRun.health_score` (DR-1).
- **FR-9.4** The system shall provide a Report History view per website, listing every past Report by date, from which any report can be reopened in full.
- **FR-9.5** The system shall let the user select any two Reports for the same website and view them side by side with a computed delta (absolute and %, where applicable) for every KPI in FR-9.2 — supporting both the common cases (most recent vs. previous report, i.e. "since last scan"; and same-period-last-month) and an arbitrary pair the user picks.
- **FR-9.6** Each Report shall lead with a short plain-language summary of what changed, in the same "here's what matters first" pattern already used for the technical audit (FR-5.6) and the since-last-scan delta (FR-1.2) — e.g., "Health Score up 7 points, 3 tasks published, 2 new keyword opportunities."
- **FR-9.7** The system shall NOT require the user to leave Trellis (e.g., to Excel or Google Analytics) to view, save, or compare any KPI covered by FR-9.2 — that data lives, is computed, and is retained entirely inside Trellis.
- *Rationale:* every KPI here is already produced somewhere else in the spec (FR-2 through FR-8); FR-9 is a persistence and presentation layer on top of existing computation, not new analysis logic — so it carries none of the schedule/onboarding risk that a new external integration would.

### FR-10 — Local SEO & Google Business Profile (Phase 2)
- **FR-10.1** The system shall check NAP (Name/Address/Phone) consistency across the site.
- **FR-10.2** The system shall let the user connect their own free Google Business Profile listing and shall surface a GBP completeness checklist via the free GBP API.
- **FR-10.3** The system shall suggest LocalBusiness schema markup based on the site's business information.
- **FR-10.4** The system shall generate periodic review-generation reminder nudges.

### FR-11 — Backlink Visibility (Phase 2)
- **FR-11.1** The system shall source referring-domain data from the user's own Google Search Console "Links" report (requires the user to complete site verification).
- **FR-11.2** The system shall surface top linked pages and top anchor text from that report.
- **FR-11.3** The system shall compute and display new/lost referring domains between scans.
- **FR-11.4** The system shall label this feature to users as "backlinks Google already sees," not a comprehensive third-party index.

### FR-12 — Guided AI-Citation Checklist (Phase 2, manual-assisted)
- **FR-12.1** The system shall generate natural-language test questions relevant to the site's topic/business.
- **FR-12.2** The user shall be able to manually run those questions in free consumer AI apps and log whether the site was cited.
- **FR-12.3** The system shall track a "cited in X of Y checks" log over time per site.
- **FR-12.4** This log shall feed the Health Score (FR-7) once available.
- *Rationale:* continuous automated cross-engine citation monitoring has no free or ToS-compliant path at volume (2.7); this is the $0-compatible substitute, explicitly positioned to users as manual-assisted, not automated monitoring.

### FR-13 — Progress Digest (Phase 2)
- **FR-13.1** The system shall generate a weekly or monthly email/in-app summary per website (e.g., "Your Health Score moved from 61 → 68 this month, 2 tasks overdue, 3 new keyword opportunities").
- **FR-13.2** The digest shall be built entirely from data already computed for the Health Score (FR-7) and the since-last-scan delta (FR-1.2); no new paid dependency.

### FR-14 — Google Ads Keyword Planner Integration (Phase 2)
Upgrades FR-8's heuristic Cost Tier to real search-volume and CPC data, once the user opts in — same $0-but-per-user-OAuth shape as FR-10 (Google Business Profile) and FR-11 (Search Console).
- **FR-14.1** The system shall let the user connect their own Google Ads account via OAuth. Creating a Google Ads account is free and does not require an active or funded campaign.
- **FR-14.2** Once connected, the system shall call the Google Ads API's Keyword Planner service (`KeywordPlanIdeaService`, available under the free Basic Access tier) to retrieve average monthly search volume and a low/high CPC bid range for each FR-8 keyword candidate, replacing the heuristic Cost Tier with these real figures.
- **FR-14.3** The system shall re-rank SEM keyword suggestions by an explicit cost-efficiency score (estimated search volume ÷ estimated CPC), surfacing the best "traffic per dollar" opportunities first, once real data is available.
- **FR-14.4** The system shall display a rough estimated monthly ad-spend for the user's currently-accepted SEM keyword set (sum of low-end CPC × an assumed click volume), clearly labeled as an estimate for planning purposes, not a bill or a spend commitment — Trellis never touches the user's actual ad budget (per FR-8.10).
- *Dependency note:* Trellis's own Google Ads API Basic Access approval is a one-time, free review of the app itself (Google's stated turnaround is about 5 business days) — this is a *developer*-side step (Sloane requesting API access for Trellis), separate from each user's own OAuth connection, and should be requested early in Phase 2 planning since FR-14 can't ship without it. It does not block FR-8 or any of the rest of the MVP.

### FR-15 — Real Analytics Enrichment via Google Analytics 4 (Phase 2)
Upgrades FR-9's Reports with real traffic, conversion, and revenue data once the user opts in — same $0-but-per-user-OAuth shape as FR-10, FR-11, and FR-14.
- **FR-15.1** The system shall let the user connect their own GA4 property via OAuth. Creating and using GA4 is free and requires no credit card.
- **FR-15.2** Once connected, the system shall call the free Google Analytics Data API to retrieve, per reporting period: sessions, new vs. returning users, and (where the user has configured GA4 conversions/goals) conversion count and any tracked revenue.
- **FR-15.3** Where the site also has real ad spend data (FR-14, Google Ads connected), the system shall compute and display a real ROI figure (GA4-attributed conversions or revenue ÷ actual ad spend) alongside the existing heuristic Cost Tier view, clearly distinguishing "estimate" fields from "real" fields at all times (extending the FR-8.9 disclosure pattern).
- **FR-15.4** The system shall add real GA4 metrics as additional KPI rows in the FR-9 Report and its comparison view, rather than a separate report — so a user with GA4 connected sees one enriched report, not two.
- **FR-15.5** The system shall clearly label any KPI in FR-15.2/15.3 as sourced from the user's own GA4 account, and shall never modify or write to the user's GA4 property — read-only, exactly as FR-11 reads Search Console without writing to it.
- *Dependency note:* unlike FR-14's Google Ads API, the Google Analytics Data API does not require a separate developer-side app review — only the per-user OAuth connection (FR-15.1) — so FR-15 has less setup risk than FR-14, though it still depends on the user already having GA4 installed on their site, which Trellis cannot do for them.

### FR-16 — Competitor & Entity Benchmarking (Phase 3)
- **FR-16.1** The system shall accept 1–3 competitor URLs and run the existing scrape + keyword + AEO pipeline against each for side-by-side comparison.
- **FR-16.2** The system shall generate entity/topic mapping suggestions feeding schema.org `about`/`sameAs` markup.
- **FR-16.3** The system shall compute a TF-IDF score for each keyword candidate across the comparison set formed by the analyzed site plus its 1–3 competitor sites (FR-16.1), and shall surface, as a distinct "distinctive to you" list, the keywords that score highly for the analyzed site but are common (low-IDF) across the whole comparison set — separating the site's real differentiators from table-stakes terms every site in the set already uses.
- *Rationale (FR-16.3):* this is the comparison-across-sites use case TF-IDF is actually built for (unlike FR-3.1's single-site ranking); reuses the same scikit-learn `TfidfVectorizer` already added for FR-3.5/FR-6.7, so it adds no new dependency or cost.

### FR-17 — AI-Drafted Opening Paragraph (Phase 3, optional)
- **FR-17.1** For each content suggestion (FR-3.2), the system shall optionally draft a short opening paragraph via the free-tier LLM, in addition to the existing outline.
- *Rationale:* kept optional/Phase 3 since full content generation isn't core to the MVP's differentiation and several funded competitors already offer it (2.8).

### DR — Data Requirements
Core (MVP) entities and relationships: **User** → **Website** → **AnalysisRun** → **Keyword**, **Suggestion**, **TechnicalFinding**, **Report**; **Website** also owns **OrganizerItem**, and **OrganizerStageHistory** records task movement. A single `OrganizerItem` model serves AEO, SEO/content, and SEM work; its `item_type` distinguishes those experiences while preserving one combined workflow. Scraped page content is processed temporarily and is not stored as raw HTML or permanent page snapshots; `Suggestion.affected_page_url` and `TechnicalFinding.affected_page_url` / `related_page_url` retain the evidence needed to explain page-specific and comparison results. New entities supporting Phase 2 and Phase 3 are added only when those phases are implemented. The implementation-ready MVP relationships are defined in `planning_documents/architecture and data model/data model/Trellis_Data_Model.md` and its companion PDF.

- **DR-1** `AnalysisRun.health_score` (int, 0–100) — snapshot of the Health Score (FR-7) at the time of the run, enabling the trend line on the Website Overview.
- **DR-2** `Suggestion.rationale` (text) — the one-sentence "why this matters" explanation (FR-5.3).
- **DR-3** `Suggestion.status` (enum: `pending` / `accepted` / `dismissed`) — an explicit acceptance state supporting the decision workflow in UC-2 and making suggestion acceptance measurable.
- **DR-4** `Suggestion.dismiss_reason` (enum, nullable: `not_relevant` / `too_much_work` / `already_doing_this` / `other`) — captured only when dismissed; feeds Phase 2 suggestion-quality tuning.
- **DR-5** `OrganizerItem.stage` (enum: `backlog` / `in_production` / `in_review` / `published`) — the single stored source of truth for work progress. Before acceptance, a suggestion displays the computed label `Suggested`; after acceptance, its displayed stage comes from its linked Organizer item. This avoids storing two stage values that could disagree while satisfying FR-2.3/FR-4.3.
- **DR-6** `Suggestion.category` (enum) — extended to include `sem` alongside the existing `aeo` / `seo_content` values (FR-8).
- **DR-7** `Suggestion.cost_tier` (enum, nullable: `low` / `medium` / `high`) — heuristic SEM cost estimate (FR-8.1); nullable, populated only for `category = sem`.
- **DR-8** `Suggestion.cpc_low`, `Suggestion.cpc_high` (decimal, nullable), `Suggestion.search_volume` (int, nullable) — real Keyword Planner figures, populated once FR-14 is connected.
- **DR-9** `Suggestion.ad_group_label` (text, nullable), `Suggestion.landing_page_match` (text, nullable), `Suggestion.targeting_notes` (text, nullable), `Suggestion.negative_keywords` (text[], nullable) — starter ad-group grouping (FR-8.5), landing-page match (FR-8.6), placement guidance (FR-8.4), and negative-keyword list (FR-8.7).
- **DR-10** `Website.google_ads_connected` (boolean) — mirrors the existing `gbp_connected` / `search_console_connected` pattern; gates FR-14.
- **DR-11** `Report` (new entity, one-to-one with `AnalysisRun`) — a KPI snapshot generated after every analysis run (FR-9.1, FR-9.3): `id` (PK), `website_id` (FK), `analysis_run_id` (FK, unique), `generated_at`, `health_score`/`health_score_delta`, `aeo_completion_pct`/`aeo_completion_delta`, `technical_findings_resolved`/`technical_findings_open`, `content_published_count`, `top_keywords` (text[]/JSON), `sem_accepted_count`, `sem_cost_tier_breakdown` (JSON), `ad_groups_defined_count`, `organizer_stage_counts` (JSON), `summary_text` (FR-9.6). Comparison (FR-9.5) is a computed operation over two `Report` rows, not a separately stored entity.
- **DR-12** `Report.ga4_sessions`, `Report.ga4_new_users`, `Report.ga4_returning_users`, `Report.ga4_conversions`, `Report.ga4_revenue` (nullable) — real GA4 figures, populated once FR-15 is connected.
- **DR-13** `Report.real_ad_spend`, `Report.real_roi_pct` (decimal, nullable) — populated once both FR-14 and FR-15 are connected (FR-15.3).
- **DR-14** `Website.ga4_connected` (boolean) — mirrors the `gbp_connected` / `search_console_connected` / `google_ads_connected` pattern; gates FR-15.

### NFR — Non-Functional Requirements
- **NFR-1 (Security):** authentication via Supabase Auth (JWT-based); all data scoped per-user, enforced via Supabase row-level security (RLS) at the database level, not application code alone; URL validation blocking requests to private/internal network addresses on every submitted website (SSRF protection); `robots.txt` compliance with a clear user agent; HTML sanitization of scraped content; secrets managed via environment/secret-store, never committed; rate limiting on all endpoints, per-user and shared, to protect shared free-tier quota.
- **NFR-2 (Scalability):** stateless API design; because Render's free tier provides no background-worker product (2.7), long-running analysis (FR-5) runs as a single request broken into resumable stages, with `AnalysisRun.status` updated after each stage (FR-5.2) so the frontend can poll for progress and a failed run can resume rather than restart; true async background jobs become an option once usage or hosting budget grows beyond the free tier; caching of scrape/keyword results to avoid redundant free-tier API calls.
- **NFR-3 (Cost management):** request budgets and a request queue in front of the LLM providers (2.6); caching wherever a re-computation would otherwise re-spend a free-tier quota unit.
- **NFR-4 (Accessibility):** WCAG 2.1 AA compliance across the frontend.
- **NFR-5 (Performance):** time-to-first-actionable-plan under 5 minutes from URL submission (UC-1), acknowledging free-hosting cold starts (2.7) as a bounded exception.
- **NFR-6 (Reliability):** JSON-schema validation with automatic retry on every LLM structured-output call (FR-5.5), since free-tier models are more prone to schema drift than paid frontier models.

---

## 4. External Interface Requirements

### 4.1 User Interfaces
Shallow navigation: **Login → My Websites → Add Website wizard → Website Workspace** (Overview, AEO, SEO/Content, SEM, Reports, Organizer tabs).

- **Website Overview:** summary cards lead with the Health Score (large, prominent number) and its change since the last scan (e.g., "68 ▲ +7"), followed by since-last-scan delta callouts (e.g., "3 new keyword opportunities"), then last-analysis date, top keywords, AEO completion %, and pipeline counts (FR-1.2).
- **AEO / SEO sections:** each recommendation shows its rationale beneath the recommendation text, a priority badge, and a stage tag; an Accept/Dismiss action pair replaces a single "add" button, with dismissal opening a one-tap reason picker (FR-2.2–2.4, DR-4).
- **SEM section:** mirrors the AEO/SEO layout — each suggestion shows its Cost Tier badge (Low/Medium/High, or a real CPC range once FR-14 is connected), rationale, priority, and stage tag, grouped visually by starter ad group (FR-8.5). A "cheaper alternative" chip surfaces the FR-8.3 long-tail sibling next to any Medium/High-tier suggestion. Once FR-14 is connected, an estimated-monthly-spend summary appears at the top of the section (FR-14.4).
- **Reports section:** a list of past Reports (newest first) with the FR-9.6 one-line summary shown per row; opening one shows the full KPI breakdown grouped Organic / Paid / Pipeline, matching the section layout used elsewhere. A "Compare" control lets the user pick any two reports (defaulting to "most recent vs. previous") and see every KPI side by side with its delta, using the same up/down indicator style as the Health Score trend (FR-7.3). Once FR-15 is connected, a GA4 row group appears with real traffic/conversion figures, and a real-ROI figure replaces the heuristic Cost Tier summary wherever both FR-14 and FR-15 are connected — with "estimate" vs. "real" labeled per FR-8.9/FR-15.5's disclosure pattern throughout.
- **Organizer:** kanban board (FR-4.1) plus separate AEO/SEO task list views (FR-4.2).

**Core user flows covered by these screens:** create the first website action plan (UC-1); accept or dismiss recommendations to form a focused plan (UC-2); move accepted AEO, SEO/content, and SEM work through the Organizer (UC-3); review clearly labeled paid-search guidance without launching a campaign (UC-4); and review or compare Reports after rescanning to measure progress (UC-5).

### 4.2 Hardware Interfaces
None. This is a standard responsive web application with no dedicated hardware dependency; it runs on any device with a modern browser and an internet connection.

### 4.3 Software Interfaces
| Interface | Direction | Purpose | Auth | Notes |
|---|---|---|---|---|
| Groq API (Llama 3.3 70B) | Outbound | Primary LLM for suggestion generation (FR-5.4) | API key | **~1,000 req/day free tier (30 RPM, 6,000 TPM)** — corrected from an earlier draft that cited 14,400 req/day, which applies only to Groq's Llama Guard safety models, not this generation model (2.6) |
| Google Gemini API (free tier) | Outbound | Backup LLM if Groq is unavailable/rate-limited (FR-5.4) | API key | ~1,500 req/day free tier; note its data-training clause (5.3 Risks) — strip PII from page text before sending |
| Google PageSpeed Insights API | Outbound | Core Web Vitals / mobile score (FR-6.1) | API key (free) | No paid crawler needed |
| Google Business Profile API | Outbound | GBP completeness checklist (FR-10.2) | Per-user OAuth | User connects their own free listing |
| Google Search Console API | Outbound | Backlink/"Links" report (FR-11.1) | Per-user OAuth | Requires per-site verification by the user |
| HTTPX + BeautifulSoup | Internal | Default site scraping for all analysis features (FR-5.2) | N/A | Self-hosted within the API tier; lightweight enough for Render's free-tier memory limit |
| Playwright | Internal | Fallback scraping only for JavaScript-rendered sites HTTPX/BeautifulSoup can't read | N/A | Self-hosted; used selectively, not by default — headless Chromium's memory footprint doesn't fit Render's free-tier RAM if run on every analysis |
| scikit-learn (`TfidfVectorizer`) | Internal | Cross-page boilerplate filtering ahead of keyword ranking (FR-3.5); near-duplicate/thin-content detection (FR-6.7); site-vs-competitor keyword differentiation (FR-16.3) | N/A | Open source, self-hosted within the API tier; used only where a multi-document comparison naturally exists — not for single-page keyword ranking, which stays YAKE/RAKE (FR-3.1) |
| Pydantic | Internal | Validates LLM structured output against the expected schema (FR-5.5) | N/A | Open source, self-hosted |
| SQLAlchemy + Alembic | Internal | Database access layer and schema-migration tracking for all entities (DR-1–DR-14) | N/A | Open source, self-hosted |
| Transactional email API (Resend/Postmark free tier) | Outbound | Progress digest delivery (FR-13.1) | API key | Phase 2; stays within free send limits at this usage scale |
| Google Ads API (Basic Access) | Outbound | Keyword Planner search volume + CPC bid ranges (FR-14.2) | Per-user OAuth + Trellis developer token | Free tier; Basic Access supports 15,000 ops/day; requires a one-time ~5-business-day review of Trellis itself |
| Google Analytics Data API (GA4) | Outbound | Real sessions, users, conversions, revenue for Report enrichment (FR-15.2) | Per-user OAuth | Free tier; generous free quota; no developer-side app review required (unlike Google Ads API) |
| Supabase (PostgreSQL + Auth) | Internal | Primary data store for all entities (DR-1–DR-14) and user authentication (NFR-1) | Connection credentials / Supabase Auth | Free tier; 500MB storage, pauses (not deletes) after 7 days idle, restorable for up to a year; pgvector added Phase 2 |

### 4.4 Communications Interfaces
- All client–server and server–third-party communication shall use HTTPS.
- The frontend and API server communicate via a REST API returning JSON.
- Authenticated requests use JWT bearer tokens (NFR-1).
- Per-user and shared free-tier rate limits are enforced server-side (NFR-1, NFR-3) to prevent one user's activity from exhausting the shared LLM/API quota.

---

## 5. Preliminary Schedule & Budget

### 5.1 Budget
The build-and-demo cost of this project is **$0**: every component in Sections 2.5 and 4.3 runs on a free tier or is open-source, with no credit card required anywhere in the stack. The only real cost is developer time (Sloane, part-time, ~5–10 hrs/week — see 5.2). This is an implementation constraint for the current project, not a permanent customer-pricing commitment if usage later exceeds free-tier limits.

**What would cost money later:** if this becomes a paid product with real customers, the free-tier caps below become a cost-of-goods question that needs revisiting (not a Phase 1–3 concern):
- LLM requests/day beyond Groq's/Gemini's free limits (2.6).
- Database storage beyond the free Postgres tier's cap.
- Transactional email sends beyond the free tier (FR-13).
- Backend hosting beyond free-tier compute/uptime (cold starts, 2.7).

**Monetization note (future, non-binding):** a plausible path is self-serve subscription pricing below the competitive set in 2.8 — e.g., $15–40/month for the solo/nonprofit tier, higher for a Phase 2 agency tier — validated against real users before committing to a number.

### 5.2 Preliminary Schedule
**Delivery policy:** feature completeness governs Phase 1. The MVP is released only when all FR-1 through FR-9 requirements and their security, accessibility, reliability, and acceptance checks pass. September 14, 2026 is no longer a release deadline; dates may move rather than cutting an MVP requirement.

**Capacity assumption:** one solo, part-time developer at roughly 5–10 hours per week. The working estimate is approximately 20 weeks, reviewed after every milestone. Phase 2/3 work and new feature requests remain outside the MVP so they cannot displace FR-1 through FR-9.

**Test-first rule:** automated tests are part of every milestone from the first day, not a final cleanup task. Before implementing each user case, write its expected behavior as a failing test, implement the smallest working behavior, then rerun the relevant unit and integration tests until they pass. **Unit tests** verify one small function or component in isolation; **integration tests** verify that connected parts (such as the API, database, scraper, and LLM boundary) work together. Playwright end-to-end tests cover the most important complete user journeys, while unit and integration tests provide broader behavior coverage.

**Phase 1 — MVP (estimated 20 weeks; acceptance-driven)**

| Date | Milestone | Required outcome, including tests written first |
|---|---|---|
| Weeks 1–3 | Foundation, test harness, and contracts | Configure pytest, Vitest, and Playwright; establish test folders, fixtures/mocks, a separate test database, and CI test commands before feature work. Then scaffold the app and implement database (DR-1–DR-14), Supabase Auth/RLS (NFR-1), and API-contract foundations against the first unit/integration tests. |
| Weeks 4–7 | First end-to-end analysis path | First write user-case and integration tests for URL validation, workspace creation, safe scraping, failed/retried analysis, persisted status, and visible results. Then implement FR-1, FR-3, and the first critical Playwright journey: sign in → add website → analyze → view results. |
| Weeks 8–10 | AI recommendation pipeline | First write unit tests for pipeline stages, prompt-input preparation, Pydantic validation, retry/fallback behavior, and mocked LLM responses; add an integration test for recommendations saved to the database. Then implement FR-2, FR-3, and FR-5. |
| Weeks 11–12 | Action workflow | First write tests for Accept/Dismiss decisions, dismiss reasons, task creation, valid Organizer stage changes, persistence, and user isolation. Then implement FR-4 and extend the Playwright journey through the Organizer. |
| Weeks 13–14 | Technical audit | First write unit/integration tests for each FR-6 rule, PageSpeed success/failure handling, and TF-IDF near-duplicate thresholds using fixed fixtures. Then implement the audit and findings UI. |
| Weeks 15–16 | SEM strategy | First write tests for FR-8 suggestion fields, deterministic heuristic Cost Tier boundaries, negative keywords, disclosure text, and saved SEM output. Then implement the SEM engine and UI. |
| Weeks 17–18 | Measurement | First write tests for Health Score calculations/deltas, Report creation on every completed analysis, immutable snapshots, KPI aggregation, and report comparison. Then implement FR-7 and FR-9. |
| Week 19 | Complete integrated UI | First write component and integration tests for all six views and their loading, empty, failure, and retry states. Then connect every view to the same website/analysis data and finish the critical Playwright rescan/report-comparison journey. |
| Week 20 | Regression, accessibility, deployment, and acceptance | Run the complete test suite, fix regressions, complete accessibility checks, deploy to Render/Netlify, run production smoke tests, verify the critical journeys, and rehearse the demo. |

**Definition of done for Phase 1:** a user can sign in, add a website, run and monitor an analysis, view SEO/AEO/technical/SEM recommendations, accept or dismiss recommendations, move accepted work through the Organizer, view the Health Score, rescan the website, and view/compare saved Reports in the deployed app. Required security controls in NFR-1 and critical-path automated tests must pass. Phase 2/3 features and nonessential visual refinements remain outside Phase 1.

**Daily control point:** no feature is considered complete until its relevant unit and integration tests pass in CI and its scheduled behavior is verified in the running app. At the end of each day, run the accumulated suite so earlier behavior cannot silently break. Any incomplete blocker becomes the first task the following morning. No new feature may displace a critical-path FR-1–FR-9 requirement before final acceptance.

**Phase 2 — Grow (schedule to be estimated after Phase 1 acceptance)**
Multi-user orgs, scheduled re-analysis, CMS integrations, Search Console/rank tracking, local SEO & Google Business Profile (FR-10), backlink visibility (FR-11), guided AI-citation checklist (FR-12), Google Ads Keyword Planner integration (FR-14), real analytics enrichment via Google Analytics 4 (FR-15, built right after FR-14 since FR-15.3's real ROI figure depends on both being connected), notifications, progress digest (FR-13).

**Phase 3 — Scale (schedule to be re-estimated after Phase 2 planning)**
Multi-site benchmarking, competitor & entity benchmarking (FR-16, including the FR-16.3 TF-IDF keyword-differentiation view), white-label agency reporting, browser extension, optional AI-drafted opening paragraphs (FR-17).

*Every phase remains $0 to build (5.1); schedule risk, not budget risk, is the main variable — see 5.3.*

### 5.3 Risks Affecting Schedule and Scope
- **Free-tier LLM rate limits are tighter than earlier drafts assumed** — Groq's actual free-tier limit for the Llama 3.3 70B model FR-5.4 calls is ~1,000 requests/day (30 RPM), not the 14,400/day figure an earlier draft cited (that number belongs to a different, safety-classifier model — see 2.6); mitigated with a request queue (NFR-3) and graceful degradation on rate-limit responses, but a burst of testing/demo traffic could still hit daily caps sooner than expected.
- **Free-model JSON consistency** — mitigated with Pydantic schema validation + one retry (FR-5.5, NFR-6); persistent drift could slow Phase 1's agent milestone.
- **Gemini's free-tier data-training clause** — a legal/privacy consideration for the backup LLM path (FR-5.4); mitigated by stripping PII (emails, phone numbers, forms, tracking values) from page text before any request and using Gemini only as a fallback when Groq is unavailable — should still be disclosed to end users eventually.
- **Free-hosting cold starts** — accepted tradeoff (2.7) that affects perceived performance (NFR-5), not correctness.
- **pytrends is no longer functional** (archived April 2025) — removed as an MVP dependency; FR-3.1/FR-8.1 rely on frequency and TF-IDF instead, and live trend data is deferred to a future phase (2.7).
- **Render's free tier has no background-worker product** — a full analysis (crawl + PageSpeed + multiple LLM calls) can run long enough to strain a single synchronous request; mitigated by breaking FR-5.2 into resumable, status-tracked stages with frontend polling (NFR-2) rather than assuming a background job queue is available for free.
- **Fly.io and Railway are not reliable $0 hosts and were removed from the committed stack** (2.5) — Fly.io's own pricing documentation states a credit card is required for all organizations except linked ones; Railway's free access beyond its one-time trial credit isn't clearly guaranteed card-free. Render is the single committed backend host.
- **Netlify was chosen over Vercel for frontend hosting** because Vercel's Hobby plan is explicitly restricted to non-commercial use, while Netlify's free plan permits commercial use — relevant given the future subscription-pricing path noted in 5.1; revisit only if a concrete reason to prefer Vercel emerges.
- **Scraping reliability** — HTTPX/BeautifulSoup and the Playwright fallback are both best-effort and subject to site-specific blocking; no SLA exists (2.7).
- **TF-IDF boilerplate filtering is threshold-dependent** (FR-3.5) — too aggressive a similarity threshold risks stripping out a genuinely important term that happens to recur intentionally across many pages (e.g., a tagline or core service name); should be spot-checked against a few real sites before being treated as tuned correctly, the same category of judgment call already flagged for the Health Score weighting (FR-7) and predefined-KPI set (FR-9.2).
- **AEO best practices still evolving** — the best-practice knowledge base (FR-5.2) will need periodic manual updates until a RAG-backed refresh pipeline exists (Phase 2+).
- **Automated AI-citation tracking is deliberately excluded from $0 scope** — FR-12 is the manual substitute; true automation would be a future paid upgrade, not a schedule slip.
- **Backlink visibility is scoped to Search Console data only** (FR-11), not a full third-party index — an explicit scope tradeoff.
- **Search Console/GBP both require per-website user verification** — real onboarding friction (2.7) that could slow Phase 2 adoption testing even though the engineering is straightforward.
- **Health Score weighting is an unvalidated product judgment call** (FR-7) — should be tested with a few real users before Phase 2, or the "measure improvement over time" promise (UC-5) is undercut by a score that feels arbitrary.
- **SEM Cost Tier is a heuristic, not real auction data** (FR-8.1) — needs the same persistent-disclosure treatment as Gemini's data-training clause (FR-8.9), so users never mistake it for a real Google Ads quote.
- **Google Ads API Basic Access review turnaround** (FR-14) — the one-time ~5-business-day review of Trellis itself should be requested at the start of Phase 2 planning, not discovered as a blocker mid-sprint.
- **Google Ads account creation is a real onboarding step** (FR-14.1) — even though free, asking a nonprofit/solo marketer to create a Google Ads account is the same category of friction already logged for GBP/Search Console above.
- **Predefined-KPI set is a product judgment call, not a technical one** (FR-9.2) — same category of open question already flagged for Health Score weighting (FR-7) and SEM Cost Tier (FR-8); should be sanity-checked with a real marketer before being treated as the definitive "what matters" list.
- **GA4 connection requires the user to already have GA4 installed on their site** (FR-15.1) — Trellis can't do this step for them; same onboarding-friction category as Search Console verification and GBP listing ownership, already logged above.
- **Report snapshot immutability vs. scoring changes** — once Health Score's weighting formula (still unvalidated per FR-7) is tuned, old Reports and the live Health Score will intentionally disagree on "what a 68 meant" for older data; this needs a one-line disclosure in the UI so it doesn't read as a bug.
- **Solo-developer schedule variance** — the approximately 20-week estimate may move as integration risks are discovered. Milestone acceptance, not a calendar deadline, controls release; weekly reviews should update forecasts without removing FR-1–FR-9 requirements.
- **Open questions:** timing for multi-user orgs; real rank-tracking integration (beyond what Search Console provides); whether Search Console's Performance report (clicks/impressions/position/CTR) should be folded into FR-15 as real organic-search analytics alongside GA4, so both sides of the Report reach "real data" together in Phase 2.

---

## Appendix A: Decision Log
- **Aug 17, 2026 (initial spec):** stack choices deferred to Claude — React frontend, LangGraph orchestration, cloud-agnostic Docker deployment, single consolidated spec document.
- **Aug 17, 2026 (4.3 update):** added starter outline + keyword usage counts to each content suggestion.
- **Aug 17, 2026 (Alphametic-parity discussion):** explored expanding scope to match a full-service AEO/SEO consultancy. A detailed edit proposal was presented but not applied at that point.
- **Aug 17, 2026 (zero-cost rework):** reworked the existing MVP/Phase2/Phase3 stack to be $0 — LLM switched to Groq/Gemini free tiers, storage consolidated into one free Postgres instance, free-tier hosting throughout.
- **Aug 17, 2026 (Alphametic-parity, $0-only):** added the consultancy-parity features from the earlier proposal, but only the ones achievable for $0 — technical SEO audit, local SEO/GBP, backlink visibility via Search Console (reframed from a paid backlink-index tool), competitor & entity benchmarking, and a guided/manual AI-citation checklist (explicitly scaled down from continuous automated cross-engine monitoring, which has no $0 path).
- **Aug 17, 2026 (north star):** added an explicit north-star statement to the Executive Summary.
- **Aug 26, 2026 (positioning & mottoes):** adopted three product mottoes and added a competitive-landscape review and monetization note.
- **Aug 26, 2026 (functionality revision):** added Health Score (new MVP feature) with a snapshot on every `AnalysisRun`; added `rationale`, `status`, `dismiss_reason`, and `stage` fields to `Suggestion`; moved the since-last-scan delta up from Phase 2 into the MVP; added Accept/Dismiss actions with a one-tap dismiss reason; added Progress Digest (Phase 2) and optional AI-drafted opening paragraphs (Phase 3).
- **Aug 26, 2026 (differentiation language sharpened):** reworded the differentiation framing to "strategy + execution workspace" rather than "SEO + AEO in one place."
- **Aug 26, 2026 (Flask swap):** switched the API server from FastAPI to Flask. No other component changes.
- **Aug 26, 2026 (one-pager):** produced an investor/employer-facing one-pager (`SEO_AEO_Platform_OnePager.pdf`) summarizing the problem, solution, personas, and differentiation from this spec.
- **Aug 26, 2026 (this revision — SRS restructure):** reorganized the entire document into a standard SRS structure (Introduction, Overall Description, System Features and Requirements, External Interface Requirements, Preliminary Schedule & Budget) at Sloane's request, so requirements and scope are unambiguous for both engineering use and external review. Added explicit requirement IDs (FR-/DR-/NFR-) for every functional, data, and non-functional requirement; added a new External Interface Requirements section (4) detailing every third-party API/software interface and its auth method; added a new Preliminary Schedule & Budget section (5) with a phased timeline sized to a solo part-time developer at ~5–10 hrs/week, and consolidated all prior risk notes under 5.3 since they now bear directly on schedule realism. No functional scope was added or removed in this pass — this is a structural and traceability revision of the same v1.5 content.
- **Sep 1, 2026 (FR-10 moved to Phase 2):** moved FR-10 (Local SEO & Google Business Profile) from the MVP (Phase 1) into Phase 2, per Sloane's request. Retagged the FR-10 section header; removed the local-listing-check step from FR-5.2's MVP agent orchestration order (it no longer runs during the MVP's one-click analysis); removed FR-10/GBP work from the Phase 1 schedule's Technical Audit milestone (5.2) and added FR-10 to the Phase 2 — Grow schedule description alongside FR-11 and FR-12. Requirement content and IDs (FR-10.1–FR-10.4) are unchanged.
- **Sep 1, 2026 (SEM feature added):** added SEM (paid search) strategy as a new MVP feature — FR-8 generates keyword, ad-group, placement, and negative-keyword suggestions with a heuristic Cost Tier (Low/Medium/High), built entirely from existing scrape/keyword/LLM infrastructure at $0 with no new account connection; real Google Ads Keyword Planner data (search volume, CPC bid ranges) added as a Phase 2 upgrade (FR-14) via per-user Google Ads OAuth, mirroring the FR-10/FR-11 pattern — deferred from MVP for onboarding-friction and schedule reasons, not cost (Google Ads API Basic Access is free). Extended the `Suggestion` entity with a `sem` category and related nullable fields (DR-6–DR-9) rather than introducing a new entity; added `Website.google_ads_connected` (DR-10); added a fifth SEM workspace tab (FR-1.3); added an SEM row to External Interfaces (4.3); added an SEM milestone to the Phase 1 schedule (5.2, ~2 weeks, extending the MVP estimate from ~16 to ~18 weeks) and FR-14 to the Phase 2 description; added SEM-specific risks to 5.3; the Health Score (FR-7) formula is intentionally left unchanged — SEM gets its own summary rather than being blended in.
- **Sep 1, 2026 (SEM elevated to core product identity):** per Sloane's request, reworked the document's framing so SEM reads as core to what Trellis is, not an appended feature. Retitled the document (title heading and version bumped to v2.1) from "A SEO / AEO Content Strategy Platform" to "A SEO / AEO / SEM Growth Strategy Platform"; rewrote the cover definition, the product mottoes, the 1.1 Purpose statement, and the North Star to name organic (SEO/AEO) and paid (SEM) strategy as coequal, not SEM as an extra; reordered and reworded the 1.3 Product Scope in-scope list so the SEM bullet sits with the core AEO/SEO bullets rather than tacked on last; added a "full-funnel growth product" framing paragraph to 2.1 Product Perspective; rewrote 2.2 Product Functions so SEM is woven into functions 2 and 5 instead of isolated as function 6; updated the 2.3.1 persona description ("no dedicated SEO/AEO specialist" → "no dedicated SEO/AEO/SEM specialist... unsure whether/where paid search would be worth the spend"). No requirement IDs, data model fields, or phase assignments changed in this pass — this is a framing/positioning revision on top of the FR-8/FR-14 content added earlier today, not a new functional scope change.
- **Sep 1, 2026 (mottoes revised):** replaced the three product mottoes per Sloane's request, so they communicate brand story rather than restate feature scope. Kept *"The AEO/SEO/SEM consultant you can't afford, minus the invoice"* unchanged (carries the access/affordability mission). Replaced *"Your SEO, AEO & SEM strategy — planned, prioritized, and done"* with *"Your full organic-and-paid search growth strategy — from insight to execution"* (states full-service scope and the follow-through differentiator together). Replaced *"From audit to published — one workspace, zero budget"* with *"No more spreadsheets. One workspace, start to published"* (echoes the Brand Brief's own "back in a spreadsheet" language and names the specific competitor gap — tools that stop at insight, and the spreadsheet-chaos Priya currently lives in). No functional scope changed.
- **Sep 1, 2026 (Reporting & Analytics added):** added Reporting & Analytics as a new MVP feature (FR-9) at Sloane's request, closing the gap where growth strategy was "all in one place" for planning but not for reporting — every AnalysisRun now automatically generates a saved Report snapshotting a predefined KPI set (Health Score, AEO completion, technical findings, content published, SEM acceptance/cost-tier mix, Organizer pipeline counts), with a Report History view and a Compare view (any two reports, full KPI deltas covering both month-over-month and last-analysis-vs-current use cases) — built entirely from data the spec already computes, at $0, with no new external dependency. Real Google Analytics 4 traffic/conversion/revenue data, plus a real-ROI figure once combined with FR-14's real ad spend, added as a Phase 2 upgrade (FR-15) via per-user GA4 OAuth, mirroring the FR-10/FR-11/FR-14 pattern of deferring OAuth-gated integrations past MVP for onboarding-friction and schedule reasons, not cost. Added new `Report` entity (DR-11, one-to-one with `AnalysisRun`) with GA4/real-spend/real-ROI fields populated once FR-15 connects (DR-12, DR-13); added `Website.ga4_connected` (DR-14); added a sixth Reports workspace tab (FR-1.3, now six views); added FR-9 to the FR-5.2 MVP agent orchestration order (Report generation runs right after Health Score computation); added a Reports & KPI Comparison milestone to the Phase 1 schedule (5.2, ~1.5–2 weeks, extending the MVP estimate from ~18 to ~19.5–20 weeks) and FR-15 to the Phase 2 description, sequenced after FR-14 since real ROI depends on both; added Reporting/GA4-specific risks to 5.3, including an open question on whether Search Console's Performance report should be folded into FR-15 alongside GA4 for real organic-search analytics. The Health Score (FR-7) formula and the existing FR-8/FR-14 SEM requirements are unchanged by this pass.
- **Sep 1, 2026 (Section 3 regrouped by phase, then reverted to numeric order):** first regrouped Section 3 into MVP / Phase 2 / Phase 3 subsections at Sloane's request, but under the IDs that existed at the time, that grouping still left MVP requirement IDs non-sequential within their own group (the MVP set skipped over several numbers that belonged to Phase 2/3 requirements), which Sloane flagged as still "scattered." Reverted to a single, strictly numeric FR-1 → FR-17 listing for Section 3 (removing the 3.1/3.2/3.3 phase subsections and their intro note), with each requirement's phase called out only in its own header/tag rather than by grouping — intended as the simplest, single predictable reading order, matching this document's numbering everywhere else (DR-1→DR-14, NFR-1→NFR-6 are already sequential). DR and NFR sections were unchanged and never affected by the phase-grouping attempt. This step turned out to be an intermediate one, superseded later the same day by an actual ID renumbering (see the final entry below) once it became clear that keeping the original IDs could never satisfy both "numeric order" and "grouped by phase" at once.

- **Sep 1, 2026 (FR IDs renumbered so MVP is 1–9, Phase 2 is 10–15, Phase 3 is 16–17):** per Sloane's explicit request, actually reassigned every requirement ID — not just its position on the page — so the numbering itself is contiguous within each phase and the whole list reads in strict ascending order with no gaps: **FR-1 through FR-9 are the complete MVP**, **FR-10 through FR-15 are Phase 2**, **FR-16 and FR-17 are Phase 3**. Within each phase group, requirements kept their original relative order (e.g. the MVP requirement that used to be first, `FR-1` Website Workspace, is still `FR-1`; the one that used to be `FR-16` Analysis Reports, the last-added MVP feature, is now `FR-9`, the last MVP number). Every reference to a renumbered ID was updated throughout this entire document in the same pass — every FR-N.M sub-requirement ID, every cross-reference in prose, the DR block, the NFR block, the External Interfaces table (4.3), the User Interfaces section (4.1), the Preliminary Schedule (5.2), the Risks list (5.3), and prior decision log entries above — so a given requirement is called by the same, single ID everywhere in this document. Sub-requirement suffixes (the `.1`, `.2`, etc. after the FR number) did not change, only the leading FR number. **Old ID → new ID mapping, for translating any other document that still cites the old numbers** (this includes, as of this writing, `claude/Trellis_Data_Model.md`'s prose notes, `trellis_sem_proposal.md`, `trellis_reporting_analytics_proposal.md`, and the one-pager docs — none of which have been repointed to the new IDs yet):

  | Old ID | New ID | Requirement | Phase |
  |---|---|---|---|
  | FR-1 | FR-1 | Website Workspace | MVP |
  | FR-2 | FR-2 | AEO Section | MVP |
  | FR-3 | FR-3 | SEO/Content Marketing Section | MVP |
  | FR-4 | FR-4 | Organizer | MVP |
  | FR-5 | FR-5 | AI Agent Subsystem | MVP |
  | FR-6 | FR-6 | Technical SEO Audit | MVP |
  | FR-11 | FR-7 | Health Score | MVP |
  | FR-14 | FR-8 | SEM Keyword & Ad Strategy | MVP |
  | FR-16 | FR-9 | Analysis Reports & KPI Comparison | MVP |
  | FR-7 | FR-10 | Local SEO & Google Business Profile | Phase 2 |
  | FR-8 | FR-11 | Backlink Visibility | Phase 2 |
  | FR-10 | FR-12 | Guided AI-Citation Checklist | Phase 2 |
  | FR-12 | FR-13 | Progress Digest | Phase 2 |
  | FR-15 | FR-14 | Google Ads Keyword Planner Integration | Phase 2 |
  | FR-17 | FR-15 | Real Analytics Enrichment via Google Analytics 4 | Phase 2 |
  | FR-9 | FR-16 | Competitor & Entity Benchmarking | Phase 3 |
  | FR-13 | FR-17 | AI-Drafted Opening Paragraph | Phase 3 |

  No requirement's text, phase assignment, or sub-requirement content changed in this pass — this is purely a relabeling, applied consistently everywhere the old label appeared. `claude/Trellis_Data_Model.md` should be updated to match on the next pass that touches it, since its notes section still names a few requirements by their old IDs.
- **Sep 2, 2026 (TF-IDF added for multi-document keyword analysis):** per Sloane's request, added TF-IDF (Term Frequency–Inverse Document Frequency) to the spec, scoped specifically to the situations where it's the right tool — anywhere a natural multi-document comparison already exists — rather than as a replacement for FR-3.1's single-page YAKE/RAKE keyword ranking, which it is not suited to (TF-IDF requires a comparison corpus; a single page has none, and using it site-wide would systematically down-rank the very terms that recur across a site's pages, i.e. its real core themes). Three additions, all implemented with the open-source `scikit-learn` `TfidfVectorizer` (no new cost or account dependency): **FR-3.5** (new) — a TF-IDF pass across a site's own scraped pages that filters out boilerplate (nav/footer/cookie-banner text repeated near-identically on every page) before FR-3.1's keyword ranking runs, so that ranking isn't diluted by non-distinctive template text. **FR-6.7** (new) — reuses the same page-vs-page TF-IDF pass to compute cosine similarity between pages and flag near-duplicate content, a signal FR-6.5's exact-repetition check can't catch on its own. **FR-16.3** (new, Phase 3) — reuses TF-IDF again across the analyzed site plus its 1–3 competitor sites (FR-16.1) to surface keywords distinctive to the analyzed site versus common across the whole competitive set, which is the comparison-across-documents use case TF-IDF is actually built for. Added a `TF-IDF` definition to 1.4; added a `scikit-learn (TfidfVectorizer)` row to the Software Interfaces table (4.3); updated FR-5.2's MVP agent orchestration order and the Phase 1 "Scrape + keyword pipeline" and "Technical audit" schedule line items (5.2) to note the new sub-requirements (no change to overall duration estimates, since this reuses the existing scrape/keyword milestone rather than adding a new one); added a TF-IDF-threshold-tuning risk to 5.3, in the same "unvalidated judgment call" category already used for Health Score weighting (FR-7) and the predefined-KPI set (FR-9.2). No existing requirement ID, DR field, or phase assignment was changed or renumbered in this pass.
- **Sep 2, 2026 (project doc cleanup + brand reconciliation):** per Sloane's request, reviewed all nine project docs for consistency. Fixed a stale date reference in 5.2 ("today" was still August 26, 2026; updated to September 2, 2026, the actual date of this pass — no schedule durations or milestone dates changed, only the anchor date label). Updated `Trellis_Brand_Brief.md` and `Trellis_Identity_Guide.md` to reflect the Sep 1, 2026 "SEM elevated to core product identity" decision above, which those two brand docs had not yet caught up to (their mission/positioning language still read SEO/AEO-only). Deleted four stale/duplicate docs from the `claude/` folder that were superseded by current root-level versions: `claude/SEO_AEO_Platform_Spec.md` (old v1.3, already self-labeled "Superseded" in its own header), `claude/SEO_AEO_Platform_OnePager.md` (pre-SEM pitch, superseded by `trellis_onepager_pitch.md`), `claude/Trellis_SEO_AEO_Platform_OnePagerPitch.md` (word-for-word duplicate of `trellis_onepager_pitch.md`), and `claude/Trellis_Brand_Brief.md` (older near-duplicate of the root Brand Brief). No requirement content, IDs, or phase assignments changed in this pass — this was a housekeeping and cross-document consistency pass only.
- **Sep 2, 2026 (identity guide artifact corrected):** the published Identity Guide artifact's "Logo & Trademark" section still described an earlier fence-posts-and-X logo concept in words, even though the actual embedded logo artwork had already been updated to the final open-grid-and-vine mark (confirmed by inspecting the artifact's own image data) — the descriptive text simply hadn't been updated to match. Corrected the artifact's mark description and clear-space wording to match both the actual artwork and this spec/the Identity Guide doc's own description. No change to this document's content; logged here since it's the kind of cross-artifact drift this decision log otherwise tracks.
- **Sep 2, 2026 (one-sentence summary added):** per Sloane's request, added an explicit plain-language "In one sentence" summary right after the cover definition and before "Built to cost $0," so the spec states the literal end-to-end workflow (scrape by URL → SEO/AEO/SEM insights and suggestions in place of a paid consultant → accept/reject → turn into tasks → track to completion → reporting) in one place, in addition to the more abstract North Star (1.1) and the three brand-voice mottoes. Order standardized to SEO/AEO/SEM to match this document's established ordering everywhere else (Sloane's own phrasing used SEO/SEM/AEO informally). No functional scope, requirement IDs, or phase assignments changed — this is a framing addition only.
- **Sep 2, 2026 (v2.2 — product promise and use-case communication):** replaced the long cover summary with separate outcome-focused Product Promise and How It Works statements; revised the North Star to promise consultancy-style guidance without claiming guaranteed equivalence to a human consultancy; added the defining product loop (Analyze → Recommend → Prioritize → Complete the work → Rescan → Measure progress) and a Promise and Boundaries table; reorganized the Section 2.2 summary around four user outcomes; separated the nonprofit primary persona from the agency persona; converted the end-user objectives into a scannable list; added five numbered core use cases with needs, triggers, system responses, visible outcomes, boundaries, and requirement traceability; and clarified that single-user MVP accounts can save multiple website workspaces while analyzing one site at a time. Renumbered the former Sections 2.4–2.7 to 2.5–2.8 and updated their cross-references. Also corrected FR-15.5's mistyped cross-reference from `17.3` to `15.3`. No feature, phase, requirement ID, or implementation scope changed in this revision.
- **Sep 2, 2026 (v2.3 — unified paid-and-organic messaging):** established **“Your paid and organic search growth strategy—all in one place”** as the primary positioning; revised the cover definition, Product Promise, How It Works, North Star, Product Perspective, and Product Functions around repeatable analyses that strengthen one evolving strategy, prioritized plan, Organizer, and reporting history; and clarified why the shared workflow retains separate organic Health Score and SEM summary signals. Synchronized this hierarchy and homepage/pitch opening across `README.md`, `trellis_onepager_pitch.md`, `Trellis_Brand_Brief.md`, and `Trellis_Identity_Guide.md`. No features, phases, requirement IDs, data fields, or implementation scope changed.
- **Sep 3, 2026 (v2.4 — problem-to-solution story refined):** sharpened the shared audience story across the spec, README, one-pager, Brand Brief, and Identity Guide: marketers own a complete SEO/AEO/SEM strategy; consultancy and audit support often stops at recommendations; execution and reporting remain fragmented; and Trellis closes that gap by connecting repeatable website analysis, prioritized consultancy-style guidance, accept/dismiss decisions, Kanban task execution, automatic Reports, the organic Health Score, and the separate SEM summary in one workspace. Replaced the README's ambiguous “submit a website URL once” language with repeatable analyze/rescan wording and synchronized the full “completion and measurement” promise in all recommended hero copy. No features, phases, requirement IDs, data fields, or implementation scope changed.
- **Sep 3, 2026 (v2.5 — product category and purpose clarified):** made the opening definition explicitly state what Trellis is (a website analysis and action-planning app), who it serves (solo marketers and small teams responsible for search), and what it does (connects paid and organic opportunities from repeat analysis through prioritized action, completion, and measurement). Added a brand rule that paid and organic search remain the focal point while AI, the garden metaphor, individual features, and the $0 build stack remain supporting details. Synchronized the definition across the README, one-page pitch, Brand Brief, and Identity Guide, and corrected the imagery guide's workflow from five steps to the approved six-step sequence by restoring Rescan. No features, phases, requirement IDs, data fields, or implementation scope changed.
- **Sep 3, 2026 (v2.6 — tech stack verified and simplified):** per Sloane's request, checked every "free tier" claim in the planned stack against current terms and corrected several that had gone stale or were mis-cited, then simplified the stack for a solo beginner developer. Changes: **(1)** removed LangGraph from the MVP — the pipeline (FR-5.2) is a fixed, sequential sequence, not a branching agent, so it's now built as plain Python functions; LangGraph is deferred to a future phase if genuinely branching agent behavior emerges. **(2)** Committed to a single backend host, **Render free tier**, and dropped Fly.io and Railway from the $0 hosting claim — Fly.io's own docs now require a credit card for all organizations, and Railway's post-trial free terms aren't clearly guaranteed card-free. **(3)** Committed to **Netlify** over Vercel for frontend hosting, since Vercel's Hobby plan is restricted to non-commercial use while Netlify's free plan isn't — relevant given 5.1's future monetization path. **(4)** Committed to **Supabase** over "Neon or Supabase," since it bundles Postgres, authentication, row-level security, and a dashboard in one free project — replacing hand-rolled JWT auth with Supabase Auth removes a common beginner security risk. Added **SQLAlchemy + Alembic** as the database access/migration layer and **Pydantic** as the concrete implementation of FR-5.5's schema validation, since the spec previously named neither. **(5)** Corrected the Groq free-tier figure from ~14,400 req/day to the accurate ~1,000 req/day (30 RPM) for the Llama 3.3 70B model FR-5.4 actually calls — the higher figure belongs to a different Groq safety-classifier model and was a citation error carried since the spec's first zero-cost rework. **(6)** Removed pytrends as an MVP dependency (FR-3.1, FR-8.1) since the library was archived in April 2025 and is no longer reliable, and Google's official Trends API remains in closed alpha; FR-3.1 keyword ranking and FR-8.1 Cost Tier now rely on frequency and TF-IDF distinctiveness alone for the MVP, with live trend data deferred to a future phase. **(7)** Made HTTPX + BeautifulSoup the default scraper in FR-5.2/4.3 rather than Playwright, since headless-browser scraping doesn't reliably fit Render's free-tier 512MB RAM if run on every analysis; Playwright is retained only as a fallback for JavaScript-rendered sites. **(8)** Removed Docker as an MVP deployment requirement (2.5), since Render and Netlify both build directly from a GitHub repo with no Dockerfile needed. **(9)** Added a resumable, status-polling design to FR-5.2/NFR-2 for long-running analyses, since Render's free tier has no background-worker product and a full analysis pipeline can run long enough to strain a single synchronous request; `AnalysisRun.status` (already modeled in the data model) now has an explicit role in FR-5.2. **(10)** Expanded NFR-1 (Security) to name concrete, free, open-source practices the spec hadn't previously called out given that Trellis accepts arbitrary user-submitted URLs: SSRF protection (URL validation against private/internal network addresses), `robots.txt` compliance, per-user rate limiting, HTML sanitization, and Supabase row-level security scoping data per user. **(11)** Added pytest, Vitest, and Playwright (end-to-end) as the named testing stack in the Phase 1 schedule (5.2), supporting NFR-4's accessibility requirement and general reliability, since the spec previously said "end-to-end testing" without naming tools. Updated 2.5, 2.6, 2.7, FR-3.1, FR-5.2, FR-8.1, FR-8's rationale, NFR-1, NFR-2, the Section 4.3 Software Interfaces table, the Phase 1 schedule (5.2), and 5.3 Risks to reflect all of the above. No requirement ID, phase assignment, or functional scope was added or removed — this is a stack-accuracy and architecture-simplification pass, consistent with the $0-build constraint (5.1) throughout.
- **Sep 4, 2026 (v2.7 — MVP deadline reset to Sep 14):** replaced the earlier ~19.5–20-week Phase 1 estimate with a fixed, deadline-driven September 4–14 build schedule so the complete MVP (FR-1 through FR-9) is deployed and demo-ready by Monday, September 14, 2026. Added dated daily milestones, an explicit acceptance-based definition of done, a daily control point, and a schedule-compression risk. Froze the sprint against new features and deferred Phase 2/3 date estimates until after MVP acceptance. No functional requirement, phase assignment, data field, or $0-stack commitment changed.
- **Sep 4, 2026 (v2.8 — testing moved to the start and throughout the sprint):** changed Phase 1 from a build-then-test sequence to a test-first workflow beginning September 4. Added the pytest/Vitest/Playwright harness, fixtures, mocks, test database, and CI commands to the foundation milestone; identified the unit, integration, and critical end-to-end coverage written before each feature milestone; and reframed September 13 as full regression/accessibility/deployment verification rather than the first testing day. Updated the daily definition of complete so a feature is not complete until its tests pass. No functional scope or deadline changed.
- **Sep 4, 2026 (v2.9 — implementation model and feature-complete schedule):** made the MVP data model implementation-ready around one `OrganizerItem` table for AEO, SEO/content, and SEM work, with `OrganizerItem.stage` as the single stored workflow state. Removed permanent page snapshots/raw HTML in favor of temporary processing plus affected-page URLs on suggestions and findings, and aligned user ownership with Supabase Auth. Replaced the September 14 deadline with an acceptance-driven approximately 20-week estimate: all FR-1 through FR-9 requirements remain required, and dates move rather than cutting feature completeness.
