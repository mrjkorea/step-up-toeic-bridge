# Script hunt — 2026-10-30

## Found
The answer-key PDFs ARE "녹음 대본 & 정답" booklets with full audioscripts. Local copies (no new Drive download needed):
- /workspace/toeic-bridge/build-pack/pdf/int-key.pdf — Part I scripts on PDF pages 3–6 (book p.298–301)
- /workspace/toeic-bridge/build-pack/pdf/adv-key.pdf — Part I scripts on PDF pages 3–6 (book p.294–297)
- bas-key.pdf has scripts too. The student-book LC PDFs (int-lc/adv-lc/bas-lc) have NO audioscript pages.

pdftotext output is jumbled (two columns plus rotated text), so the statements were read from rendered page images (pdftoppm -r 110 → /tmp/pg/*.png).
The positional mapping (a..d/f within 1-1, 1-2) was checked against the T/F keys and every line made sense (e.g. int s01 1-1 bicycle T T F F).

## Recovered
- tf_statements_int_adv.json: 68/68 null Check-Up (2) statements (int s01–s04 ×8, adv s02–s04 ×12). confidence high.

## Still missing
- Part II: 39 entries in part2_responses.json still need text (adv-lc-p2-s01..s07, bas-lc-p2-s06, int-lc-p2-s03, plus 2 under int-lc-p1-s01).
  Their scripts are in the same key PDFs (adv Part II starts on PDF p.6; int Part II starts on p.6). I have NOT transcribed them yet, so part2_remaining.json was not written.
- No Drive search was needed. The local key PDFs already cover this.
