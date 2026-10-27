# Photo extension fix (2026-10-28)
Unique refs before: page-*.png 532, TYS/other q*.png 72, AT */at/qNN.png 45
Unique refs after:  page-*.jpg 532, TYS/other q*.png 72 (unchanged), AT .png 45 (unchanged)
Total occurrences rewritten: 2671 (page-*.png -> .jpg). Stems/keys untouched; all JSON re-validated.

## AT Part I photos (45 new PNGs)
Auto-cropped (150 dpi, largest non-white region per half-page, 2 photos/page, q15 alone) from:
- basic: bas-lc.pdf pp.140-147 -> photos/basic/at/q01-q15.png
- intermediate: int-lc.pdf pp.135-142 -> photos/intermediate/at/q01-q15.png
- advanced: adv-lc.pdf pp.129-136 -> photos/advanced/at/q01-q15.png
Visually checked on a contact sheet; all 45 clean, order = page order (top, bottom). No gaps.
