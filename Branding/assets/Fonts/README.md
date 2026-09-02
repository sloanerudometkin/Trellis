# Trellis Fonts

Font files for the Trellis brand system, matching `Trellis_Identity_Guide.md` and `Trellis_Brand_Brief.md`. All three are free, open-source Google Fonts (SIL Open Font License — see each folder's `OFL.txt`), so they're safe to embed in the app, marketing site, and any design files.

## Fraunces — display
Wordmark logotype (Bold), headlines, and the tagline. Use weight ~500 for headlines/tagline, Bold reserved for the logotype itself.
- `Fraunces-Variable.ttf` — variable font, weight axis + optical size (`opsz`) + softness/wonk axes. Set `font-weight` anywhere from 100–900.
- `Fraunces-Italic-Variable.ttf` — italic companion.

## Public Sans — body / UI
Everything the user reads to get work done: body copy, UI labels, buttons.
- `PublicSans-Variable.ttf` — variable font, weight axis 100–900.
- `PublicSans-Italic-Variable.ttf` — italic companion.

## IBM Plex Mono — utility
Health Score, deltas ("68 ▲ +7"), counts, timestamps — anything numeric/tabular.
- Ships as static weight files (Thin, ExtraLight, Light, Regular, Medium, SemiBold, Bold — each with an Italic).

## Using these in CSS
```css
@font-face {
  font-family: "Fraunces";
  src: url("Fraunces-Variable.ttf") format("truetype-variations");
  font-weight: 100 900;
}
@font-face {
  font-family: "Public Sans";
  src: url("PublicSans-Variable.ttf") format("truetype-variations");
  font-weight: 100 900;
}
@font-face {
  font-family: "IBM Plex Mono";
  src: url("IBMPlexMono-Regular.ttf") format("truetype");
  font-weight: 400;
}
```

*Source: google/fonts repo, latest OFL release as of Aug 31, 2026.*
