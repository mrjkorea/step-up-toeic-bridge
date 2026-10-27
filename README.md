# Step Up TOEIC Bridge (MRJ)

Zap-style online practices for **YBM Step Up TOEIC Bridge** (Basic / Intermediate / Advanced). This repo is separate from the newer MRJ TOEIC Bridge banks — do not mix IDs or JSON shapes.

**Live site (GitHub Pages):** [https://mrjkorea.github.io/step-up-toeic-bridge/](https://mrjkorea.github.io/step-up-toeic-bridge/)

## Tracks

The home page lists six entry cards:

- Basic / Intermediate / Advanced × Listening (LC) / Reading (RC)

Each track has **43 practice days** aligned with LearnWorlds (section practices + five 10-question Actual Test packs). LC **AUDIO** ebook leaves are not quizzes.

## Pilot content

- **Intermediate LC · Part II · Section 01 (Yes/No)** — full sample (`data/intermediate/lc/int-lc-p2-s01.json`) with scoring and in-page audio.
- All other practices ship as **stubs** (empty `items[]`) so navigation and file layout are ready for content.

## Local preview

Static files only — any static server works:

```bash
python3 -m http.server 8080
# open http://localhost:8080/  (or http://localhost:8080/step-up-toeic-bridge/ if you serve from a parent folder)
```

Hash routes: `#/`, `#/track/intermediate-lc`, `#/practice/int-lc-p2-s01`.

## Adding practice content

1. Edit or replace JSON under `data/<level>/<lc|rc>/<practiceId>.json`.
2. Regenerate stubs/catalog after changing structure: `node scripts/generate-stubs.mjs` (overwrites stubs; back up real content first).
3. Required fields per practice file:
   - `practiceId`, `title`, `level`, `skill`, `items[]`
   - Each item: `id`, `label` (book question number), `type` (`choice` | `match` | `dropdown` | `text`), `accept`
   - For choice: `choices` as `{ "A": "...", "B": "...", ... }`
   - For match (Korean meaning, no typing): `pairs` + `options.right`
4. Set `stub: false` when the practice is ready.

`data/catalog.json` is generated and lists every practice card (titles, groups, subtitles/themes).

## Audio

- Section MP4s live under `audio/<level>/` (see `audio/manifest.json` for `practiceId` → file mapping).
- LC practices use `audioRef` on the JSON (usually same as `practiceId`; Actual Test chunks share `<prefix>-lc-at`).
- **Intermediate Part II §06** uses two files: `p2-s06a.mp4` + `p2-s06b.mp4` (two players in the UI).
- This scaffold commits **short silent stub MP4s**; replace with real Drive exports without renaming paths.

Regenerate stubs + manifest paths:

```bash
node scripts/generate-stubs.mjs
```

## Part I photos

Place images under `assets/photos/<level>/p1-sNN/` (SVG/PNG/JPG). The UI loads `placeholder.svg` until real photos are added; point items at specific files in JSON when you add multi-photo sections.

## Scores & sign-in

- **mrj-signin** loads from `mrjkorea.github.io/mrj-signin` (`data-mrj-app="step-up-toeic-bridge"`).
- **mrj-scores** posts to the shared Classroom Metrics sheet when a student is signed in; otherwise scores are stored in `localStorage` (`stepup.score.<practiceId>`).

## GitHub Pages

- `.nojekyll` is present for static assets.
- Pushing to `main` runs `.github/workflows/pages.yml` (artifact = repo root).
- In repo **Settings → Pages**, set source to **GitHub Actions** if not already enabled.

## Answer modes (Jay)

- LC and most RC: **A–D choice**
- Korean meaning: **match** or **dropdown** — never require Korean typing
- English typing allowed where needed (`type: "text"`)

## License / data

Book content © YBM; MRJ practice JSON and code for classroom use.
