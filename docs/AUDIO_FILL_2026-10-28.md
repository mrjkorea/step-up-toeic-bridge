# LC section audio fill import (2026-10-28)

This note records the **fill-pack** drop that adds on-screen items for answerable spoken exercises in LC section practice audio. Source: `fill-pack` tarball (CHANGELOG + DEFERRED from that pack).

## Summary

- **688** new `choice` / `audioOnly` items across **51** LC section practices (`bas|int|adv-lc-p*`, not Actual Test).
- Existing Warm-Up / Check-Up / Test Your Skills content kept; items reordered to **audio order**; renumbered `q1…qn`; one score per section practice.
- **LC Actual Test** (`*-lc-at.json`) and all **RC** practices unchanged.

## Totals by banner

| Banner | Items added |
|--------|-------------|
| Warm-Up | 272 |
| Check-Up (2) | 150 |
| Listening Practice | 84 |
| Check-Up | 64 |
| Listening Practice 2 | 36 |
| Listening Practice 1 | 33 |
| Listening Practice 3 | 29 |
| Pronunciation Check-Up | 20 |

Full per-practice before/after table: see pack `CHANGELOG.md` (mirrored below).

---

# Fill-pack CHANGELOG (2026-10-28 KST)

Items added: **688** across **51** practices. AT untouched. Drop files from `data/<level>/lc/` into the site repo `data/<level>/lc/`. All new items are `type: choice`, `audioOnly: true` (the live quiz-engine renders only choice + match). Every accept comes from the 답지 (blocks.json / key text); garbled int Part II spots read from int-key.pdf page images p.22–23.

Audio order per practice: Pronunciation Check-Up → Warm-Up → Check-Up → Listening Practice → Check-Up (2) [P1] / Listening Practice → Check-Up [P2] / Warm-Up → Listening Practice 1–3 [P3] → Test Your Skills.

Bank-style items (Check-Up fill-ins, Warm-Ups, P3 LP): choices = that block's own key answers, alphabetised; letter-only items: choices (A)/(B)/(C).

## Totals by banner
- Warm-Up: 272
- Check-Up (2): 150
- Listening Practice: 84
- Check-Up: 64
- Listening Practice 2: 36
- Listening Practice 1: 33
- Listening Practice 3: 29
- Pronunciation Check-Up: 20

## Per practice

| practiceId | before | after | added by banner |
|---|---|---|---|
| bas-lc-p1-s01 | 8 | 24 | Check-Up 4, Check-Up (2) 12 |
| bas-lc-p1-s02 | 8 | 24 | Check-Up 4, Check-Up (2) 12 |
| bas-lc-p1-s03 | 8 | 24 | Check-Up 4, Check-Up (2) 12 |
| bas-lc-p1-s04 | 8 | 30 | Pronunciation Check-Up 6, Check-Up 4, Check-Up (2) 12 |
| bas-lc-p2-s01 | 9 | 23 | Warm-Up 10, Listening Practice 4 |
| bas-lc-p2-s02 | 9 | 23 | Warm-Up 10, Listening Practice 4 |
| bas-lc-p2-s03 | 9 | 23 | Warm-Up 10, Listening Practice 4 |
| bas-lc-p2-s04 | 9 | 23 | Warm-Up 10, Listening Practice 4 |
| bas-lc-p2-s05 | 9 | 23 | Warm-Up 10, Listening Practice 4 |
| bas-lc-p2-s06 | 6 | 26 | Pronunciation Check-Up 3, Warm-Up 10, Listening Practice 4, Check-Up 3 |
| bas-lc-p2-s07 | 9 | 26 | Pronunciation Check-Up 3, Warm-Up 10, Listening Practice 4 |
| bas-lc-p3-s01 | 6 | 19 | Warm-Up 9, Listening Practice 1 1, Listening Practice 2 2, Listening Practice 3 1 |
| bas-lc-p3-s02 | 6 | 19 | Warm-Up 7, Listening Practice 1 2, Listening Practice 2 2, Listening Practice 3 2 |
| bas-lc-p3-s03 | 6 | 19 | Warm-Up 7, Listening Practice 1 2, Listening Practice 2 2, Listening Practice 3 2 |
| bas-lc-p3-s04 | 6 | 19 | Warm-Up 7, Listening Practice 1 2, Listening Practice 2 2, Listening Practice 3 2 |
| bas-lc-p3-s05 | 6 | 25 | Pronunciation Check-Up 4, Warm-Up 9, Listening Practice 1 2, Listening Practice 2 2, Listening Practice 3 2 |
| bas-lc-p3-s06 | 6 | 24 | Pronunciation Check-Up 4, Warm-Up 8, Listening Practice 1 2, Listening Practice 2 2, Listening Practice 3 2 |
| int-lc-p1-s01 | 6 | 28 | Warm-Up 2, Check-Up 5, Check-Up (2) 15 |
| int-lc-p1-s02 | 8 | 26 | Check-Up 5, Check-Up (2) 13 |
| int-lc-p1-s03 | 8 | 21 | Check-Up (2) 13 |
| int-lc-p1-s04 | 8 | 26 | Check-Up 5, Check-Up (2) 13 |
| int-lc-p2-s01 | 9 | 23 | Warm-Up 10, Listening Practice 4 |
| int-lc-p2-s02 | 9 | 23 | Warm-Up 10, Listening Practice 4 |
| int-lc-p2-s03 | 6 | 23 | Warm-Up 10, Listening Practice 4, Check-Up 3 |
| int-lc-p2-s04 | 9 | 23 | Warm-Up 10, Listening Practice 4 |
| int-lc-p2-s05 | 9 | 23 | Warm-Up 10, Listening Practice 4 |
| int-lc-p2-s06 | 9 | 23 | Warm-Up 10, Listening Practice 4 |
| int-lc-p2-s07 | 9 | 23 | Warm-Up 10, Listening Practice 4 |
| int-lc-p3-s01 | 6 | 18 | Warm-Up 6, Listening Practice 1 2, Listening Practice 2 2, Listening Practice 3 2 |
| int-lc-p3-s02 | 6 | 18 | Warm-Up 6, Listening Practice 1 2, Listening Practice 2 2, Listening Practice 3 2 |
| int-lc-p3-s03 | 6 | 17 | Warm-Up 6, Listening Practice 1 1, Listening Practice 2 2, Listening Practice 3 2 |
| int-lc-p3-s04 | 6 | 18 | Warm-Up 6, Listening Practice 1 2, Listening Practice 2 2, Listening Practice 3 2 |
| int-lc-p3-s05 | 6 | 18 | Warm-Up 6, Listening Practice 1 2, Listening Practice 2 2, Listening Practice 3 2 |
| int-lc-p3-s06 | 6 | 18 | Warm-Up 6, Listening Practice 1 2, Listening Practice 2 2, Listening Practice 3 2 |
| adv-lc-p1-s01 | 6 | 26 | Warm-Up 2, Check-Up 6, Check-Up (2) 12 |
| adv-lc-p1-s02 | 8 | 26 | Check-Up 6, Check-Up (2) 12 |
| adv-lc-p1-s03 | 8 | 26 | Check-Up 6, Check-Up (2) 12 |
| adv-lc-p1-s04 | 8 | 26 | Check-Up 6, Check-Up (2) 12 |
| adv-lc-p2-s01 | 9 | 18 | Warm-Up 5, Listening Practice 4 |
| adv-lc-p2-s02 | 9 | 18 | Warm-Up 5, Listening Practice 4 |
| adv-lc-p2-s03 | 9 | 13 | Listening Practice 4 |
| adv-lc-p2-s04 | 9 | 18 | Warm-Up 5, Listening Practice 4 |
| adv-lc-p2-s05 | 9 | 18 | Warm-Up 5, Listening Practice 4 |
| adv-lc-p2-s06 | 9 | 18 | Warm-Up 5, Listening Practice 4 |
| adv-lc-p2-s07 | 6 | 18 | Warm-Up 5, Listening Practice 4, Check-Up 3 |
| adv-lc-p3-s01 | 4 | 10 | Warm-Up 3, Listening Practice 1 1, Listening Practice 2 2 |
| adv-lc-p3-s02 | 4 | 11 | Warm-Up 3, Listening Practice 1 2, Listening Practice 2 2 |
| adv-lc-p3-s03 | 4 | 11 | Warm-Up 3, Listening Practice 1 2, Listening Practice 2 2 |
| adv-lc-p3-s04 | 6 | 15 | Warm-Up 3, Listening Practice 1 2, Listening Practice 2 2, Listening Practice 3 2 |
| adv-lc-p3-s05 | 6 | 12 | Listening Practice 1 2, Listening Practice 2 2, Listening Practice 3 2 |
| adv-lc-p3-s06 | 6 | 15 | Warm-Up 3, Listening Practice 1 2, Listening Practice 2 2, Listening Practice 3 2 |

---

# DEFERRED (not added — never guessed)

| practiceId | block | item | reason |
|---|---|---|---|
| bas-lc-p1-s01 | Listening Practice 1 & 2 | all | picture-letter match (a–j) needs book page crops; DEFERRED until photos exist |
| bas-lc-p1-s02 | Listening Practice 1 & 2 | all | picture-letter match (a–j) needs book page crops; DEFERRED until photos exist |
| bas-lc-p1-s03 | Listening Practice 1 & 2 | all | picture-letter match (a–j) needs book page crops; DEFERRED until photos exist |
| bas-lc-p1-s04 | Listening Practice 1 & 2 | all | picture-letter match (a–j) needs book page crops; DEFERRED until photos exist |
| bas-lc-p2-s01 | Listening Practice part 2 (dictation) | all | English dictation; live quiz-engine renders only choice/match (no text input yet) |
| bas-lc-p2-s02 | Listening Practice part 2 (dictation) | all | English dictation; live quiz-engine renders only choice/match (no text input yet) |
| bas-lc-p2-s03 | Listening Practice part 2 (dictation) | all | English dictation; live quiz-engine renders only choice/match (no text input yet) |
| bas-lc-p2-s04 | Listening Practice part 2 (dictation) | all | English dictation; live quiz-engine renders only choice/match (no text input yet) |
| bas-lc-p2-s05 | Listening Practice part 2 (dictation) | all | English dictation; live quiz-engine renders only choice/match (no text input yet) |
| bas-lc-p2-s06 | Listening Practice part 2 (dictation) | all | English dictation; live quiz-engine renders only choice/match (no text input yet) |
| bas-lc-p2-s07 | Listening Practice part 2 (dictation) | all | English dictation; live quiz-engine renders only choice/match (no text input yet) |
| bas-lc-p3-s01 | Listening Practice 1 | (a) | key garbled / no clue-answer separator in 답지 text: 'bread baker' |
| bas-lc-p3-s01 | Listening Practice 3 | (a) | key garbled / no clue-answer separator in 답지 text: '8:40 At 9:00' |
| int-lc-p1-s01 | Listening Practice 1 & 2 | all | picture-letter match (a–j) needs book page crops; DEFERRED until photos exist |
| int-lc-p1-s02 | Listening Practice 1 & 2 | all | picture-letter match (a–j) needs book page crops; DEFERRED until photos exist |
| int-lc-p1-s03 | Listening Practice 1 & 2 | all | picture-letter match (a–j) needs book page crops; DEFERRED until photos exist |
| int-lc-p1-s04 | Listening Practice 1 & 2 | all | picture-letter match (a–j) needs book page crops; DEFERRED until photos exist |
| int-lc-p2-s01 | Listening Practice part 2 (dictation) | all | English dictation; live quiz-engine renders only choice/match (no text input yet) |
| int-lc-p2-s02 | Listening Practice part 2 (dictation) | all | English dictation; live quiz-engine renders only choice/match (no text input yet) |
| int-lc-p2-s03 | Listening Practice part 2 (dictation) | all | English dictation; live quiz-engine renders only choice/match (no text input yet) |
| int-lc-p2-s04 | Listening Practice part 2 (dictation) | all | English dictation; live quiz-engine renders only choice/match (no text input yet) |
| int-lc-p2-s05 | Listening Practice part 2 (dictation) | all | English dictation; live quiz-engine renders only choice/match (no text input yet) |
| int-lc-p2-s06 | Listening Practice part 2 (dictation) | all | English dictation; live quiz-engine renders only choice/match (no text input yet) |
| int-lc-p2-s07 | Listening Practice part 2 (dictation) | all | English dictation; live quiz-engine renders only choice/match (no text input yet) |
| int-lc-p3-s03 | Listening Practice 1 | (a) | key garbled / no clue-answer separator in 답지 text: 'make it See you then. At five' |
| adv-lc-p1-s01 | Listening Practice 1 & 2 | all | picture-letter match (a–j) needs book page crops; DEFERRED until photos exist |
| adv-lc-p1-s01 | Check-Up (2) part 2 | all | paraphrase pairs ("repair a car - fix a car"): no answerable stem without book page; needs text-entry type the app does not render |
| adv-lc-p1-s02 | Listening Practice 1 & 2 | all | picture-letter match (a–j) needs book page crops; DEFERRED until photos exist |
| adv-lc-p1-s02 | Check-Up (2) part 2 | all | paraphrase pairs ("repair a car - fix a car"): no answerable stem without book page; needs text-entry type the app does not render |
| adv-lc-p1-s03 | Listening Practice 1 & 2 | all | picture-letter match (a–j) needs book page crops; DEFERRED until photos exist |
| adv-lc-p1-s03 | Check-Up (2) part 2 | all | paraphrase pairs ("repair a car - fix a car"): no answerable stem without book page; needs text-entry type the app does not render |
| adv-lc-p1-s04 | Listening Practice 1 & 2 | all | picture-letter match (a–j) needs book page crops; DEFERRED until photos exist |
| adv-lc-p1-s04 | Check-Up (2) part 2 | all | paraphrase pairs ("repair a car - fix a car"): no answerable stem without book page; needs text-entry type the app does not render |
| adv-lc-p2-s01 | Warm-Up 2 | all | two-blank dictation pairs / garbled; app has no text-entry renderer |
| adv-lc-p2-s01 | Listening Practice part 2 (dictation) | all | English dictation; live quiz-engine renders only choice/match (no text input yet) |
| adv-lc-p2-s02 | Warm-Up 2 | all | two-blank dictation pairs / garbled; app has no text-entry renderer |
| adv-lc-p2-s02 | Listening Practice part 2 (dictation) | all | English dictation; live quiz-engine renders only choice/match (no text input yet) |
| adv-lc-p2-s03 | Warm-Up 1 & 2 | all | two-blank dictation pairs / garbled; app has no text-entry renderer |
| adv-lc-p2-s03 | Listening Practice part 2 (dictation) | all | English dictation; live quiz-engine renders only choice/match (no text input yet) |
| adv-lc-p2-s04 | Warm-Up 2 | all | two-blank dictation pairs / garbled; app has no text-entry renderer |
| adv-lc-p2-s04 | Listening Practice part 2 (dictation) | all | English dictation; live quiz-engine renders only choice/match (no text input yet) |
| adv-lc-p2-s05 | Warm-Up 2 | all | two-blank dictation pairs / garbled; app has no text-entry renderer |
| adv-lc-p2-s05 | Listening Practice part 2 (dictation) | all | English dictation; live quiz-engine renders only choice/match (no text input yet) |
| adv-lc-p2-s06 | Warm-Up 2 | all | two-blank dictation pairs / garbled; app has no text-entry renderer |
| adv-lc-p2-s06 | Listening Practice part 2 (dictation) | all | English dictation; live quiz-engine renders only choice/match (no text input yet) |
| adv-lc-p2-s07 | Warm-Up 2 | all | two-blank dictation pairs / garbled; app has no text-entry renderer |
| adv-lc-p2-s07 | Listening Practice part 2 (dictation) | all | English dictation; live quiz-engine renders only choice/match (no text input yet) |
| adv-lc-p3-s01 | Listening Practice 1 | (a) | key garbled / no clue-answer separator in 답지 text: None |
| adv-lc-p3-s05 | Warm-Up | all | key missing/garbled in 답지 text layer |
| bas-lc-p2-s06 | Pronunciation Check-Up 2 | all | key "(c) d3" garbled phonetic symbol |
| bas-lc-p2-s07 | Pronunciation Check-Up 1 | all | key "0 / Ŏ" garbled phonetic symbols |
| adv-lc-p2-s03 | Warm-Up 1 | all | item (d)/(e) run together in 답지 text ("eWhich car is yours? ()") |
| int-lc-p1-s03 | Check-Up (first) | all | columns interleaved ("a lot of cars table … on the") |
| adv-lc-p3-s05 | Warm-Up | all | Warm-Up key not printed/merged into Words header |
| ALL | Pronunciation listen-and-repeat | all | no answers (out of scope) |
| ALL | Words and Idioms [Check-Up] | all | not in audio (out of scope) |
