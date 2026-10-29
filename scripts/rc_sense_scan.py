#!/usr/bin/env python3
"""Scan RC practice JSON for CoS sense failures (instructions, OCR, accept=stem)."""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(ROOT, "data")

INSTRUCTION = re.compile(
    r"(?i)(make it negative|change to a question|rewrite|passive|active|"
    r"replace the noun with a pronoun|correct the error|participle|"
    r"put the words in order|complete the sentence|fill in|write a,? or x|"
    r"translate|following the example|correct or complete|combine|"
    r"change .+ to|turn .+ into|negative|question form|error correction|"
    r"correct the wrong|using the superlative|using the comparative|"
    r"choose .+ or write|write the full sentence|type your answer|"
    r"match the related|write as)"
)

OCR_PATTERNS = [
    (re.compile(r"______ _|_ ______"), "stray-blank"),
    (re.compile(r"\bIam\b"), "Iam-glue"),
    (re.compile(r"\bgoto\b"), "goto-glue"),
    (re.compile(r"\btogo\b"), "togo-glue"),
    (re.compile(r"Font he"), "font-he"),
    (re.compile(r"\b5re\b"), "5re"),
    (re.compile(r"\ban dId\b"), "an-dId"),
    (re.compile(r"\bcomedown\b"), "comedown"),
    (re.compile(r"whit h"), "whit-h"),
    (re.compile(r"tooth\. ______"), "tooth-dot"),
    (re.compile(r"XCH"), "XCH-junk"),
    (re.compile(r"It['']scold|It’scold"), "itscold"),
    (re.compile(r"jJ i jjiiJ"), "passage-junk"),
    (re.compile(r"\bcari sparked\b"), "cari"),
    (re.compile(r"do- doing|to stay stay"), "garbled-accept-token"),
    (re.compile(r"couldn ’the lp|Is aw"), "adv-p4-s01-ocr"),
    (re.compile(r"\bhs his\b"), "hs-his"),
]


def iter_rc():
    for level in ("basic", "intermediate", "advanced"):
        rc = os.path.join(DATA, level, "rc")
        if not os.path.isdir(rc):
            continue
        for name in sorted(os.listdir(rc)):
            if name.endswith(".json"):
                yield os.path.join(rc, name)


def main() -> int:
    no_instr: list[str] = []
    ocr_hits: list[str] = []
    accept_eq_stem: list[str] = []
    bad_intro: list[str] = []
    junk_accept: list[str] = []

    for path in iter_rc():
        d = json.load(open(path, encoding="utf-8"))
        pid = d.get("practiceId", os.path.basename(path)[:-5])
        intro = d.get("introEn") or ""
        if pid.endswith("-p4-") or re.search(r"-p4-s\d+", pid):
            has_transform = any(
                (it.get("type") == "text")
                and (it.get("section") or "") in ("Warm-Up", "Grammar Practice")
                for it in d.get("items") or []
            )
            if has_transform and re.search(r"(?i)choose the best answer", intro):
                bad_intro.append(f"{pid}: introEn={intro[:80]!r}")

        for it in d.get("items") or []:
            iid = it.get("id", "?")
            label = it.get("label", "")
            loc = f"{pid} {iid} {label}"
            ty = it.get("type")
            sec = it.get("section") or ""
            prompt = (it.get("prompt") or "").strip()
            stem = (it.get("stem") or "").strip()
            blob = json.dumps(it, ensure_ascii=False)

            for pat, name in OCR_PATTERNS:
                if pat.search(blob):
                    ocr_hits.append(f"{loc}: {name}")

            if ty == "text" and sec in ("Warm-Up", "Grammar Practice"):
                if not INSTRUCTION.search(prompt):
                    no_instr.append(f"{loc}: {prompt[:120]}")

            acc = it.get("accept")
            if ty == "text" and acc:
                accs = acc if isinstance(acc, list) else [acc]
                for a in accs:
                    s = str(a).strip()
                    if s and stem and s.lower() == stem.lower():
                        accept_eq_stem.append(f"{loc}: {stem[:100]}")
                    if s in ("x", "X") and "article" not in prompt.lower() and "Write a, or x" not in prompt:
                        if re.fullmatch(r"[xX]", s):
                            junk_accept.append(f"{loc}: accept={s!r} (non-article)")
                    if "XCH" in s or re.fullmatch(r"[xX]", s) and "article" not in prompt.lower():
                        pass
                if any("XCH" in str(x) for x in accs):
                    junk_accept.append(f"{loc}: {accs}")

    print("=== no instruction (Warm-Up/Grammar text) ===", len(no_instr))
    for x in no_instr[:80]:
        print(x)
    if len(no_instr) > 80:
        print(f"... +{len(no_instr)-80} more")

    print("\n=== OCR / garble ===", len(ocr_hits))
    for x in sorted(set(ocr_hits)):
        print(x)

    print("\n=== accept === stem ===", len(accept_eq_stem))
    for x in accept_eq_stem:
        print(x)

    print("\n=== bad introEn ===", len(bad_intro))
    for x in bad_intro:
        print(x)

    print("\n=== junk accept ===", len(junk_accept))
    for x in junk_accept:
        print(x)

    return 0


if __name__ == "__main__":
    sys.exit(main())
