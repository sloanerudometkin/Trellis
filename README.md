<p align="center">
  <img src="Branding/assets/logo/PNGs/trellis-horizontal-green-logo-2C4E35-transparent.png" alt="Trellis logo" width="360">
</p>

<h3 align="center">Your paid and organic search growth strategy—all in one place.</h3>

<p align="center">
  One website analysis. One coordinated strategy. One prioritized plan, Organizer, and reporting system.
</p>

<p align="center">
  <img alt="status" src="https://img.shields.io/badge/status-spec%20%26%20design%20phase-A9791F">
  <img alt="cost" src="https://img.shields.io/badge/build%20cost-%240%20(free%20tier%20%2B%20open%20source)-3F6B4A">
  <img alt="license" src="https://img.shields.io/badge/license-unlicensed-1D2A20">
</p>

---

## What is Trellis?

**Trellis analyzes your website and turns its findings into one prioritized plan for improving organic visibility, appearing in AI answers, and making smarter paid-search decisions—then helps you carry the work through to completion and measure progress.**

*Give your content something to climb.*

A **trellis** is a framework that gives a climbing plant something to grow against — the plant supplies the growth, the trellis supplies the structure. Website content works the same way: most small teams aren't short on ambition, they're short on structure — a prioritized order to work in, a place to track what's done, and a way to see whether it's working.

You submit a website URL, then Trellis analyzes the site and turns that analysis into a single guided workflow:

**Analyze → Recommend → Prioritize → Complete the work → Rescan → Measure progress**

The result is not separate SEO, AEO, and advertising plans. It is one coordinated paid-and-organic search strategy: Trellis produces prioritized organic and cost-conscious paid-search recommendations from the same website analysis, turns accepted recommendations into trackable tasks in one Organizer, and automatically saves comparable Reports so you can see what changed.

## The Problem

Small-business and nonprofit marketers are often responsible for organic search, AI-answer visibility, content, and paid-search decisions all at once, with no specialist team and no specialist-tool budget. Today that usually means separate organic and paid tools, audits that point out problems but don't help finish the work, plans scattered across spreadsheets, and reporting rebuilt by hand. There's plenty of information, but no coordinated path from *"where should we grow?"* to *"what should I do next?"* to *"what did we accomplish, and is it working?"*

## How It Works

1. **Analyze** — submit a website URL once to uncover connected organic and paid-search opportunities.
2. **Recommend** — receive plain-language, site-specific recommendations across SEO, AEO, content, technical health, and SEM.
3. **Prioritize** — compare impact, rationale, and clearly labeled paid Cost Tiers, then accept or dismiss each recommendation.
4. **Complete** — move accepted organic and paid work through one Organizer from Backlog to Published or Live.
5. **Rescan** — analyze the site again to identify changes and new opportunities.
6. **Measure progress** — follow the organic Health Score, review the separate SEM summary, and compare saved Reports in one reporting system.

## Who It's For

- **Priya, a one-person marketing department** *(primary)* — a nonprofit marketing manager or solo agency marketer who owns SEO, AEO, and paid search alone, without a specialist on the team. Needs plain-language direction, not raw data.
- **Small agency account managers** *(secondary)* — need the same audit-to-action workflow repeated consistently across several client websites.

## Key Features (MVP)

- **Website workspaces** — save and revisit multiple sites; analyze one at a time.
- **Unified site analysis** — one submitted URL produces structured, rationale-backed opportunities across organic SEO, AEO, content, technical health, and paid search.
- **Cost-conscious paid-search strategy** — SEM keyword, ad-group, landing-page, targeting, and negative-keyword guidance with clearly labeled Cost Tier estimates, without launching or spending on a real campaign.
- **Organizer (kanban)** — every recommendation, organic or paid, moves visibly from Suggested through to Published.
- **Health Score** — a single 0–100 score summarizing organic SEO/AEO progress, plus the change since your last scan.
- **Automatic Reports** — every analysis run saves a comparable snapshot, so progress is visible without a spreadsheet.

See [`trellis_onepager_pitch.md`](trellis_onepager_pitch.md) for the full pitch and [`trellis_spec.md`](trellis_spec.md) for the complete requirements.

## Tech Stack (planned)

| Layer | Choice |
|---|---|
| Frontend | React + TypeScript |
| Backend | Python / Flask |
| AI agents | LangGraph, running on Groq / Gemini |
| Database | PostgreSQL |

Every layer runs on a free tier or open-source software — no credit card required anywhere in the MVP build. (This describes the build-and-demo stack for this project, not a permanent pricing promise.)

## Project Status

Trellis is currently in the **specification and design phase** — the requirements, data model, and brand identity are written, but application code hasn't started yet. This repository is the source of truth while that's being built:

| Path | What's in it |
|---|---|
| [`trellis_spec.md`](trellis_spec.md) | The full Software Requirements Specification (SRS) — scope, features, and acceptance criteria. |
| [`trellis_onepager_pitch.md`](trellis_onepager_pitch.md) | The one-page pitch: problem, promise, and roadmap at a glance. |
| [`architecture and data model/`](architecture%20and%20data%20model) | The database/data model design (`Trellis_Data_Model.md`, plus a rendered PDF). |
| [`Branding/`](Branding) | The brand brief, identity guide, design-system tokens, and logo/favicon assets. |
| [`new feature proposals/`](new%20feature%20proposals) | Design-history proposals that informed the current SEM strategy and reporting requirements. |

## Roadmap

- **MVP** — website workspaces; SEO/AEO/content and technical analysis; accept/dismiss decisions; the Organizer; the organic Health Score; heuristic SEM strategy; automatic Reports and comparisons.
- **Phase 2** — local SEO / Google Business Profile; backlink visibility via Google Search Console; guided manual AI-citation checks; real Google Ads keyword/CPC data; GA4-enriched Reports.
- **Phase 3** — competitor and entity benchmarking, plus optional AI-drafted content openings.

## What Trellis Doesn't Promise

Trellis gives consultancy-style guidance — it doesn't guarantee rankings, traffic, AI citations, or revenue, and it never changes your website, launches campaigns, or spends money on your behalf.

## Author

Built by **Sloane Rudometkin** as a data engineering / software capstone and portfolio project.
Contact: [sloanerudometkin@gmail.com](mailto:sloanerudometkin@gmail.com)

## License

No license has been applied yet, so all rights are reserved by default. If you'd like this open-sourced under something like MIT, that can be added.
