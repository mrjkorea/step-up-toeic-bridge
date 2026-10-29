# Step Up TOEIC Bridge — book-text extracts (2026-10-30)

Sources: sources/stepuptoeicalllevelsquestions_20260415.txt (OCR of all 3 books), basic/intermediate/advanced_answers.txt, data/*.json, FAILS.json.
Every record carries practiceId + itemIdOrLabel (same string as FAILS.json) + id + app accept (unchanged).

## Coverage
| File | Fails | Fully recovered | Partial | Missing |
|---|---|---|---|---|
| tf_statements.json + tf_statements_int_adv.json | 92 | 92 (Basic 24 + Int/Adv 68 from 녹음 대본 & 정답) | 0 | 0 |
| part2_responses.json | 123 | 84 (Bas 28 high, Int 28 med-high, Adv Ex2 28 high/med) | 28 (Adv Ex1: question only) | 11 (9 Check-Up + 2 int-lc-p1-s01 Warm-Up photo items) |
| rc_blanks.json | 8 | 8 (exact, high) | 0 | 0 |
| sense_fixes.json | 5 | 5 proposals (all book-backed) | — | — |
Total: T/F lane closed (92/92). Part II: 84 full + 28 question-only + 11 blocked pending next extract.

## Apply path

Use **`python3 scripts/apply_extracts.py`** only (reads `extracts/*.json`). Do not use removed OCR-invent scripts from the earlier hardfix subagent run.

## Gaps (why) — need the book's audioscript pages (not in OCR or answer keys)
- Adv Part II Listening Practice Ex1 (1-1..1-4, 28 items): question recovered (printed partial + key blank), but its (A)(B)(C) are audio-only and differ from Ex2 (different accept letters).
- Part II Check-Up (bas-s06, int-s03, adv-s07 ×3) and int-lc-p1-s01 Warm-Up 1–2: book prints "Q. (A)(B)(C)" / photo only.
- Option if no script available: convert those items to audio-only with a "listen" note rather than inventing text.

## Confidence / caveats
- Basic Part II: Ex1 prints Q + (A)(B) exactly; (C) taken from Ex2. Book Ex1 is 2-choice — app may drop C. bas-lc-p2-s06 #3: Ex1 order (A) Yes, I do. (B) I played baseball. used (Ex2 puts it as C).
- Int Part II: Ex1 choices are audio; used Ex2 (same questions, printed 3 choices, blanks filled from key). All 28 accept letters semantically consistent.
- Adv Part II Ex2: several blank placements inferred — see per-item `note` (s02 #4 "I was a nice party." OCR/book typo; s05 #4 "Yes, I can hardly believe it." guessed filler "I can"; s06 #4 "I hope so." placement; s07 #1 C "No, I will be away for five days.").
- bas-lc-p1-s02 1-1) key F,F,F,T (sitting/relaxing = False, reading = True) — matches app accept and key, but worth a photo check.
- int-rc-p4-s03 3-(c): OCR "(All Every)" — restored slash.
- Sense: adv q5 stem should be "I was ______ my new sunglasses." (book exact). "boat"/"film"/"use a drill"/"have a meeting" are the book's exact pairings — propose verb glosses in prompt, keep accepts.
