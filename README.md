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
- Some RC / Actual Test stems still carry OCR gaps (`_note` on items) — proofread against the book before classroom use.
- **Audio MP4s** under `audio/<level>/` are still **short silent placeholders**. Replace with real Drive exports using the same paths (`audio/manifest.json`).

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
   - Each item: `id`, `label`, `type` (`choice` | `match`), `accept`, `choices` as `{ "A": "...", ... }`
   - LC Part II / Actual Test listening items may use letter-only choices (`"A": "A"`) and `audioOnly: true` (three options for Part II Bridge).
4. `data/catalog.json` lists every practice card (titles, groups, subtitles/themes, `stub` flag).

Part II / Part IV theme subtitles follow the LearnWorlds day-split cheat sheet (see `STEP_UP_DAY_SPLITS.md` in content drops).

## Audio

- Section MP4s live under `audio/<level>/` (see `audio/manifest.json` for `practiceId` → file mapping).
- LC practices use `audioRef` on the JSON (usually same as `practiceId`; Actual Test chunks share `<prefix>-lc-at`).
- **Intermediate Part II §06** uses two files: `p2-s06a.mp4` + `p2-s06b.mp4` (two players in the UI).
- Regenerate manifest paths after structural changes: `node scripts/generate-stubs.mjs` (does not replace real MP4s if files already exist).

## Part I photos

Place images under `assets/photos/<level>/p1-sNN/` (SVG/PNG/JPG). The UI loads `placeholder.svg` until real photos are added; item `photo` fields reference filenames under that folder when multi-photo sections are wired up.

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
- English typing allowed where needed (`type: "text"`)

## License / data

Book content © YBM; MRJ practice JSON and code for classroom use.
