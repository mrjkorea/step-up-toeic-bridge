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


def apply_tf_record(rec: dict) -> tuple[str, Path] | None:
    stmt = rec.get("statement")
    if not stmt:
        return None
    path, doc = load_practice(rec["practiceId"])
    it = item_by_id(doc, rec["id"])
    if not it:
        raise KeyError((rec["practiceId"], rec["id"]))
    label = rec.get("label") or it.get("label", "")
    it["stem"] = stmt
    it["prompt"] = f"Check-Up (2) {label}: {stmt} (T/F)"
    save_practice(path, doc)
    return rec["practiceId"], path


def apply_tf():
    n = 0
    touched = set()
    skipped = 0
    files = [EX / "tf_statements.json", EX / "tf_statements_int_adv.json"]
    for fp in files:
        if not fp.is_file():
            continue
        for rec in json.loads(fp.read_text(encoding="utf-8")):
            if not rec.get("statement"):
                skipped += 1
                continue
            apply_tf_record(rec)
            touched.add(rec["practiceId"])
            n += 1
    return n, touched, skipped


def listen_prompt_for_item(it: dict, rec: dict | None = None) -> str:
    pl = (it.get("prompt") or "").strip()
    if pl and "listen" in pl.lower() and (not it.get("stem") or it.get("stem") not in pl):
        return pl
    label = it.get("label") or ""
    if "choose the best response" in pl.lower() and "Listening Practice" in pl:
        return pl
    if "Listening Practice" in pl and re.search(r"\d", pl):
        base = pl.split(":")[0].strip()
        if base:
            return base + ": Listen and choose the best response."
    if "Check-Up" in (it.get("section") or ""):
        return pl or "Listen and choose the best response."
    return f"Listening Practice {label}): Listen and choose the best response."


def apply_part2_item(it: dict, rec: dict) -> str:
    """Returns: full | qonly | warmup | skip"""
    q = rec.get("question")
    ch = rec.get("choices")
    if q and ch:
        it["prompt"] = listen_prompt_for_item(it, rec)
        it["stem"] = q
        it["choices"] = ch
        it["hideChoicesUntilAnswered"] = True
        it.pop("hideQuestionUntilAnswered", None)
        return "full"
    if q and not ch:
        it["prompt"] = listen_prompt_for_item(it, rec)
        it["stem"] = q
        it["choices"] = {"A": "(A)", "B": "(B)", "C": "(C)"}
        it["hideChoicesUntilAnswered"] = True
        it["hideQuestionUntilAnswered"] = True
        return "qonly"
    if ch and not q:
        it["choices"] = ch
        it.pop("stem", None)
        it.pop("hideQuestionUntilAnswered", None)
        it.pop("hideChoicesUntilAnswered", None)
        return "warmup"
    return "skip"


def merge_part2_records() -> list[dict]:
    """Merge part2_responses + part2_remaining; later file wins non-null fields."""
    merged: dict[tuple[str, str], dict] = {}
    for fname in ("part2_responses.json", "part2_remaining.json"):
        fp = EX / fname
        if not fp.is_file():
            continue
        for rec in json.loads(fp.read_text(encoding="utf-8")):
            key = (rec["practiceId"], rec["id"])
            base = merged.setdefault(key, dict(rec))
            for field in (
                "itemIdOrLabel",
                "accept",
                "question",
                "choices",
                "confidence",
                "source",
                "note",
            ):
                if rec.get(field) is not None:
                    base[field] = rec[field]
    return list(merged.values())


def apply_part2():
    touched = set()
    n_full = n_qonly = n_warmup = n_skip = 0
    null_only_in_responses = 0
    resp_path = EX / "part2_responses.json"
    if resp_path.is_file():
        for rec in json.loads(resp_path.read_text(encoding="utf-8")):
            if rec.get("question") is None and rec.get("choices") is None:
                null_only_in_responses += 1
    for rec in merge_part2_records():
        path, doc = load_practice(rec["practiceId"])
        it = item_by_id(doc, rec["id"])
        if not it:
            raise KeyError((rec["practiceId"], rec["id"]))
        kind = apply_part2_item(it, rec)
        if kind == "skip":
            n_skip += 1
            continue
        save_practice(path, doc)
        touched.add(rec["practiceId"])
        if kind == "full":
            n_full += 1
        elif kind == "qonly":
            n_qonly += 1
        elif kind == "warmup":
            n_warmup += 1
    return n_full, n_qonly, n_warmup, n_skip, null_only_in_responses, touched


def main():
    rc_n, rc_p = apply_rc()
    sense_n, sense_p = apply_sense()
    tf_n, tf_p, tf_skip = apply_tf()
    p2_full, p2_q, p2_w, p2_skip, p2_null_resp, p2_p = apply_part2()
    print(
        json.dumps(
            {
                "rc": rc_n,
                "sense": sense_n,
                "tf_applied": tf_n,
                "tf_skipped_null": tf_skip,
                "tf_int_adv_file": (EX / "tf_statements_int_adv.json").is_file(),
                "part2_full": p2_full,
                "part2_question_only": p2_q,
                "part2_warmup_statements": p2_w,
                "part2_skipped": p2_skip,
                "part2_null_rows_in_responses_only": p2_null_resp,
                "part2_remaining_file": (EX / "part2_remaining.json").is_file(),
                "practices_touched": sorted(
                    rc_p | sense_p | tf_p | p2_p
                ),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
