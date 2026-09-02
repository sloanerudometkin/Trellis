from pathlib import Path
from PIL import Image


HERE = Path(__file__).resolve().parent
MASTER_ICON = HERE / "trellis-icon-green-2C4E35-transparent.png"
MASTER_WORDMARK = HERE / "trellis-horizontal-green-logo-2C4E35-transparent.png"

VARIANTS = {
    "ink": ((29, 42, 32), "ink-1D2A20", "ink-logo-1D2A20"),
    "white": ((255, 255, 255), "white", "white-logo"),
    "green": ((44, 78, 53), "green-2C4E35", "green-logo-2C4E35"),
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


for color, icon_name, horizontal_name in VARIANTS.values():
    solid_variant(MASTER_ICON, color, HERE / f"trellis-icon-{icon_name}-transparent.png")
    solid_variant(
        MASTER_WORDMARK,
        color,
        HERE / f"trellis-horizontal-{horizontal_name}-transparent.png",
    )
