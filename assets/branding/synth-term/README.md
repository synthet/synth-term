# Synth Term icon sources

Vector masters for every shipped Synth Term app icon and the Windows installer images. The mark is a
silver terminal window frame holding a `>_` prompt, on the Synth plate (flat `#101014`, inset
64/1024, corner radius 184, transparent surround). It is an original mark, not Warp's two-panel
logo, and shares the Synth plate with Synth Code.

| File | Used for |
| --- | --- |
| [synth-term.svg](synth-term.svg) | 48 px and up, and the 1024 px preview |
| [synth-term-small-32.svg](synth-term-small-32.svg) | 24 and 32 px: frame widened to 192..832 with an 80-unit border, heavier prompt |
| [synth-term-small-16.svg](synth-term-small-16.svg) | 16 px: frame dropped, the prompt alone on a 64-unit grid |

| Colour | Role |
| --- | --- |
| `#101014` | Plate |
| `#F8FAFC` → `#C3CFDC` → `#A9B7C6` | Silver gradient on the frame and prompt |

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
