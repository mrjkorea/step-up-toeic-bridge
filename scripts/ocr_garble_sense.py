#!/usr/bin/env python3
"""Fail CI if OCR garble or RC typed items lack transform instructions."""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(ROOT, "data")

INSTRUCTION_RE = re.compile(
    r"(?i)(make it negative|change to a question|rewrite|passive|active|"
    r"replace the noun with a pronoun|correct the error|participle|"
    r"put the words in order|complete the sentence|fill in the blank|fill in|"
    r"write a,? or x|translate|following the example|correct or complete|"
    r"combine|underline the adverb|change the sentence|put a slash|"
    r"choose the verb|choose the correct|find the wrong word|correct the wrong word|"
    r"match parts of the body|complete the phrase|complete the health phrase|"
    r"type your answer|write the full sentence)"
)

ARTICLE_X_OK = re.compile(r"(?i)write a,? or x|fill in a, an, the, or x|no article is needed")

OCR_CHECKS = [
    (re.compile(r"______ _|_ ______"), "stray-blank"),
    (re.compile(r"\bIam\b"), "Iam"),
    (re.compile(r"\bgoto\b"), "goto"),
    (re.compile(r"\btogo\b"), "togo"),
    (re.compile(r"Font he"), "Font-he"),
    (re.compile(r"\b5re\b"), "5re"),
    (re.compile(r"\ban dId\b"), "an-dId"),
    (re.compile(r"\bcomedown\b"), "comedown"),
    (re.compile(r"whit h"), "whit-h"),
    (re.compile(r"XCH"), "XCH"),
    (re.compile(r"It’scold|It'cold"), "itscold"),
    (re.compile(r"jJ i jjiiJ"), "passage-junk"),
    (re.compile(r"do- doing|to stay stay"), "garbled-accept"),
    (re.compile(r"couldn ’the lp|Is aw"), "ocr-stem"),
    (re.compile(r"\bhs his\b"), "hs-his"),
    (re.compile(r"The cari sparked"), "cari"),
    (re.compile(r"\bIgo\b"), "Igo"),
    (re.compile(r"fast ly"), "fast-ly"),
    (re.compile(r"dam age"), "dam-age"),
    (re.compile(r"It’stood ark"), "itstood"),
    (re.compile(r"tooth\. ______"), "tooth-dot"),
]


def iter_practice_json():
    for dirpath, _, files in os.walk(DATA):
        for name in files:
            if name.endswith(".json"):
                yield os.path.join(dirpath, name)


def needs_instruction(it: dict) -> bool:
    if it.get("type") != "text" or it.get("displayOnly"):
        return False
    if it.get("section") not in ("Warm-Up", "Grammar Practice"):
        return False
    prompt = it.get("prompt") or ""
    if INSTRUCTION_RE.search(prompt):
        return False
    stem = (it.get("stem") or "").strip()
    if "______" in stem and stem.startswith("______"):
        return False
    if re.search(r"\([^)]+\s/\s[^)]+\)", stem) and re.search(r"(?i)fill in|choose", prompt):
        return False
    return True


def check() -> list[str]:
    errors: list[str] = []
    for path in iter_practice_json():
        d = json.load(open(path, encoding="utf-8"))
        pid = d.get("practiceId", os.path.basename(path)[:-5])
        raw = json.dumps(d, ensure_ascii=False)
        for pat, tag in OCR_CHECKS:
            if pat.search(raw):
                errors.append(f"{pid}: OCR pattern {tag}")
        for it in d.get("items") or []:
            iid = it.get("id", "?")
            loc = f"{pid} {iid} {it.get('label','')}"
            if needs_instruction(it):
                errors.append(f"{loc}: missing typed instruction")
            stem = (it.get("stem") or "").strip()
            acc = it.get("accept")
            if it.get("type") == "text" and stem and acc:
                accs = acc if isinstance(acc, list) else [acc]
                for a in accs:
                    s = str(a).strip()
                    if s and s.lower() == stem.lower():
                        errors.append(f"{loc}: accept equals stem")
                    if s in ("x", "X") and not ARTICLE_X_OK.search(it.get("prompt") or ""):
                        errors.append(f"{loc}: junk accept x")
                    if "XCH" in s:
                        errors.append(f"{loc}: junk accept {s!r}")
    return sorted(set(errors))


def main() -> int:
    errors = check()
    if errors:
        print("ocr_garble_sense: FAIL", len(errors), file=sys.stderr)
        for e in errors[:200]:
            print(" ", e, file=sys.stderr)
        if len(errors) > 200:
            print(f"  ... and {len(errors)-200} more", file=sys.stderr)
        return 1
    print("ocr_garble_sense: OK (0 issues)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
