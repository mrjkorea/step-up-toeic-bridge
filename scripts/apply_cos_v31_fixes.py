#!/usr/bin/env python3
"""Apply CoS v31 content fixes (run once)."""
from __future__ import annotations

import json
import os
import re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA = os.path.join(ROOT, "data")

FILL_LABEL = "Fill in the blank:"
COMPOUND_LABEL = "Complete the compound word:"


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def set_prompt(item: dict, new_prefix: str, stem: str | None = None) -> None:
    st = stem if stem is not None else (item.get("stem") or "")
    label_m = re.match(r"^[^:]+:\s*", item.get("prompt") or "")
    head = label_m.group(0) if label_m else ""
    if not head:
        sec = item.get("section") or "Item"
        lab = item.get("label") or ""
        head = f"{sec} {lab}: " if lab else f"{sec}: "
    item["prompt"] = f"{head}{new_prefix} {st}".strip()


def is_sentence_fill(st: str) -> bool:
    if st.count("______") != 1:
        return False
    if "." in st or "?" in st:
        return True
    if st.strip().startswith("______"):
        return True
    return bool(
        re.search(
            r"\b(I|My|We|They|She|He|It|The|Can I|Jane|Paul|Laura|Students|If you|In winter|The bakers|This)\b",
            st,
        )
    )


def replace_odd_one_out_sentence(item: dict) -> None:
    set_prompt(item, FILL_LABEL)


def replace_vp2_vague(item: dict, label: str = COMPOUND_LABEL) -> None:
    pr = item.get("prompt") or ""
    if not re.search(r"correct or complete it", pr, re.I):
        return
    m = re.search(r"(Vocabulary Practice 2-\([a-d]\):\s*)", pr)
    if not m:
        return
    stem = item.get("stem") or re.split(r"\s*[—–-]\s*", pr, maxsplit=1)[-1].strip()
    item["prompt"] = f"{m.group(1)}{label} {stem}"


def main() -> None:
    # int-rc-p4-s07 VP3
    p = os.path.join(DATA, "intermediate/rc/int-rc-p4-s07.json")
    d = load(p)
    for iid in ("q12", "q13", "q14"):
        for it in d["items"]:
            if it.get("id") == iid:
                replace_odd_one_out_sentence(it)
    save(p, d)

    # int-rc-p4-s08
    p = os.path.join(DATA, "intermediate/rc/int-rc-p4-s08.json")
    d = load(p)
    for it in d["items"]:
        if it.get("id") == "q9":
            it["stem"] = "playing ______ with pets"
            it["prompt"] = "Vocabulary Practice 2-(a): Complete the phrase: playing ______ with pets"
            it["accept"] = ["with", "playing with pets"]
        elif it.get("id") in ("q10", "q11", "q12"):
            replace_vp2_vague(it)
        elif it.get("id") == "q14":
            replace_odd_one_out_sentence(it)
        elif it.get("id") == "q15":
            st = "Have you watched the movie that has been released recently? It was very ______."
            it["stem"] = st
            it["prompt"] = f"Vocabulary Practice 3-(c): Complete the sentence: {st}"
    save(p, d)

    # int-rc-p4-s09
    p = os.path.join(DATA, "intermediate/rc/int-rc-p4-s09.json")
    d = load(p)
    for it in d["items"]:
        if it.get("id") == "q6":
            st = "toothpaste / toothbrush / nightstand / washstand"
            it["stem"] = st
            it["prompt"] = (
                "Vocabulary Practice 1-(b): Write the word that does not belong with the other three — "
                + st
            )
            it["accept"] = ["nightstand"]
        elif it.get("id") in ("q8", "q9", "q10", "q11"):
            replace_vp2_vague(it)
        elif it.get("id") in ("q12", "q14"):
            replace_odd_one_out_sentence(it)
    save(p, d)

    # int-rc-p4-s06 VP2
    p = os.path.join(DATA, "intermediate/rc/int-rc-p4-s06.json")
    d = load(p)
    for it in d["items"]:
        replace_vp2_vague(it)
    save(p, d)

    # adv-rc-p4-s09 VP2
    p = os.path.join(DATA, "advanced/rc/adv-rc-p4-s09.json")
    d = load(p)
    for it in d["items"]:
        replace_vp2_vague(it)
    save(p, d)

    # adv-rc-p4-s04 q13
    p = os.path.join(DATA, "advanced/rc/adv-rc-p4-s04.json")
    d = load(p)
    for it in d["items"]:
        if it.get("id") == "q13":
            st = it.get("stem") or "People say he is right, and I don't agree with him."
            it["prompt"] = (
                "Warm-Up 2-(a): Correct the connector (and / but): " + st
            )
            it["accept"] = [
                "but",
                "and → but",
                "People say he is right, but I don't agree with him.",
            ]
    save(p, d)

    # adv-lc-p2-s04 q23
    p = os.path.join(DATA, "advanced/lc/adv-lc-p2-s04.json")
    d = load(p)
    for it in d["items"]:
        if it.get("id") == "q23":
            st = it.get("stem") or (
                "Should we paint the fence today, or should we finish the house chores?"
            )
            it["prompt"] = f"Listening Practice 1-3): {st}"
    save(p, d)

    # bas-rc-p4 sentence mislabels (Vocab 2–3 fill sentences)
    for rel in (
        "basic/rc/bas-rc-p4-s06.json",
        "basic/rc/bas-rc-p4-s07.json",
        "basic/rc/bas-rc-p4-s08.json",
        "basic/rc/bas-rc-p4-s09.json",
    ):
        p = os.path.join(DATA, rel)
        d = load(p)
        for it in d["items"]:
            pr = it.get("prompt") or ""
            st = it.get("stem") or ""
            if "Write the word that does not belong" not in pr:
                continue
            if is_sentence_fill(st):
                replace_odd_one_out_sentence(it)
        save(p, d)

    # adv-rc-p4-s07 VP3 sentence fills (scan sweep)
    p = os.path.join(DATA, "advanced/rc/adv-rc-p4-s07.json")
    d = load(p)
    for it in d["items"]:
        if it.get("id") in ("q13", "q14", "q15", "q16"):
            replace_odd_one_out_sentence(it)
    save(p, d)

    print("cos v31 fixes applied")


if __name__ == "__main__":
    main()
