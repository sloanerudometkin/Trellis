# Trellis logo asset set

This folder contains transparent PNG and true vector SVG versions of the selected open-grid trellis and climbing-vine concept.

- Standalone icons and horizontal lockups in primary Ink, Moss Deep, and white.
- Ink is the default dark lockup. Moss Deep is the marketing alternate. White is the reversed version for Ink or Moss Deep backgrounds. Pure black is not part of the Trellis brand system.
- Use SVG on websites and in layouts whenever possible; use PNG where an application does not accept SVG.
- The SVG wordmark is vector geometry, so it does not depend on the viewer having Fraunces installed.
- Website-ready favicon files live in `Favicons/`. Each uses the approved Trellis icon unchanged and centered on a transparent square canvas.
- `PNGs/logo-watermark.png` is the approved current logo rendered in Moss Deep at low opacity on a transparent background.

Green is the exact Trellis Moss Deep color: `#2C4E35`.

The white files may appear blank in viewers that use a white preview background. Place them over a dark color to see them.

`SVGs/render_svg_variants.py` follows and simplifies the approved PNG alpha outlines into continuous vector paths. It preserves the approved icon and Fraunces wordmark, and the SVGs do not embed raster images or depend on installed fonts.

`Favicons/render_favicons.py` creates the SVG favicon and 16px, 32px, 180px, 192px, and 512px PNG fallbacks from the approved Moss Deep icon.
