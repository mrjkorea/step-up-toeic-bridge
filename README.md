# Step Up TOEIC Bridge (MRJ)

Zap-style online practices for **YBM Step Up TOEIC Bridge** (Basic / Intermediate / Advanced). This repo is separate from the newer MRJ TOEIC Bridge banks — do not mix IDs or JSON shapes.

**Live site (GitHub Pages):** [https://mrjkorea.github.io/step-up-toeic-bridge/](https://mrjkorea.github.io/step-up-toeic-bridge/)

## Tracks

The home page lists six entry cards:

- Basic / Intermediate / Advanced × Listening (LC) / Reading (RC)

Each track has **43 practice days** aligned with LearnWorlds (section practices + five 10-question Actual Test packs). LC **AUDIO** ebook leaves are not quizzes.

## Content source

- **Practice JSON** (`data/<level>/<lc|rc>/<practiceId>.json`) is imported from the internal YBM content pack (book OCR + Drive answer-key PDFs). Re-import with:

  ```bash
  # Extract CONTENT_PACK_items_keys.tar.gz to ./_pack (not committed)
  node scripts/import-content-pack.mjs
  ```

- **Answer keys** in the pack (`keys/*-answers.json`) drive `accept` values; `stub: false` when every item has a key.
- Some RC / Actual Test stems still carry OCR gaps — import the latest content pack and run `python3 scripts/check_practice_data.py` before classroom use.
- **Section audio** — **55 MP4s** from Drive are committed under `audio/<level>/`. LC practices play them in-quiz via `audio/manifest.json` (`audioRef` on each practice JSON).

## Local preview

Static files only — any static server works:

```bash
python3 -m http.server 8080
# open http://localhost:8080/  (or http://localhost:8080/step-up-toeic-bridge/ if you serve from a parent folder)
```

Hash routes: `#/`, `#/track/intermediate-lc`, `#/practice/int-lc-p2-s01`.

## Adding or refreshing practice content

1. Edit pack items under `_pack/items/` or fix OCR in the pack, then run `node scripts/import-content-pack.mjs`.
2. To reset layout only (wipes JSON content): `node scripts/generate-stubs.mjs` — **back up** real `data/` first.
3. Required fields per practice file:
   - `practiceId`, `title`, `level`, `skill`, `items[]`, `stub`
   - Each item: `id`, `label`, `type`, `accept` (see **[docs/item-fields.md](docs/item-fields.md)**). Optional `"blocked": true` hides an item until stems are ready.
   - LC Part II / Actual Test listening items may use letter-only choices (`"A": "A"`) and `audioOnly: true` (three options for Part II Bridge).
4. `data/catalog.json` lists every practice card (titles, groups, subtitles/themes, `stub` flag).

Part II / Part IV theme subtitles follow the LearnWorlds day-split cheat sheet (see `STEP_UP_DAY_SPLITS.md` in content drops).

## Audio

- **55 section MP4s** (Drive exports) live under `audio/<level>/` and are wired through `audio/manifest.json` (`practiceId` / `audioRef` → file paths).
- The in-quiz player loads those files for LC practices (`audioRef` on the JSON; Actual Test chunks share `<prefix>-lc-at`).
- **Intermediate Part II §06** uses two files: `p2-s06a.mp4` + `p2-s06b.mp4` (two players in the UI).
- After adding or renaming tracks only: `node scripts/generate-stubs.mjs` updates manifest paths (existing MP4 files are left in place).

## Part I photos (student UI)

Students only see **tight picture crops**, not workbook page scans:

- LC Actual Test: `assets/photos/<level>/at/q01.png` … `q15.png`
- Part I Test Your Skills: `assets/photos/<level>/p1-sNN/q01.png` … `q06.png`
- Part I section picture grids (when present): `p1-sNN/wu1.jpg`, `wu2.jpg`, `lp1.jpg`, `lp2.jpg` — tight crops only, never `page-NNN`

Full book pages (`page-NNN.jpg`, `bookPages`, `pageImage`, `passageImage`, `passagePage`) are **forbidden** in the student UI and in publish checks. RC reading uses `passage` text in JSON.

Before deploy:

```bash
python3 scripts/check_practice_data.py          # full (JSON + assets)
python3 scripts/check_practice_data.py --assets-only   # page-scan files only
```

Items marked `"blocked": true` in the content pack are hidden from students until stems are ready (append `#debug=1` to preview them locally).

## Scores & sign-in

- **mrj-signin** loads from `mrjkorea.github.io/mrj-signin` (`data-mrj-app="step-up-toeic-bridge"`).
- **mrj-scores** posts to the shared Classroom Metrics sheet when a student is signed in; otherwise scores are stored in `localStorage` (`stepup.score.<practiceId>`).

## GitHub Pages

- `.nojekyll` is present for static assets.
- Pushing to `main` runs `.github/workflows/pages.yml` (artifact = repo root).
- In repo **Settings → Pages**, set source to **GitHub Actions** if not already enabled.

## Answer modes (Jay)

- LC and most RC: **A–D choice** (Part II LC: **A–C**)
- Korean meaning: **match** or **dropdown** — never require Korean typing
- English typing: `text` / `fill` (+ optional `wordBank`), **true/false** (`tf`), **listen & repeat** (`selfcheck`), Warm-Up / instruction cards (`displayOnly`)

## License / data

Book content © YBM; MRJ practice JSON and code for classroom use.
