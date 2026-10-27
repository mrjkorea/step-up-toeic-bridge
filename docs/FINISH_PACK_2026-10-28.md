# Finish-pack import (2026-10-28)

This note records the **finish-pack** drop (`v4-finishpack-2026-10-28`) that completes practice JSON for LC and RC across Basic, Intermediate, and Advanced. Source: finish-pack data tarball (CHANGELOG, DEFERRED, SUMMARY from that pack).

## Clearance follow-up (2026-10-28 KST)

A second drop cleared all **65** deferrals (**deferred_count → 0**), raising total items **3445 → 3607** (+33 `displayOnly` cards for Korean-only / vocab-table Warm-Ups; **3574** interactive). See **`docs/FINISH_PACK_CLEARANCE_2026-10-28.md`** for the rebuilt DEFERRED note and clearance `SUMMARY.json`. Overrides: `scripts/overrides.py`, `scripts/postfix.py`.

## Summary (SUMMARY.json) — initial PR #11 import

| Field | Value |
|--------|--------|
| `contentVersion` | `v4-finishpack-2026-10-28` |
| Practice JSON files | **117** (`data/{basic,intermediate,advanced}/{lc,rc}/`) |
| Total items | **3445** (was **1584** on live `_live` data) |
| `validation_failures` | 0 |
| Deferred (not built) | **65** (G=61, I=4) |
| Page renders (photos pack) | 532 |

### Items per bucket

| Bucket | Count | Meaning (from pack README) |
|--------|------|------------------------------|
| A | 272 | P1 picture-letter match |
| B | 312 | P2 dictation + adv paraphrase |
| C | 18 | garbled keys |
| D | 4 | truncated choices |
| E | 144 | RC passageImage |
| F | 24 | Warm-Up P1 photos |
| G | 823 | non-MC blocks |
| H | 79 | pronunciation repeat |
| I | 357 | Words & Idioms Check-Up |

**New/fixed items this session (CHANGELOG):** RP questions now read with tesseract OCR of 250dpi page renders (the PDF text layer was garbled); `adv-lc-p1-s01` LP1 slash-less item 8 fixed; `adv-lc-p3-s01` LP1 dictation hardcoded from the key image; OCR-duplicated answers collapsed; real hyphenated words (Check-in, toll-free) kept.

### Site changes

- Replaced all **117** practice JSON files under `data/`.
- Cache bust: `index.html` → `app.js?v=8`.
- Photos: **532** JPEG page crops merged from photo shards into `assets/photos/<level>/...` (see pack README path map). Test Your Skills items keep existing `q01`–`q06` **PNG** photo paths; new Warm-Up / LP / RC renders use **`.jpg`** page crops.
- Quiz engine and scoring UI unchanged except cache bust (scoring UI per PR #10).

---

# CHANGELOG — finish-pack v4-finishpack-2026-10-28

Per-practice item counts (before = live _live data, after = finish-pack):

| practice | before | after |
|---|---|---|
| adv-lc-at | 50 | 50 |
| adv-lc-p1-s01 | 26 | 70 |
| adv-lc-p1-s02 | 26 | 70 |
| adv-lc-p1-s03 | 26 | 68 |
| adv-lc-p1-s04 | 26 | 72 |
| adv-lc-p2-s01 | 18 | 45 |
| adv-lc-p2-s02 | 18 | 45 |
| adv-lc-p2-s03 | 13 | 45 |
| adv-lc-p2-s04 | 18 | 45 |
| adv-lc-p2-s05 | 18 | 45 |
| adv-lc-p2-s06 | 18 | 44 |
| adv-lc-p2-s07 | 18 | 45 |
| adv-lc-p3-s01 | 10 | 24 |
| adv-lc-p3-s02 | 11 | 27 |
| adv-lc-p3-s03 | 11 | 25 |
| adv-lc-p3-s04 | 15 | 32 |
| adv-lc-p3-s05 | 12 | 32 |
| adv-lc-p3-s06 | 15 | 31 |
| adv-rc-at-q01-10 | 10 | 10 |
| adv-rc-at-q11-20 | 10 | 10 |
| adv-rc-at-q21-30 | 10 | 10 |
| adv-rc-at-q31-40 | 10 | 10 |
| adv-rc-at-q41-50 | 10 | 10 |
| adv-rc-p4-s01 | 6 | 21 |
| adv-rc-p4-s02 | 6 | 35 |
| adv-rc-p4-s03 | 6 | 31 |
| adv-rc-p4-s04 | 6 | 19 |
| adv-rc-p4-s05 | 6 | 6 |
| adv-rc-p4-s06 | 4 | 20 |
| adv-rc-p4-s07 | 4 | 19 |
| adv-rc-p4-s08 | 4 | 21 |
| adv-rc-p4-s09 | 4 | 21 |
| adv-rc-p5-s01 | 4 | 21 |
| adv-rc-p5-s02 | 4 | 20 |
| adv-rc-p5-s03 | 4 | 17 |
| adv-rc-p5-s04 | 4 | 19 |
| adv-rc-p5-s05 | 4 | 19 |
| adv-rc-p5-s06 | 4 | 19 |
| adv-rc-p5-s07 | 4 | 20 |
| bas-lc-at | 50 | 50 |
| bas-lc-p1-s01 | 24 | 50 |
| bas-lc-p1-s02 | 24 | 51 |
| bas-lc-p1-s03 | 24 | 52 |
| bas-lc-p1-s04 | 30 | 50 |
| bas-lc-p2-s01 | 23 | 41 |
| bas-lc-p2-s02 | 23 | 42 |
| bas-lc-p2-s03 | 23 | 40 |
| bas-lc-p2-s04 | 23 | 40 |
| bas-lc-p2-s05 | 23 | 40 |
| bas-lc-p2-s06 | 26 | 40 |
| bas-lc-p2-s07 | 26 | 39 |
| bas-lc-p3-s01 | 19 | 31 |
| bas-lc-p3-s02 | 19 | 31 |
| bas-lc-p3-s03 | 19 | 29 |
| bas-lc-p3-s04 | 19 | 30 |
| bas-lc-p3-s05 | 25 | 31 |
| bas-lc-p3-s06 | 24 | 32 |
| bas-rc-at-q01-10 | 10 | 10 |
| bas-rc-at-q11-20 | 10 | 10 |
| bas-rc-at-q21-30 | 10 | 10 |
| bas-rc-at-q31-40 | 10 | 10 |
| bas-rc-at-q41-50 | 10 | 10 |
| bas-rc-p4-s01 | 6 | 36 |
| bas-rc-p4-s02 | 6 | 28 |
| bas-rc-p4-s03 | 6 | 33 |
| bas-rc-p4-s04 | 6 | 33 |
| bas-rc-p4-s05 | 6 | 34 |
| bas-rc-p4-s06 | 4 | 17 |
| bas-rc-p4-s07 | 4 | 17 |
| bas-rc-p4-s08 | 4 | 17 |
| bas-rc-p4-s09 | 4 | 17 |
| bas-rc-p5-s01 | 4 | 21 |
| bas-rc-p5-s02 | 4 | 20 |
| bas-rc-p5-s03 | 4 | 21 |
| bas-rc-p5-s04 | 4 | 21 |
| bas-rc-p5-s05 | 4 | 21 |
| bas-rc-p5-s06 | 4 | 21 |
| bas-rc-p5-s07 | 4 | 20 |
| int-lc-at | 50 | 50 |
| int-lc-p1-s01 | 28 | 51 |
| int-lc-p1-s02 | 26 | 46 |
| int-lc-p1-s03 | 21 | 49 |
| int-lc-p1-s04 | 26 | 49 |
| int-lc-p2-s01 | 23 | 41 |
| int-lc-p2-s02 | 23 | 42 |
| int-lc-p2-s03 | 23 | 40 |
| int-lc-p2-s04 | 23 | 38 |
| int-lc-p2-s05 | 23 | 36 |
| int-lc-p2-s06 | 23 | 37 |
| int-lc-p2-s07 | 23 | 40 |
| int-lc-p3-s01 | 18 | 36 |
| int-lc-p3-s02 | 18 | 39 |
| int-lc-p3-s03 | 17 | 31 |
| int-lc-p3-s04 | 18 | 34 |
| int-lc-p3-s05 | 18 | 32 |
| int-lc-p3-s06 | 18 | 31 |
| int-rc-at-q01-10 | 10 | 10 |
| int-rc-at-q11-20 | 10 | 10 |
| int-rc-at-q21-30 | 10 | 10 |
| int-rc-at-q31-40 | 10 | 10 |
| int-rc-at-q41-50 | 10 | 10 |
| int-rc-p4-s01 | 6 | 37 |
| int-rc-p4-s02 | 6 | 18 |
| int-rc-p4-s03 | 6 | 6 |
| int-rc-p4-s04 | 6 | 38 |
| int-rc-p4-s05 | 6 | 28 |
| int-rc-p4-s06 | 4 | 20 |
| int-rc-p4-s07 | 4 | 17 |
| int-rc-p4-s08 | 4 | 17 |
| int-rc-p4-s09 | 4 | 18 |
| int-rc-p5-s01 | 4 | 18 |
| int-rc-p5-s02 | 4 | 17 |
| int-rc-p5-s03 | 4 | 18 |
| int-rc-p5-s04 | 4 | 21 |
| int-rc-p5-s05 | 4 | 17 |
| int-rc-p5-s06 | 4 | 21 |
| int-rc-p5-s07 | 4 | 23 |

**Totals:** before 1584, after 3445.

New/fixed items per bucket: A=272, B=312, C=18, D=4, E=144, F=24, G=823, H=79, I=357.

---

# DEFERRED — items not built (proof per item)

Every row quotes the literal key text from keytree.json / the PDF key page. None is "out of scope"; each is a key that is Korean-only (English-only rule), empty, or ambiguous so that building it would mean inventing an answer.

| bucket | practice | section/label | reason | key text (literal) |
|---|---|---|---|---|
| G | bas-rc-p4-s02 | Warm-Up 1-(a) | key gives a multi-word alternative set that cannot be split into exact accepts without guessing | David and Diane / love movies. |
| G | bas-rc-p4-s02 | Warm-Up 1-(b) | key gives a multi-word alternative set that cannot be split into exact accepts without guessing | You and I/learn English at school. |
| G | bas-rc-p4-s02 | Grammar Practice 1-(a) | Korean | window/ 창문을 |
| G | bas-rc-p4-s02 | Grammar Practice 1-(b) | key gives a multi-word alternative set that cannot be split into exact accepts without guessing | fly / 난다 (C) He / 그는 |
| G | bas-rc-p4-s02 | Grammar Practice 2-(a) | answer is Korean/blank in key (English-only rule) | 동사 |
| G | bas-rc-p4-s02 | Grammar Practice 2-(b) | answer is Korean/blank in key (English-only rule) | 목적어 |
| G | bas-rc-p4-s02 | Grammar Practice 2-(c) | answer is Korean/blank in key (English-only rule) | 주어 |
| G | bas-rc-p4-s03 | Grammar Practice 4-(a) | key shows a word pair joined by a dash (two-blank answer); split ambiguous | tooth-tooths |
| G | bas-rc-p4-s03 | Grammar Practice 4-(b) | key shows a word pair joined by a dash (two-blank answer); split ambiguous | knife-knifes |
| G | bas-rc-p4-s03 | Grammar Practice 4-(c) | key shows a word pair joined by a dash (two-blank answer); split ambiguous | foot-foots |
| G | bas-rc-p4-s04 | Grammar Practice 3-(a) | key gives a multi-word alternative set that cannot be split into exact accepts without guessing | Jane bought shoes. / X |
| G | bas-rc-p4-s04 | Grammar Practice 3-(b) | key gives a multi-word alternative set that cannot be split into exact accepts without guessing | Jane is buying shoes. / X |
| G | bas-rc-p4-s04 | Grammar Practice 3-(c) | key gives a multi-word alternative set that cannot be split into exact accepts without guessing | Jane does not buy shoes. / 제인이 신발을 사지 않는다. |
| G | bas-rc-p4-s06 | Warm-Up | vocabulary table / Korean-only key, no blank answers |  |
| G | bas-rc-p4-s07 | Warm-Up | vocabulary table / Korean-only key, no blank answers |  |
| G | bas-rc-p4-s08 | Warm-Up | vocabulary table / Korean-only key, no blank answers |  |
| G | bas-rc-p4-s09 | Warm-Up | vocabulary table / Korean-only key, no blank answers |  |
| G | bas-rc-p5-s07 | Warm-Up 1- | key text empty/garbled | Check-in |
| G | int-rc-p4-s01 | Warm-Up 4-(a) | answer is Korean/blank in key (English-only rule) | 식사 중인 (C) 개는 |
| G | int-rc-p4-s01 | Warm-Up 4-(b) | answer is Korean/blank in key (English-only rule) | 뉴턴과 같은 사람 |
| G | int-rc-p4-s01 | Warm-Up 4-(d) | answer is Korean/blank in key (English-only rule) | 잠자리에 든다. |
| G | int-rc-p4-s02 | Warm-Up 1-(d) | key text empty/garbled |  |
| G | int-rc-p4-s02 | Warm-Up 3-(a) | answer is Korean/blank in key (English-only rule) | 너는 이 문제를 풀 수 있니? |
| G | int-rc-p4-s02 | Warm-Up 3-(b) | answer is Korean/blank in key (English-only rule) | 그녀는 아마 스파이인 것 같아. |
| G | int-rc-p4-s02 | Warm-Up 3-(c) | answer is Korean/blank in key (English-only rule) | 우리는 저녁 7시 이전에 호텔에 도착해야만 해. |
| G | int-rc-p4-s02 | Warm-Up 3-(d) | answer is Korean/blank in key (English-only rule) | 그는 분명 피곤할 것이다. |
| G | int-rc-p4-s02 | Grammar Practice | answer-key OCR scrambled: text before first marker: will be | will be (b) am 1. (a) wills will (c) plays play (d) is - be 2. (a) should (b) did (c) must should do 3. (c) should be 4. (a) |
| I | int-rc-p4-s03 | Words and Idioms Check-Up | answer-key OCR scrambled: duplicate None(b); duplicate None(c); duplicate None(d) | (a) president (b) ghost (c) auditorium (d) coin -Up IWarm1.a) ninth (b) fifth (c) twelfth (d) twentieth (e) ninetieth (f) twenty-first (g) second (h)  |
| G | int-rc-p4-s03 | Grammar Practice | answer-key OCR scrambled: duplicate 1(a); duplicate 3(b); duplicate 3(c) | 1. (a) five thousand four hundred sixty-two (b) three fifths (c) two point four seven eight zero nine five three four two f) (d) two thousand seven (e |
| G | int-rc-p4-s04 | Warm-Up 3-(c) | key shows a word pair joined by a dash (two-blank answer); split ambiguous | expensively-expensive |
| G | int-rc-p4-s05 | Warm-Up 2-(a) | key gives a multi-word alternative set that cannot be split into exact accepts without guessing | more most / more - most best / better - best |
| G | int-rc-p4-s05 | Warm-Up 2-(c) | key gives a multi-word alternative set that cannot be split into exact accepts without guessing | worse worst / worse - worst |
| G | int-rc-p4-s05 | Warm-Up 4-(a) | answer is Korean/blank in key (English-only rule) | 탐은 그의 친구 제임스보다 더 빨리 달린다. |
| G | int-rc-p4-s05 | Warm-Up 4-(b) | answer is Korean/blank in key (English-only rule) | 존은 데이빗보다 더 유명하다. (C) 엘리스의 차는 캐시의 차보다 더 비싸다. |
| G | int-rc-p4-s05 | Warm-Up 4-(d) | answer is Korean/blank in key (English-only rule) | 리타는 학급에서 가장 아름다운 소녀이다. |
| G | int-rc-p4-s06 | Warm-Up | vocabulary table / Korean-only key, no blank answers |  |
| G | int-rc-p4-s07 | Warm-Up | vocabulary table / Korean-only key, no blank answers |  |
| G | int-rc-p4-s08 | Warm-Up | vocabulary table / Korean-only key, no blank answers |  |
| G | int-rc-p4-s08 | Vocabulary Practice 3-(d) | key gives a multi-word alternative set that cannot be split into exact accepts without guessing | scuba diving / dangerous |
| G | int-rc-p4-s09 | Warm-Up | vocabulary table / Korean-only key, no blank answers |  |
| I | adv-lc-p3-s05 | Words and Idioms Check-Up (e) | key text empty/garbled | illegal -Up /Warm1.Take out all electronic devices |
| G | adv-rc-p4-s01 | Warm-Up | answer-key OCR scrambled: duplicate 3(b); duplicate 3(d) | 1. (a) to see (b) visiting (c) getting 2. (a) what to wear (d) to meet (c) when to leave 3. (a) go (b) how to start (d) where to meet (b) to do (c) wo |
| G | adv-rc-p4-s01 | Grammar Practice 1- | key gives a multi-word alternative set that cannot be split into exact accepts without guessing | playing to come / finishing / to take |
| G | adv-rc-p4-s01 | Grammar Practice 3-(d) | key gives a multi-word alternative set that cannot be split into exact accepts without guessing | / |
| G | adv-rc-p4-s01 | Grammar Practice 4-(a) | answer is Korean/blank in key (English-only rule) | 형용사적 용법 |
| G | adv-rc-p4-s01 | Grammar Practice 4-(b) | answer is Korean/blank in key (English-only rule) | 명사적 용법 (C) 부사적 용법 |
| G | adv-rc-p4-s01 | Grammar Practice 4-(d) | answer is Korean/blank in key (English-only rule) | 부사적 용법 |
| G | adv-rc-p4-s02 | Grammar Practice 1-1) | key text empty/garbled |  |
| G | adv-rc-p4-s02 | Grammar Practice 2-(d) | key gives a multi-word alternative set that cannot be split into exact accepts without guessing | / boring - bored |
| G | adv-rc-p4-s03 | Grammar Practice 1-(a) | answer is Korean/blank in key (English-only rule) | 부자들이 항상 행복한 것은 아니다. |
| G | adv-rc-p4-s03 | Grammar Practice 1-(b) | answer is Korean/blank in key (English-only rule) | 고인은 나라를 위해 사셨다고 한다. (C) 학급의 5분의 1은 하와이로 여행 가기를 원한다. |
| G | adv-rc-p4-s03 | Grammar Practice 1-(d) | answer is Korean/blank in key (English-only rule) | 내 가족은 대가족이다. |
| G | adv-rc-p4-s04 | Warm-Up 4-(a) | answer is Korean/blank in key (English-only rule) | 그것들은 값이 쌀 뿐만 아니라 유용하다. |
| G | adv-rc-p4-s04 | Warm-Up 4-(b) | answer is Korean/blank in key (English-only rule) | 지금 일어나. 그렇지 않으면 기차를 놓칠 거야. |
| G | adv-rc-p4-s04 | Warm-Up 4-(c) | answer is Korean/blank in key (English-only rule) | 많은 사람들은 그가 다른 나라의 스파이라고 주장한다. |
| G | adv-rc-p4-s04 | Warm-Up 4-(d) | answer is Korean/blank in key (English-only rule) | 나의 아버지와 삼촌 모두 그 비밀을 모른다. |
| G | adv-rc-p4-s04 | Grammar Practice | answer-key OCR scrambled: duplicate 3(d); duplicate 3(d); duplicate 3(c) | 1. (a) if/or (c) if (b) because 2. (a), (b) since 3. (a) when (d) Although (c), (d) as (b) where (d) which/that (c) when 4. (a) In case of (c) While ( |
| I | adv-rc-p4-s05 | Words and Idioms Check-Up | answer-key OCR scrambled: text before first marker: fill out c | fill out c (a) keep an eye on (b) think about (d) take pictures |
| G | adv-rc-p4-s05 | Warm-Up | answer-key OCR scrambled: duplicate 3(b); duplicate 3(d) | 1. (c)(a) on by (b) in -on (d) with of 2. (a) in /for (c) for 3. (a), (b) by (b) at/on (d) in (c), (d) for |
| G | adv-rc-p4-s05 | Grammar Practice | answer-key OCR scrambled: duplicate 4(b); duplicate 4(d) | 1. (a) between (b) by (c) under (d) on 2. (d) In 3. (a) by (c) from 4. (a) for (c) within (b) until (d) since (b) during (d) after 5. (a) Because of t |
| G | adv-rc-p4-s06 | Warm-Up | vocabulary table / Korean-only key, no blank answers |  |
| G | adv-rc-p4-s07 | Warm-Up | vocabulary table / Korean-only key, no blank answers |  |
| G | adv-rc-p4-s08 | Warm-Up | vocabulary table / Korean-only key, no blank answers |  |
| G | adv-rc-p4-s09 | Warm-Up | vocabulary table / Korean-only key, no blank answers |  |
| I | adv-rc-p5-s03 | Words and Idioms Check-Up | answer-key OCR scrambled: duplicate None(b) | (a) situation (b) violence (b) amount |
