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

def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(s).lower().replace("'", "'"))


def accept_list(a) -> list:
    if a is None:
        return []
    return a if isinstance(a, list) else [a]


def json_files() -> list[str]:
    return sorted(glob.glob(os.path.join(DATA, "*", "*", "*.json")))


BLANK_PAIR = re.compile(r"\b(\w+)\s+______\s+(\w+)\b", re.I)


def _exercise_texts(prompt: str, stem: str) -> list[str]:
    texts: list[str] = []
    if stem:
        texts.append(stem)
    if prompt:
        texts.append(prompt)
        if re.search(r"[—–]", prompt):
            texts.append(re.split(r"\s*[—–]\s*", prompt, maxsplit=1)[-1].strip())
    # de-dupe while preserving order
    seen: set[str] = set()
    out: list[str] = []
    for t in texts:
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out


def _accept_parts(acc: str) -> list[str]:
    raw = str(acc).strip()
    if ":" in raw:
        raw = raw.split(":")[0].strip()
    return [norm(p) for p in re.split(r"[\s\-/,]+", raw) if norm(p)]


def _accept_matches_compound(acc: str, left: str, right: str) -> bool:
    left_n, right_n = norm(left), norm(right)
    compact = norm(str(acc).split(":")[0].strip())
    if compact == left_n + right_n:
        return True
    parts = _accept_parts(acc)
    if len(parts) >= 2 and parts[0] == left_n and parts[-1] == right_n:
        return True
    return False


def check_vocab_stem_leak(pid: str, it: dict) -> str | None:
    if it.get("type") != "text":
        return None
    pr = it.get("prompt") or ""
    st = it.get("stem") or ""
    al = accept_list(it.get("accept"))
    if not al:
        return None
    texts = _exercise_texts(pr, st)
    if not any("______" in t for t in texts):
        return None

    for text in texts:
        for m in BLANK_PAIR.finditer(text):
            left, right = m.group(1), m.group(2)
            for acc in al:
                if _accept_matches_compound(acc, left, right):
                    return f"compound-blank-leak:{left}-{right}"

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
