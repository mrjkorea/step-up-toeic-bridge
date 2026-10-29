#!/usr/bin/env python3
"""Apply CoS content fixes across data/**/*.json. Idempotent where possible."""
from __future__ import annotations

import glob
import json
import os
import re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA = os.path.join(ROOT, "data")

INSTR_KEYWORDS = re.compile(
    r"Fill|Make|Change|Rewrite|Replace|Correct|Underline|Choose|Write|Translate|"
    r"Combine|Put|Circle|Match|Complete|Find|Arrange|type|Use|Listen|Say|Correct the|"
    r"Type the words you hear|Shorten|What|Refer|Reduce",
    re.I,
)

NEG_FRAGS = {"doesn't", "don't", "aren't", "isn't", "won't", "can't", "cannot", "does not", "do not"}


def accept_list(a):
    if a is None:
        return []
    return a if isinstance(a, list) else [a]


def fix_ocr_string(s: str) -> str:
    if not s or not isinstance(s, str):
        return s
    s = s.replace("’", "'").replace("‘", "'")
    s = re.sub(r"(\w)\s+'\s*(\w)", r"\1'\2", s)
    s = re.sub(r"\bIam\b", "I am", s)
    s = re.sub(r"\bgoto\b", "go to", s, flags=re.I)
    s = re.sub(r"\btogo\b", "to go", s, flags=re.I)
    s = re.sub(r"\bFont he\b", "F on the", s)
    s = re.sub(r"\bwhit h\b", "with", s, flags=re.I)
    s = re.sub(r"\ban dId\b", "and I", s)
    s = re.sub(r"\bcomedown\b", "come down", s, flags=re.I)
    s = re.sub(r"\btakeoff\b", "take off", s, flags=re.I)
    s = re.sub(r"\s3\s:\s*55", " 3:55", s)
    s = re.sub(r"p\.m\s*\.", "p.m.", s)
    s = re.sub(r"a\.m\s*\.", "a.m.", s)
    return s


def walk_strings(obj, fn):
    if isinstance(obj, str):
        return fn(obj)
    if isinstance(obj, list):
        return [walk_strings(x, fn) for x in obj]
    if isinstance(obj, dict):
        return {k: walk_strings(v, fn) for k, v in obj.items()}
    return obj


def split_prompt_prefix(prompt: str) -> tuple[str, str]:
    m = re.match(r"^([^:]{3,80}:\s*)", prompt)
    if m:
        return m.group(1), prompt[len(m.group(1)) :]
    return "", prompt


def infer_instruction(item: dict, pid: str) -> str | None:
    pr = item.get("prompt") or ""
    if INSTR_KEYWORDS.search(pr):
        return None
    st = item.get("stem") or ""
    body = st if st else pr
    prefix, _ = split_prompt_prefix(pr)
    al = accept_list(item.get("accept"))
    sec = item.get("section") or ""

    if "Vocabulary Practice" in sec and len(al) == 1 and len(str(al[0]).split()) == 1:
        if re.search(r"\b\w+\s+\w+\s+\w+", body):
            return prefix + "Write the word that does not belong: " + (st or pr[len(prefix) :] if prefix else pr)

    if "______" in body or "______" in st:
        if "(" in body and "/" in body:
            return prefix + "Choose the correct form: " + (st or pr[len(prefix) :] if prefix else pr)
        return prefix + "Fill in the blank: " + (st or pr[len(prefix) :] if prefix else pr)

    if "(" in body and "/" in body:
        return prefix + "Choose the correct form: " + body

    if len(al) == 1 and str(al[0]).strip().lower() in NEG_FRAGS:
        return prefix + "Make it negative: " + body

    acc0 = str(al[0]) if al else ""
    if al and any(" by " in str(x).lower() for x in al):
        if re.search(r"\bby\b", st, re.I) or re.search(r"\b(was|were|been|being)\b", st, re.I):
            return prefix + "Rewrite in the active voice: " + body
        return prefix + "Rewrite in the passive voice: " + body

    if re.search(r"\b(was|were)\s+\w+ed\b", st, re.I) and al and " by " not in acc0.lower():
        return prefix + "Rewrite in the active voice: " + body

    if re.search(r"\(\s*\w+\s*\)", st):
        return prefix + "Write the correct form: " + body

    if "?" in acc0 or acc0.strip().endswith("?"):
        return prefix + "Change to a question: " + body

    if " will " in acc0.lower() and " will " not in st.lower() and "teaches" in st.lower():
        return prefix + "Change to the future tense: " + body

    if " will not " in acc0.lower() or " won't " in acc0.lower():
        return prefix + "Make it negative: " + body

    if "Grammar Practice" in sec or "Warm-Up" in sec:
        if al and len(str(al[0]).split()) > 3:
            if re.search(r"\bby\b", body, re.I):
                return prefix + "Rewrite in the active voice: " + body
            if re.search(r"\b(is|are|was|were)\s+(a|an)\s+", str(al[0]), re.I):
                return prefix + "Rewrite using a noun phrase: " + body

    return prefix + "Type your answer: " + body


def expand_transform_accepts(item: dict) -> None:
    pr = item.get("prompt") or ""
    st = item.get("stem") or ""
    al = accept_list(item.get("accept"))
    if not al or not st:
        return
    if re.search(r"Make it negative", pr, re.I):
        frag = str(al[0]).strip()
        if frag.lower() in NEG_FRAGS or len(frag.split()) <= 2:
            base = st.rstrip(".")
            if frag.lower() in ("doesn't", "does not"):
                full = re.sub(r"\bruns\b", "doesn't run", base, flags=re.I)
                if full == base:
                    full = f"{base} (negative form)"
            elif frag.lower() in ("don't", "do not"):
                full = re.sub(r"\b(clean|like|watch)\b", r"don't \1", base, flags=re.I)
            elif frag.lower() in ("aren't", "are not"):
                full = re.sub(r"\bare\b", "aren't", base, flags=re.I)
            else:
                full = None
            if full and full not in al:
                item["accept"] = al + [full] if isinstance(item.get("accept"), list) else [frag, full]
    if re.search(r"Take out|______ your books", pr + st, re.I):
        if set(x.lower() for x in al) >= {"take", "out"}:
            item["accept"] = list(dict.fromkeys(al + ["Take out", "take out"]))


# Explicit per-item patches: (practiceId, id) -> dict of fields to merge
PATCHES: dict[tuple[str, str], dict] = {
    ("bas-rc-p4-s01", "q10"): {
        "prompt": "Warm-Up 2-(a): Make it negative: She runs fast.",
        "accept": ["She doesn't run fast.", "She does not run fast.", "doesn't"],
    },
    ("bas-rc-p4-s01", "q11"): {
        "prompt": "Warm-Up 2-(b): Make it negative: They clean the room.",
        "accept": ["They don't clean the room.", "They do not clean the room.", "don't"],
    },
    ("bas-rc-p4-s01", "q12"): {
        "prompt": "Warm-Up 2-(c): Make it negative: John and Jane are diligent.",
        "accept": ["John and Jane aren't diligent.", "John and Jane are not diligent.", "aren't"],
    },
    ("bas-rc-p4-s04", "q24"): {
        "prompt": "Grammar Practice 4-(c): Correct the wrong word — He wash his car.",
        "stem": "He wash his car.",
        "accept": ["washes", "He washes his car."],
    },
    ("bas-rc-p4-s05", "q14"): {
        "prompt": "Warm-Up 4-(a): What does It refer to? — I bought a cake. It tasted very good.",
        "accept": ["a cake", "cake"],
    },
    ("bas-rc-p4-s05", "q13"): {
        "prompt": "Warm-Up 3-(c): Replace the noun with a pronoun: It is your notebook.",
        "accept": ["It is yours.", "It's yours."],
    },
    ("bas-rc-p4-s02", "q9"): {
        "prompt": "Warm-Up 1-(c): Replace the noun with a pronoun: She is very smart.",
        "accept": ["She is very smart.", "She's very smart."],
    },
    ("bas-rc-p4-s07", "q14"): {
        "prompt": "Vocabulary Practice 3-(c): Fill in the blank: Let's get started. ______ your books.",
        "accept": ["Take out", "take out", "Take", "out"],
    },
    ("int-rc-p4-s01", "q31"): {
        "prompt": "Grammar Practice 3-(c): Correct the error — I don't like the winter.",
        "stem": "I don't like the winter.",
        "accept": ["I don't like winter.", "I do not like winter."],
    },
    ("int-rc-p4-s01", "q29"): {
        "prompt": "Grammar Practice 3-(a): Correct the error — I like to play the baseball with the my friends.",
        "accept": ["I like to play baseball with my friends."],
    },
    ("int-rc-p4-s01", "q32"): {
        "prompt": "Grammar Practice 3-(d): Correct the error — A waiter, please give me the some water.",
        "accept": ["Waiter, please give me some water.", "A waiter, please give me some water."],
    },
    ("int-rc-p4-s04", "q6"): {
        "prompt": "Warm-Up 1-(a): Underline the adverb — I will study very hard.",
        "accept": ["very"],
    },
    ("int-rc-p4-s04", "q7"): {
        "prompt": "Warm-Up 1-(b): Underline the adverb — The math exam was very difficult.",
        "accept": ["very"],
    },
    ("int-rc-p4-s04", "q8"): {
        "prompt": "Warm-Up 1-(c): Underline the adverb — Happily, he passed the exam.",
        "accept": ["Happily"],
    },
    ("int-rc-p4-s04", "q9"): {
        "prompt": "Warm-Up 1-(d): Underline the adverb — She ran out of the room very quickly.",
        "accept": ["quickly"],
    },
    ("int-rc-p4-s04", "q21"): {
        "prompt": "Grammar Practice 1-(a): Write the adverb form — fast — ______",
        "stem": "fast — ______",
        "accept": ["fast", "fastly"],
    },
    ("int-rc-p4-s04", "q20"): {
        "prompt": "Grammar Practice 4: Correct the word order — We watch often movies at home.",
    },
    ("adv-rc-p4-s02", "q16"): {
        "prompt": "Warm-Up 3-(d): Rewrite in the active voice: I am called Mr. Kim by them.",
        "stem": "I am called Mr. Kim by them.",
        "accept": ["They call me Mr. Kim.", "They called me Mr. Kim."],
    },
    ("adv-rc-p4-s02", "q15"): {
        "prompt": "Warm-Up 3-(c): Rewrite in the active voice: The result was announced by him.",
        "accept": ["He announced the result."],
    },
    ("adv-rc-p4-s04", "q35"): {
        "prompt": "Grammar Practice 5-(b): Rewrite using 'after' — You may get out after you finish your homework.",
        "stem": "You may get out after you finish your homework.",
    },
    ("adv-rc-p4-s04", "q36"): {
        "prompt": "Grammar Practice 5-(c): Rewrite using 'when' — When she was 18 years old, she moved to Seoul.",
        "stem": "When she was 18 years old, she moved to Seoul.",
    },
    ("adv-rc-p4-s04", "q37"): {
        "prompt": "Grammar Practice 5-(d): Rewrite using 'if' — Please call me if you find the person.",
        "stem": "Please call me if you find the person.",
    },
    ("int-rc-p4-s02", "q6"): {
        "prompt": "Warm-Up 2-(c): Make it negative: Jane can speak Korean.",
    },
    ("int-rc-p4-s02", "q7"): {
        "prompt": "Warm-Up 2-(d): Make it negative: Sam will go to see his aunt tomorrow.",
    },
    ("int-rc-p4-s02", "q12"): {
        "prompt": "Warm-Up 2-(a): Change to a question: Gary can read Japanese novels.",
    },
    ("int-rc-p4-s02", "q13"): {
        "prompt": "Warm-Up 2-(b): Change to a question: Candy will use my computer tomorrow.",
        "stem": "Candy will use my computer tomorrow.",
    },
    ("int-rc-p4-s02", "q14"): {
        "prompt": "Warm-Up 4-(a): Change to the future tense: He teaches me.",
    },
    ("int-rc-p4-s02", "q15"): {
        "prompt": "Warm-Up 4-(b): Make it negative: We will meet him at the mart early in the morning.",
    },
    ("int-rc-p4-s02", "q16"): {
        "prompt": "Warm-Up 4-(c): Change to a question: You are in a hurry.",
    },
    ("int-rc-p4-s02", "q17"): {
        "prompt": "Warm-Up 4-(d): Change to a question: She will bring her younger sister here.",
    },
    ("bas-rc-p4-s02", "q9"): {
        "stem": "Mary is very smart.",
        "prompt": "Warm-Up 1-(c): Replace the noun with a pronoun: Mary is very smart.",
        "accept": ["She is very smart.", "She's very smart."],
    },
    ("int-rc-p4-s01", "q30"): {
        "prompt": "Grammar Practice 3-(b): Correct the error — We go to the church after a breakfast.",
        "stem": "We go to the church after a breakfast.",
        "accept": ["We go to the church after breakfast."],
    },
    ("int-rc-p4-s04", "q21"): {
        "accept": ["fastly"],
    },
    ("adv-rc-p4-s07", "q10"): {
        "prompt": "Vocabulary Practice 2-(b): Match the related words — hand ______ / thumb, ______",
        "stem": "hand ______ / thumb, ______",
        "accept": ["hand - thumb, palm", "hand, thumb, palm", "hand thumb palm"],
    },
    ("adv-rc-p4-s02", "q13"): {
        "prompt": "Warm-Up 3-(a): Rewrite in the active voice: English is spoken by my friends in class.",
    },
    ("adv-rc-p4-s02", "q14"): {
        "prompt": "Warm-Up 3-(b): Rewrite in the active voice: She has been supported by him.",
    },
    ("adv-rc-p4-s02", "q21"): {
        "prompt": "Grammar Practice 3-(a): Shorten using a participial phrase: When I walked on the street, I encountered him.",
    },
    ("adv-rc-p4-s02", "q22"): {
        "prompt": "Grammar Practice 3-(b): Shorten using a participial phrase: Though I feel sleepy, I must not go to bed.",
    },
    ("adv-rc-p4-s02", "q23"): {
        "prompt": "Grammar Practice 3-(c): Shorten using a participial phrase: As she does the dishes, she sings pop songs.",
    },
    ("adv-rc-p4-s02", "q24"): {
        "prompt": "Grammar Practice 3-(d): Shorten using a participial phrase: As it was made in Japan, it is expensive.",
    },
    ("adv-rc-p4-s02", "q28"): {
        "prompt": "Grammar Practice 4-(d): Rewrite in the passive voice: I saw my grandfather playing basketball at dawn.",
    },
    ("adv-rc-p4-s02", "q32"): {
        "prompt": "Grammar Practice 5-(d): Rewrite in the passive voice: She made him pick it up.",
        "stem": "She made him pick it up.",
    },
    ("bas-rc-p4-s04", "q27"): {
        "prompt": "Grammar Practice 1-(c): Change to the simple present: He is kicking the ball.",
    },
    ("bas-rc-p4-s05", "q10"): {
        "prompt": "Warm-Up 2-(a): Replace the noun with a pronoun: The actor wants to talk to you.",
    },
    ("bas-rc-p4-s05", "q11"): {
        "prompt": "Warm-Up 2-(b): Replace the noun with a pronoun: Mr. Baker washes his shoes.",
    },
    ("bas-rc-p4-s05", "q12"): {
        "prompt": "Warm-Up 2-(c): Replace the noun with a pronoun: Susan is my best friend.",
    },
    ("int-rc-p4-s04", "q29"): {
        "prompt": "Grammar Practice 2-(a): Change to a noun phrase: He sings very well.",
    },
    ("int-rc-p4-s04", "q30"): {
        "prompt": "Grammar Practice 2-(b): Change to a noun phrase: She runs very fast.",
    },
    ("int-rc-p4-s04", "q31"): {
        "prompt": "Grammar Practice 2-(c): Change to a noun phrase: The girl plays beautifully.",
    },
    ("int-rc-p4-s04", "q32"): {
        "prompt": "Grammar Practice 2-(d): Change to a noun phrase: He drives carefully.",
    },
    ("int-rc-p5-s06", "q20"): {
        "passage": "To all students, / In these days, some of our school students are suffering from eye diseases. All students must wash their hands after each class. Use hot water and soap at all times. If anyone has any eye disease symptom, report it to his or her teacher. / You are welcome to visit our School Health Care Center for checkup between classes. / Office hours: 9 a.m. till 6 p.m. (Mon-Fri) / No reservations needed. / For phone counseling, call 080-114-1114.",
    },
    ("int-rc-p5-s06", "q21"): {
        "passage": "To all students, / In these days, some of our school students are suffering from eye diseases. All students must wash their hands after each class. Use hot water and soap at all times. If anyone has any eye disease symptom, report it to his or her teacher. / You are welcome to visit our School Health Care Center for checkup between classes. / Office hours: 9 a.m. till 6 p.m. (Mon-Fri) / No reservations needed. / For phone counseling, call 080-114-1114.",
    },
}

PASSAGE_PATCHES: dict[tuple[str, str], str] = {
    (
        "int-rc-p5-s06",
        "q14",
    ): "To: John / Date: May 7 / Time: 3:55 p.m. / From: Jane / Will call again / Message: The meeting is at 9 in the morning. / Taken by: Bob",
    (
        "int-rc-p5-s06",
        "q15",
    ): "To: John / Date: May 7 / Time: 3:55 p.m. / From: Jane / Will call again / Message: The meeting is at 9 in the morning. / Taken by: Bob",
    (
        "int-rc-p5-s06",
        "q16",
    ): "SuperComputers Office Memorandum / To all staff members, / All employees and their families are invited to the Super Computers Annual Family Barbecue Party at Mooney's Bay Beach Resort on July 16th. The company has rented a bus for the event and it will leave the headquarters at 8:00 a.m. Please make reservations for seats with the general affairs department no later than July 10th. / See you there.",
    (
        "int-rc-p5-s06",
        "q17",
    ): "SuperComputers Office Memorandum / To all staff members, / All employees and their families are invited to the Super Computers Annual Family Barbecue Party at Mooney's Bay Beach Resort on July 16th. The company has rented a bus for the event and it will leave the headquarters at 8:00 a.m. Please make reservations for seats with the general affairs department no later than July 10th. / See you there.",
    (
        "adv-rc-at-q31-40",
        "q9",
    ): "PLEASE READ THE FOLLOWING CAREFULLY. / You are now entering passport control. You must follow the guidelines below exactly. / Have your passport ready and ensure that your immigration form is fully completed and signed. / Wait behind the red line until you are told which desk you have to go to. / Do NOT cross the yellow line until an immigration officer authorizes you to do so.",
    (
        "adv-rc-at-q31-40",
        "q10",
    ): "PLEASE READ THE FOLLOWING CAREFULLY. / You are now entering passport control. You must follow the guidelines below exactly. / Have your passport ready and ensure that your immigration form is fully completed and signed. / Wait behind the red line until you are told which desk you have to go to. / Do NOT cross the yellow line until an immigration officer authorizes you to do so.",
}

CORRECTION_FULL: dict[tuple[str, str], list[str]] = {
    ("bas-rc-p4-s02", "q25"): ["He seems sad.", "sad"],
    ("bas-rc-p4-s02", "q26"): ["It smells bad.", "bad"],
    ("bas-rc-p4-s02", "q27"): ["It sounds nice.", "nice"],
    ("bas-rc-p4-s04", "q23"): ["She quit her job.", "quit"],
    ("adv-rc-p4-s03", "q18"): ["All pay attention to me when I give a speech.", "pay"],
    ("int-rc-p4-s04", "q3"): ["He works very hard.", "hard"],
    ("int-rc-p4-s04", "q4"): ["This watch is very expensive.", "expensive"],
    ("int-rc-p4-s04", "q5"): ["Tom is often late for school.", "late"],
}


def fix_vocab_stems(item: dict) -> None:
    pr = item.get("prompt") or ""
    st = item.get("stem") or ""
    if "touch — ?" in st or "touch ______" in st:
        item["stem"] = "touch ______"
        item["prompt"] = re.sub(r"touch — \?.*", "touch ______", pr)
    if re.search(r"taste ______\s+\w+$", st):
        item["stem"] = re.sub(r"(\w+)\s+______\s+\w+$", r"\1 ______", st)
    if "department" in st.lower() and "store" in st.lower():
        item["stem"] = re.sub(r"department\s+______\s+store", "department ______", st, flags=re.I)


def clean_passage_text(p: str) -> str:
    p = fix_ocr_string(p)
    p = p.replace("^", "")
    p = re.sub(r"\bri\s+ht\b", "right", p, flags=re.I)
    p = re.sub(r"\bPlea\s+5\s+e\b", "Please", p, flags=re.I)
    p = re.sub(r"Mary\^s", "Mary's", p)
    p = re.sub(r"^jJ[^/]*/\s*", "", p)
    p = re.sub(r"\\ \} J Hi LeV\s+u\s+", "", p)
    p = re.sub(r"T\s+ech\s+nic\s+al", "Technical", p)
    p = re.sub(r"\*\ \*", "", p)
    return p.strip()


def fix_item(item: dict, pid: str) -> int:
    n = 0
    iid = item.get("id", "")
    key = (pid, iid)
    if key in PATCHES:
        item.update(PATCHES[key])
        n += 1
    if key in CORRECTION_FULL:
        item["accept"] = CORRECTION_FULL[key]
        pr = item.get("prompt") or ""
        if "wrong word" in pr.lower():
            item["prompt"] = re.sub(r"correct the wrong word", "Correct the error", pr, flags=re.I)
        n += 1
    if key in PASSAGE_PATCHES and item.get("passage"):
        item["passage"] = PASSAGE_PATCHES[key]
        n += 1
    elif item.get("passage") and "^" in item.get("passage", ""):
        item["passage"] = clean_passage_text(item["passage"])
        n += 1
    elif item.get("passage") and re.search(r"\bjJ\b|MmM", item.get("passage", "")):
        item["passage"] = clean_passage_text(item["passage"])
        n += 1

    if item.get("type") == "text":
        if key not in PATCHES:
            new_pr = infer_instruction(item, pid)
            if new_pr and new_pr != item.get("prompt"):
                item["prompt"] = new_pr
                n += 1
        expand_transform_accepts(item)
        fix_vocab_stems(item)

    return n


def strip_vague_book_page(obj):
    if isinstance(obj, str):
        return re.sub(r"\s*\(see the book page\)\.?", "", obj, flags=re.I).replace(
            "see the book page", ""
        ).strip()
    if isinstance(obj, list):
        return [strip_vague_book_page(x) for x in obj]
    if isinstance(obj, dict):
        return {k: strip_vague_book_page(v) for k, v in obj.items()}
    return obj


def main() -> None:
    total = 0
    for f in sorted(glob.glob(os.path.join(DATA, "*", "*", "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        pid = d.get("practiceId") or os.path.basename(f)[:-5]
        d = walk_strings(d, fix_ocr_string)
        d = strip_vague_book_page(d)
        for it in d.get("items", []):
            total += fix_item(it, pid)
        d["contentVersion"] = "v29-cos-fix"
        json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("cos_apply_fixes: updated fields", total)


if __name__ == "__main__":
    main()
