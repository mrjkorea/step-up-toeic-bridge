# Practice JSON — item fields & UI types

Content packs import into `data/<level>/<lc|rc>/<practiceId>.json`. The quiz shell reads these fields; assets live under `assets/photos/` and `audio/`.

## Practice-level

| Field | Purpose |
|--------|---------|
| `practiceId`, `title`, `level`, `skill`, `items`, `stub` | Required metadata |
| `audioRef` | LC section audio via `audio/manifest.json` |
| `photoDir` | Folder under `assets/photos/` for this practice (e.g. `basic/p1-s01`) |
| `pageImage` | **Part I** (or shared) full book page (`a`–`j` labels) shown once above all items |
| `introEn` | Short English intro above the form |

## Shared item fields

| Field | Purpose |
|--------|---------|
| `id`, `label` | Stable id + display label |
| `type` | See table below |
| `prompt` / `stem` | Question text (English) |
| `accept` | Correct answer: letter for choice/tf, string or string[] for text/fill/self-check |
| `displayOnly` | Instruction / warm-up card — not scored |
| `scored` | Set `false` to show UI but exclude from score (e.g. optional drill) |
| `photo` | Image under `assets/photos/<path>` (Warm-Up, TYS single picture, etc.) |
| `pageImage` | Per-item full page above the question (Part I letter grid, match page) |
| `photos` | String or array — first entry used as `pageImage` |
| `passage` | RC passage text (fallback when no page image) |
| `passagePage` | Book page id → `assets/photos/<level>/rc/<page>.png` or `photoDir/<page>.png` |
| `passageImage` | Explicit passage/chart image path under `assets/photos/` |
| `wordBank` | Optional chips for `fill` / `text` (tap to insert into the input) |
| `audioClip` / `clip` | Short clip under `audio/` (self-check, repeat) |

### RC passage images

Prefer a page scan over OCR `passage` when available:

1. `passageImage`: `basic/rc/p4-s02-page12.png`
2. `passagePage`: `12` → `assets/photos/basic/rc/12.png`
3. With `photoDir`: `intermediate/rc-p5-s01` + `passagePage` `chart-a` → `assets/photos/intermediate/rc-p5-s01/chart-a.png`

Duplicate passage blocks on consecutive items are collapsed when the same image or text repeats.

## Item `type` values

| `type` | UI | Grading |
|--------|-----|---------|
| `choice` (default) | A–D (or custom) radio | `accept` letter |
| `dropdown` | Same as choice | `accept` letter |
| `tf` | True / False (defaults A=True, B=False) | `accept` `A` or `B` |
| `match` | Left column + dropdowns; optional `options.right` | Each `pairs[].right` |
| `text` / `typed` | Single-line English input | Case-insensitive trim vs `accept` |
| `fill` | Text input + optional `wordBank` | Same as `text` |
| `selfcheck` / `repeat` / `listen-repeat` | Target phrase, optional clip, type and/or “I repeated aloud” | Correct if typed match **or** heard checkbox (when `allowHeard` ≠ false) |
| *(display)* | `displayOnly: true` — no input | Not in score |

Korean is never required in a text field; use `match` for Korean↔English pairing.

## Examples (for content authors)

**Typed dictation**

```json
{
  "id": "q3",
  "label": "3",
  "type": "text",
  "prompt": "Type the word you hear.",
  "accept": ["library", "Library"]
}
```

**Word-bank fill-in**

```json
{
  "id": "q2",
  "label": "2",
  "type": "fill",
  "prompt": "Complete the sentence.",
  "wordBank": ["is", "are", "am"],
  "accept": "is"
}
```

**True / false**

```json
{
  "id": "q1",
  "label": "1",
  "type": "tf",
  "prompt": "The store opens at nine.",
  "accept": "A"
}
```

**Listen & repeat (self-check)**

```json
{
  "id": "r1",
  "label": "1",
  "type": "selfcheck",
  "phrase": "Could you tell me where the station is?",
  "audioClip": "basic/clips/p2-warm-01.mp4",
  "accept": "Could you tell me where the station is?",
  "inputMode": "both"
}
```

**Part I practice page + per-question photo**

```json
{
  "practiceId": "bas-lc-p1-s01",
  "photoDir": "basic/p1-s01",
  "pageImage": "basic/p1-s01/page.png",
  "items": [
    {
      "id": "q1",
      "type": "choice",
      "photo": "basic/p1-s01/q01.png",
      "accept": "B"
    }
  ]
}
```

**Words & idioms check-up** — use normal `choice`, `match`, or `text` with book `prompt` / `pairs`; no separate type.
