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

ODD_ONE_OUT = re.compile(r"Write the word that does not belong", re.I)
WRITE_THE_ADVERB = re.compile(r"Write the adverb", re.I)
VAGUE_CORRECT_COMPLETE = re.compile(r"correct or complete it\s*[—–-]", re.I)
CUTOFF_LISTENING = re.compile(
    r"Listening Practice 1-\d+\):\s*today,\s*or should we",
    re.I,
)
JUNK_MULTI_ACCEPT = re.compile(r"^and\s+but$", re.I)

SENTENCE_START = re.compile(
    r"\b(I|My|We|They|She|He|It|The|Have you|Can I|Jane|Paul|Laura|Students|If you|In winter|There is|Every|Don't|Fish)\b",
    re.I,
)


def _exercise_stem(prompt: str, stem: str) -> str:
    if stem:
        return stem
    if not prompt:
        return ""
    m = re.search(r":\s*(.+)$", prompt)
    return (m.group(1) if m else prompt).strip()


def _odd_one_out_slash_text(pr: str, st: str) -> str:
    if st and "/" in st:
        return st.strip()
    m = re.search(r"[—–-]\s*(.+)$", pr)
    return m.group(1).strip() if m else _exercise_stem(pr, st)


def check_odd_one_out_glued_slash(pr: str, st: str) -> str | None:
    """Missing slash between odd-one-out words (other-three lists should have 3 slashes)."""
    if not ODD_ONE_OUT.search(pr):
        return None
    ex = _odd_one_out_slash_text(pr, st)
    if "/" not in ex:
        return None
    if re.search(r"\bill tasting\b", ex, re.I):
        return "odd-one-out-ill-tasting-space"
    if not re.search(r"other three", pr, re.I) or ex.count("/") != 2:
        return None
    for tok in (t.strip() for t in ex.split("/")):
        if " " not in tok or "'" in tok or "-" in tok:
            continue
        parts = tok.split()
        if len(parts) >= 2 and all(re.match(r"^[A-Za-z]+$", p) for p in parts):
            return f"odd-one-out-glued-slash-token:{tok}"
    return None


def check_other_three_three_token_list(pr: str, st: str) -> str | None:
    """Basic odd-one-out uses 나머지 두 (other two) for 3-word lists."""
    if not ODD_ONE_OUT.search(pr) or not re.search(r"other three", pr, re.I):
        return None
    ex = _odd_one_out_slash_text(pr, st)
    if ex.count("/") == 2:
        return "other-three-but-three-token-list"
    return None


def check_write_adverb_accept_in_stem(pr: str, st: str, al: list) -> str | None:
    if not WRITE_THE_ADVERB.search(pr) or not st or not al:
        return None
    first = str(al[0]).strip()
    if first and re.search(rf"\b{re.escape(first)}\b", st, re.I):
        return "write-adverb-accept-in-stem"
    return None


def check_bas_rc_p4_s07_bare_language(pid: str, pr: str, st: str) -> str | None:
    if pid != "bas-rc-p4-s07" or not ODD_ONE_OUT.search(pr):
        return None
    ex = (st or "").strip()
    if re.search(r"/\s*language(?:\s|$)", ex) and "language lab" not in ex:
        return "bas-rc-p4-s07-bare-language"
    return None


def check_misapplied_odd_one_out(pr: str, st: str) -> str | None:
    if not ODD_ONE_OUT.search(pr):
        return None
    ex = _exercise_stem(pr, st)
    blanks = ex.count("______")
    if blanks == 1 and ("." in ex or "?" in ex or SENTENCE_START.search(ex)):
        return "odd-one-out-on-sentence-fill"
    if blanks == 0 and not re.search(r"/", ex):
        if re.search(r"\?", ex) or SENTENCE_START.search(ex):
            return "odd-one-out-without-blank-or-list"
        return None
    return None


def check_vague_correct_complete(pr: str) -> str | None:
    if VAGUE_CORRECT_COMPLETE.search(pr) and re.search(r"Vocabulary Practice 2-", pr):
        return "vague-correct-or-complete"
    return None


def check_cutoff_listening(pr: str, st: str) -> str | None:
    if CUTOFF_LISTENING.search(pr) or CUTOFF_LISTENING.search(st or ""):
        return "cutoff-listening-prompt"
    return None


def check_junk_accept(al: list) -> str | None:
    for x in al:
        s = str(x).strip()
        if JUNK_MULTI_ACCEPT.match(s):
            return "junk-multi-word-accept"
        if " " in s and not re.search(r"[→/,]", s):
            words = s.split()
            if len(words) >= 2 and all(len(w) <= 4 for w in words):
                if s.lower() in ("and but", "or and", "but and"):
                    return "junk-multi-word-accept"
    return None

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
    tokens = _accept_word_tokens(acc)
    for i in range(len(tokens) - 1):
        if tokens[i] == left_n and tokens[i + 1] == right_n:
            return True
    return False


def _accept_word_tokens(acc: str) -> list[str]:
    raw = str(acc).strip()
    if ":" in raw:
        raw = raw.split(":")[0].strip()
    return [norm(w) for w in re.findall(r"\w+", raw)]


def _check_blank_following_token_leak(text: str, al: list) -> str | None:
    """Fail when ______ <word> reveals the next token of a multi-word accept phrase."""
    multi = [acc for acc in al if len(_accept_word_tokens(acc)) >= 2]
    if not multi:
        return None
    for m in re.finditer(r"______", text):
        tail = text[m.end() :]
        rm = re.match(r"\s+(\w+)", tail)
        if not rm:
            continue
        revealed = norm(rm.group(1))
        before_norm = [norm(w) for w in re.findall(r"\w+", text[: m.start()])]
        if not before_norm:
            continue
        for acc in multi:
            acc_norm = _accept_word_tokens(acc)
            for k in range(1, min(len(before_norm), len(acc_norm)) + 1):
                if before_norm[-k:] != acc_norm[:k] or k >= len(acc_norm):
                    continue
                if acc_norm[k] == revealed:
                    return f"blank-following-token-leak:{revealed}"
    return None


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
        leak = _check_blank_following_token_leak(text, al)
        if leak:
            return leak
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

            if it.get("type") == "choice":
                cut = check_cutoff_listening(pr, st)
                if cut:
                    fails.append((pid, iid, cut, pr[:100], it.get("accept")))

            if it.get("type") != "text":
                continue

            if (
                st
                and "______" not in st
                and any(norm(x) == norm(st) for x in al)
                and "slash" not in pr.lower()
            ):
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

            mis = check_misapplied_odd_one_out(pr, st)
            if mis:
                fails.append((pid, iid, mis, pr[:100], it.get("accept")))

            vague = check_vague_correct_complete(pr)
            if vague:
                fails.append((pid, iid, vague, pr[:100], it.get("accept")))

            junk = check_junk_accept(al)
            if junk:
                fails.append((pid, iid, junk, pr[:100], it.get("accept")))

            glued = check_odd_one_out_glued_slash(pr, st)
            if glued:
                fails.append((pid, iid, glued, pr[:100], it.get("accept")))

            o3 = check_other_three_three_token_list(pr, st)
            if o3:
                fails.append((pid, iid, o3, pr[:100], it.get("accept")))

            adv_stem = check_write_adverb_accept_in_stem(pr, st, al)
            if adv_stem:
                fails.append((pid, iid, adv_stem, pr[:100], it.get("accept")))

            bare_lang = check_bas_rc_p4_s07_bare_language(pid, pr, st)
            if bare_lang:
                fails.append((pid, iid, bare_lang, pr[:100], it.get("accept")))

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
