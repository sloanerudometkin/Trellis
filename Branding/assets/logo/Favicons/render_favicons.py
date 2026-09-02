"""Create square favicon exports from the approved Trellis icon unchanged."""

from pathlib import Path
import xml.etree.ElementTree as ET

from PIL import Image

HERE = Path(__file__).resolve().parent
LOGO_DIR = HERE.parent
PNG_SOURCE = LOGO_DIR / "PNGs" / "trellis-icon-green-2C4E35-transparent.png"
SVG_SOURCE = LOGO_DIR / "SVGs" / "trellis-icon-green-2C4E35.svg"
PNG_SIZES = (16, 32, 180, 192, 512)


def square_canvas(image: Image.Image) -> Image.Image:
    side = max(image.size)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.alpha_composite(image, ((side - image.width) // 2, (side - image.height) // 2))
    return canvas


source = Image.open(PNG_SOURCE).convert("RGBA")
square = square_canvas(source)
for size in PNG_SIZES:
    square.resize((size, size), Image.Resampling.LANCZOS).save(
        HERE / f"trellis-favicon-{size}.png", "PNG", optimize=True
    )

svg_root = ET.parse(SVG_SOURCE).getroot()
namespace = "{http://www.w3.org/2000/svg}"
view_box = [float(value) for value in svg_root.attrib["viewBox"].split()]
width, height = view_box[2], view_box[3]
side = max(width, height)
x_offset = (side - width) / 2
path = svg_root.find(f"{namespace}path")
if path is None:
    raise ValueError("Approved SVG icon has no vector path")

favicon = (
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {side:g} {side:g}" '
    'role="img" aria-labelledby="title">\n'
    '  <title id="title">Trellis</title>\n'
    f'  <g transform="translate({x_offset:g} 0)">\n'
    f'    <path fill="#2C4E35" fill-rule="evenodd" d="{path.attrib["d"]}"/>\n'
    '  </g>\n'
    '</svg>\n'
)
(HERE / "trellis-favicon.svg").write_text(favicon, encoding="utf-8")
