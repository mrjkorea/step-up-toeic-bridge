# Finish-pack clearance (2026-10-28 KST)

Follow-up drop after PR #11: resolves all **65** former deferrals (**deferred_count → 0**) by key/student-book page images. Adds **162** interactive items and **33** `displayOnly` cards (Korean-only / vocab-table Warm-Ups, not scored).

## SUMMARY.json

```json
{
 "contentVersion": "v4-finishpack-2026-10-28",
 "items_per_bucket": {
  "A": 272,
  "B": 312,
  "C": 18,
  "G": 823,
  "I": 357,
  "H": 79,
  "E": 144,
  "D": 4,
  "F": 24
 },
 "total_items": 3445,
 "validation_failures": 0,
 "deferred_count": 0,
 "deferred_per_bucket": {
  "G": 61,
  "I": 4
 },
 "renders": 532,
 "files": 117,
 "updated": "2026-10-28 KST",
 "items": 3607,
 "bucketCounts": {
  "A": 272,
  "B": 312,
  "C": 18,
  "G": 973,
  "I": 369,
  "H": 79,
  "E": 144,
  "D": 4,
  "F": 24
 },
 "deferred_before": 65,
 "displayOnly": 33,
 "interactive": 3574,
 "validationBad": 0
}
```

| Metric | Before clearance (PR #11) | After clearance |
|--------|---------------------------|-----------------|
| Total items | 3445 | **3607** |
| Deferred | 65 | **0** |
| `displayOnly` cards | — | **33** |
| Interactive (scored) | — | **3574** |

Audit trail: `scripts/overrides.py`, `scripts/postfix.py` (key page citations per override).

---

# DEFERRED — Step Up TOEIC Bridge finish-pack (rebuilt 2026-10-28 KST)

**deferred_count: 65 → 0.** There are no true impossibles left. Every former deferral was resolved by reading the key PDF page images (proof/bas-key-19..23, int-key-27..30, adv-key-28..36) and the student-book page images. The answers live in scripts/overrides.py (each entry cites its key page) and scripts/postfix.py.

## Converted to displayOnly (type "display", displayOnly:true, scored:false, with pageImage)

Under Jay's English-only rule, Korean answers are never scored. These cards show the book page image and the English source sentence.

- Korean-translation tasks: int-rc-p4-s01 WU4 (a-d), int-rc-p4-s02 WU3 (a-d), int-rc-p4-s05 WU4 (a-d), adv-rc-p4-s03 GP1 (a-d), adv-rc-p4-s04 WU4 (a-d), bas-rc-p4-s04 GP3 translation half.
- Vocabulary-table Warm-Ups (Korean meaning to English word tables, rc-p4 s06–s09, all levels): one page-image card per table.
- Total display cards: 33.

## Notes, no deferral

- adv-rc-p5-s03 Words & Idioms: the printed key reads "(a) situation (b) violence (b) amount". The second "(b)" is a key typo for (c) (proof/adv-key-35.png).
- adv-rc-p4-s05 GP2: the key prints "(d) In". It is built as choice (d) plus the text answer "In" (proof/adv-key-32.png).
