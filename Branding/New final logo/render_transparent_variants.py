from pathlib import Path
from PIL import Image


HERE = Path(__file__).resolve().parent
MASTER_ICON = HERE / "master-icon-green.png"
MASTER_WORDMARK = HERE / "master-horizontal-green.png"

COLORS = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "green-2C4E35": (44, 78, 53),
}


def crop_transparent(image: Image.Image, padding: int = 32) -> Image.Image:
    image = image.convert("RGBA")
    bbox = image.getchannel("A").getbbox()
    if bbox is None:
        raise ValueError("Master image has no visible pixels")
    cropped = image.crop(bbox)
    canvas = Image.new(
        "RGBA",
        (cropped.width + padding * 2, cropped.height + padding * 2),
        (0, 0, 0, 0),
    )
    canvas.alpha_composite(cropped, (padding, padding))
    return canvas


def solid_variant(master: Path, color: tuple[int, int, int], output: Path) -> None:
    image = crop_transparent(Image.open(master))
    alpha = image.getchannel("A")
    solid = Image.new("RGBA", image.size, (*color, 0))
    solid.putalpha(alpha)
    solid.save(output, "PNG", optimize=True)


for color_name, color in COLORS.items():
    solid_variant(MASTER_ICON, color, HERE / f"trellis-icon-{color_name}-transparent.png")
    solid_variant(
        MASTER_WORDMARK,
        color,
        HERE / f"trellis-horizontal-{color_name}-transparent.png",
    )

