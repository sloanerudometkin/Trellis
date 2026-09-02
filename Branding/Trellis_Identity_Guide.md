# Trellis — Visual & Verbal Identity Guide (v3.0, September 2026)

Published artifact (full designed version — logo, color, type, voice, tagline, in-product proof): https://claude.ai/code/artifact/8dbdd7ac-d76f-48d0-99c5-5185a7c6fd0c
(Rebuilt Aug 28, 2026 with the finalized Fraunces-wordmark logo art and full logo/icon specimen set.)

This doc is a text summary for search inside the project. See the artifact for the actual visual specimens.

## 1. Logo & Trademark — FINALIZED (logo art updated Aug 27, 2026)
The mark: an open trellis grid—two vertical supports crossed by three horizontal rails—with a single climbing vine weaving diagonally through the grid and sprouting two simple leaves. A plain, single-color drawing with no gradient or decorative effect. It works as an icon alone (favicon, app icon, avatar) or paired with the wordmark.
- **Wordmark typeface: Fraunces, Bold** — reserved for the logotype at this weight; Fraunces at lighter weights also carries headlines and the tagline (see Typography), so the wordmark and the rest of the brand's display type now share one family instead of two. This replaces the earlier decision to set the wordmark in Source Serif 4 Bold.
- **Primary lockup:** Ink (#1D2A20) icon + wordmark on Paper/white.
- **Reversed:** Paper/white icon + wordmark on a dark ground (Ink or Moss Deep).
- **Brand-color alternate:** Moss Deep icon + wordmark on Paper/white, for marketing contexts wanting the brand green.
- Minimum clear space = the width of one post, on all sides. Use the icon alone below 120px wide; use the horizontal lockup at 120px and above.
- Don't: outline the mark, add a drop shadow, stretch it off-square, substitute the wordmark typeface, or permanently attach the tagline to the lockup in-product.
- Final logo files live in `Branding/assets/logo/`: transparent raster exports are in `PNGs/`, and scalable vector exports are in `SVGs/`. Both sets contain the icon and horizontal lockup in primary Ink, Moss Deep, and white. Pure black is not part of the Trellis brand palette.
- Use SVG for the website, presentations, and scalable layouts whenever supported. Use PNG only where SVG is unsupported. Never place a PNG inside an SVG wrapper and call it a vector logo.
- Website favicon files live in `Branding/assets/logo/Favicons/`. They place the approved Trellis icon unchanged on a transparent square canvas; they do not redraw or simplify it. Use the SVG favicon when supported and the supplied PNG sizes for platform fallbacks.
- `PNGs/logo-watermark.png` uses the finalized Fraunces wordmark and current open-trellis icon at low opacity. It is a supporting watermark only, never a substitute for a primary logo lockup.

## 2. Color Palette
| Name | Hex | Role |
|---|---|---|
| Paper | #F1F3EA | Primary background |
| Ink | #1D2A20 | Body text, primary logo color |
| Moss | #3F6B4A | Primary brand color — links, active states, progress fill |
| Moss Deep | #2C4E35 | Headlines, primary buttons, brand-color logo alternate |
| Gold | #A9791F | Reserved — deltas, badges, "new" flags. Never in the logo, never a button/link. |
| Sage Tint | #E2E9DB | Card/panel surfaces |

Rule: if Gold appears more than once per screen, pull it back — it works because it's rare. Ink/Paper and Paper/Moss Deep clear WCAG AA for body text; Gold-on-Paper is AA for large text/labels only.

## 3. Typography
- **Fraunces** — wordmark at 700; display headlines and tagline at 500. Do not use it for paragraphs, navigation, forms, or data tables.
- **Public Sans** — body and UI at 400; labels, buttons, and emphasized body copy at 600. This is everything the user reads to get work done.
- **IBM Plex Mono** — utility data at 400: Health Score, deltas ("68 ▲ +7"), counts, timestamps, and short metadata only.

| Role | Typeface | Weight | Responsive size | Line height |
|---|---|---:|---:|---:|
| Display statement | Fraunces | 500 | 48–88px | 0.98 |
| H1 | Fraunces | 500 | 40–72px | 1.0 |
| H2 | Fraunces | 500 | 32–52px | 1.05 |
| H3 | Fraunces | 500 | 24–32px | 1.1 |
| H4 | Fraunces | 500 | 20px | 1.2 |
| Large body | Public Sans | 400 | 18px | 1.6 |
| Body | Public Sans | 400 | 16px | 1.6 |
| Small body/label | Public Sans | 400/600 | 14px | 1.4 |
| Button | Public Sans | 600 | 16px | 1.2 |
| Utility data | IBM Plex Mono | 400 | 14px or larger | 1.35 |

Headlines use sentence case, not title case or all caps. Body copy stays near 70 characters per line. Never imitate the wordmark by typing “Trellis” in a live heading; use the official logo asset when the wordmark is intended.

*Source Serif 4 has been removed from the system — it is no longer used anywhere, including the logotype.*

## 4. Tone & Voice
Personality: a capable friend who happens to know SEO — never a vendor, never a professor.
Pillars: **Direct** (recommendation before methodology), **Plain** (jargon always gets a one-sentence plain-language reason), **Unhurried** (progress framed as movement, not a verdict).

| Trellis says | Not this |
|---|---|
| "Here's what I'd fix first, and why." | "The following issues were detected during the crawl." |
| "Your Health Score moved from 61 to 68 this week." | "Your SEO performance metrics have been recalculated." |
| "3 new keyword opportunities since your last scan." | "Please review the updated keyword corpus." |
| "Not relevant right now? Tell us why and we'll skip it." | "Dismiss recommendation." |

Sample microcopy:
- Empty state (no sites): "Add your first site and we'll have a plan for it in under five minutes."
- Error (scan failed): "We couldn't reach that site. Double-check the URL, or try again in a minute — sometimes it's just a slow server."
- Success (task published): "Nice — that's live. Your Health Score will reflect it on the next scan."
- Onboarding: "You bring the content. We'll bring the structure — starting with a full audit of what's already on your site."

## 5. Tagline & Verbal System
- **Primary tagline:** "Give your content something to climb."
- **One-sentence definition:** "Trellis is a digital marketing workspace that analyzes your website, recommends prioritized SEO, AEO, and SEM improvements, and helps you manage and measure your progress."
- **Positioning line** (pitch/landing): "A complete search strategy — without the consultant-sized invoice."
- **In-app empty state:** "Every plant needs something to climb. Add your first site to get started."
- **Onboarding/email:** "You bring the content. We'll bring the structure."
- **Never say:** "AI-powered SEO optimization platform."

On marketing pages, lead with the outcome before the category names:

> Know what to fix, what to create, and what to do next—without needing an expensive search consultancy.

The official product story is: **Analyze → Recommend → Prioritize → Complete → Measure progress.** Use this sequence in diagrams, demonstrations, onboarding, and product tours so visitors can see that Trellis continues beyond the audit.

## 6. In Product (proof point)
The Health Score card is where color, type, and voice all have to hold up at once: large mono score + gold delta, Moss progress bar, plain-language copy naming what changed and what's next, Moss Deep CTA. The SEM section mirrors this pattern but keeps its own small summary (accepted keyword count, cost-tier mix) rather than folding into the Health Score — paid and organic are tracked as coequal disciplines, not blended into one number.

## 7. Digital UI System

### Layout and spacing
- Use an 8px spacing foundation. Common values are 8, 16, 24, 32, 48, 64, and 96px.
- Keep reading text to approximately 65–75 characters per line.
- Use generous Paper-colored space to create calm and hierarchy; do not fill every area with cards.
- Design mobile-first, then verify mobile, tablet, laptop, and wide-desktop widths. Content order must remain understandable when stacked.

### Buttons and links
- Use one primary action per section: Moss Deep background, Paper text, and a clear action verb.
- Secondary buttons use a transparent or Paper background with an Ink or Moss Deep border.
- Text links use Moss plus an underline in body copy. Color alone must never be the only link indicator.
- Gold is never a button or ordinary link color.
- Hover, pressed, disabled, loading, and keyboard-focus states are required. Focus rings must be clearly visible.

### Forms
- Labels remain visible above inputs; placeholders are examples, not replacements for labels.
- Put help and error text beside the relevant field in plain language.
- Errors explain how to recover and use text or iconography as well as color.
- Touch targets should be at least 44×44px.

### Cards, status, and data
- Cards group related information, not every individual metric. Use Sage Tint selectively for grouped surfaces.
- Use IBM Plex Mono for scores, deltas, timestamps, and compact operational data—not paragraphs.
- Status always includes a written label. Never rely on green, gold, or red alone.
- Recommendation cards prioritize: recommendation, one-sentence reason, status, and next action. Methodology may follow in expandable detail.

### Feedback and empty states
- Loading states say what is happening when the wait may be noticeable.
- Success messages confirm what changed and what happens next.
- Error messages avoid blame, preserve entered work where possible, and give a recovery action.
- Empty states explain the value of the missing content and provide one obvious next step.

## 8. Accessibility Requirements
- Target WCAG 2.2 AA for the marketing site and product.
- Normal text must meet at least 4.5:1 contrast; large text and essential interface graphics at least 3:1.
- Gold on Paper is limited to large text, short labels, decorative accents, or nonessential emphasis. Confirm contrast in the final size and weight.
- All functionality must work with a keyboard, with a logical focus order and visible focus indicator.
- Use semantic headings, descriptive link and button labels, form labels, and useful alternative text.
- Do not communicate meaning through color, position, animation, or iconography alone.
- Respect reduced-motion preferences. Animation should explain change or progression, not decorate routine tasks.

## 9. Website Experience Pattern
Recommended homepage sequence:

1. Outcome-led hero and two actions: **Build my first plan** and **See how Trellis works**.
2. The problem with report-only tools.
3. The five-step audit-to-published workflow.
4. Product proof using a realistic Health Score delta and prioritized next action.
5. Plain-language explanations of SEO, AEO, and SEM.
6. Who Trellis is for.
7. An explicit explanation of the current offer, limits, and price once those decisions are finalized.
8. A focused final call to action.

Preferred hero copy:

> **Give your content something to climb.**
>
> Trellis turns your website audit into a prioritized SEO, AEO, and paid-search plan—and helps you carry every recommendation through to published.

Use the climbing metaphor at major story moments only. The interface should feel structured and supportive, not garden-themed.

## 10. Validation Before Launch
- Test responsive prototypes with at least five people resembling the primary audience.
- Ask each person to explain what Trellis does, who it is for, what they would do first, and what the current offer includes.
- Observe whether they can find the next action without coaching on desktop and mobile.
- Test the logo at 16px and 32px, all interactive states, keyboard navigation, zoom to 200%, and key color combinations.
- Revise language or hierarchy when users hesitate; aesthetic preference alone is not proof of usability.

## 11. Production Files
- Exact implementation tokens: `Branding/design-system/tokens.css` and `tokens.json`.
- Component rules: `Branding/design-system/component-spec.md`.
- Imagery, iconography, diagrams, photography, and motion: `Branding/design-system/imagery-iconography.md`.
- Approved fonts: `Branding/assets/Fonts/`.
- Approved logo exports and generation files: `Branding/assets/logo/`.

Designers and developers use the semantic tokens rather than inventing new colors, type sizes, spacing, radii, or shadows inside individual pages.

## 12. Pre-Launch Ownership
- **Owner validates:** trademark and domain availability; the final customer price/offer; testing with representative users; and final accessibility testing in the implemented website.
- **Brand system provides:** production assets, responsive typography, interface tokens, component behavior, imagery/icon/motion direction, message hierarchy, and truthful pre-pricing language.

*Status: production-ready identity foundation v3.0. The system includes final logo use, responsive typography, web tokens, components, imagery, iconography, motion, message hierarchy, and pre-pricing language. Trademark/domain validation, representative-user testing, final offer approval, and implemented-site accessibility testing remain required before public launch.*
