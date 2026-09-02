"""Create clean SVG outlines from the finalized, approved Trellis logo masks.

The vectorizer follows the existing PNG alpha edge, simplifies redundant raster
points, and writes continuous SVG outlines. It never redraws or substitutes the
approved icon or Fraunces wordmark.
"""

from pathlib import Path
from xml.sax.saxutils import escape

import matplotlib
import numpy as np
from PIL import Image

matplotlib.use("Agg")
from matplotlib import pyplot as plt
from matplotlib.path import Path as MplPath

HERE = Path(__file__).resolve().parent
PNG_DIR = HERE.parent / "PNGs"
SOURCES = {
    "trellis-icon": PNG_DIR / "trellis-icon-ink-1D2A20-transparent.png",
    "trellis-horizontal": PNG_DIR / "trellis-horizontal-ink-logo-1D2A20-transparent.png",
}
COLORS = {
    "ink-1D2A20": "#1D2A20",
    "green-2C4E35": "#2C4E35",
    "white": "#FFFFFF",
}


def vector_path(alpha: Image.Image) -> str:
    """Follow the 50% alpha edge and return a simplified compound SVG path."""
    data = np.asarray(alpha, dtype=float) / 255
    figure, axis = plt.subplots()
    contour = axis.contour(data, levels=[0.5])
    paths = contour.get_paths()
    plt.close(figure)
    if not paths:
        raise ValueError("Source logo has no visible contour")

    path = paths[0].cleaned(simplify=True)
    commands = []
    for (x, y), code in zip(path.vertices, path.codes):
        if code == MplPath.MOVETO:
            commands.append(f"M{x:.1f} {y:.1f}")
        elif code == MplPath.LINETO:
            commands.append(f"L{x:.1f} {y:.1f}")
        elif code == MplPath.CLOSEPOLY:
            commands.append("Z")
    return "".join(commands)


def write_svg(source: Path, output: Path, color: str) -> None:
    image = Image.open(source).convert("RGBA")
    path = vector_path(image.getchannel("A"))
    title = escape("Trellis" if "horizontal" in source.name else "Trellis icon")
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {image.width} {image.height}" '
        f'role="img" aria-labelledby="title">\n'
        f'  <title id="title">{title}</title>\n'
        f'  <path fill="{color}" fill-rule="evenodd" d="{path}"/>\n'
        '</svg>\n'
    )
    output.write_text(svg, encoding="utf-8")


for stem, source in SOURCES.items():
    for color_name, color in COLORS.items():
        write_svg(source, HERE / f"{stem}-{color_name}.svg", color)
