**SEO / AEO CONTENT STRATEGY PLATFORM**

Software Requirements Specification (v2.0 — August 26, 2026)

*An agentic-AI web application that helps digital marketing managers plan, prioritize, and organize SEO and Answer Engine Optimization (AEO) content strategy — designed to replicate what a full-service AEO/SEO consultancy (e.g., Alphametic) delivers, entirely on free tiers and open-source software.*

> Full formatted version with diagrams (architecture, ER model, sequence flow, nav map) was delivered to Sloane as `SEO_AEO_Platform_Spec.docx`. This doc is the text content for reference/search inside the project. A companion investor/employer one-pager (`SEO_AEO_Platform_OnePager.pdf`) summarizes this spec for an outside audience.

**Built to cost $0:** every component — frontend, backend, database, LLM, and hosting — runs on free tiers or open-source software, no credit card required anywhere in the stack (see Section 5 for the budget breakdown and Section 2.5 for free-tier limits).

**Product mottoes (guiding the functionality below):**
- *"Your SEO & AEO strategy — planned, prioritized, and done."*
- *"The AEO/SEO consultant you can't afford, minus the invoice."*
- *"From audit to published — one workspace, zero budget."*

---

## 1. Introduction

### 1.1 Purpose
This document specifies the requirements for the SEO/AEO Content Strategy Platform, a three-tier web application for Digital Marketing Managers — especially at small businesses and nonprofits — to plan, prioritize, and track SEO and AEO content strategy. It is written to give Sloane (the sole developer), and any future contributor, reviewer, or evaluator (instructor, hiring manager, or investor), a single, unambiguous reference for what the system does, what it does not do, how it's built, and when each piece is expected to ship.

**North star:** give a digital marketing manager the same outcomes they'd get from hiring a full-service AEO/SEO consultancy (technical audits, keyword/content strategy, authority building, local visibility, and AI-citation tracking) — delivered continuously through software instead of a paid engagement.

### 1.2 Intended Audience
- **Sloane (developer/product owner):** primary reference for scope, priority, and acceptance criteria while building.
- **Instructors / technical reviewers:** evidence of requirements discipline and system design for a capstone or portfolio review.
- **Prospective employers:** demonstration of end-to-end product thinking (problem framing → requirements → architecture → delivery plan).
- **Prospective investors / early users:** a clear, non-technical picture of scope and timeline sits in Sections 1–2 and 5; Sections 3–4 are the technical detail beneath it.

### 1.3 Product Scope

**In scope (this document covers):**
- A single-user (MVP) web app for auditing one website at a time and managing its AEO/SEO/content strategy through to publication.
- An AI agent subsystem that scrapes a submitted URL and returns structured, prioritized, rationale-backed recommendations.
- A trackable Organizer (kanban) that carries every recommendation from suggestion to published content.
- Consultancy-style deliverables reworked to run at $0: technical SEO audit, local SEO/Google Business Profile checklist, backlink visibility (via Search Console), competitor benchmarking, and a manual-assisted AI-citation checklist.
- A single Health Score (0–100) summarizing a website's overall SEO/AEO progress and its trend over time.

**Explicitly out of scope (for the phases defined here):**
- Fully automated, continuous polling of ChatGPT/Perplexity/other AI engines for citation tracking — no free or ToS-compliant way to do this at volume exists (see 2.6 Assumptions and Dependencies, and 5.3 Risks). A manual-assisted substitute is in scope instead (FR-10).
- A comprehensive third-party backlink index (Ahrefs/Moz/SEMrush-style) — backlink visibility is scoped to what Google Search Console already reports (FR-8).
- Paid crawler/audit tools, paid LLM tiers, paid hosting, or any component that requires a credit card, for as long as this remains a $0-to-build project (see 5.1 Budget).
- Native mobile apps; this is a responsive web application only.
- Multi-language / non-English content analysis (English-language websites only, all phases covered here).

### 1.4 Definitions, Acronyms, and Abbreviations
- **SEO** — Search Engine Optimization; improving a site's visibility in traditional search engine results.
- **AEO** — Answer Engine Optimization; improving how a site is surfaced and cited by AI answer engines (ChatGPT, Perplexity, Google AI Overviews).
- **SERP** — Search Engine Results Page.
- **Schema markup** — structured data (schema.org vocabulary) embedded in a page's HTML to help search/answer engines understand its content.
- **GBP** — Google Business Profile (formerly Google My Business); the free local-business listing product.
- **NAP** — Name, Address, Phone number; consistency of these across the web is a local-SEO ranking signal.
- **RAG** — Retrieval-Augmented Generation; retrieving relevant reference text to ground an LLM's output.
- **Kanban** — a visual workflow board with columns representing stages of work (e.g., Backlog → In Production → In Review → Published).
- **Health Score** — this product's single 0–100 composite metric summarizing a website's overall SEO/AEO progress (FR-11).
- **LLM** — Large Language Model; here, Groq's hosted Llama 3.3 70B (primary) or Google Gemini free tier (backup).
- **MVP** — Minimum Viable Product; Phase 1 of this spec.

### 1.5 References
- `SEO_AEO_Platform_Spec.docx` — full formatted version with architecture diagram, ER diagram, sequence flow, and navigation map.
- `SEO_AEO_Platform_OnePager.pdf` — investor/employer-facing summary derived from this spec.
- Google PageSpeed Insights API documentation (technical audit, FR-6).
- Google Business Profile API documentation (local SEO, FR-7).
- Google Search Console API documentation (backlink visibility, FR-8).
- Groq API documentation and Google Gemini API documentation (LLM provider, FR-5).

---

## 2. Overall Description

### 2.1 Product Perspective
This is a new, standalone product — not an extension of an existing system. It is a three-tier web application (presentation / API+agent / data, detailed in 2.4) built entirely from free-tier and open-source components so it can be built and demonstrated at $0.

Most competing AEO tools (see 2.7) stop at insight: a citation score, a dashboard, a report. This product's differentiation is that it is a **strategy + execution workspace** — every recommendation follows a visible path from **audit → suggestion → task → published** and stays a living, trackable initiative rather than a one-time report. Combined with serving a persona (solo/nonprofit marketers, no team, no budget) that established competitors price above, this is the defensible edge — not the SEO+AEO combination itself, which is now table stakes in this market.

### 2.2 Product Functions (Summary)
At a high level, the system:
1. Lets a user add a website and run a one-click analysis of it.
2. Runs an AI agent that scrapes the site and returns structured, prioritized, rationale-backed recommendations across AEO, SEO/content, technical health, and local SEO.
3. Lets the user accept or dismiss each recommendation, and tracks accepted ones through a kanban pipeline to "Published."
4. Computes and displays a single Health Score per website, trended over time, plus a since-last-scan delta of what's new.
5. In later phases, extends the same pipeline to backlink visibility, competitor benchmarking, a guided AI-citation checklist, and proactive progress digests.

Full detail and acceptance-level requirements for each function are in Section 3.

### 2.3 User Classes and Characteristics

**2.3.1 Primary persona — "Priya."** Marketing Manager at a 12-person nonprofit (or a solo marketer serving several small-business clients). Owns marketing end-to-end; no dedicated SEO/AEO specialist or budget; currently tracks content in scattered spreadsheets; newly aware AI answer engines are becoming a traffic source. Technical comfort: low-to-moderate — needs plain-language rationale, not raw data.

**2.3.2 Secondary persona — small agency account manager.** Manages multiple client sites; needs a consistent, repeatable audit-and-plan workflow she can run the same way across every client. Technical comfort: moderate; values consistency and speed over depth of customization.

**2.3.3 End-user objectives:** understand what to fix or create for organic visibility; get a fast starting point from a URL (target: actionable plan in under 5 minutes); keep strategy and content pipeline in one place per site; track content and AEO tasks to completion; see overall progress at a glance and how it's changed since the last visit; revisit sites periodically for what's new.

### 2.4 Operating Environment
- **Client:** any modern desktop or mobile browser (responsive web app); no OS-specific requirement.
- **Frontend:** React + TypeScript (Vite), Tailwind + shadcn/ui, hosted on Vercel or Netlify's free tier.
- **Backend:** Python + Flask API server, hosted on Render/Fly.io/Railway free tier (sleeps after ~15 min idle — see 5.3 Risks).
- **AI agent orchestration:** LangGraph, invoked from the Flask API (inline for MVP; background job/queue as usage grows).
- **Database:** PostgreSQL on Neon or Supabase free tier (also stores raw scrape snapshots; pgvector added in Phase 2 for the best-practice knowledge base — same free instance, no separate vector DB).
- **Deployment:** Docker containers, GitHub Actions (free tier) for CI, portable to any cloud later.

Full software-interface detail (which external APIs each component talks to) is in Section 4.3.

### 2.5 Design and Implementation Constraints
- **Zero-cost constraint:** every component must run on a free tier or be open-source, with no credit card required anywhere in the stack, for as long as this is a personal/demo project (see 5.1 Budget for what changes if it becomes a paid product).
- **Free-tier rate limits govern design:** ~14,400 req/day on Groq, ~1,500 req/day on Gemini; request queuing and caching are required, not optional (NFR-3).
- **Security constraints:** JWT-based authentication, per-user data scoping, secrets management, and rate limiting to protect shared free-tier quota (NFR-1).
- **Accessibility constraint:** WCAG 2.1 AA compliance is a requirement, not a stretch goal (NFR-4).
- **Solo-developer constraint:** all schedule estimates in Section 5 assume one part-time developer (Sloane, ~5–10 hrs/week), which shapes both scope sequencing and the decision to lean on managed free-tier services rather than self-hosting infrastructure.

### 2.6 Assumptions and Dependencies
- Groq and Google Gemini continue to offer no-credit-card free tiers at roughly current request-volume limits for the life of this project; if either changes terms, FR-5 (AI Agent Subsystem) has a documented fallback (switch primary/backup roles, or add a third free provider).
- Google's PageSpeed Insights, Business Profile, and Search Console APIs remain free and available to individual developers; Search Console and GBP both require the *user* to verify ownership of their own site/listing, which is a real onboarding step, not just an API call (documented in 5.3 Risks).
- There is no free or ToS-compliant way to programmatically poll ChatGPT, Perplexity, or other AI engines at volume; FR-10 is deliberately designed as manual-assisted rather than fully automated for this reason.
- pytrends (unofficial Google Trends access) and the Playwright/BeautifulSoup scraping stack are assumed to remain reliable enough for a best-effort signal, not an SLA-backed one (documented in 5.3 Risks).
- Free hosting tiers (Render/Fly.io/Railway) are assumed adequate for MVP traffic; cold starts after idle are an accepted tradeoff, not a defect.

### 2.7 Competitive Landscape
The AEO tooling category is roughly two years old (Profound and Otterly.AI launched late 2023) and has grown crowded through 2026. Relevant categories:
- **AEO-native platforms** (Profound, Scrunch AI, Athena HQ, AirOps) — enterprise-priced ($2,000–$5,000+/month), built for brand-scale citation tracking, not this product's persona.
- **SEO incumbents with AEO bolted on** (Conductor, Semrush AI Toolkit, Surfer AI Tracker) — already combine SEO + AEO, which means "SEO and AEO in one place" alone is not a differentiator.
- **Self-serve entry-level AEO tools** (Otterly.AI, Peec AI, Geoptie) — closest price band, starting ~$79–199/month; still priced and positioned above this product's target persona (solo/nonprofit marketers, no team, no budget).

This product's differentiation is the combination of (a) $0-to-build / low-cost-to-run positioning aimed at an underserved persona, and (b) being a strategy + execution workspace, not an insights dashboard (see 2.1).

---

## 3. System Features and Requirements

Each feature below is tagged with its target phase (**MVP** = Phase 1, **P2** = Phase 2, **P3** = Phase 3) and stated as testable "shall" requirements with a requirement ID for traceability. Rationale is included where it clarifies *why* a requirement exists, since several of these trade off against the $0 constraint.

### FR-1 — Website Workspace (MVP)
Per-site home for the AEO plan, SEO/content plan, and Organizer.
- **FR-1.1** The system shall let a user add a website (by URL) and create a dedicated workspace for it.
- **FR-1.2** The workspace overview shall display: date of the last analysis run, top keywords, AEO checklist completion %, Organizer pipeline counts, current Health Score, and the Health Score's change since the last scan.
- **FR-1.3** The workspace shall provide navigation to four views: Overview, AEO, SEO/Content, and Organizer (see 4.1 for the navigation map).

### FR-2 — AEO Section (MVP)
Trackable checklist covering identity signals, schema.org structured data, direct-answer formatting, FAQ/Q&A coverage, and citation-worthiness signals.
- **FR-2.1** The system shall present AEO recommendations as a trackable checklist scoped to the analyzed site.
- **FR-2.2** Each AEO recommendation shall display a one-sentence rationale (why it matters for *this* site — see FR-5.3) and a priority badge.
- **FR-2.3** Each AEO recommendation shall display a stage tag (Suggested → In Plan → In Production → Published) that stays in sync with its corresponding Organizer task (see FR-4.3).
- **FR-2.4** The user shall be able to Accept or Dismiss each recommendation; dismissing shall prompt a one-tap reason (see DR-3).

### FR-3 — SEO/Content Marketing Section (MVP)
Word-frequency ("wordcloud") analysis, keyword candidates, and content-gap suggestions.
- **FR-3.1** The system shall analyze scraped site content for word frequency and rank keyword candidates by frequency and trend score.
- **FR-3.2** The system shall generate content-gap suggestions, each including a starter outline (section headings), target keyword(s), and a recommended usage count per keyword.
- **FR-3.3** Each content suggestion shall carry a rationale, priority, and stage tag (as FR-2.2/2.3).
- **FR-3.4** The user shall be able to add any suggestion to the content plan with one click, which creates a corresponding Organizer card (FR-4).

### FR-4 — Organizer (MVP)
Kanban board and checklist tracking every recommendation to completion.
- **FR-4.1** The system shall provide a kanban board with columns Backlog / In Production / In Review / Published for content items.
- **FR-4.2** The system shall provide a separate AEO task checklist and a combined SEO task view.
- **FR-4.3** Every card and checklist item's stage shall reflect, and be reflected by, the stage shown on its originating suggestion in the AEO/SEO sections (bidirectional sync), so a recommendation's full journey is visible from either screen.

### FR-5 — AI Agent Subsystem (MVP)
Python agent that turns a URL into structured recommendations.
- **FR-5.1** The system shall accept a URL and optional business context as input to the AI agent.
- **FR-5.2** The agent shall orchestrate, in order: scrape → word-frequency/keyword analysis → trend lookup → best-practice retrieval → technical audit (FR-6) → local-listing check (FR-7) → generate suggestions (single structured-output LLM call) → compute Health Score (FR-11) → persist results.
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
- *Rationale:* replicates a consultancy-grade technical audit with no paid crawler tool, per the $0 constraint (2.5).

### FR-7 — Local SEO & Google Business Profile (MVP)
- **FR-7.1** The system shall check NAP (Name/Address/Phone) consistency across the site.
- **FR-7.2** The system shall let the user connect their own free Google Business Profile listing and shall surface a GBP completeness checklist via the free GBP API.
- **FR-7.3** The system shall suggest LocalBusiness schema markup based on the site's business information.
- **FR-7.4** The system shall generate periodic review-generation reminder nudges.

### FR-8 — Backlink Visibility (Phase 2)
- **FR-8.1** The system shall source referring-domain data from the user's own Google Search Console "Links" report (requires the user to complete site verification).
- **FR-8.2** The system shall surface top linked pages and top anchor text from that report.
- **FR-8.3** The system shall compute and display new/lost referring domains between scans.
- **FR-8.4** The system shall label this feature to users as "backlinks Google already sees," not a comprehensive third-party index.

### FR-9 — Competitor & Entity Benchmarking (Phase 3)
- **FR-9.1** The system shall accept 1–3 competitor URLs and run the existing scrape + keyword + AEO pipeline against each for side-by-side comparison.
- **FR-9.2** The system shall generate entity/topic mapping suggestions feeding schema.org `about`/`sameAs` markup.

### FR-10 — Guided AI-Citation Checklist (Phase 2, manual-assisted)
- **FR-10.1** The system shall generate natural-language test questions relevant to the site's topic/business.
- **FR-10.2** The user shall be able to manually run those questions in free consumer AI apps and log whether the site was cited.
- **FR-10.3** The system shall track a "cited in X of Y checks" log over time per site.
- **FR-10.4** This log shall feed the Health Score (FR-11) once available.
- *Rationale:* continuous automated cross-engine citation monitoring has no free or ToS-compliant path at volume (2.6); this is the $0-compatible substitute, explicitly positioned to users as manual-assisted, not automated monitoring.

### FR-11 — Health Score (MVP)
- **FR-11.1** The system shall compute a single 0–100 Health Score per website as a weighted blend of: AEO checklist completion %, technical audit findings resolved %, keyword/content-gap coverage, and (once available) the AI-citation check-log rate (FR-10.3).
- **FR-11.2** A Health Score snapshot shall be stored on every `AnalysisRun` (DR-1).
- **FR-11.3** The Website Overview shall display both the current Health Score and its trend as a line chart across scans.
- *Open question (carried into 5.3 Risks):* the weighting formula is a product judgment call, not a technical one, and should be validated with real users before being treated as authoritative.

### FR-12 — Progress Digest (Phase 2)
- **FR-12.1** The system shall generate a weekly or monthly email/in-app summary per website (e.g., "Your Health Score moved from 61 → 68 this month, 2 tasks overdue, 3 new keyword opportunities").
- **FR-12.2** The digest shall be built entirely from data already computed for the Health Score (FR-11) and the since-last-scan delta (FR-1.2); no new paid dependency.

### FR-13 — AI-Drafted Opening Paragraph (Phase 3, optional)
- **FR-13.1** For each content suggestion (FR-3.2), the system shall optionally draft a short opening paragraph via the free-tier LLM, in addition to the existing outline.
- *Rationale:* kept optional/Phase 3 since full content generation isn't core to the MVP's differentiation and several funded competitors already offer it (2.7).

### DR — Data Requirements
Core (MVP) entities and relationships: **User** → **Website** → **AnalysisRun** → **Keyword**, **Suggestion**; **Website** also has **ContentItem** and **AEOTask**. New entities supporting FR-6 through FR-10: **TechnicalAuditFinding**, **LocalListingCheck**, **ReferringDomain**, **Competitor**, **CitationCheckLog**. Full ER diagram (MVP-core subset) is in the delivered `.docx`.

- **DR-1** `AnalysisRun.health_score` (int, 0–100) — snapshot of the Health Score (FR-11) at the time of the run, enabling the trend line on the Website Overview.
- **DR-2** `Suggestion.rationale` (text) — the one-sentence "why this matters" explanation (FR-5.3).
- **DR-3** `Suggestion.status` (enum: `pending` / `accepted` / `dismissed`) — an explicit acceptance state so acceptance-rate is measurable (2.3.3 success metrics).
- **DR-4** `Suggestion.dismiss_reason` (enum, nullable: `not_relevant` / `too_much_work` / `already_doing_this` / `other`) — captured only when dismissed; feeds Phase 2 suggestion-quality tuning.
- **DR-5** `Suggestion.stage` (enum: `suggested` / `in_plan` / `in_production` / `published`) — mirrors the linked `ContentItem.status` or `AEOTask.status` per FR-2.3/FR-4.3.

### NFR — Non-Functional Requirements
- **NFR-1 (Security):** JWT-based authentication; all data scoped per-user; secrets managed via environment/secret-store, never committed; rate limiting on all endpoints to protect shared free-tier quota.
- **NFR-2 (Scalability):** stateless API design; long-running agent work (FR-5) run as async jobs as usage grows beyond inline-request handling; caching of scrape/trend results to avoid redundant free-tier API calls.
- **NFR-3 (Cost management):** request budgets and a request queue in front of the LLM providers (2.5); caching wherever a re-computation would otherwise re-spend a free-tier quota unit.
- **NFR-4 (Accessibility):** WCAG 2.1 AA compliance across the frontend.
- **NFR-5 (Performance):** time-to-first-actionable-plan under 5 minutes from URL submission (2.3.3), acknowledging free-hosting cold starts (2.6) as a bounded exception.
- **NFR-6 (Reliability):** JSON-schema validation with automatic retry on every LLM structured-output call (FR-5.5), since free-tier models are more prone to schema drift than paid frontier models.

---

## 4. External Interface Requirements

### 4.1 User Interfaces
Shallow navigation: **Login → My Websites → Add Website wizard → Website Workspace** (Overview, AEO, SEO/Content, Organizer tabs).

- **Website Overview:** summary cards lead with the Health Score (large, prominent number) and its change since the last scan (e.g., "68 ▲ +7"), followed by since-last-scan delta callouts (e.g., "3 new keyword opportunities"), then last-analysis date, top keywords, AEO completion %, and pipeline counts (FR-1.2).
- **AEO / SEO sections:** each recommendation shows its rationale beneath the recommendation text, a priority badge, and a stage tag; an Accept/Dismiss action pair replaces a single "add" button, with dismissal opening a one-tap reason picker (FR-2.2–2.4, DR-4).
- **Organizer:** kanban board (FR-4.1) plus separate AEO/SEO task list views (FR-4.2).

**Core user flows covered by these screens:** add a website and run the first analysis; act on a content suggestion (creates an Organizer card, sets its stage to "In Plan"); accept or dismiss a suggestion (dismissing prompts a one-tap reason); work an AEO checklist item to completion.

### 4.2 Hardware Interfaces
None. This is a standard responsive web application with no dedicated hardware dependency; it runs on any device with a modern browser and an internet connection.

### 4.3 Software Interfaces
| Interface | Direction | Purpose | Auth | Notes |
|---|---|---|---|---|
| Groq API (Llama 3.3 70B) | Outbound | Primary LLM for suggestion generation (FR-5.4) | API key | ~14,400 req/day free tier |
| Google Gemini API (free tier) | Outbound | Backup LLM if Groq is unavailable/rate-limited (FR-5.4) | API key | ~1,500 req/day free tier; note its data-training clause (5.3 Risks) |
| Google PageSpeed Insights API | Outbound | Core Web Vitals / mobile score (FR-6.1) | API key (free) | No paid crawler needed |
| Google Business Profile API | Outbound | GBP completeness checklist (FR-7.2) | Per-user OAuth | User connects their own free listing |
| Google Search Console API | Outbound | Backlink/"Links" report (FR-8.1) | Per-user OAuth | Requires per-site verification by the user |
| pytrends (unofficial Google Trends) | Outbound | Keyword trend scoring (FR-3.1) | None (unofficial) | Best-effort signal, not SLA-backed |
| Playwright + BeautifulSoup | Internal | Site scraping for all analysis features | N/A | Self-hosted within the API tier |
| Transactional email API (Resend/Postmark free tier) | Outbound | Progress digest delivery (FR-12.1) | API key | Phase 2; stays within free send limits at this usage scale |
| PostgreSQL (Neon/Supabase) | Internal | Primary data store for all entities (DR-1–DR-5) | Connection credentials | Also stores raw scrape snapshots; pgvector added Phase 2 |

### 4.4 Communications Interfaces
- All client–server and server–third-party communication shall use HTTPS.
- The frontend and API server communicate via a REST API returning JSON.
- Authenticated requests use JWT bearer tokens (NFR-1).
- Per-user and shared free-tier rate limits are enforced server-side (NFR-1, NFR-3) to prevent one user's activity from exhausting the shared LLM/API quota.

---

## 5. Preliminary Schedule & Budget

### 5.1 Budget
The build-and-demo cost of this project is **$0**: every component in Sections 2.4 and 4.3 runs on a free tier or is open-source, with no credit card required anywhere in the stack. The only real cost is developer time (Sloane, part-time, ~5–10 hrs/week — see 5.2).

**What would cost money later:** if this becomes a paid product with real customers, the free-tier caps below become a cost-of-goods question that needs revisiting (not a Phase 1–3 concern):
- LLM requests/day beyond Groq's/Gemini's free limits (2.5).
- Database storage beyond the free Postgres tier's cap.
- Transactional email sends beyond the free tier (FR-12).
- Backend hosting beyond free-tier compute/uptime (cold starts, 2.6).

**Monetization note (future, non-binding):** a plausible path is self-serve subscription pricing below the competitive set in 2.7 — e.g., $15–40/month for the solo/nonprofit tier, higher for a Phase 2 agency tier — validated against real users before committing to a number.

### 5.2 Preliminary Schedule
**Assumption:** solo developer, part-time at roughly 5–10 hours/week (per Sloane's stated availability). All dates are estimates from today (August 26, 2026) and will shift with actual weekly velocity — this schedule should be revisited once Phase 1 is underway and a real hours-per-feature rate is known.

**Phase 1 — MVP (target: ~16 weeks, Sep 2026 → mid-Dec 2026)**

| Milestone | Covers | Est. duration |
|---|---|---|
| Setup & architecture | Repo scaffolding, DB schema (DR-1–DR-5), auth (NFR-1), CI/CD | 2 weeks |
| Scrape + keyword pipeline | FR-3.1, scraping stack, word-frequency/keyword ranking | 2 weeks |
| AI agent orchestration | FR-5.1–5.6, LangGraph pipeline, LLM integration + schema validation | 3 weeks |
| AEO / SEO / Organizer UI | FR-1 through FR-4, workspace + kanban + Accept/Dismiss flow | 3 weeks |
| Technical audit + Local SEO | FR-6, FR-7, PageSpeed + GBP API integrations | 2 weeks |
| Health Score + delta + polish | FR-11, since-last-scan delta, accessibility pass (NFR-4) | 2 weeks |
| Testing & deploy | End-to-end testing, free-tier hosting deploy, bug fixing | 2 weeks |

**Phase 2 — Grow (target: ~10 weeks, mid-Dec 2026 → early March 2027)**
Multi-user orgs, scheduled re-analysis, CMS integrations, Search Console/rank tracking, backlink visibility (FR-8), guided AI-citation checklist (FR-10), notifications, progress digest (FR-12).

**Phase 3 — Scale (target: ~10 weeks, early March 2027 → mid-May 2027)**
Multi-site benchmarking, competitor & entity benchmarking (FR-9), white-label agency reporting, browser extension, optional AI-drafted opening paragraphs (FR-13).

*Every phase remains $0 to build (5.1); schedule risk, not budget risk, is the main variable — see 5.3.*

### 5.3 Risks Affecting Schedule and Scope
- **Free-tier LLM rate limits** — mitigated with a request queue (NFR-3); a burst of testing/demo traffic could still hit daily caps.
- **Free-model JSON consistency** — mitigated with schema validation + one retry (FR-5.5, NFR-6); persistent drift could slow Phase 1's agent milestone.
- **Gemini's free-tier data-training clause** — a legal/privacy consideration for the backup LLM path (FR-5.4), not a blocker, but should be disclosed to end users eventually.
- **Free-hosting cold starts** — accepted tradeoff (2.6) that affects perceived performance (NFR-5), not correctness.
- **Scraping and pytrends reliability** — both are best-effort, unofficial, or subject to site-specific blocking; no SLA exists (2.6).
- **AEO best practices still evolving** — the best-practice knowledge base (FR-5.2) will need periodic manual updates until a RAG-backed refresh pipeline exists (Phase 2+).
- **Automated AI-citation tracking is deliberately excluded from $0 scope** — FR-10 is the manual substitute; true automation would be a future paid upgrade, not a schedule slip.
- **Backlink visibility is scoped to Search Console data only** (FR-8), not a full third-party index — an explicit scope tradeoff.
- **Search Console/GBP both require per-website user verification** — real onboarding friction (2.6) that could slow Phase 2 adoption testing even though the engineering is straightforward.
- **Health Score weighting is an unvalidated product judgment call** (FR-11) — should be tested with a few real users before Phase 2, or the "track your progress" promise (2.3.3) is undercut by a score that feels arbitrary.
- **Solo part-time developer capacity** — the single biggest schedule risk. The estimates in 5.2 assume steady weekly availability; any drop below ~5 hrs/week for more than a couple of weeks should trigger an explicit re-estimate rather than letting all downstream dates silently slip.
- **Open questions:** timing for multi-user orgs; real rank-tracking integration (beyond what Search Console provides).

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
