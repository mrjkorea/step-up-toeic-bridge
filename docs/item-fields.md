# Practice JSON — item fields & UI types

Content packs import into `data/<level>/<lc|rc>/<practiceId>.json`. The quiz shell reads these fields; assets live under `assets/photos/` and `audio/`.

## Practice-level

| Field | Purpose |
|--------|---------|
| `practiceId`, `title`, `level`, `skill`, `items`, `stub` | Required metadata |
| `audioRef` | LC section audio via `audio/manifest.json` |
| `photoDir` | Folder under `assets/photos/` for this practice (e.g. `basic/p1-s01`) |
| `pageImage` | **Banned** for full workbook pages. Only tight Part I picture crops (`q01`–`q06` in `p1-sNN`, or `at/qNN`) |
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
| `blocked` | When set (boolean or reason string), item is hidden from the student quiz until stems land (`#debug=1` shows locally). Not scored. |
| `photo` | Allowed only for LC Actual Test (`at/qNN.png`) and Part I Test Your Skills crops (`p1-sNN/q01`–`q06.png`). No `page-NNN` scans. |
| `pageImage` | **Banned** (full book pages). Use written `prompt` / `passage` text instead. |
| `photos` | String or array — first entry used as `pageImage` |
| `passage` | RC passage text (required for reading items; no page scan) |
| `passageHead` | e.g. “Questions 1–2 refer to the following notice.” (deduped per block) |
| `passagePage` | **Banned** — do not reference book page scans |
| `passageImage` | **Banned** — use `passage` text (or a tight figure crop path if added later) |
| `section` | In-practice banner label (e.g. Warm-Up, Words & Idioms Check-Up) |
| `wordBank` | Optional chips for `fill` / `text` (tap to insert into the input) |
| `audioClip` / `clip` | Short clip under `audio/` (self-check, repeat) |

### RC passages

Use **`passage`** (and optional `passageHead`) only. Full workbook page images are not shown to students.

Run `python3 scripts/check_practice_data.py` before publish.

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
