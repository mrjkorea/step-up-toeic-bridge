#!/usr/bin/env python3
"""CoS content sense checks — must exit 0 with zero blocking hits on data/**/*.json."""
from __future__ import annotations

import collections
import glob
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA = os.path.join(ROOT, "data")

OCR = re.compile(
    r"\b(Iam|goto|togo|comedown|an dId|whit h|MmM|jJ|Font he)\b"
    r"|\b\w+ ’\w"
    r"|[A-Za-z]{2,}\s[’']\s?[a-z]\b"
    r"|\s\d\s:\d\d"
    r"|\^"
)

TRANSFORM_INSTR = re.compile(
    r"Make it negative|Change .*sentence|Rewrite in|Replace the noun|"
    r"Change to a question|Rewrite in the passive|Rewrite in the active|"
    r"future tense|passive|active voice",
    re.I,
)

INSTR_KEYWORDS = re.compile(
    r"Fill|Make|Change|Rewrite|Replace|Correct|Underline|Choose|Write|Translate|"
    r"Combine|Put|Circle|Match|Complete|Find|Arrange|type|Use|Listen|Say|Correct the|"
    r"Shorten|What|Refer|Reduce",
    re.I,
)

GENERIC_REWRITE = re.compile(
    r":\s*Rewrite the sentence[:\s—-]|Rewrite the sentence:",
    re.I,
)

CORRECT_WRONG = re.compile(r"Correct the (wrong word|error)", re.I)

COMPOUND_VOCAB = re.compile(
    r"write as ['\"]sense - word['\"]|Match the related words|department ______|"
    r"touch ______|taste ______|smell ______|feel ______",
    re.I,
)


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(s).lower().replace("'", "'"))


def accept_list(a) -> list:
    if a is None:
        return []
    return a if isinstance(a, list) else [a]


def json_files() -> list[str]:
    return sorted(glob.glob(os.path.join(DATA, "*", "*", "*.json")))


def check_vocab_stem_leak(pid: str, it: dict) -> str | None:
    pr = it.get("prompt") or ""
    st = it.get("stem") or ""
    if not st or "______" not in st:
        return None
    al = accept_list(it.get("accept"))
    if not al:
        return None
    for acc in al:
        acc_s = str(acc)
        if " - " in acc_s or " / " in acc_s:
            parts = re.split(r"\s*[-/,]\s*", acc_s)
            if len(parts) >= 2:
                second = parts[-1].strip()
                if second and norm(second) in norm(st.replace("______", "")):
                    return f"answer-part-in-stem:{second}"
        if "store" in acc_s.lower() and "store" in st.lower() and "______" in st:
            if re.search(r"department\s+______\s+store", st, re.I):
                return "compound-answer-in-stem"
        if re.search(r"(touch|taste|smell|feel)\s+______\s+\w+", st, re.I):
            m = re.match(r"(?P<sense>\w+)\s+______\s+(?P<word>\w+)", st, re.I)
            if m and norm(m.group("word")) in norm(acc_s):
                return f"sense-word-in-stem:{m.group('word')}"
    if COMPOUND_VOCAB.search(pr) and re.search(r"______\s+\w{3,}", st):
        tail = re.sub(r".*______\s*", "", st).strip()
        if tail and any(norm(tail) in norm(x) for x in al):
            return f"post-blank-word-in-stem:{tail}"
    return None


def scan() -> list[tuple]:
    fails: list[tuple] = []
    for f in json_files():
        d = json.load(open(f, encoding="utf-8"))
        pid = d.get("practiceId") or os.path.basename(f)[:-5]
        for it in d.get("items", []):
            if it.get("type") == "display":
                continue
            pr = it.get("prompt") or ""
            st = it.get("stem") or ""
            al = accept_list(it.get("accept"))
            iid = it.get("id", "?")
            txt = " ".join(
                map(
                    str,
                    [
                        pr,
                        st,
                        it.get("passage") or "",
                        " ".join(map(str, (it.get("choices") or {}).values())),
                    ],
                )
            )

            m = OCR.search(txt)
            if m:
                fails.append((pid, iid, "ocr", m.group(0), pr[:120]))

            if it.get("type") != "text":
                continue

            if st and any(norm(x) == norm(st) for x in al) and "slash" not in pr.lower():
                fails.append((pid, iid, "accept==stem", pr[:100], it.get("accept")))

            leak = check_vocab_stem_leak(pid, it)
            if leak:
                fails.append((pid, iid, "vocab-stem-leak", leak, st[:100]))

            if GENERIC_REWRITE.search(pr.strip()):
                fails.append((pid, iid, "generic-rewrite-instr", pr[:100], it.get("accept")))

            if re.search(r"type the words you hear|Type the words you hear", pr, re.I) and re.search(
                r"Rewrite the sentence", pr, re.I
            ):
                fails.append((pid, iid, "generic-rewrite-instr", pr[:100], it.get("accept")))

            if re.search(r"\([a-e]\s*/\s*[a-e]\)|choose the|Choose the", pr, re.I) and re.search(
                r"Rewrite the sentence", pr, re.I
            ):
                fails.append((pid, iid, "generic-rewrite-instr", pr[:100], it.get("accept")))

            if re.search(r"Fill in", pr, re.I) and re.search(r"Rewrite the sentence", pr, re.I):
                fails.append((pid, iid, "generic-rewrite-instr", pr[:100], it.get("accept")))

            if TRANSFORM_INSTR.search(pr) and al and all(len(str(x).split()) <= 2 for x in al):
                fails.append(
                    (pid, iid, "transform-instr-but-fragment-accept", pr[:100], it.get("accept"))
                )

            if "Replace the noun" in pr and any(
                re.search(r"\bby\b", st) and not re.search(r"\bby\b", str(x)) for x in al
            ):
                fails.append((pid, iid, "instr-mismatch(passive->active)", pr[:100], it.get("accept")))

            if CORRECT_WRONG.search(pr) and st and al:
                if (
                    len(al) == 1
                    and len(str(al[0]).split()) <= 2
                    and any(norm(x) in norm(st) for x in al)
                ):
                    fails.append(
                        (pid, iid, "correction-word-already-in-stem", pr[:100], it.get("accept"))
                    )

            if (
                pr
                and re.search(r"p4|p5", pid)
                and "-rc-" in pid
                and not INSTR_KEYWORDS.search(pr)
            ):
                fails.append((pid, iid, "no-instruction", pr[:100], it.get("accept")))

    return fails


def main() -> int:
    fails = scan()
    counts = collections.Counter(x[2] for x in fails)
    out_path = os.environ.get("SENSE_OUT", os.path.join(ROOT, "sense_out.json"))
    json.dump(fails, open(out_path, "w", encoding="utf-8"), indent=0, ensure_ascii=False)
    print(dict(counts), "total", len(fails))
    for row in fails:
        print(row)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
