# Trellis MVP Kanban and Development Workflow Plan

**Delivery policy:** Feature-complete, acceptance-driven MVP; dates may move rather than cutting FR-1–FR-9
**Planning estimate:** Approximately 20 weeks for one part-time developer; review after every milestone
**Source of truth:** `trellis_spec.md` v2.9
**MVP scope:** FR-1 through FR-9, DR-1 through DR-14 as they support the MVP, and NFR-1 through NFR-6  
**Team assumption:** one developer, one active implementation branch at a time  
**Release path:** feature branch → `dev` → `main`

## 1. What this plan is for

This document translates the Trellis specification into work that can be entered into a GitHub Project Kanban board. It provides:

- Four delivery milestones and their dates.
- Parent issues that represent complete, testable outcomes.
- Sub-issues that break each parent issue into small tasks.
- Requirement and user-case traceability.
- Dependencies showing what must be finished first.
- The exact point at which each development branch is created and merged.
- Acceptance criteria that define when an issue can move to Done.

The plan follows a test-first workflow. Tests and implementation stay together on the same feature branch. There is no separate testing branch and no feature is Done merely because its code was written.

## 2. Kanban board setup

### 2.1 Recommended columns

| Column | Meaning |
|---|---|
| Backlog | Valid MVP work that is not ready to begin yet. |
| Ready | Defined, unblocked, and eligible to be the next task. |
| In Progress | Actively being implemented. Keep no more than one parent issue here. |
| In Review | The branch has a pull request into `dev`; tests and acceptance checks are running. |
| Blocked | Work cannot continue until a named dependency or problem is resolved. |
| Done | Acceptance criteria pass, the pull request is merged into `dev`, and the branch is deleted. |

**WIP limit:** Keep only one parent issue in In Progress. WIP means “work in progress.” This prevents a solo developer from starting many features without finishing any of them.

### 2.2 Recommended fields

| Field | Values |
|---|---|
| Status | Backlog, Ready, In Progress, In Review, Blocked, Done |
| Milestone | M1 Foundation, M2 First Action Plan, M3 Strategy and Execution, M4 Release |
| Sprint | Sprint 0, Sprint 1, Sprint 2, Sprint 3 |
| Type | Feature, Test, Security, Infrastructure, Documentation, Release |
| Priority | P0 Blocker, P1 Required, P2 Polish |
| Target window | Milestone week range; update forecasts without changing acceptance scope |
| Requirement | UC/FR/DR/NFR IDs from the specification |
| Branch | Feature branch containing the work |

### 2.3 Labels

Create these labels so the board can be filtered quickly:

- `mvp`
- `backend`
- `frontend`
- `database`
- `testing`
- `security`
- `integration`
- `accessibility`
- `deployment`
- `documentation`
- `priority:p0`
- `priority:p1`
- `priority:p2`
- `blocked`

## 3. Definition of Ready and Definition of Done

### Definition of Ready

An issue can move from Backlog to Ready only when:

- Its requirement and user outcome are identified.
- Its acceptance criteria are clear.
- Required earlier issues are Done.
- Test data, mocks, credentials, or API contracts needed to begin are known.
- The correct feature branch is identified.

### Definition of Done

An issue can move to Done only when:

- Its unit tests were written before or with the implementation and pass.
- Its required integration tests pass.
- Any applicable critical Playwright user journey passes.
- Earlier tests still pass; there are no regressions.
- Security, error, empty, and loading behavior required by the issue is handled.
- The acceptance criteria have been demonstrated in the running app.
- No secrets or credentials were committed.
- The pull request is merged into `dev` and the feature branch is deleted.

## 4. Sprint and milestone overview

| Sprint | Dates | GitHub milestone | Milestone outcome | Associated issues |
|---|---|---|---|---|
| Sprint 0 | Weeks 1–3 | **M1 — Tested Foundation** | The app, test harness, database/auth contracts, and CI foundation exist. | MVP-001–MVP-003 |
| Sprint 1 | Weeks 4–10 | **M2 — First Website Action Plan** | A user can sign in, add a website, run a resumable analysis, and receive persisted SEO/AEO recommendations. | MVP-004–MVP-008 |
| Sprint 2 | Weeks 11–18 | **M3 — Complete Strategy and Execution Loop** | A user can decide on recommendations, manage work, review technical and SEM guidance, and measure progress. | MVP-009–MVP-013 |
| Sprint 3 | Weeks 19–20 | **M4 — Deployed MVP Release** | All six views work together; the app is accessible, tested, deployed, smoke-tested, and demo-ready. | MVP-014–MVP-016 |

## 5. Milestone 1 — Tested Foundation

**Sprint:** Sprint 0  
**Estimated window:** Weeks 1–3
**Exit condition:** all three issues are merged into `dev`, and CI automatically runs backend and frontend tests.

### MVP-001 — Establish the automated test foundation

**Type:** Test / Infrastructure  
**Priority:** P0  
**Branch:** `feature/test-foundation`  
**Create branch:** At milestone start, from the latest `dev`, before any app feature code
**Dependencies:** none  
**Spec:** Section 5.2 test-first rule; NFR-4; NFR-6

**User outcome:** Development can proceed safely because every feature has a repeatable way to prove that it works.

**Sub-issues:**

- [ ] Create the backend pytest folder and configuration.
- [ ] Create the frontend Vitest folder and configuration.
- [ ] Create the Playwright configuration for critical browser journeys.
- [ ] Create reusable backend fixtures and mocked external-service responses.
- [ ] Create a separate test database configuration so tests cannot alter development data.
- [ ] Add commands that run backend, frontend, and end-to-end tests.
- [ ] Add one deliberately simple passing test for each test runner to verify setup.
- [ ] Document how to run each test suite locally.

**Acceptance criteria:**

- All three test runners start successfully.
- Tests use isolated data and do not call paid/live services by default.
- A beginner can run each suite using the documented commands.

### MVP-002 — Establish application, data, API, and security contracts

**Type:** Infrastructure / Database / Security  
**Priority:** P0  
**Branch:** `feature/test-foundation`  
**Dependencies:** MVP-001
**Spec:** DR-1–DR-14; NFR-1–NFR-3; Section 2.5

**Sub-issues:**

- [ ] Write model/constraint tests for the MVP entities and relationships.
- [ ] Write tests for required enums, nullable rules, unique rules, and foreign keys.
- [ ] Scaffold the React/TypeScript frontend and Flask backend.
- [ ] Configure SQLAlchemy and Alembic.
- [ ] Implement the MVP database schema from the approved data model: one Organizer item table, one canonical Organizer stage, affected-page URLs instead of permanent page snapshots/raw HTML, and Supabase Auth UUID ownership.
- [ ] Define the initial REST API request/response contracts.
- [ ] Configure Supabase Auth and JWT validation.
- [ ] Add and test per-user row-level security boundaries.
- [ ] Add environment-variable examples without real secrets.
- [ ] Add baseline rate-limiting and secure error responses.

**Acceptance criteria:**

- Migrations create the expected MVP schema on an empty test database.
- Invalid relationships and enum values fail safely.
- One user cannot read another user's records.
- The frontend and backend start locally using documented setup steps.

### MVP-003 — Run quality checks automatically in CI

**Type:** Infrastructure / Testing  
**Priority:** P0  
**Branch:** `feature/test-foundation`  
**Dependencies:** MVP-001, MVP-002

**Sub-issues:**

- [ ] Add a GitHub Actions workflow for backend tests.
- [ ] Add a GitHub Actions workflow for frontend tests/build.
- [ ] Add safe test environment configuration.
- [ ] Confirm a failing test makes CI fail.
- [ ] Confirm passing tests allow the pull request to merge.

**Acceptance criteria:**

- Pull requests into `dev` automatically run the required checks.
- Failed required checks prevent a feature from being considered Done.

**Branch completion:** Open one pull request from `feature/test-foundation` into `dev`. Merge only when MVP-001–MVP-003 pass, then delete the feature branch.

## 6. Milestone 2 — First Website Action Plan

**Sprint:** Sprint 1  
**Due:** Monday, September 7  
**Exit condition:** UC-1 and the recommendation portion of UC-2 work through the real frontend, API, and database.

### MVP-004 — Create and open a website workspace

**Type:** Feature / Full stack  
**Priority:** P0  
**Branch:** `feature/analysis-flow`  
**Create branch:** After `feature/test-foundation` is merged, from the latest `dev`
**Dependencies:** M1 complete  
**Spec:** UC-1; FR-1.1; FR-1.3; FR-5.1; NFR-1

**Sub-issues:**

- [ ] Write unit tests for URL normalization and validation.
- [ ] Write security tests that reject private/internal addresses (SSRF protection).
- [ ] Write integration tests for authenticated workspace creation and user isolation.
- [ ] Build the Add Website form with optional business context.
- [ ] Create and persist the Website record.
- [ ] Create the workspace shell and six-view navigation.
- [ ] Add invalid URL, duplicate, loading, and failure states.

**Acceptance criteria:**

- An authenticated user can add a valid public website.
- Unsafe/private URLs are rejected before any network request.
- The created workspace belongs only to that user.
- The six MVP views are navigable, even where later data is not yet available.

### MVP-005 — Scrape and analyze website content safely

**Type:** Feature / Backend  
**Priority:** P0  
**Branch:** `feature/analysis-flow`  
**Dependencies:** MVP-004  
**Spec:** FR-3.1; FR-3.5; FR-5.2; NFR-2; NFR-3; NFR-5

**Sub-issues:**

- [ ] Create fixed HTML fixtures representing normal, empty, duplicate, and malformed pages.
- [ ] Write unit tests for robots.txt handling, HTML sanitization, text extraction, and page limits.
- [ ] Write unit tests for unigrams, bigrams, trigrams, frequency ranking, and TF-IDF filtering.
- [ ] Write integration tests for success, timeout, retry, partial failure, and blocked-site behavior.
- [ ] Implement HTTPX/BeautifulSoup scraping with the required clear user agent.
- [ ] Add bounded page crawling and cache/reuse behavior.
- [ ] Implement keyword extraction and multi-page TF-IDF boilerplate filtering.
- [ ] Persist page count, keywords, and `AnalysisRun` state without permanent raw-HTML storage.

**Acceptance criteria:**

- A safe public test site produces persisted keyword results.
- Boilerplate is down-weighted when multiple pages are available.
- Failed requests produce a useful failure state and do not corrupt saved data.

### MVP-006 — Make analysis resumable and visible to the user

**Type:** Feature / Integration  
**Priority:** P0  
**Branch:** `feature/analysis-flow`  
**Dependencies:** MVP-005  
**Spec:** FR-5.2; NFR-2; UC-1

**Sub-issues:**

- [ ] Write state-transition tests for queued, scraping, analyzing, generating, completed, and failed.
- [ ] Write an integration test that resumes after a failed completed stage.
- [ ] Implement stage persistence and restart rules.
- [ ] Add frontend polling and understandable progress messages.
- [ ] Add retry behavior that does not duplicate completed data.
- [ ] Create the first Playwright journey: sign in → add website → analyze → view results.

**Acceptance criteria:**

- The user sees analysis progress rather than waiting on an unexplained request.
- An interrupted run resumes from its last completed stage.
- The first critical Playwright journey passes using controlled test services.

**Branch completion:** Open a pull request from `feature/analysis-flow` into `dev`. Merge only after MVP-004–MVP-006 and the first critical Playwright journey pass; delete the branch.

### MVP-007 — Generate and validate site-specific recommendations

**Type:** Feature / Backend / AI integration  
**Priority:** P0  
**Branch:** `feature/recommendations`  
**Create branch:** After `feature/analysis-flow` is merged, from the latest `dev`
**Dependencies:** MVP-005, MVP-006  
**Spec:** FR-5.2–FR-5.6; NFR-3; NFR-6

**Sub-issues:**

- [ ] Define and test the structured Pydantic response schema.
- [ ] Write unit tests for each plain-Python pipeline stage.
- [ ] Write tests for prompt input, including PII removal and site context.
- [ ] Mock Groq success, malformed JSON, rate limit, and outage responses.
- [ ] Mock Gemini fallback behavior.
- [ ] Test one automatic retry after schema-validation failure.
- [ ] Implement the single structured-output LLM call.
- [ ] Persist validated suggestions with rationale, priority, category, status, and stage.

**Acceptance criteria:**

- Invalid model output cannot be saved as valid recommendations.
- One retry and the backup-provider path behave as specified.
- Every saved suggestion contains a site-specific rationale.

### MVP-008 — Display actionable AEO and SEO/content recommendations

**Type:** Feature / Full stack  
**Priority:** P0  
**Branch:** `feature/recommendations`  
**Dependencies:** MVP-007  
**Spec:** UC-1; UC-2; FR-2; FR-3.2–FR-3.4

**Sub-issues:**

- [ ] Write component tests for rationale, priority, stage, and recommendation content.
- [ ] Write integration tests for loading persisted AEO and SEO/content suggestions.
- [ ] Build the AEO checklist view.
- [ ] Build the SEO/content suggestion view.
- [ ] Display outlines, target keywords, and recommended usage counts.
- [ ] Add loading, empty, incomplete-analysis, and failure states.
- [ ] Verify the first action plan appears in under five minutes, excluding a documented free-host cold start.

**Acceptance criteria:**

- The user receives understandable, site-specific AEO and SEO/content actions.
- Every recommendation shows rationale, priority, and stage.
- Content recommendations include the required outline and keyword information.

**Branch completion:** Open a pull request from `feature/recommendations` into `dev`. Merge when MVP-007–MVP-008 pass, then delete the branch. Milestone M2 is complete.

## 7. Milestone 3 — Complete Strategy and Execution Loop

**Sprint:** Sprint 2  
**Estimated window:** Weeks 11–18
**Exit condition:** UC-2 through UC-5 work and all FR-1–FR-9 capabilities are present on `dev`.

### MVP-009 — Accept, dismiss, and manage recommendations

**Type:** Feature / Full stack  
**Priority:** P0  
**Branch:** `feature/organizer`  
**Create branch:** After M2 is complete, from the latest `dev`
**Dependencies:** MVP-008  
**Spec:** UC-2; UC-3; FR-2.3–FR-2.4; FR-3.3–FR-3.4; FR-4; DR-3–DR-5

**Sub-issues:**

- [ ] Write state-transition tests for pending, accepted, dismissed, and dismiss reasons.
- [ ] Write tests proving acceptance creates exactly one corresponding task.
- [ ] Write tests proving both the suggestion view and Organizer display the same canonical `OrganizerItem.stage` value.
- [ ] Write authorization tests for task and suggestion ownership.
- [ ] Implement Accept/Dismiss actions and the one-tap reason picker.
- [ ] Implement the Backlog, In Production, In Review, and Published board.
- [ ] Implement the separate AEO checklist and combined SEO task view.
- [ ] Extend Playwright coverage through accept → Organizer → Published.

**Acceptance criteria:**

- Accepting creates one task; dismissing stores a reason and creates none.
- Updating a task through either interface changes the same Organizer stage record and both views display it consistently.
- The critical action workflow passes end to end.

**Branch completion:** Merge `feature/organizer` into `dev` after MVP-009 passes; delete the branch.

### MVP-010 — Produce the technical SEO audit

**Type:** Feature / Full stack  
**Priority:** P1  
**Branch:** `feature/technical-audit`  
**Create branch:** After `feature/organizer` is merged, from the latest `dev`
**Dependencies:** MVP-005, MVP-007  
**Spec:** UC-1; FR-5.6; FR-6

**Sub-issues:**

- [ ] Create fixed fixtures for every technical-audit rule.
- [ ] Write PageSpeed success, timeout, quota, and malformed-response tests.
- [ ] Write tests for crawl errors, sitemap, robots.txt, metadata, headings, and alt text.
- [ ] Write tests for duplicate/thin content and TF-IDF similarity thresholds.
- [ ] Implement the PageSpeed adapter and graceful failure behavior.
- [ ] Implement all local technical checks and persist findings.
- [ ] Build the prioritized fix list and plain-language “fix first” summary.

**Acceptance criteria:**

- Every FR-6 rule has deterministic automated coverage.
- One unavailable third-party service does not erase the rest of the audit.
- Findings appear as a prioritized, understandable list.

**Branch completion:** Merge `feature/technical-audit` into `dev` after MVP-010 passes; delete the branch.

### MVP-011 — Generate the disclosed SEM strategy

**Type:** Feature / Full stack  
**Priority:** P1  
**Branch:** `feature/sem-strategy`  
**Create branch:** After `feature/technical-audit` is merged, from the latest `dev`
**Dependencies:** MVP-005, MVP-007, MVP-009  
**Spec:** UC-4; FR-8; DR-6–DR-9

**Sub-issues:**

- [ ] Write deterministic tests for Cost Tier boundaries and commercial-intent modifiers.
- [ ] Write tests for long-tail alternatives, ad groups, targeting, landing pages, and negative keywords.
- [ ] Write tests requiring the heuristic-estimate disclosure wherever Cost Tier appears.
- [ ] Write a boundary test proving no campaign-launch or spending action exists.
- [ ] Implement SEM candidate ranking and persisted SEM fields.
- [ ] Build the SEM view, ad-group presentation, cheaper-alternative chip, and summary.
- [ ] Connect SEM Accept/Dismiss actions to the Organizer.

**Acceptance criteria:**

- SEM produces all FR-8 planning outputs from existing MVP data.
- Estimates are always clearly labeled and cannot be mistaken for live Google Ads data.
- The app cannot create campaigns or spend money.

**Branch completion:** Merge `feature/sem-strategy` into `dev` after MVP-011 passes; delete the branch.

### MVP-012 — Calculate and display the organic Health Score

**Type:** Feature / Full stack  
**Priority:** P1  
**Branch:** `feature/health-reports`  
**Create branch:** After `feature/sem-strategy` is merged, from the latest `dev`
**Dependencies:** MVP-008–MVP-011  
**Spec:** UC-5; FR-1.2; FR-7; DR-1

**Sub-issues:**

- [ ] Write unit tests for each scoring component, boundary values, and weighting.
- [ ] Write integration tests for one immutable score snapshot per analysis.
- [ ] Write tests for first-run/no-delta and later-run delta behavior.
- [ ] Implement score calculation and persistence.
- [ ] Display current score, change since prior scan, and trend line.
- [ ] Verify SEM data is not included in the organic Health Score.

**Acceptance criteria:**

- Scores always remain between 0 and 100.
- Every completed analysis stores its own score snapshot.
- The Overview accurately shows current score and historical trend.

### MVP-013 — Generate, retain, and compare Reports

**Type:** Feature / Full stack  
**Priority:** P0  
**Branch:** `feature/health-reports`  
**Dependencies:** MVP-012 and all data-producing features  
**Spec:** UC-5; FR-9; DR-11

**Sub-issues:**

- [ ] Write tests for automatic Report creation after every completed analysis.
- [ ] Write tests for every predefined organic, paid, and pipeline KPI.
- [ ] Write immutability tests proving old snapshots do not change.
- [ ] Write comparison tests for absolute/percentage delta and zero/empty cases.
- [ ] Implement Report generation, summary text, history, reopening, and comparison.
- [ ] Add clear grouping for Organic, Paid, and Pipeline KPIs.
- [ ] Add the snapshot/scoring-change disclosure.
- [ ] Add Playwright coverage for rescan → open history → compare two reports.

**Acceptance criteria:**

- Each completed run creates exactly one immutable Report.
- Any two reports for the same website can be compared correctly.
- Report data remains inside Trellis and the critical rescan/compare journey passes.

**Branch completion:** Open one pull request from `feature/health-reports` into `dev`. Merge after MVP-012–MVP-013 pass; delete the branch. Milestone M3 is complete.

## 8. Milestone 4 — Deployed MVP Release

**Sprint:** Sprint 3  
**Estimated window:** Weeks 19–20
**Exit condition:** the definition of done in Section 5.2 of the specification passes against the deployed application.

### MVP-014 — Integrate and finish all six workspace views

**Type:** Feature / Integration / Frontend  
**Priority:** P0  
**Branch:** `feature/ui-deployment`  
**Create branch:** After M3 is complete, from the latest `dev`
**Dependencies:** MVP-004–MVP-013  
**Spec:** FR-1.2–FR-1.3; Section 4.1; NFR-4

**Sub-issues:**

- [ ] Write component/integration tests for Overview, AEO, SEO/Content, SEM, Reports, and Organizer.
- [ ] Test shared website and AnalysisRun context across every view.
- [ ] Test navigation, responsive behavior, and keyboard use.
- [ ] Test loading, empty, failed, partial, retry, and unauthorized states.
- [ ] Complete the Overview summary cards and since-last-scan callouts.
- [ ] Reconcile visual patterns and remove disconnected placeholder data.
- [ ] Confirm both critical Playwright journeys pass against the integrated app.

**Acceptance criteria:**

- All six views use real data belonging to the selected website.
- No MVP screen depends on hard-coded demonstration results.
- Required states and critical journeys pass.

### MVP-015 — Run full regression, accessibility checks, and deployment

**Type:** Release / Testing / Accessibility / Deployment  
**Priority:** P0  
**Branch:** `feature/ui-deployment`  
**Target:** After MVP-014 passes
**Dependencies:** MVP-014

**Sub-issues:**

- [ ] Run all accumulated pytest, Vitest, and Playwright tests.
- [ ] Fix regressions; do not add unplanned features.
- [ ] Run automated accessibility checks and complete keyboard/manual checks.
- [ ] Verify focus, labels, contrast, status text, and responsive layouts.
- [ ] Configure production environment variables without committing secrets.
- [ ] Deploy the Flask backend to Render.
- [ ] Deploy the React frontend to Netlify.
- [ ] Configure frontend/backend origins, HTTPS, auth callbacks, and production database access.
- [ ] Run post-deployment smoke tests and record failures as release blockers.

**Acceptance criteria:**

- The complete suite passes before deployment.
- The deployed frontend securely communicates with the deployed backend.
- Critical accessibility checks and post-deploy smoke tests pass.

**Branch completion:** Open a pull request from `feature/ui-deployment` into `dev`. Merge only after MVP-014–MVP-015 pass and the deployed release candidate is smoke-tested; delete the branch.

### MVP-016 — Accept and release the MVP

**Type:** Release / Documentation  
**Priority:** P0  
**Branch:** no planned feature branch; use `fix/release-blockers` only if an acceptance blocker requires code changes  
**Create blocker branch:** From the latest `dev` only when a specific failed acceptance check has an issue; merge it back into `dev` after the focused regression test passes
**Dependencies:** MVP-015  
**Spec:** UC-1–UC-5; FR-1–FR-9; NFR-1–NFR-6; Section 5.2 definition of done

**Sub-issues:**

- [ ] Run the full automated suite on the release candidate.
- [ ] Run a production smoke test using a representative public website.
- [ ] Verify sign in → add website → analyze → recommendations → accept/dismiss → Organizer.
- [ ] Verify rescan → Health Score change → Report history → compare Reports.
- [ ] Verify SEM disclosures and the no-spending boundary.
- [ ] Verify user isolation, URL safety, rate limits, and secret handling.
- [ ] Confirm the analysis normally reaches an actionable plan within five minutes.
- [ ] Record and fix only release-blocking defects.
- [ ] Rehearse the end-to-end demonstration.
- [ ] Open the release pull request from `dev` into `main`.
- [ ] Merge only after all required checks and the acceptance checklist pass.
- [ ] Tag or record the released MVP version and verify production after the merge.

**Acceptance criteria:**

- All five user cases pass in the deployed app.
- All P0/P1 MVP issues are Done; any P2 visual polish is explicitly deferred.
- The `dev` → `main` pull request passes required checks.
- Production is rechecked after the release merge.

## 9. Branch creation and merge sequence

Do not create every branch on the first day. A branch must start from the newest tested `dev`, so create it only after the preceding branch has merged.

| Start when | Create branch from latest `dev` | Issues | Merge target | Merge gate |
|---|---|---|---|---|
| Now | `feature/test-foundation` | MVP-001–MVP-003 | `dev` | Test harness, schema/auth contracts, and CI pass |
| After M1 | `feature/analysis-flow` | MVP-004–MVP-006 | `dev` | Workspace/analyze/result journey passes |
| After analysis flow | `feature/recommendations` | MVP-007–MVP-008 | `dev` | Validated recommendations render correctly |
| After M2 | `feature/organizer` | MVP-009 | `dev` | Accept/Dismiss/Organizer journey passes |
| After Organizer | `feature/technical-audit` | MVP-010 | `dev` | FR-6 tests and audit UI pass |
| After technical audit | `feature/sem-strategy` | MVP-011 | `dev` | FR-8 tests, disclosures, and Organizer link pass |
| After SEM | `feature/health-reports` | MVP-012–MVP-013 | `dev` | Health/Report/rescan comparison tests pass |
| After M3 | `feature/ui-deployment` | MVP-014–MVP-015 | `dev` | Full regression, accessibility, and deployed smoke checks pass |
| Only if needed | `fix/release-blockers` | Focused sub-issue under MVP-016 | `dev` | Failed acceptance test is fixed and full regression remains green |
| After acceptance | No new feature branch | MVP-016 | Pull request: `dev` → `main` | Complete production acceptance checklist passes |

Use this command sequence whenever a new planned branch begins:

```bash
git switch dev
git pull origin dev
git switch -c feature/branch-name
```

After its pull request is merged, return to and update `dev` before creating the next branch:

```bash
git switch dev
git pull origin dev
git branch -d feature/branch-name
```

The local delete command removes only the already-merged local copy. GitHub can delete the remote feature branch when the pull request is merged.

## 10. Dependency chain and critical path

The critical path is the sequence that directly controls when the feature-complete MVP can be released:

```text
MVP-001 Test foundation
  → MVP-002 Data/auth contracts
  → MVP-003 CI
  → MVP-004 Workspace
  → MVP-005 Scrape/keywords
  → MVP-006 Resumable analysis
  → MVP-007 AI recommendations
  → MVP-008 AEO/SEO views
  → MVP-009 Organizer
  → MVP-010 Technical audit
  → MVP-011 SEM
  → MVP-012 Health Score
  → MVP-013 Reports
  → MVP-014 Integrated UI
  → MVP-015 Deployment
  → MVP-016 Acceptance/release
```

If a critical-path issue is blocked, move it to Blocked, write the blocker directly on the issue, and work only on a sub-issue that does not create incompatible or disposable code. Do not silently skip the blocked requirement.

## 11. Daily operating routine

### Start of day

1. Update local `dev`.
2. Confirm the prior feature branch was merged and deleted.
3. Move today's first unblocked issue to Ready.
4. Create the scheduled feature branch from the latest `dev`.
5. Move only that issue to In Progress.

### For every sub-issue

1. Write the expected behavior as a failing test.
2. Implement the smallest behavior that makes the test pass.
3. Refactor without changing behavior.
4. Run the relevant focused tests.
5. Run all accumulated unit and integration tests before committing.
6. Check off the sub-issue and link the commit or pull request.

This cycle is commonly called **red → green → refactor**: red means the new test fails, green means the implementation makes it pass, and refactor means improving the code while keeping the tests green.

### End of day

1. Run the complete accumulated test suite.
2. Demonstrate the parent issue's acceptance criteria in the running app.
3. Open or update the pull request into `dev`.
4. Move the issue to In Review.
5. Merge only after required checks pass.
6. Move the issue to Done and delete the merged branch.
7. Record any carryover blocker as the first task for the following morning.

## 12. Release rules and scope protection

- FR-10 through FR-17 are not part of this board; label requests for them `post-mvp` and leave them outside these milestones.
- Do not add live Google Ads, GA4, Search Console, GBP, campaign creation, or spending behavior to the MVP.
- Do not trade away authentication, user isolation, SSRF protection, test isolation, or secret handling to save time.
- Do not postpone tests for a feature to September 13.
- Do not merge a red pull request into `dev` or merge an unaccepted `dev` into `main`.
- If time becomes constrained, defer P2 visual polish first. Do not quietly redefine a missing P0/P1 requirement as complete.

## 13. Final traceability check

| Spec area | Implemented/verified by issues |
|---|---|
| UC-1 — First website action plan | MVP-004–MVP-008, MVP-010, MVP-011, MVP-016 |
| UC-2 — Focus recommendations | MVP-008–MVP-009, MVP-011, MVP-016 |
| UC-3 — Manage through completion | MVP-009, MVP-011, MVP-016 |
| UC-4 — Paid-search decision support | MVP-011, MVP-016 |
| UC-5 — Measure improvement | MVP-012–MVP-013, MVP-016 |
| FR-1 | MVP-004, MVP-012, MVP-014 |
| FR-2 | MVP-007–MVP-009 |
| FR-3 | MVP-005, MVP-008–MVP-009 |
| FR-4 | MVP-009 |
| FR-5 | MVP-006–MVP-007, MVP-010 |
| FR-6 | MVP-010 |
| FR-7 | MVP-012 |
| FR-8 | MVP-011 |
| FR-9 | MVP-013 |
| DR-1–DR-14 applicable to MVP | MVP-002 and each data-producing feature issue |
| NFR-1 Security | MVP-002, MVP-004–MVP-005, MVP-009, MVP-016 |
| NFR-2 Scalability/resumability | MVP-005–MVP-006 |
| NFR-3 Cost management | MVP-002, MVP-005, MVP-007 |
| NFR-4 Accessibility | MVP-001, MVP-014–MVP-015 |
| NFR-5 Performance | MVP-005, MVP-008, MVP-016 |
| NFR-6 Reliability | MVP-001, MVP-007 |

Every MVP functional requirement, non-functional requirement, and core user case has at least one associated issue and acceptance check. This plan describes intended work; an issue becomes implemented only after its tests pass, its pull request merges into `dev`, and its acceptance criteria are verified.
