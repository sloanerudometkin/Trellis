# Trellis Web Design System

This folder translates the Trellis identity into production-ready website rules.

## Source of truth

- `tokens.css` contains reusable website design variables.
- `tokens.json` provides the same values for design tools and non-CSS applications.
- `component-spec.md` defines how recurring interface elements look and behave.
- `imagery-iconography.md` defines the visual style beyond the logo.

The Brand Brief defines why Trellis exists and what it promises. The Identity Guide defines how Trellis looks and sounds. This folder defines how those decisions become a consistent website and product interface.

## Font roles

- Fraunces: logo, display headlines, and tagline.
- Public Sans: body copy and interface controls.
- IBM Plex Mono: scores, deltas, counts, timestamps, and compact metadata.

Only the approved local files in `Branding/assets/Fonts/` should be loaded. Website fallbacks are included in `tokens.css`.

## Implementation rule

Use semantic token names such as `--color-text` and `--color-action`, not raw hex codes inside components. This makes future accessibility or theme improvements consistent across the entire website.
