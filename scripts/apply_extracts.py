#!/usr/bin/env python3
"""Apply structured book extracts from extracts/*.json to data/ practice JSON."""
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EX = ROOT / "extracts"
DATA = ROOT / "data"
CV = "v6-hardfix-228-2026-10-30"
CAP = re.compile(r"^\([A-E]\)$")


def load_practice(pid: str) -> tuple[Path, dict]:
    for p in DATA.rglob(f"{pid}.json"):
        return p, json.loads(p.read_text(encoding="utf-8"))
    raise FileNotFoundError(pid)


def save_practice(path: Path, doc: dict) -> None:
    doc["contentVersion"] = CV
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def item_by_id(doc: dict, iid: str) -> dict | None:
    for it in doc.get("items", []):
        if it.get("id") == iid:
            return it
    return None


def apply_rc():
    n = 0
    touched = set()
    for rec in json.loads((EX / "rc_blanks.json").read_text(encoding="utf-8")):
        path, doc = load_practice(rec["practiceId"])
        it = item_by_id(doc, rec["id"])
        if not it:
            raise KeyError((rec["practiceId"], rec["id"]))
        stem = rec["stem"]
        it["stem"] = stem
        label = rec.get("label") or it.get("label", "")
        sec = it.get("section", "Grammar Practice")
        if "Grammar Practice" in (it.get("prompt") or ""):
            it["prompt"] = f"Grammar Practice {label}: Fill in the blank — {stem}"
        else:
            it["prompt"] = f"{sec} {label}: Fill in the blank — {stem}"
        if rec.get("wordBank"):
            wb = rec["wordBank"]
            it["wordBank"] = wb if isinstance(wb, list) else wb.split()
        save_practice(path, doc)
        touched.add(rec["practiceId"])
        n += 1
    return n, touched


def apply_sense():
    n = 0
    touched = set()
    for rec in json.loads((EX / "sense_fixes.json").read_text(encoding="utf-8")):
        path, doc = load_practice(rec["practiceId"])
        it = item_by_id(doc, rec["id"])
        if not it:
            raise KeyError((rec["practiceId"], rec["id"]))
        if rec.get("proposedStem"):
            it["stem"] = rec["proposedStem"]
        if rec.get("proposedPrompt"):
            it["prompt"] = rec["proposedPrompt"]
        save_practice(path, doc)
        touched.add(rec["practiceId"])
        n += 1
    return n, touched


def apply_tf():
    n = 0
    touched = set()
    skipped = 0
    for rec in json.loads((EX / "tf_statements.json").read_text(encoding="utf-8")):
        stmt = rec.get("statement")
        if not stmt:
            skipped += 1
            continue
        path, doc = load_practice(rec["practiceId"])
        it = item_by_id(doc, rec["id"])
        if not it:
            raise KeyError((rec["practiceId"], rec["id"]))
        label = rec.get("label") or it.get("label", "")
        it["stem"] = stmt
        it["prompt"] = f"Check-Up (2) {label}: {stmt} (T/F)"
        save_practice(path, doc)
        touched.add(rec["practiceId"])
        n += 1
    return n, touched, skipped


def apply_part2():
    n_full = n_qonly = n_skip = 0
    touched = set()
    for rec in json.loads((EX / "part2_responses.json").read_text(encoding="utf-8")):
        path, doc = load_practice(rec["practiceId"])
        it = item_by_id(doc, rec["id"])
        if not it:
            raise KeyError((rec["practiceId"], rec["id"]))
        q = rec.get("question")
        ch = rec.get("choices")
        if ch and q:
            listen = (it.get("prompt") or "").strip()
            if not listen.lower().startswith("listen"):
                listen = "Listen and choose the best response."
            it["prompt"] = listen
            it["stem"] = q
            it["choices"] = ch
            it["hideChoicesUntilAnswered"] = True
            n_full += 1
        elif q and not ch:
            it["stem"] = q
            it["hideChoicesUntilAnswered"] = True
            it["hideQuestionUntilAnswered"] = True
            n_qonly += 1
        else:
            n_skip += 1
            continue
        save_practice(path, doc)
        touched.add(rec["practiceId"])
    return n_full, n_qonly, n_skip, touched


def main():
    rc_n, rc_p = apply_rc()
    sense_n, sense_p = apply_sense()
    tf_n, tf_p, tf_skip = apply_tf()
    p2_full, p2_q, p2_skip, p2_p = apply_part2()
    print(
        json.dumps(
            {
                "rc": rc_n,
                "sense": sense_n,
                "tf_applied": tf_n,
                "tf_skipped_null": tf_skip,
                "part2_full": p2_full,
                "part2_question_only": p2_q,
                "part2_skipped": p2_skip,
                "practices_touched": sorted(
                    rc_p | sense_p | tf_p | p2_p
                ),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
