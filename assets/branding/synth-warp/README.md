# Synth Warp icon sources

Vector masters for every shipped Synth Warp app icon and the Windows installer images. The mark is
the **carved W**: a white W with two accent-coloured S-curve carves at its top-left and bottom-right
corners, on the Synth plate (flat `#101014`, inset 64/1024, corner radius 184, transparent
surround). It is an original mark, not Warp's two-panel logo, and belongs to the same family as the
Synth Zed carved Z.

| File | Used for |
| --- | --- |
| [synth-warp.svg](synth-warp.svg) | 48 px and up, and the 1024 px preview |
| [synth-warp-small-32.svg](synth-warp-small-32.svg) | 24 and 32 px: box widened to 208..816, thicker strokes |
| [synth-warp-small-16.svg](synth-warp-small-16.svg) | 16 px: 64-unit grid, straight carves |

| Colour | Role |
| --- | --- |
| `#101014` | Plate |
| `#FFFFFF` | W |
| `#1FD3F2` | Carves |

Regenerate the PNG/ICO icons for the `oss`, `warp-oss` and `local` channels and the installer
bitmaps, or validate them without writing:

```sh
uv run --with pillow python script/apply_branding_icons.py
uv run --with pillow python script/apply_branding_icons.py --check
```

Both need ImageMagick 7 with SVG support (`magick` on `PATH`). Renders happen at each target size
rather than by downscaling, and `--check` fails if any frame has an opaque edge.

Not produced here: the macOS `AppIcon.icon` bundles and the in-app Warp marks under
`app/assets/bundled/svg/`.
