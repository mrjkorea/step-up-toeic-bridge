#!/usr/bin/env python3
"""Apply CoS lanes A–E fixes to RC/LC practice JSON under data/."""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(ROOT, "data")

INSTRUCTION_RE = re.compile(
    r"(?i)(make it negative|change to a question|rewrite|passive|active|"
    r"replace the noun with a pronoun|correct the error|participle|"
    r"put the words in order|complete the sentence|fill in the blank|fill in|"
    r"write a,? or x|translate|following the example|correct or complete|"
    r"combine|underline the adverb|change the sentence|put a slash|"
    r"choose the verb|choose the correct|find the wrong word|correct the wrong word|"
    r"type your answer|write the full sentence)"
)

INTRO_TYPED = (
    "Read each item carefully. For multiple-choice items, choose the best answer. "
    "For Warm-Up and Grammar Practice, follow the instruction in each prompt and "
    "type your answer (rewritten sentence, correction, or word/phrase as asked)."
)

# (practiceId, itemId) -> partial item updates
EXPLICIT: dict[tuple[str, str], dict] = {
    ("adv-rc-p4-s03", "q17"): {
        "prompt": "Grammar Practice 4-(b): Correct the error — The sun goes around the earth.",
        "stem": "The sun goes around the earth.",
        "accept": ["The earth goes around the sun."],
    },
    ("adv-rc-p4-s01", "q26"): {
        "prompt": "Grammar Practice 5-(a): Correct the wrong word — I couldn't help cry when I saw the poor puppy.",
        "stem": "I couldn't help cry when I saw the poor puppy.",
        "accept": ["crying"],
    },
    ("adv-rc-p4-s01", "q33"): {
        "prompt": "Grammar Practice 3-(b): Correct the wrong word — He has finished do his homework.",
        "accept": ["doing"],
    },
    ("adv-rc-p4-s01", "q34"): {
        "prompt": "Grammar Practice 3-(c): Correct the wrong word — The doctor made her to stay at home for the time being.",
        "accept": ["stay"],
    },
    ("int-rc-p4-s01", "q29"): {
        "prompt": "Grammar Practice 3-(a): Correct the error — I like to play the baseball with the my friends.",
        "accept": ["I like to play baseball with my friends."],
    },
    ("int-rc-p4-s01", "q31"): {
        "prompt": "Grammar Practice 3-(c): Correct the error — I don't like the winter.",
        "accept": ["I don't like the winter."],
    },
    ("int-rc-p4-s01", "q32"): {
        "prompt": "Grammar Practice 3-(d): Correct the error — A waiter, please give me the some water.",
        "accept": ["Waiter, please give me some water."],
    },
    ("bas-rc-p4-s02", "q9"): {
        "prompt": "Warm-Up 1-(c): Put a slash (/) between the subject and the verb: She is very smart.",
        "accept": ["She / is very smart.", "She/is very smart."],
    },
    ("bas-rc-p4-s05", "q13"): {
        "prompt": "Warm-Up 3-(c): Replace the noun with a pronoun — This is your notebook.",
        "stem": "This is your notebook.",
        "accept": ["It is your notebook."],
    },
    ("int-rc-p4-s04", "q6"): {
        "prompt": "Warm-Up 1-(a): Underline the adverb — I will study very hard.",
        "accept": ["very hard"],
    },
    ("int-rc-p4-s04", "q7"): {
        "prompt": "Warm-Up 1-(b): Underline the adverb — The math exam was very difficult.",
        "accept": ["very difficult"],
    },
    ("int-rc-p4-s04", "q8"): {
        "prompt": "Warm-Up 1-(c): Underline the adverb — Happily, he passed the exam.",
        "accept": ["Happily"],
    },
    ("int-rc-p4-s04", "q9"): {
        "prompt": "Warm-Up 1-(d): Underline the adverb — She ran out of the room very quickly.",
        "accept": ["very quickly"],
    },
    ("bas-rc-p4-s02", "q14"): {
        "prompt": "Warm-Up 3-(b): Fill in the blank — He picked up the ______.",
        "stem": "He picked up the ______.",
        "accept": ["ball"],
    },
    ("bas-rc-p4-s02", "q15"): {
        "prompt": "Warm-Up 3-(c): Fill in the blank — He sang a ______.",
        "stem": "He sang a ______.",
        "accept": ["song"],
    },
    ("bas-rc-p4-s04", "q25"): {
        "prompt": "Grammar Practice 1-(a): Change the sentence into the present progressive — He writes a letter.",
        "stem": "He writes a letter.",
    },
    ("bas-rc-p4-s04", "q27"): {
        "prompt": "Grammar Practice 1-(c): Change the sentence into the simple present — He is kicking the ball.",
        "stem": "He is kicking the ball.",
    },
    ("bas-rc-p4-s04", "q24"): {
        "prompt": "Grammar Practice 4-(c): Correct the wrong word — He washes his car.",
        "stem": "He washes his car.",
    },
    ("int-rc-p4-s06", "q8"): {
        "prompt": "Vocabulary Practice 2-(a): correct or complete it — baseball ______ player",
        "stem": "baseball ______ player",
        "accept": ["baseball player"],
    },
    ("int-rc-p4-s06", "q9"): {
        "prompt": "Vocabulary Practice 2-(b): correct or complete it — police ______ officer",
        "stem": "police ______ officer",
        "accept": ["police officer"],
    },
    ("int-rc-p4-s06", "q10"): {
        "prompt": "Vocabulary Practice 2-(c): correct or complete it — hair ______ dresser",
        "stem": "hair ______ dresser",
        "accept": ["hairdresser"],
    },
    ("int-rc-p4-s06", "q11"): {
        "prompt": "Vocabulary Practice 2-(d): correct or complete it — fire ______ fighter",
        "stem": "fire ______ fighter",
        "accept": ["firefighter"],
    },
    ("int-rc-p4-s07", "q8"): {
        "prompt": "Vocabulary Practice 2-(a): Complete the health phrase — take ______ temperature",
        "stem": "take ______ temperature",
        "accept": ["one's temperature", "take one's temperature"],
    },
    ("int-rc-p4-s07", "q9"): {
        "prompt": "Vocabulary Practice 2-(b): Complete the health phrase — lose ______",
        "stem": "lose ______",
        "accept": ["consciousness", "lose consciousness"],
    },
    ("int-rc-p4-s07", "q10"): {
        "prompt": "Vocabulary Practice 2-(c): Complete the health phrase — come down ______ a cold",
        "stem": "come down ______ a cold",
        "accept": ["with", "come down with"],
    },
    ("int-rc-p4-s07", "q11"): {
        "prompt": "Vocabulary Practice 2-(d): Complete the health phrase — have ______ operation",
        "stem": "have ______ operation",
        "accept": ["an operation", "have an operation"],
    },
    ("int-rc-p4-s08", "q9"): {
        "prompt": "Vocabulary Practice 2-(a): correct or complete it — playing ______ pets",
        "stem": "playing ______ pets",
        "accept": ["with", "playing with pets"],
    },
    ("int-rc-p4-s08", "q10"): {
        "prompt": "Vocabulary Practice 2-(b): correct or complete it — Internet ______ surfing",
        "stem": "Internet ______ surfing",
        "accept": ["Internet surfing"],
    },
    ("int-rc-p4-s08", "q11"): {
        "prompt": "Vocabulary Practice 2-(c): correct or complete it — scuba ______ diving",
        "stem": "scuba ______ diving",
        "accept": ["scuba diving"],
    },
    ("int-rc-p4-s08", "q12"): {
        "prompt": "Vocabulary Practice 2-(d): correct or complete it — water ______ skiing",
        "stem": "water ______ skiing",
        "accept": ["water-skiing", "waterskiing"],
    },
    ("int-rc-p4-s08", "q13"): {
        "prompt": "Vocabulary Practice 3-(a): Fill in the blank — I like reading ______. They are some of my favorites.",
        "stem": "I like reading ______. They are some of my favorites.",
        "accept": ["comic books"],
    },
    ("int-rc-p4-s09", "q8"): {
        "prompt": "Vocabulary Practice 2-(a): correct or complete it — wash ______ stand",
        "stem": "wash ______ stand",
        "accept": ["washstand"],
    },
    ("int-rc-p4-s09", "q9"): {
        "prompt": "Vocabulary Practice 2-(b): correct or complete it — tooth ______ brush",
        "stem": "tooth ______ brush",
        "accept": ["toothbrush"],
    },
    ("int-rc-p4-s09", "q10"): {
        "prompt": "Vocabulary Practice 2-(c): correct or complete it — cup ______ board",
        "stem": "cup ______ board",
        "accept": ["cupboard"],
    },
    ("int-rc-p4-s09", "q11"): {
        "prompt": "Vocabulary Practice 2-(d): correct or complete it — bath ______ tub",
        "stem": "bath ______ tub",
        "accept": ["bathtub"],
    },
    ("int-rc-p4-s09", "q15"): {
        "prompt": "Vocabulary Practice 3-(d): Fill in the blank — The car is parked in the ______.",
        "stem": "The car is parked in the ______.",
        "accept": ["garage"],
    },
    ("adv-rc-p4-s07", "q9"): {
        "prompt": "Vocabulary Practice 2-(a): Match parts of the body — head: ______, ______ (clue: mouth, hair)",
        "stem": "head: ______, ______ (mouth, hair)",
        "accept": ["mouth, hair"],
    },
    ("adv-rc-p4-s07", "q10"): {
        "prompt": "Vocabulary Practice 2-(b): Match parts of the body — hand: ______, ______ (clue: thumb, palm)",
        "stem": "hand: ______, ______ (thumb, palm)",
        "accept": ["thumb, palm"],
    },
    ("adv-rc-p4-s07", "q11"): {
        "prompt": "Vocabulary Practice 2-(c): Match parts of the body — leg: ______, ______ (clue: toe, knee)",
        "stem": "leg: ______, ______ (toe, knee)",
        "accept": ["toe, knee"],
    },
    ("adv-rc-p4-s07", "q12"): {
        "prompt": "Vocabulary Practice 2-(d): Match parts of the body — organs: ______, ______ (clue: liver, heart)",
        "stem": "organs: ______, ______ (liver, heart)",
        "accept": ["liver, heart"],
    },
    ("adv-lc-p1-s04", "q64"): {
        "accept": ["take a picture", "take a video", "record"],
    },
}

GLOBAL_SUBS = [
    (re.compile(r"______ _"), "______"),
    (re.compile(r"_ ______"), "______"),
    (re.compile(r"\bIam\b"), "I'm"),
    (re.compile(r"\bgoto\b"), "go to"),
    (re.compile(r"\btogo\b"), "to go"),
    (re.compile(r"Font he"), "F on the"),
    (re.compile(r"you 5re"), "you're"),
    (re.compile(r"\b5re\b"), "are"),
    (re.compile(r"an dId on ’t"), "and I don't"),
    (re.compile(r"\bcomedown\b"), "come down"),
    (re.compile(r"whit h"), "with"),
    (re.compile(r"It’scold"), "It's cold"),
    (re.compile(r"It'cold"), "It's cold"),
    (re.compile(r"It’stood ark"), "It's too dark"),
    (re.compile(r"Tomis often"), "Tom is often"),
    (re.compile(r"Tomis "), "Tom is "),
    (re.compile(r"He sanga"), "He sang a"),
    (re.compile(r"\bhs his\b"), "washes his"),
    (re.compile(r"\bcomed\b"), "came"),
    (re.compile(r"\]tis\b"), "It is"),
    (re.compile(r"The cari sparked"), "The car is parked"),
    (re.compile(r"jJ i jjiiJ\|Ja / "), ""),
    (re.compile(r"M on-Fri"), "Mon-Fri"),
    (re.compile(r"080-1 14-11 14"), "080-114-1114"),
    (re.compile(r"I always\. ______"), "I always ______"),
    (re.compile(r"couldn ’the lp cry when Is aw"), "couldn't help cry when I saw"),
    (re.compile(r"\bIgo\b"), "I go"),
    (re.compile(r"fast ly"), "fast"),
    (re.compile(r"dam age"), "damage"),
    (re.compile(r"It’stood ark"), "It's too dark"),
    (re.compile(r"It' stood ark"), "It's too dark"),
    (re.compile(r"to meet meeting"), "meeting"),
]


def _walk_strings(obj, fn):
    if isinstance(obj, dict):
        for k, v in obj.items():
            obj[k] = _walk_strings(v, fn)
        return obj
    if isinstance(obj, list):
        return [_walk_strings(v, fn) for v in obj]
    if isinstance(obj, str):
        return fn(obj)
    return obj


def apply_global_subs(d: dict) -> None:
    def sub(s: str) -> str:
        for pat, rep in GLOBAL_SUBS:
            s = pat.sub(rep, s)
        return s

    _walk_strings(d, sub)


def infer_instruction(it: dict) -> str | None:
    if it.get("type") != "text" or it.get("displayOnly"):
        return None
    if it.get("section") not in ("Warm-Up", "Grammar Practice"):
        return None
    prompt = it.get("prompt") or ""
    if INSTRUCTION_RE.search(prompt):
        return None
    stem = (it.get("stem") or "").strip()
    acc = it.get("accept")
    accs = acc if isinstance(acc, list) else ([acc] if acc is not None else [])
    accs = [str(a).strip() for a in accs if str(a).strip()]
    has_blank = "______" in stem or "______" in prompt

    neg_words = {"doesn't", "don't", "aren't", "isn't", "wasn't", "weren't", "didn't", "can't", "cannot"}
    if not has_blank and accs and accs[0].lower().replace("'", "'") in neg_words:
        return "Make it negative:"
    if not has_blank and accs and all(a.split()[0] in ("He", "She", "It", "They") for a in accs if a.split()):
        if stem and stem.split()[0] not in ("He", "She", "It", "They"):
            return "Replace the noun with a pronoun:"
    if stem and accs:
        passive_markers = (" was ", " were ", " is ", " are ", " been ", " being ")
        if any(" by " in a.lower() for a in accs) and any(m in a for a in accs for m in passive_markers):
            if re.search(r"(?i)\b(by him|by her|by them|is spoken|was announced|been supported)\b", stem):
                return "Rewrite in the active:"
            return "Rewrite in the passive:"
    if stem and accs and any(
        a.startswith(("When ", "Though ", "As ", "Doing ", "Made ", "Walking ", "Though feeling"))
        for a in accs
    ):
        return "Rewrite using a participle:"
    if has_blank:
        if stem.startswith("______") or re.search(r"\([^)]+\s/\s[^)]+\)", stem):
            return "Fill in the blank:"
        return "Fill in the blank:"
    if stem and accs and all(" " in a for a in accs):
        return "Rewrite the sentence:"
    return "Rewrite the sentence:"


def prepend_instruction(it: dict, instruction: str) -> None:
    prompt = it.get("prompt") or ""
    m = re.match(r"^([^:]+:\s*)(.*)$", prompt, re.S)
    if m:
        it["prompt"] = f"{m.group(1)}{instruction} {m.group(2).lstrip()}"
    else:
        it["prompt"] = f"{instruction} {prompt}"


def maybe_fix_intro(d: dict) -> bool:
    pid = d.get("practiceId", "")
    if not re.match(r"(bas|int|adv)-rc-p4-s0[1-5]$", pid):
        return False
    has_typed = any(
        it.get("type") == "text" and it.get("section") in ("Warm-Up", "Grammar Practice")
        for it in d.get("items") or []
    )
    if not has_typed:
        return False
    if d.get("introEn") == INTRO_TYPED:
        return False
    d["introEn"] = INTRO_TYPED
    return True


def iter_json():
    for dirpath, _, files in os.walk(DATA):
        for name in files:
            if name.endswith(".json"):
                yield os.path.join(dirpath, name)


def main() -> int:
    changed_files = 0
    instr_count = 0
    explicit_count = 0

    for path in iter_json():
        d = json.load(open(path, encoding="utf-8"))
        pid = d.get("practiceId", os.path.basename(path)[:-5])
        orig = json.dumps(d, ensure_ascii=False, sort_keys=True)
        apply_global_subs(d)

        for it in d.get("items") or []:
            key = (pid, it.get("id", ""))
            if key in EXPLICIT:
                it.update(EXPLICIT[key])
                explicit_count += 1
            if it.get("type") == "text" and not it.get("displayOnly"):
                ins = infer_instruction(it)
                if ins:
                    prepend_instruction(it, ins)
                    instr_count += 1

        if maybe_fix_intro(d):
            pass

        new = json.dumps(d, ensure_ascii=False, sort_keys=True)
        if new != orig:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
                f.write("\n")
            changed_files += 1

    print(
        f"cos_apply_fixes: {changed_files} files, "
        f"{explicit_count} explicit item patches, {instr_count} instructions added"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
