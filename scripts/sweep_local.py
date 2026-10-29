#!/usr/bin/env python3
"""Run sweep.py logic against data/catalog.json dataPath layout."""
import json
import os
import re
import collections as C
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
os.chdir(ROOT)
B = "https://mrjkorea.github.io/step-up-toeic-bridge/"
BOOK = {
    "basic-lc": "bas-lc",
    "basic-rc": "bas-rc",
    "intermediate-lc": "int-lc",
    "intermediate-rc": "int-rc",
    "advanced-lc": "adv-lc",
    "advanced-rc": "adv-rc",
}
CAP = re.compile(r"^\([A-E]\)$")
LET = re.compile(r"^\(?[A-Za-z]\)?\.?$")
STUB = re.compile(
    r"\bTODO\b|DEFERRED|see (the )?(book|page|textbook)|\[blank\]|placeholder|lorem|^…$|^\.\.\.$|page-\d+\.(png|jpg)",
    re.I,
)
cat = json.load(open(os.path.join(ROOT, "data", "catalog.json")))
fails = []
warns = []


def add(L, b, pid, it, pat, ex):
    L.append(
        dict(
            book=b,
            practiceId=pid,
            itemIdOrLabel=f"{it.get('id')} / {it.get('label')} [{it.get('section','')}]",
            pattern=pat,
            excerpt=ex[:300],
            url=B + "#/practice/" + pid,
        )
    )


for t in cat["tracks"]:
    b = BOOK[t["trackId"]]
    for p in t["practices"]:
        pid = p["id"]
        path = os.path.join(ROOT, p["dataPath"])
        d = json.load(open(path))
        raw = json.dumps(d, ensure_ascii=False)
        for m in set(re.findall(r"[\w/.-]*page-\d+\.(?:png|jpg)", raw)):
            add(fails, b, pid, {}, "page-image-ref", m)
        if p.get("stub") or d.get("stub"):
            add(fails, b, pid, {}, "stub-practice", "stub true")
        if not d.get("items"):
            add(fails, b, pid, {}, "no-items", "")
        for it in d.get("items", []):
            if it.get("photo"):
                pass
            ty = it.get("type")
            pr = (it.get("prompt") or "").strip()
            st = (it.get("stem") or "").strip()
            texts = [pr, st, str(it.get("passage") or ""), str(it.get("passageHead") or "")]
            for s in texts:
                if STUB.search(s):
                    add(fails, b, pid, it, "placeholder/see-book", s)
            if ty == "display":
                continue
            if not pr and not st:
                add(fails, b, pid, it, "empty-stem", json.dumps(it, ensure_ascii=False))
            if "stem" in it and not st:
                add(fails, b, pid, it, "empty-stem-field", pr)
            if (
                re.search(r"true|false|\bT/F\b", pr + st, re.I)
                or (
                    ty == "choice"
                    and set(map(str.lower, map(str, (it.get("choices") or {}).values())))
                    <= {"true", "false", "t", "f"}
                    and it.get("choices")
                )
            ):
                body = re.sub(r"^.*?:\s*", "", st or pr).strip()
                if not st and (
                    re.search(r"Is it True or False\??$", pr)
                    or len(re.sub(r"\(T/F\)", "", body).strip()) < 8
                ):
                    add(fails, b, pid, it, "tf-empty-statement", pr)
            a = it.get("accept")
            if ty != "display" and (
                a is None or a == "" or a == [] or (isinstance(a, list) and not any(str(x).strip() for x in a))
            ):
                add(fails, b, pid, it, "missing-accept", pr)
            if ty == "choice":
                ch = it.get("choices") or {}
                if not ch:
                    add(fails, b, pid, it, "no-choices", pr)
                vals = [str(v).strip() for v in ch.values()]
                if any(not v for v in vals):
                    add(fails, b, pid, it, "empty-choice", json.dumps(ch, ensure_ascii=False))
                if vals and all(CAP.match(v) for v in vals):
                    if it.get("photo"):
                        add(
                            warns,
                            b,
                            pid,
                            it,
                            "bare-(A)(B)(C)-with-photo (listen-only labels; photo carries cues)",
                            (pr + " " + st).strip()
                            + " | "
                            + json.dumps(ch, ensure_ascii=False),
                        )
                    else:
                        add(
                            fails,
                            b,
                            pid,
                            it,
                            "bare-(A)(B)(C)-choices-no-english",
                            (pr + " " + st).strip()
                            + " | "
                            + json.dumps(ch, ensure_ascii=False),
                        )
                elif vals and all(LET.match(v) for v in vals):
                    combined = f"{pr} {st}".strip()
                    stem_labels = len(re.findall(r"\([a-d]\)", combined, re.I)) >= 2
                    if it.get("photo"):
                        add(
                            warns,
                            b,
                            pid,
                            it,
                            "letter-only-choices-with-photo (picture-label match)",
                            pr + " | " + json.dumps(ch),
                        )
                    elif "Pronunciation" in pr:
                        add(
                            warns,
                            b,
                            pid,
                            it,
                            "phoneme-letter-choices (b/v, f/p, s/z — legit sound contrast)",
                            pr + " | " + json.dumps(ch),
                        )
                    elif stem_labels or (st and len(st.strip()) >= 40):
                        add(
                            warns,
                            b,
                            pid,
                            it,
                            "letter-label-choices-in-stem (grammar RC; full options in stem/prompt)",
                            pr + " " + st + " | " + json.dumps(ch, ensure_ascii=False),
                        )
                    else:
                        add(
                            fails,
                            b,
                            pid,
                            it,
                            "letter-only-choices-no-english",
                            pr + " " + st + " | " + json.dumps(ch, ensure_ascii=False),
                        )
            if ty == "text" and not it.get("audioOnly") and not st and not it.get("passage") and (
                re.search(r"Fill in the blank\.?$", pr)
                or not re.search(r"_{2,}|\w{3,} \w{3,} \w{3,}|Write .+ in words|Combine:", pr)
            ):
                add(fails, b, pid, it, "text-item-no-standalone-content", pr)

out = os.path.join(ROOT, "sweep_out.json")
json.dump(dict(fails=fails, warns=warns), open(out, "w"), ensure_ascii=False, indent=1)
print("fails", len(fails), "warns", len(warns))
print(C.Counter((f["book"], f["pattern"]) for f in fails))
