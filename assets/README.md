# assets/

Put **your own** assets here — nothing brand-specific ships in this repo.

- **Fonts** — a display/bold `.ttf` for end cards and captions (the scripts default to
  [Inter / Inter Display](https://rsms.me/inter/); pass `--font path/to/YourBold.ttf`).
- **Mascot / logo** — a transparent PNG if your end card uses one (e.g. `mascot.png`). Pixel-art
  scales crisp with `Image.NEAREST` — the end-card script already does this.
- **Raw clips** — keep source footage in a separate `raw/` folder (gitignored). Sources stay
  untouched; renders go to `edit/`.

Everything in this folder except this README is gitignored, so drop assets in freely.
