# Proposed Spec Addition: SEM (Paid Search) Strategy Feature

*Drafted for review against `Trellis_SEO_AEO_Platform_Spec5_1.md` (v2.0, Aug 26, 2026). Nothing in the actual spec has been changed yet — this is the proposal. Once you sign off, I'll fold the approved parts into the real spec doc and update the decision log.*

---

## 0. Quick concepts, since this is new territory

A few terms this feature introduces, in plain language, before the requirements use them:

- **SEM (Search Engine Marketing)** — paid search: buying ads that appear on Google's results page, as opposed to SEO/AEO which is about earning placement for free ("organic").
- **PPC (Pay-Per-Click)** — the pricing model behind most SEM: you don't pay for an ad to be shown, only when someone clicks it.
- **CPC (Cost Per Click)** — what one click on an ad costs. This varies enormously by keyword — a competitive term like "insurance" can cost $50+/click, while a specific long-tail term might cost $1-2.
- **Keyword Planner** — Google's own free tool (and the API behind it) for looking up search volume and CPC bid ranges for a keyword before you buy it.
- **Quality Score** — Google's 1-10 rating of how relevant your ad, keyword, and landing page are to each other. It directly sets your CPC: a 10/10 score can cost ~50% less per click than a 5/10 score for the *same* keyword, and a 1/10 score can cost 4x more. This is the mechanical reason "cost-efficient SEM" is really about relevance, not just picking cheap words.
- **Long-tail keyword** — a longer, more specific search phrase ("women's waterproof hiking boots size 8" vs. "boots"). Long-tail terms almost always have lower CPC and lower competition than short "head" terms, because fewer advertisers bid on them — and the traffic that does convert tends to convert better, because the searcher is more specific about what they want.
- **Negative keyword** — a term you tell Google *not* to show your ad for. E.g., a paid boot retailer might add "free" and "repair" as negatives so they don't pay for clicks from people who don't want to buy.
- **Ad group** — a small cluster of closely related keywords that share one ad. Tightly-themed ad groups (few keywords, all very related) get better Quality Scores than loosely-themed ones.

---

## 1. Why this fits Trellis, and the one real trade-off

Your ask maps cleanly onto the pattern the spec already uses for AEO and SEO/Content: analyze the site → generate prioritized, rationale-backed suggestions → let the user Accept/Dismiss → track accepted ones through the Organizer. SEM slots in as a fourth suggestion category alongside AEO and SEO/Content.

**The one real design decision:** getting *real* CPC and search-volume numbers requires Google's Keyword Planner data, which only comes through the Google Ads API — and using it means the user connects their own Google Ads account via OAuth (creating that account is free, no ad spend required). That's the same shape of friction as the Google Business Profile connection in FR-7, which you moved from MVP into Phase 2 earlier today for exactly that reason.

Both paths are $0 — the Google Ads API's "Basic Access" tier (which includes keyword research) has no cost, just a one-time ~5-business-day review of Trellis itself as an app (not something each user has to do). So the constraint here isn't budget, it's **onboarding friction and schedule**, matching FR-7's precedent.

**What I'm proposing (recommended, and what I've drafted below):**
- **FR-14 (MVP):** A full SEM strategy feature — which keywords, where to advertise, starter ad groups, negative keywords, landing-page matches — built entirely from data Trellis already collects (the FR-3 keyword/word-frequency pipeline, pytrends, the LLM). Cost is shown as a heuristic *Cost Tier* (Low/Medium/High), not a real dollar figure, and is clearly labeled as an estimate.
- **FR-15 (Phase 2):** The user optionally connects a free Google Ads account, and Trellis swaps the heuristic Cost Tier for real search volume and CPC bid ranges from Keyword Planner, and adds a cost-efficiency ranking and a rough monthly-spend estimate.

This means SEM genuinely ships in the MVP, as you asked — full guidance on what to advertise, where, and how to keep it cheap — just with real Google dollar figures arriving in Phase 2 once the account-linking step is worth building. If you'd rather pull the Google Ads connection into MVP anyway (it's still $0, just adds an OAuth flow and a dependency on Google's review turnaround to the Phase 1 timeline), say so and I'll rewrite this as one FR instead of two.

---

## 2. Proposed changes to Section 1 (Introduction)

**1.3 Product Scope — add to "In scope":**
> - A cost-conscious SEM (paid search) strategy layer: keyword and ad-group suggestions, placement/targeting guidance, and a Cost Tier estimate per keyword, generated from the same site analysis used for SEO/AEO — with an optional (Phase 2) upgrade to real Google Ads Keyword Planner data via the user's own free Google Ads account.

**1.4 Definitions, Acronyms, and Abbreviations — add:**
> - **SEM** — Search Engine Marketing; paid placement in search results, priced per click (PPC), as distinct from the unpaid ("organic") SEO/AEO placement this product otherwise focuses on.
> - **PPC** — Pay-Per-Click; the pricing model where an advertiser is charged only when their ad is clicked.
> - **CPC** — Cost Per Click; what one ad click costs, set by keyword competitiveness and Quality Score.
> - **Quality Score** — Google's 1–10 relevance rating (keyword ↔ ad ↔ landing page) that directly sets CPC.
> - **Keyword Planner** — Google's free keyword research tool; its API (Google Ads API, Basic Access tier) is the data source for FR-15's real search-volume/CPC figures.
> - **Long-tail keyword** — a longer, more specific search phrase; generally lower CPC and lower competition than a short "head" term.
> - **Negative keyword** — a term explicitly excluded from triggering an ad, to avoid paying for irrelevant clicks.

---

## 3. Proposed changes to Section 2 (Overall Description)

**2.2 Product Functions (Summary) — add:**
> 6. Generates a cost-conscious SEM (paid search) plan alongside the organic AEO/SEO plan: which keywords to buy, where ads should be targeted, and a cost-efficiency estimate per keyword — so a beginner marketer gets one coherent growth strategy across both organic and paid channels instead of needing a second tool.

**2.3.3 End-user objectives — add:**
> understand not just what to fix organically, but what would be worth paying for and roughly what it would cost, without needing to already know how Google Ads auctions work.

**2.7 Competitive Landscape — add a closing line:**
> None of the tools in this landscape — including the AEO-native and self-serve entry-level categories — bundle a cost-conscious SEM/paid-search plan into the same $0 workspace as the organic strategy. For a solo or nonprofit marketer weighing "should I ever pay for ads, and which ones," that's currently a third tool and a third bill. Folding it in here (FR-14/FR-15) extends the same differentiation logic as 2.1: not a new category, but full-stack coverage at a price point nobody else in this landscape offers.

---

## 4. New requirement: FR-14 — SEM Keyword & Ad Strategy (MVP)

*Generates a cost-conscious paid-search plan using only data the system already collects — no new account connection, no external cost, no waiting on any third-party review.*

- **FR-14.1** The system shall generate SEM keyword candidates from the same keyword/content analysis already produced for organic SEO (FR-3.1), each tagged with a relative **Cost Tier** (Low / Medium / High) inferred from: keyword length (long-tail vs. short "head" term), presence of commercial-intent modifiers (e.g., "buy," "near me," "best," "pricing," "vs"), and pytrends interest-over-time volatility as a rough competition proxy.
- **FR-14.2** The system shall prioritize long-tail, high-commercial-intent, lower-Cost-Tier keywords over expensive head terms in its default suggestion ranking, consistent with the cost-efficiency goal.
- **FR-14.3** For each higher-Cost-Tier keyword candidate, the system shall suggest 2–4 long-tail sibling variants targeting similar intent at a presumed lower Cost Tier, so the user always sees a cheaper alternative next to the expensive option, not just the expensive option alone.
- **FR-14.4** The system shall recommend, in plain language, where each ad should be targeted: Search vs. Display network, relevant audience/topic targeting, and — for a local business (detected from FR-1's `business_context`) — a suggested geographic radius.
- **FR-14.5** The system shall group keyword candidates into 2–4 tightly-themed starter **ad groups**, each with a suggested headline/description angle, and explain in the rationale that tight theming is what keeps Quality Score up and CPC down (not a separate, unexplained best practice).
- **FR-14.6** The system shall match each ad group to the existing scraped page (or an FR-3.2 content-gap suggestion, if no matching page exists yet) it should link to, so ad-to-landing-page relevance — a direct Quality Score input — is addressed by default rather than left to the user to figure out.
- **FR-14.7** The system shall suggest a starter negative-keyword list per ad group, drawn from off-topic terms surfaced by the existing word-frequency analysis (FR-3.1) and common irrelevant-intent modifiers (e.g., "free," "jobs," "DIY," "how to" — where these don't match the site's actual offering), to reduce wasted spend from day one.
- **FR-14.8** Each SEM suggestion shall carry the same rationale, priority badge, stage tag, and Accept/Dismiss pattern as AEO/SEO suggestions (FR-2.2–2.4, FR-5.3); accepting one shall create a corresponding Organizer card (FR-4), so an SEM item moves through the same Suggested → In Plan → In Production → Published pipeline as everything else.
- **FR-14.9** The system shall clearly and persistently label Cost Tier as a **heuristic estimate**, not a guaranteed or real Google Ads bid price, everywhere it's displayed, until FR-15 is connected.
- **FR-14.10** The system shall NOT create, launch, or manage live ad campaigns, and shall NOT move or spend the user's money in any way — FR-14 produces a strategy the user manually implements in their own Google Ads account, exactly as FR-8 reads Search Console data without ever modifying the user's site. This boundary matters both for scope (a real ad-buying/bidding engine is a much larger, higher-stakes build) and so the product is never mistaken for a financial tool making spending decisions on the user's behalf.

*Rationale:* every sub-requirement here reuses infrastructure the spec already commits to (FR-3's scraping/keyword pipeline, FR-5's LLM call, pytrends) — no new external dependency, so this is buildable within the $0 constraint and doesn't introduce new schedule risk from third-party account linking.

---

## 5. New requirement: FR-15 — Google Ads Keyword Planner Integration (Phase 2)

*Upgrades FR-14's heuristic Cost Tier to real search-volume and CPC data, once the user opts in — same $0-but-per-user-OAuth shape as FR-7 (Google Business Profile) and FR-8 (Search Console).*

- **FR-15.1** The system shall let the user connect their own Google Ads account via OAuth. Creating a Google Ads account is free and does not require an active or funded campaign.
- **FR-15.2** Once connected, the system shall call the Google Ads API's Keyword Planner service (`KeywordPlanIdeaService`, available under the free Basic Access tier) to retrieve average monthly search volume and a low/high CPC bid range for each FR-14 keyword candidate, replacing the heuristic Cost Tier with these real figures.
- **FR-15.3** The system shall re-rank SEM keyword suggestions by an explicit cost-efficiency score (estimated search volume ÷ estimated CPC), surfacing the best "traffic per dollar" opportunities first, once real data is available.
- **FR-15.4** The system shall display a rough estimated monthly ad-spend for the user's currently-accepted SEM keyword set (sum of low-end CPC × an assumed click volume), clearly labeled as an estimate for planning purposes, not a bill or a spend commitment — Trellis never touches the user's actual ad budget (per FR-14.10).
- **Dependency note:** Trellis's own Google Ads API Basic Access approval is a one-time, free review of the app itself (Google's stated turnaround is about 5 business days) — this is a *developer*-side step (Sloane requesting API access for Trellis), separate from each user's own OAuth connection, and should be requested early in Phase 2 planning since FR-15 can't ship without it. It does not block FR-14 or any of the rest of the MVP.

---

## 6. Data model changes

Rather than a whole new entity, I'd extend the existing `Suggestion` entity (already the "most-connected entity" per the data model doc) with a `sem` category and a handful of nullable fields only populated for that category — this keeps SEM suggestions on the same Accept/Dismiss/stage/Organizer machinery as everything else instead of building a parallel system.

**Proposed additions to `Suggestion` (claude/Trellis_Data_Model.md):**
| Field | Type | Notes |
|---|---|---|
| `category` | enum | add `sem` alongside existing `aeo` / `seo_content` values |
| `cost_tier` | enum, nullable (`low`/`medium`/`high`) | heuristic estimate, FR-14.1 |
| `cpc_low`, `cpc_high` | decimal, nullable | populated once FR-15 is connected |
| `search_volume` | int, nullable | populated once FR-15 is connected |
| `ad_group_label` | text, nullable | which starter ad group (FR-14.5) this belongs to |
| `landing_page_match` | text, nullable | matched page URL or content-gap reference (FR-14.6) |
| `targeting_notes` | text, nullable | placement/targeting guidance (FR-14.4) |
| `negative_keywords` | text[], nullable | starter negative list (FR-14.7) |

**New field on `Website`:** `google_ads_connected` (boolean) — mirrors the existing `gbp_connected` / `search_console_connected` pattern, gates FR-15.

---

## 7. UI / navigation changes

**FR-1.3** — add a fifth workspace tab: **Overview, AEO, SEO/Content, SEM, Organizer.**

**4.1 User Interfaces** — add:
> **SEM section:** mirrors the AEO/SEO layout — each suggestion shows its Cost Tier badge (Low/Medium/High, or real CPC range once FR-15 is connected), rationale, priority, and stage tag, grouped visually by starter ad group (FR-14.5). A small "cheaper alternative" chip surfaces the FR-14.3 long-tail sibling next to any Medium/High-tier suggestion. Once FR-15 is connected, an estimated-monthly-spend summary appears at the top of the section (FR-15.4).

A note on brand voice, since the Identity Guide's tone pillars (Direct / Plain / Unhurried) should carry through here too — sample microcopy in this voice:
> - "This one's popular but pricey — here's a cheaper way to reach the same people."
> - "We matched this ad to your Services page — that match is what keeps your cost per click down."
> - "Estimate only — connect your Google Ads account for real numbers."

---

## 8. External interfaces (4.3) — new row

| Interface | Direction | Purpose | Auth | Notes |
|---|---|---|---|---|
| Google Ads API (Basic Access) | Outbound | Keyword Planner search volume + CPC bid ranges (FR-15.2) | Per-user OAuth + Trellis developer token | Free tier; Basic Access supports 15,000 ops/day; requires a one-time ~5-business-day review of Trellis itself |

---

## 9. Schedule impact (5.2)

- **Phase 1 (MVP):** add an **"SEM strategy engine"** milestone (~2 weeks) — heuristic Cost Tier logic, ad-group/negative-keyword generation, SEM tab UI. This is new scope on top of the existing ~16-week estimate, so the honest framing is either the MVP timeline extends by ~2 weeks, or FR-14 trades priority against something else already in Phase 1 — worth deciding explicitly rather than assuming it's free to add.
- **Phase 2 (Grow):** add FR-15 (Google Ads Keyword Planner integration) to the existing Phase 2 description, alongside FR-7, FR-8, FR-10.

---

## 10. Risks (5.3) — additions

- **Heuristic Cost Tier accuracy** — FR-14's Low/Medium/High estimate is a proxy, not real auction data; needs the same persistent-disclosure treatment as Gemini's data-training clause (i.e., don't let users mistake it for a real quote) — this is FR-14.9.
- **Google Ads API review turnaround** — the one-time Basic Access review (~5 business days) for Trellis itself should be requested at the start of Phase 2 planning, not discovered as a blocker mid-sprint.
- **Google Ads account creation friction** — even though free, asking a nonprofit/solo marketer to create a Google Ads account is a real onboarding step (same category of risk already logged for GBP/Search Console in 5.3).

---

## 11. Proposed decision log entry (Appendix A)

> **Sep 1, 2026 (SEM feature proposal):** added SEM (paid search) strategy as a new MVP feature (FR-14) — keyword/ad-group/negative-keyword suggestions, placement guidance, and a heuristic Cost Tier, built entirely from existing scrape/keyword/LLM infrastructure at $0 with no new account connection. Real Google Ads Keyword Planner data (search volume, CPC bid ranges) proposed as a Phase 2 upgrade (FR-15) via per-user Google Ads OAuth, mirroring the FR-7/FR-8 pattern — deferred from MVP for onboarding-friction and schedule reasons, not cost (Google Ads API Basic Access is free). Added `sem` category and related nullable fields to the `Suggestion` entity rather than a new entity; added a fifth SEM workspace tab (FR-1.3).

---

## 12. Open questions for you

1. **Does the FR-14/FR-15 (MVP heuristic / Phase 2 real-data) split work, or do you want the Google Ads connection pulled into MVP** since it's also $0 — just with the added OAuth flow and API-review dependency?
2. **Should SEM feed into the single Health Score (FR-11),** or stay a separate metric? My instinct: keep Health Score focused on organic SEO/AEO (its current formula), and give SEM its own small summary (e.g., "X keywords in your plan, estimated $Y-Z/mo range") rather than diluting one score with two very different disciplines — but this is a product-feel call, not a technical one, same as the existing Health Score weighting is already flagged as unvalidated.
3. **Any preference on the ad-group count (I proposed 2–4 starter groups)** or is that a reasonable default to build against?

Once you weigh in, I'll write the approved version into `Trellis_SEO_AEO_Platform_Spec5_1.md` and `claude/Trellis_Data_Model.md` directly and update the decision log.
