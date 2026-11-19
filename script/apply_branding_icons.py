"""Generate and check the Synth Warp app icons and installer images from the vector masters.

The masters live in assets/branding/synth-warp/. Requires ImageMagick 7 with SVG support (`magick`
on PATH) and Pillow:

    uv run --with pillow python script/apply_branding_icons.py           # regenerate
    uv run --with pillow python script/apply_branding_icons.py --check   # validate, no writes
"""

from __future__ import annotations

import argparse
import io
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "assets" / "branding" / "synth-warp"
PREVIEW = SOURCES / "synth-warp-app-icon.png"
INSTALLER_IMAGES = ROOT / "script" / "windows" / "installer-images"

ICO_SIZES = (16, 24, 32, 48, 64, 128, 256)
PNG_SIZES = (16, 32, 48, 64, 128, 256, 512)
CHANNELS = ("oss", "warp-oss", "local")
PLATE = (0x10, 0x10, 0x14)

# Inno Setup wizard images, at the sizes the previous Warp bitmaps used.
INSTALLER_LOGO = ("warp-logo.bmp", (58, 58))
INSTALLER_BANNER = ("warp-banner.bmp", (202, 385))

SILVER_FILL = 'fill="url(#silver)"'
FLAT_FILL = 'fill="#A9B7C6"'
ACCENT_FILL = 'fill="#1FD3F2"'


def source_for(size: int) -> Path:
    """Small sizes use hand-simplified geometry so the notches and carves stay readable."""
    if size <= 16:
        return SOURCES / "synth-warp-small-16.svg"
    if size <= 32:
        return SOURCES / "synth-warp-small-32.svg"
    return SOURCES / "synth-warp.svg"


def render_svg(source: Path, size: int, glyph_fill: str | None = None) -> Image.Image:
    magick = shutil.which("magick")
    if magick is None:
        raise SystemExit("ImageMagick 7 with SVG support is required")

    markup = source.read_text(encoding="utf-8")
    if glyph_fill:
        markup = markup.replace(SILVER_FILL, f'fill="{glyph_fill}"')
        markup = markup.replace(FLAT_FILL, f'fill="{glyph_fill}"')
        markup = markup.replace(ACCENT_FILL, f'fill="{glyph_fill}"')
    # Rasterize at the target size rather than downscaling from 1024. Downscaling
    # smears the plate edge into the outermost pixel, which costs the 16 px
    # variant its transparent margin and makes the tile read as a solid square.
    markup = markup.replace(
        'width="1024" height="1024"', f'width="{size}" height="{size}"', 1
    )

    with tempfile.TemporaryDirectory(prefix="synth-icon-") as temporary:
        staged = Path(temporary) / source.name
        staged.write_text(markup, encoding="utf-8")
        result = subprocess.run(
            [magick, "-background", "none", str(staged), "-strip", "png32:-"],
            check=True,
            capture_output=True,
        )

    image = Image.open(io.BytesIO(result.stdout)).convert("RGBA")
    if image.size != (size, size):
        raise SystemExit(f"{source} rendered at {image.size}, expected {size}x{size}")
    return image


def check_transparent_surround(image: Image.Image, label: str) -> None:
    """The plate is inset, so every canvas edge must be clear. An opaque edge is
    exactly what the black frame on the Windows desktop looked like."""
    width, height = image.size
    probes = (
        (0, 0),
        (width - 1, 0),
        (0, height - 1),
        (width - 1, height - 1),
        (0, height // 2),
        (width // 2, 0),
        (width - 1, height // 2),
        (width // 2, height - 1),
    )
    for point in probes:
        if image.getpixel(point)[3] != 0:
            raise SystemExit(f"{label} is opaque at {point}; the surround must be clear")


def check_ico(path: Path, expected_sizes: tuple[int, ...]) -> None:
    expected = {(size, size) for size in expected_sizes}
    with Image.open(path) as icon:
        actual_sizes = icon.ico.sizes()
        if actual_sizes != expected:
            raise SystemExit(
                f"{path} contains {sorted(actual_sizes)}, expected {sorted(expected)}"
            )
        for size in expected_sizes:
            frame = icon.ico.getimage((size, size)).convert("RGBA")
            check_transparent_surround(frame, f"{path} {size}x{size}")

    data = path.read_bytes()
    entry_count = struct.unpack_from("<H", data, 4)[0]
    for index in range(entry_count):
        entry_offset = 6 + index * 16
        width = data[entry_offset] or 256
        height = data[entry_offset + 1] or 256
        payload_offset = struct.unpack_from("<I", data, entry_offset + 12)[0]
        is_png = data[payload_offset : payload_offset + 8] == b"\x89PNG\r\n\x1a\n"
        expected_png = width == 256
        if is_png != expected_png:
            expected_encoding = "PNG" if expected_png else "BMP32"
            actual_encoding = "PNG" if is_png else "BMP32"
            raise SystemExit(
                f"{path} stores {width}x{height} as {actual_encoding}, "
                f"expected {expected_encoding}"
            )
        if not is_png:
            header_size = struct.unpack_from("<I", data, payload_offset)[0]
            bit_depth = struct.unpack_from("<H", data, payload_offset + 14)[0]
            if header_size != 40 or bit_depth != 32:
                raise SystemExit(
                    f"{path} stores {width}x{height} as a "
                    f"{header_size}-byte, {bit_depth}-bit DIB; expected BMP32"
                )


def check_png(path: Path) -> None:
    with Image.open(path) as image:
        check_transparent_surround(image.convert("RGBA"), str(path))


def save_png(path: Path, image: Image.Image) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", optimize=True)


def read_ico_entries(path: Path) -> dict[tuple[int, int], tuple[bytes, bytes]]:
    data = path.read_bytes()
    reserved, image_type, entry_count = struct.unpack_from("<HHH", data, 0)
    if reserved != 0 or image_type != 1:
        raise SystemExit(f"{path} is not a Windows icon")

    entries = {}
    for index in range(entry_count):
        entry_offset = 6 + index * 16
        width = data[entry_offset] or 256
        height = data[entry_offset + 1] or 256
        payload_size, payload_offset = struct.unpack_from(
            "<II", data, entry_offset + 8
        )
        metadata = data[entry_offset : entry_offset + 8]
        payload = data[payload_offset : payload_offset + payload_size]
        entries[(width, height)] = (metadata, payload)
    return entries


def write_ico_entries(
    path: Path,
    entries: list[tuple[bytes, bytes]],
) -> None:
    payload_offset = 6 + len(entries) * 16
    directory = bytearray(struct.pack("<HHH", 0, 1, len(entries)))
    payloads = bytearray()

    for metadata, payload in entries:
        directory.extend(metadata)
        directory.extend(struct.pack("<II", len(payload), payload_offset))
        payloads.extend(payload)
        payload_offset += len(payload)

    path.write_bytes(directory + payloads)


def save_ico(path: Path, frames: dict[int, Image.Image], sizes: tuple[int, ...]) -> None:
    """Inno Setup needs sub-256 frames as BMP32 and the 256 frame as embedded
    PNG, so splice the ImageMagick directory together with the Pillow one."""
    path.parent.mkdir(parents=True, exist_ok=True)
    magick = shutil.which("magick")
    if magick is None:
        raise SystemExit("ImageMagick 7 is required to generate Windows icons")

    with tempfile.TemporaryDirectory(prefix="synth-icon-ico-") as temporary:
        temporary_path = Path(temporary)
        frame_paths = []
        for size in sizes:
            frame_path = temporary_path / f"{size}.png"
            save_png(frame_path, frames[size])
            frame_paths.append(frame_path)

        bitmap_icon = temporary_path / "bitmap.ico"
        subprocess.run(
            [magick, *map(str, frame_paths), str(bitmap_icon)],
            check=True,
        )

        png_icon = temporary_path / "png.ico"
        frames[256].save(png_icon, format="ICO", sizes=[(256, 256)])

        bitmap_entries = read_ico_entries(bitmap_icon)
        png_entries = read_ico_entries(png_icon)
        combined_entries = []
        for size in sizes:
            source = png_entries if size == 256 else bitmap_entries
            try:
                combined_entries.append(source[(size, size)])
            except KeyError:
                raise SystemExit(f"ICO generator omitted the {size}x{size} frame")

        write_ico_entries(path, combined_entries)



def icon_dir(channel: str) -> Path:
    return ROOT / "app" / "channels" / channel / "icon" / "no-padding"


def installer_image(size: tuple[int, int]) -> Image.Image:
    """The mark centred on a plate-coloured field, flattened for a 24-bit BMP."""
    width, height = size
    edge = min(width, 160)
    canvas = Image.new("RGB", size, PLATE)
    mark = render_svg(source_for(edge), edge)
    canvas.paste(mark, ((width - edge) // 2, (height - edge) // 2), mark)
    return canvas


def check() -> None:
    for channel in CHANNELS:
        out_dir = icon_dir(channel)
        check_ico(out_dir / "icon.ico", ICO_SIZES)
        for size in PNG_SIZES:
            check_png(out_dir / f"{size}x{size}.png")
        print(f"Verified {channel} icons under {out_dir}")
    for name, size in (INSTALLER_LOGO, INSTALLER_BANNER):
        with Image.open(INSTALLER_IMAGES / name) as image:
            if image.size != size:
                raise SystemExit(f"{name} is {image.size}, expected {size}")
    print(f"Verified installer images under {INSTALLER_IMAGES}")


def apply() -> None:
    save_png(PREVIEW, render_svg(SOURCES / "synth-warp.svg", 1024))
    for channel in CHANNELS:
        out_dir = icon_dir(channel)
        for size in PNG_SIZES:
            save_png(out_dir / f"{size}x{size}.png", render_svg(source_for(size), size))
        frames = {size: render_svg(source_for(size), size) for size in ICO_SIZES}
        save_ico(out_dir / "icon.ico", frames, ICO_SIZES)
        print(f"Updated {channel} icons under {out_dir}")
    for name, size in (INSTALLER_LOGO, INSTALLER_BANNER):
        installer_image(size).save(INSTALLER_IMAGES / name, format="BMP")
    print(f"Updated installer images under {INSTALLER_IMAGES}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify generated icons without modifying files",
    )
    args = parser.parse_args()
    if args.check:
        check()
    else:
        apply()


if __name__ == "__main__":
    main()
