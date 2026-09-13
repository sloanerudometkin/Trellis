# MVP-015 Release Blockers

Last verified: September 9, 2026

MVP-015 is locally release-ready but is not deployment-complete. Do not merge or delete `feature/ui-deployment` until every blocker below is closed and the production smoke checks pass.

## Closed local gates

- `make test`: 146 pytest tests, 33 Vitest tests, and both critical Playwright journeys pass.
- Automated axe WCAG A/AA scans pass on Overview, AEO, SEO/Content, SEM, Reports, and Organizer.
- Keyboard arrow navigation, visible focus, labels/status regions, 375 px responsive layout, and horizontal overflow checks pass.
- `render.yaml` and `netlify.toml` declare reproducible production builds without storing secret values in Git.

## Open release blockers

1. **Deployment accounts are not authenticated.** The in-app browser reaches sign-in screens for Render, Netlify, and Supabase, and the GitHub CLI reports that its saved token is invalid. Signed-in accounts are required before the branch can be pushed and services, environment variables, database access, HTTPS origins, or callbacks can be configured.
2. **The production environment values are unavailable.** Render still needs `DATABASE_URL`, `SUPABASE_URL`, `FRONTEND_ORIGIN`, and provider API keys entered in its secret store. Netlify still needs `VITE_API_BASE_URL` entered in its environment-variable settings. Never paste these values into tracked files.
3. **The implemented Supabase sign-in flow is not connected to a real project yet.** The frontend now includes account creation, email/password sign-in, session restoration/refresh, sign-out, and tested configuration/error states. Real acceptance still requires a Supabase Project URL and publishable key in Netlify, the matching `SUPABASE_URL` in Render, and a successful live sign-up/sign-in smoke test.
4. **Production smoke tests have no target URLs.** The Render and Netlify services do not exist yet, so HTTPS, CORS, JWT validation, production migrations, the health endpoint, and both critical journeys cannot be verified.

## Required production smoke gate

After the blockers are closed:

1. Open the deployed Netlify HTTPS URL and sign in through Supabase.
2. Add a public test website, run an analysis, and verify AEO/SEO/SEM results, Report creation, and Organizer updates.
3. Rescan the same website, reopen Report history, and compare the two immutable Reports.
4. Verify the browser console has no mixed-content or CORS errors and `https://<render-service>/api/v1/health` returns a healthy response.
5. Repeat keyboard navigation and a 375 px responsive check on the deployed frontend.
6. Record any failure here and treat it as a blocker rather than merging the branch.
