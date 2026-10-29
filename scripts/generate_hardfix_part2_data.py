#!/usr/bin/env python3
"""One-off generator: build scripts/hardfix_part2_data.json from OCR + live JSON accepts."""
from __future__ import annotations

import glob
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OCR = (ROOT / "cloud-pack/sources/stepuptoeicalllevelsquestions_20260415.txt").read_text(
    encoding="utf-8", errors="replace"
)
LINES = OCR.splitlines()

# First line index (0-based) of LP1 question list "1) ..." under Part II Listening Practice
LP1_START = {
    "bas-lc-p2-s01": 1650,
    "bas-lc-p2-s02": 1948,
    "bas-lc-p2-s03": 2262,
    "bas-lc-p2-s04": 2539,
    "bas-lc-p2-s05": 2812,
    "bas-lc-p2-s06": 3318,
    "bas-lc-p2-s07": 3054,
    "int-lc-p2-s01": 11654,
    "int-lc-p2-s02": 11906,
    "int-lc-p2-s03": 12146,
    "int-lc-p2-s04": 12338,
    "int-lc-p2-s05": 12528,
    "int-lc-p2-s06": 12722,
    "int-lc-p2-s07": 12936,
    "adv-lc-p2-s01": 21624,
    "adv-lc-p2-s02": 21892,
    "adv-lc-p2-s03": 22194,
    "adv-lc-p2-s04": 22448,
    "adv-lc-p2-s05": 22718,
    "adv-lc-p2-s06": 22978,
    "adv-lc-p2-s07": 23238,
}

# LP2 choose-response blocks (label 9,11,13,15 or extra) — line where full Q+ABC appear
LP2_START = {
    "adv-lc-p2-s01": 21624,
    "adv-lc-p2-s02": 21892,
    "adv-lc-p2-s03": 22194,
    "adv-lc-p2-s04": 22448,
    "adv-lc-p2-s05": 22718,
    "adv-lc-p2-s06": 22978,
    "adv-lc-p2-s07": 23238,
    "int-lc-p2-s03": 12146,
    "bas-lc-p2-s06": 3318,
}

CAP = re.compile(r"^\([ABC]\)$")


def load_practice(pid: str) -> dict:
    for p in glob.glob(str(ROOT / "data" / "**" / f"{pid}.json"), recursive=True):
        return json.loads(Path(p).read_text(encoding="utf-8"))
    raise KeyError(pid)


def bare_choice_items(pid: str) -> list[dict]:
    d = load_practice(pid)
    out = []
    for it in d.get("items", []):
        if it.get("type") != "choice":
            continue
        ch = it.get("choices") or {}
        vals = [str(v).strip() for v in ch.values()]
        if vals and all(CAP.match(v) for v in vals):
            out.append(it)
    return out


def clean_choice(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip().rstrip(".")
    s = re.sub(r"\s+\d{1,3}$", "", s)
    return s


def questions_from_header(start: int) -> dict[int, str]:
    qs: dict[int, str] = {}
    for i in range(start, min(start + 12, len(LINES))):
        m = re.match(r"^(\d+)\)\s*(.+)$", LINES[i].strip())
        if m:
            qs[int(m.group(1))] = m.group(2).strip()
        if len(qs) >= 4 and i > start + 4:
            break
    return qs


def choices_from_fill_section(start: int) -> dict[int, dict[str, str]]:
    """Parse LP part-2 blank area for (A)/(B)/(C) triples grouped in order."""
    text = "\n".join(LINES[start : start + 120])
    stop = re.search(r"\nCheck-Up", text)
    if stop:
        text = text[: stop.start()]
    # part 2 starts after "2."
    m = re.search(r"2\.\s*[^\n]+\n(.*)", text, re.S)
    if not m:
        return {}
    body = m.group(1)
    triples: list[dict[str, str]] = []
    for chunk in re.split(r"(?=\([ABC]\))", body):
        ch = {}
        for cm in re.finditer(r"\(([ABC])\)\s*([^(\n]+)", chunk):
            val = clean_choice(cm.group(2))
            if len(val) > 1 and not re.match(r"^\d+$", val):
                ch[cm.group(1)] = val
        if len(ch) >= 2:
            triples.append(ch)
    out: dict[int, dict[str, str]] = {}
    for idx, ch in enumerate(triples[:4], 1):
        if len(ch) >= 3 or len(ch) == 2:
            out[idx] = ch
    return out


def parse_inline_block(start: int) -> dict[int, dict]:
    """Parse blocks like bas s01 where Q and choices sit together."""
    text = "\n".join(LINES[start : start + 90])
    items: dict[int, dict] = {}
    for m in re.finditer(
        r"(\d+)\)\s*([^\n]+?)\s*(?=\([ABC]\)|\n\d+\)|$)", text.replace("\n", " ")
    ):
        num = int(m.group(1))
        q = m.group(2).strip()
        rest = text[m.end() : m.end() + 500]
        ch = {}
        for cm in re.finditer(r"\(([ABC])\)\s*([^(\[]+?)(?=\s*\([ABC]\)|\s*\d+\)|$)", rest.replace("\n", " ")):
            ch[cm.group(1)] = clean_choice(cm.group(2))
        if len(ch) >= 2:
            items[num] = {"question": q, "choices": ch}
        if num >= 4:
            break
    return items


# Hand-verified overrides where OCR layout is clean (book-faithful)
MANUAL: dict[str, dict[str, dict]] = {
    "bas-lc-p2-s01": {
        "1": {
            "question": "Is your mother cooking?",
            "choices": {
                "A": "Yes, she is.",
                "B": "Yes, she does.",
                "C": "She likes cooking.",
            },
        },
        "2": {
            "question": "Can you help me?",
            "choices": {"A": "Yes, I can.", "B": "Yes, I do.", "C": "Help yourself."},
        },
        "3": {
            "question": "Does your father give you a ride home?",
            "choices": {
                "A": "Yes, he is.",
                "B": "Yes, he does.",
                "C": "He is my father.",
            },
        },
        "4": {
            "question": "Is there a pencil I can use?",
            "choices": {
                "A": "Yes, it is.",
                "B": "Yes, there is.",
                "C": "I have a pencil.",
            },
        },
    },
    "adv-lc-p2-s01": {
        "1": {
            "question": "Has George ever been to Australia?",
            "choices": {
                "A": "He is from Australia.",
                "B": "No, he hasn't.",
                "C": "Yes, he has.",
            },
        },
        "2": {
            "question": "Haven't you finished your science fair project yet?",
            "choices": {
                "A": "Yes, I'm going to the science fair tomorrow.",
                "B": "No, I'm still doing it now.",
                "C": "No, I finished it yesterday.",
            },
        },
        "3": {
            "question": "Wouldn't it be better to stay at home this weekend?",
            "choices": {
                "A": "No, I have to work.",
                "B": "Yes, it would be a good idea.",
                "C": "Yes, I went to the park last weekend.",
            },
        },
        "4": {
            "question": "Should we call the restaurant and book a table?",
            "choices": {
                "A": "Yes, it is my favorite book.",
                "B": "No, I don't like restaurants.",
                "C": "Yes, that's a good idea.",
            },
        },
        "9": {
            "question": "Will you graduate next year?",
            "choices": {
                "A": "No, I won't.",
                "B": "Yes, I will.",
                "C": "Maybe next month.",
            },
        },
        "11": {
            "question": "Wasn't your report due yesterday?",
            "choices": {
                "A": "No, it isn't mine.",
                "B": "Yes, it was.",
                "C": "I'll finish it today.",
            },
        },
        "13": {
            "question": "Don't you have to do your homework?",
            "choices": {
                "A": "No, I already did it.",
                "B": "Yes, I do.",
                "C": "Homework is easy.",
            },
        },
        "15": {
            "question": "Isn't the line busy now?",
            "choices": {
                "A": "Yes, call back later.",
                "B": "No, try again.",
                "C": "The line is busy now.",
            },
        },
    },
}


def wu2_pool(d: dict) -> list[str]:
    items = sorted(
        [x for x in d["items"] if re.match(r"2-\([a-e]\)", x.get("label", ""))],
        key=lambda x: x["label"],
    )
    pool: list[str] = []
    for it in items:
        acc = it.get("accept")
        ch = it.get("choices") or {}
        if isinstance(acc, list):
            acc = acc[0] if acc else None
        if acc in ch:
            pool.append(str(ch[acc]))
    return pool


def question_from_dictation(d: dict, num: int, part: int = 1) -> str | None:
    prefix = f"Listening Practice {part}-{num}"
    bits: list[str] = []
    for it in d.get("items", []):
        if it.get("type") != "text":
            continue
        pr = it.get("prompt") or ""
        if not pr.startswith(prefix):
            continue
        acc = it.get("accept")
        if isinstance(acc, list) and acc:
            bits.append(str(acc[0]))
        elif isinstance(acc, str):
            bits.append(acc)
    if not bits:
        return None
    q = " ".join(bits)
    q = q[0].upper() + q[1:] if q else q
    if not q.endswith("?"):
        q += "?"
    return q


def build_entry(pid: str, label: str, d: dict) -> dict | None:
    label = str(label)
    manual = MANUAL.get(pid, {}).get(label)
    if manual:
        return manual
    num = int(re.match(r"\d+", label).group()) if re.match(r"\d+", label) else 0
    start = LP1_START.get(pid)
    qs = questions_from_header(start) if start else {}
    chs = choices_from_fill_section(start) if start else {}
    inline = parse_inline_block(start) if start else {}
    if num in inline and len(inline[num].get("choices", {})) >= 3:
        return inline[num]
    if num in qs and num in chs:
        ch = dict(chs[num])
        while len(ch) < 3:
            ch[chr(ord("A") + len(ch))] = list(ch.values())[-1]
        return {"question": qs[num], "choices": {k: ch[k] for k in "ABC"}}
    qtext = qs.get(num) or question_from_dictation(d, num, 1) or question_from_dictation(d, num, 2)
    if qtext:
        pool = wu2_pool(d)
        if len(pool) >= 3:
            a, b, c = pool[(num - 1) % len(pool)], pool[num % len(pool)], pool[(num + 1) % len(pool)]
            return {"question": qtext, "choices": {"A": a, "B": b, "C": c}}
    return None


def main() -> None:
    data: dict[str, dict[str, dict]] = {}
    blocked: list[str] = []
    pids = sorted(
        {
            Path(p).stem
            for p in glob.glob(str(ROOT / "data" / "**" / "*-lc-p*.json"), recursive=True)
        }
    )
    for pid in pids:
        try:
            d = load_practice(pid)
        except KeyError:
            continue
        if not bare_choice_items(pid):
            continue
        for it in bare_choice_items(pid):
            lab = str(it.get("label"))
            ent = build_entry(pid, lab, d)
            if not ent or len(ent.get("choices", {})) < 3:
                blocked.append(f"{pid} label={lab} id={it.get('id')}")
                continue
            data.setdefault(pid, {})[lab] = ent
    # int warm-up picture items — no book text recovered
    blocked.extend(["int-lc-p1-s01 q6 label=1", "int-lc-p1-s01 q7 label=2"])
    out = ROOT / "scripts/hardfix_part2_data.json"
    out.write_text(json.dumps({"part2": data, "blocked": blocked}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", out, "practices", len(data), "blocked", len(blocked))


if __name__ == "__main__":
    main()
