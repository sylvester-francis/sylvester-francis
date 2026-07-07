# Syltech AI Systems — Brand Kit

Brand assets for **Syltech AI Systems, Inc.** Identity: signal orange on ink, geometric, technical. All source art is committed as SVG; PNG/JPG are rendered outputs.

## Colors

| Role | Name | Hex |
|---|---|---|
| Primary accent | Signal Orange | `#ff5c00` |
| Accent / node | Amber | `#ffa566` |
| Background | Ink | `#0b0b0c` |
| Background 2 | Slate | `#161619` |
| Text on dark | Mist | `#cfcfd4` |
| Secondary text | Ash | `#8f8f97` |

Full rules (clear space, minimum size, typography, voice) are in **`syltech-brand-sheet.png`** / `.svg`.

Typography: heavy geometric sans, uppercase and tracked for the wordmark (Helvetica / Arial Bold; web: Archivo or Inter).

## Logo

| File | Use |
|---|---|
| `syltech-icon.svg` / `.png` | App icon / avatar (badge tile, works on light and dark) |
| `syltech-logo-horizontal.svg` / `.png` | Icon + wordmark, for headers and signatures |
| `syltech-logo-stacked.svg` / `.png` | Vertical lockup, for square spaces |
| `syltech-mark-transparent.svg` / `.png` | S mark only, transparent background |

## Favicon (`favicon/`)

`favicon.ico` (multi-res) · `favicon-16/32/48.png` · `apple-touch-icon.png` (180) · `icon-192.png` · `icon-512.png`

```html
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
```

## LinkedIn Company Page (`linkedin/`)

Sized to LinkedIn's official spec (PNG/JPEG, under 3 MB, centered, edge-safe).

| File | Slot | Size |
|---|---|---|
| `logo-400x400.png` / `.jpg` | Page logo | 400x400 |
| `cover-4200x700.jpg` / `.png` | Page cover (upload the JPG) | 4200x700 |
| `life-main-1128x376.png` | Life tab main | 1128x376 |
| `life-module-502x282.png` | Life custom module | 502x282 |
| `company-photo-900x600.png` | Company photo | 900x600 |
| `share-1200x627.png` / `.jpg` | Link-share / OG image (1.91:1) | 1200x627 |

## Covers (`cover/`)

| File | Use | Size |
|---|---|---|
| `syltech-cover-linkedin.png` / `.svg` | Compact LinkedIn cover variant | 1128x191 |
| `syltech-cover.png` / `.svg` | General brand cover / web hero | 1584x396 |

## Social posts (`social/`)

Instagram-ready, 1080x1080 unless noted (PNG + JPG).

| File | Post |
|---|---|
| `instagram-announcement-1080` | Launch announcement (square) |
| `instagram-story-1080x1920` | Launch announcement (Story) |
| `what-we-do-1080` | Three-pillar overview |
| `pillar-01-1080` | Intelligent Software & AI |
| `pillar-02-1080` | Platform & Infrastructure Engineering |
| `pillar-03-1080` | Enterprise Full-Stack Solutions |
| `open-for-work-1080` | Availability / CTA |
| `founder-about-1080` | Founder / About |

Tip: post `what-we-do` + `pillar-01/02/03` as a single carousel.

## Regenerating

All art is authored as SVG and rasterized with cairosvg. When exporting to PNG/JPG, flatten onto Ink (`#0b0b0c`) and only use the alpha channel as a paste mask when the image mode is RGBA (using it on RGB output drops the blue-zero orange).
