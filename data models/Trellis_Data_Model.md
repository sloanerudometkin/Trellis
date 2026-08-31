## Trellis Data Model (v1 — Aug 26, 2026, diagram rebuilt Aug 31, 2026)

Companion to `SEO_AEO_Platform_Spec5.md` §DR (Data Requirements). Full visual UML class diagram, styled per the Trellis Identity Guide, is published as an artifact: **[Trellis Data Model — full diagram, relationships & glossary](https://claude.ai/code/artifact/3da52f6c-f659-4ef0-9254-5af20e31f871)**. A trimmed, diagram-only version for dropping into slides: **[Trellis Schema Diagram](https://claude.ai/code/artifact/b49e0dd9-9a3d-4379-8a81-c8552ce99dcb)**.

## Summary
12 entities total — **9 MVP, 2 Phase 2, 1 Phase 3**. Two hub entities:
- **Website** — everything a user tracks long-term for one site (content pipeline, AEO tasks, competitors, referring domains, citation checks).
- **AnalysisRun** — everything one scan produces (keywords, suggestions, audit findings), timestamped so the Health Score can trend over time.

## Entities

| Entity | Phase | Parent | Key fields |
|---|---|---|---|
| User | MVP | — | id (PK), email, password_hash, created_at |
| Website | MVP | User | id (PK), user_id (FK), url, business_context, gbp_connected, search_console_connected, created_at |
| AnalysisRun | MVP | Website | id (PK), website_id (FK), run_at, health_score (DR-1), status |
| Keyword | MVP | AnalysisRun | id (PK), analysis_run_id (FK), term, frequency, trend_score |
| Suggestion | MVP | AnalysisRun | id (PK), analysis_run_id (FK), category, title, rationale (DR-2), priority, status (DR-3), dismiss_reason (DR-4), stage (DR-5), content_item_id (FK, null), aeo_task_id (FK, null) |
| ContentItem | MVP | Website | id (PK), website_id (FK), title, status, created_at |
| AEOTask | MVP | Website | id (PK), website_id (FK), title, status, created_at |
| TechnicalAuditFinding | MVP | AnalysisRun | id (PK), analysis_run_id (FK), category, description, severity, resolved |
| LocalListingCheck | MVP | AnalysisRun | id (PK), analysis_run_id (FK), check_type, description, resolved |
| ReferringDomain | Phase 2 | Website | id (PK), website_id (FK), domain, top_linked_page, top_anchor_text, status |
| CitationCheckLog | Phase 2 | Website | id (PK), website_id (FK), question, cited, checked_at |
| Competitor | Phase 3 | Website | id (PK), website_id (FK), url, added_at |

## Relationships
- User 1—* Website (owns)
- Website 1—* AnalysisRun (has)
- Website 1—* ContentItem, AEOTask, ReferringDomain, CitationCheckLog, Competitor (tracks/monitors/benchmarks)
- AnalysisRun 1—* Keyword, Suggestion, TechnicalAuditFinding, LocalListingCheck (produces/generates)
- Suggestion 0..1—1 ContentItem (creates, on accept — FR-3.4)
- Suggestion 0..1—1 AEOTask (creates, on accept — FR-2.3/4.3)

## Notes / open items carried from the spec
- Suggestion is the most-connected entity — it's the pivot between "what the AI found" and "what the user is doing about it."
- Bidirectional stage sync (FR-4.3) between Suggestion.stage and ContentItem.status / AEOTask.status is a business-logic rule, not a foreign-key constraint — needs to be enforced in the API layer (e.g., updating one triggers an update to the other).
- Health Score weighting formula (FR-11.1) is still an open product question — doesn't change the schema, only how `AnalysisRun.health_score` gets computed.
- User model is single-user for MVP but already scoped by `user_id` throughout so multi-user orgs (a Phase 2 open question) don't require a schema rewrite.

## Diagram history
- **Aug 26, 2026:** first published ER diagram artifact (superseded, link no longer maintained here).
- **Aug 31, 2026:** diagram rebuilt as a full UML class diagram (PK/FK markers, per-field data types, phase-grouped color coding, cardinality labels, plus a relationship reference table and a beginner glossary) for presenting to instructors. Trellis icon mark added to both artifacts' headers, pulled from `Branding/New final logo/` in the project repo.

## Next step
UX/UI wireframes for the Website Workspace (Overview, AEO, SEO/Content, Organizer tabs — see spec §4.1) can now be built against this schema.
