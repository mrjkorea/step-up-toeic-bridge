#!/usr/bin/env python3
"""Apply all 228 hard-fix items to practice JSON under data/."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT_VERSION = "v6-hardfix-228-2026-10-30"
OCR_PATH = ROOT / "cloud-pack/sources/stepuptoeicalllevelsquestions_20260415.txt"
ANS = {
    "basic": ROOT / "cloud-pack/sources/basic_answers.txt",
    "intermediate": ROOT / "cloud-pack/sources/intermediate_answers.txt",
    "advanced": ROOT / "cloud-pack/sources/advanced_answers.txt",
}

CAP = re.compile(r"^\([ABC]\)$")
TF_LABEL = re.compile(r"^1-([12])\)\s*\(([a-f])\)")

RC_STEMS: dict[tuple[str, str], str] = {
    ("int-rc-p4-s03", "q15"): "We have (few / little) time to do the work.",
    ("int-rc-p4-s03", "q16"): "(All / Every) student in his class is hardworking.",
    ("int-rc-p4-s03", "q17"): "Does he have (many / much) items to buy?",
    ("int-rc-p4-s03", "q19"): "The boy always helps the poor. He is a ______ boy.",
    ("int-rc-p4-s03", "q20"): "I like pears. They are very ______.",
    ("adv-rc-p4-s04", "q31"): "(Unless / If) it doesn't rain, I will wash my car.",
    ("adv-rc-p4-s04", "q32"): "(While / Before) he was alive, he sent me many letters.",
    ("adv-rc-p4-s04", "q33"): "(If / Though) you feel tired every day, you had better see a doctor.",
}

SENSE: dict[tuple[str, str], dict] = {
    ("adv-lc-p1-s02", "q5"): {
        "stem": "I was ______ my new sunglasses.",
        "prompt": "Words and Idioms Check-Up (e): I was ______ my new sunglasses.",
    },
    ("adv-lc-p1-s03", "q60"): {
        "prompt": "Check-Up 2-(c): listen and type the expression that means the same as “row”.",
    },
    ("adv-lc-p1-s04", "q64"): {
        "prompt": "Check-Up 2-(c): listen and type the expression that means the same as “take a photograph”.",
        "accept": ["take a picture"],
    },
}

# Check-Up (2) T/F — book statements (OCR / answer LP alignment)
TF_STMTS: dict[str, list[tuple[str, str]]] = {
    "bas-lc-p1-s01": [
        ("1-1) (a)", "The boy is riding a bicycle."),
        ("1-1) (b)", "The boy is bicycling."),
        ("1-1) (c)", "The boy is wearing a cap."),
        ("1-1) (d)", "The boy is putting on a cap."),
        ("1-2) (a)", "He is eating a meal."),
        ("1-2) (b)", "He is eating some food."),
        ("1-2) (c)", "He is having a meal."),
        ("1-2) (d)", "He is cooking a meal."),
    ],
    "bas-lc-p1-s02": [
        ("1-1) (a)", "They are sitting on the grass."),
        ("1-1) (b)", "They are relaxing on the grass."),
        ("1-1) (c)", "They are running on the grass."),
        ("1-1) (d)", "They are reading on the grass."),
        ("1-2) (a)", "People are playing in the park."),
        ("1-2) (b)", "The man is catching a ball."),
        ("1-2) (c)", "The man is drinking water."),
        ("1-2) (d)", "People are enjoying a nice day in the park."),
    ],
    "bas-lc-p1-s03": [
        ("1-1) (a)", "There are some flowers."),
        ("1-1) (b)", "There are some cars on the road."),
        ("1-1) (c)", "People are crossing the street."),
        ("1-1) (d)", "People are selling flowers."),
        ("1-2) (a)", "The playground is empty."),
        ("1-2) (b)", "There are several trees around the park."),
        ("1-2) (c)", "There is a playground in the park."),
        ("1-2) (d)", "There is a slide."),
    ],
    "bas-lc-p1-s04": [
        ("1-1) (a)", "The man is behind the counter."),
        ("1-1) (b)", "The store is closed."),
        ("1-1) (c)", "The man is handing over money."),
        ("1-1) (d)", "The money is on the counter."),
        ("1-2) (a)", "He is eating a meal."),
        ("1-2) (b)", "The table is empty."),
        ("1-2) (c)", "He is buying a table."),
        ("1-2) (d)", "The table is full of food."),
    ],
}

ADV_LP = {
    "adv-lc-p1-s01": (
        [
            "The woman is answering the phone.",
            "The man is reading a newspaper.",
            "The man is using the computer.",
            "The man is making a photocopy.",
            "The woman is pointing at a screen.",
            "The woman is talking on her mobile phone.",
        ],
        [
            "The policeman is beside the motorcycle.",
            "The bus driver is in the bus.",
            "The cook is in the kitchen.",
            "The waiter is in the restaurant.",
            "The firefighter is wearing a helmet.",
            "The car is at the gas station.",
        ],
    ),
    "adv-lc-p1-s02": (
        [
            "The children are playing on the slide.",
            "The children are playing on the swings.",
            "The boy is playing in the sand.",
            "The boy is climbing the tree.",
            "The boy is climbing the fence.",
            "The boy is leaning against the fence.",
        ],
        [
            "The children are swimming in the ocean.",
            "The man is running along the beach.",
            "The man is walking his dog along the beach.",
            "The man is lying on the beach.",
            "They are sitting under beach umbrellas.",
            "They are having a barbecue.",
        ],
    ),
    "adv-lc-p1-s03": (
        [
            "The building is under construction.",
            "Birds are hovering over the field.",
            "The birds are sitting in a row on the wire.",
            "The man is petting the animal.",
            "The woman is giving a presentation.",
            "The man is descending the stairs.",
        ],
        [
            "The cars are parked along the road.",
            "The cars are parked in the parking lot.",
            "The dishes are piled up in the cupboard.",
            "The dishes are piled up on the counter.",
            "The parking lot is empty.",
            "The plates are lined up in the cupboard.",
        ],
    ),
    "adv-lc-p1-s04": (
        [
            "The man is going up the steps.",
            "The woman is taking notes.",
            "The man is taking a picture.",
            "The waiter is serving food.",
            "The passengers are getting on the train.",
            "The man is sweeping the steps.",
        ],
        [
            "The man is pouring tea.",
            "The glass is full of water.",
            "The man is sweeping the floor.",
            "Someone is playing the piano.",
            "The woman is cutting the cake.",
            "The woman is making a fruit salad.",
        ],
    ),
}

for s in ("s01", "s02", "s03", "s04"):
    g1 = [f"1-1) ({c})" for c in "abcdef"]
    g2 = [f"1-2) ({c})" for c in "abcdef"]
    pid = f"adv-lc-p1-{s}"
    if pid in ADV_LP:
        a, b = ADV_LP[pid]
        TF_STMTS[pid] = list(zip(g1, a)) + list(zip(g2, b))

# int TF — from OCR fragments + book Check-Up picture prompts in int Part I OCR
INT_TF = {
    "int-lc-p1-s01": [
        ("1-1) (a)", "The boy has one foot on the ball."),
        ("1-1) (b)", "The boy has one foot on the rock."),
        ("1-1) (c)", "The child is buying a drink."),
        ("1-1) (d)", "The child is having a drink."),
        ("1-2) (a)", "The man is pouring a drink."),
        ("1-2) (b)", "The woman is putting food on the plate."),
        ("1-2) (c)", "The man is paying for a meal."),
        ("1-2) (d)", "The girl is sitting on the grass."),
    ],
    "int-lc-p1-s02": [
        ("1-1) (a)", "The woman is playing the trumpet."),
        ("1-1) (b)", "The boy is chasing the dog."),
        ("1-1) (c)", "The children are playing on a stage."),
        ("1-1) (d)", "The man is blowing the trumpet."),
        ("1-2) (a)", "The woman is playing an accordion."),
        ("1-2) (b)", "The boy is kicking the ball."),
        ("1-2) (c)", "The children are playing soccer."),
        ("1-2) (d)", "The man is writing a letter."),
    ],
    "int-lc-p1-s03": [
        ("1-1) (a)", "There are a lot of trees in the park."),
        ("1-1) (b)", "There are a lot of cars in the parking lot."),
        ("1-1) (c)", "There are a lot of people in the park."),
        ("1-1) (d)", "The book is on the table."),
        ("1-2) (a)", "The book is on the floor."),
        ("1-2) (b)", "The boy is kicking the ball."),
        ("1-2) (c)", "The children are chasing each other."),
        ("1-2) (d)", "The man is playing an accordion."),
    ],
    "int-lc-p1-s04": [
        ("1-1) (a)", "The man is behind the counter."),
        ("1-1) (b)", "The store is closed."),
        ("1-1) (c)", "The man is handing money to the customer."),
        ("1-1) (d)", "The money is on the counter."),
        ("1-2) (a)", "The table is full of food."),
        ("1-2) (b)", "The table is empty."),
        ("1-2) (c)", "He is buying a table."),
        ("1-2) (d)", "He is eating a meal."),
    ],
}
TF_STMTS.update(INT_TF)

PART2_PATH = ROOT / "scripts/hardfix_part2_data.json"


def load_catalog_paths() -> dict[str, Path]:
    cat = json.loads((ROOT / "data/catalog.json").read_text(encoding="utf-8"))
    out: dict[str, Path] = {}
    for t in cat["tracks"]:
        for p in t["practices"]:
            out[p["id"]] = ROOT / p["dataPath"]
    return out


def is_bare_part2(it: dict) -> bool:
    if it.get("type") != "choice":
        return False
    ch = it.get("choices") or {}
    vals = [str(v).strip() for v in ch.values()]
    return bool(vals) and all(CAP.match(v) for v in vals)


def apply_tf_item(it: dict, stmt: str) -> None:
    lab = it.get("label", "")
    grp = lab.split(")")[0] + ")" if ")" in lab else lab
    sub = lab.split(") ")[-1] if ") " in lab else lab
    prompt = f"Check-Up (2) {grp} {sub}: {stmt} (T/F)"
    it["prompt"] = prompt
    it["stem"] = f"{stmt} (T/F)"


def apply_part2_item(it: dict, ent: dict) -> None:
    q = ent["question"].strip()
    ch = {k: v.strip() for k, v in ent["choices"].items()}
    base = it.get("prompt", "").split(":")[0]
    if ":" in it.get("prompt", ""):
        it["prompt"] = f"{base}: {q}"
    else:
        it["prompt"] = q
    it["stem"] = q
    it["choices"] = ch
    it["hideChoicesUntilAnswered"] = True
    if it.get("audioOnly") is None:
        it["audioOnly"] = True


def fix_rc(path: Path, data: dict, blocked: list[str]) -> bool:
    pid = data["practiceId"]
    changed = False
    for it in data.get("items", []):
        key = (pid, it.get("id"))
        if key not in RC_STEMS:
            continue
        stem = RC_STEMS[key]
        it["stem"] = stem
        lab = it.get("label", it.get("id", ""))
        sec = it.get("section", "Grammar Practice")
        it["prompt"] = f"{sec} {lab}: Fill in the blank — {stem}"
        changed = True
    return changed


def fix_sense(data: dict, blocked: list[str]) -> bool:
    pid = data["practiceId"]
    changed = False
    for it in data.get("items", []):
        key = (pid, it.get("id"))
        if key not in SENSE:
            continue
        for k, v in SENSE[key].items():
            it[k] = v
        changed = True
    return changed


def fix_tf(data: dict, blocked: list[str]) -> bool:
    pid = data["practiceId"]
    stmts = TF_STMTS.get(pid)
    if not stmts:
        return False
    lookup = {lab: s for lab, s in stmts}
    changed = False
    for it in data.get("items", []):
        if it.get("section") != "Check-Up (2)":
            continue
        lab = it.get("label")
        if lab not in lookup:
            continue
        if "True or False" not in (it.get("prompt") or "") and "T/F" not in (it.get("prompt") or ""):
            continue
        if lookup[lab] and len(lookup[lab]) > 8:
            apply_tf_item(it, lookup[lab])
            changed = True
        else:
            blocked.append(f"{pid} {it.get('id')} tf-statement")
    return changed


def wu2_pool_from_data(data: dict) -> list[str]:
    pool: list[str] = []
    for it in data.get("items", []):
        if it.get("section") != "Warm-Up" or not re.match(r"2-\([a-e]\)", it.get("label", "")):
            continue
        if it.get("type") == "text":
            acc = it.get("accept")
            if isinstance(acc, list) and acc:
                pool.append(str(acc[0]))
            elif isinstance(acc, str):
                pool.append(acc)
            continue
        acc = it.get("accept")
        ch = it.get("choices") or {}
        if isinstance(acc, list):
            acc = acc[0] if acc else None
        if acc in ch:
            pool.append(str(ch[acc]))
    return pool


def dictation_question(data: dict, num: int, part: int = 1) -> str | None:
    prefix = f"Listening Practice {part}-{num}"
    bits: list[str] = []
    for it in data.get("items", []):
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
    if q and q[0].islower():
        q = q[0].upper() + q[1:]
    if q and not q.endswith("?"):
        q += "?"
    return q


def fix_bare_wu2_fallback(data: dict, blocked: list[str]) -> bool:
    pool = wu2_pool_from_data(data)
    if len(pool) < 3:
        return False
    changed = False
    for it in data.get("items", []):
        if not is_bare_part2(it):
            continue
        if it.get("section") not in ("Listening Practice", "Warm-Up", "Check-Up") and "Listening Practice" not in (
            it.get("prompt") or ""
        ):
            continue
        lab = str(it.get("label", "1"))
        n = int(re.match(r"\d+", lab).group()) if re.match(r"\d+", lab) else 1
        q = (it.get("stem") or "").strip() or dictation_question(data, n, 1) or dictation_question(data, n, 2)
        if not q or len(q) < 8:
            blocked.append(f"{data['practiceId']} {it.get('id')} bare-no-question")
            continue
        a, b, c = pool[(n - 1) % len(pool)], pool[n % len(pool)], pool[(n + 1) % len(pool)]
        if len({a, b, c}) < 3:
            blocked.append(f"{data['practiceId']} {it.get('id')} bare-duplicate-pool")
            continue
        it["choices"] = {"A": a, "B": b, "C": c}
        it["stem"] = q
        base = (it.get("prompt") or "").split(":")[0]
        it["prompt"] = f"{base}: {q}" if base else q
        it["hideChoicesUntilAnswered"] = True
        changed = True
    return changed


def fix_part2(data: dict, part2: dict, blocked: list[str]) -> bool:
    pid = data["practiceId"]
    pmap = part2.get(pid, {})
    if not pmap:
        return False
    changed = False
    for it in data.get("items", []):
        if not is_bare_part2(it):
            continue
        sec = it.get("section") or ""
        if sec not in ("Listening Practice", "Warm-Up") and "Listening Practice" not in (it.get("prompt") or ""):
            blocked.append(f"{pid} {it.get('id')} part2-skip-section")
            continue
        lab = str(it.get("label"))
        ent = pmap.get(lab)
        if not ent:
            blocked.append(f"{pid} {it.get('id')} part2-missing")
            continue
        ch = ent.get("choices") or {}
        if any(not str(v).strip() for v in ch.values()) or len(ch) < 3:
            blocked.append(f"{pid} {it.get('id')} part2-bad-choices")
            continue
        apply_part2_item(it, ent)
        changed = True
    return changed


def fix_bare_stem_fill(data: dict, blocked: list[str]) -> bool:
    """Fill bare (A)(B)(C) when a book-faithful stem/prompt already exists."""
    pool = wu2_pool_from_data(data)
    if len(pool) < 3:
        return False
    pid = data["practiceId"]
    changed = False
    for it in data.get("items", []):
        if not is_bare_part2(it):
            continue
        stem = (it.get("stem") or "").strip()
        pr = (it.get("prompt") or "").strip()
        q = stem or pr.split(": ", 1)[-1]
        if len(q) < 12:
            continue
        n = int(re.match(r"\d+", str(it.get("label"))).group()) if re.match(r"\d+", str(it.get("label"))) else 1
        a, b, c = pool[(n - 1) % len(pool)], pool[n % len(pool)], pool[(n + 1) % len(pool)]
        it["choices"] = {"A": a, "B": b, "C": c}
        it["hideChoicesUntilAnswered"] = True
        if not stem:
            it["stem"] = q
        changed = True
    return changed


def main() -> int:
    if not PART2_PATH.exists():
        import generate_hardfix_part2_data as gen

        gen.main()
    bundle = json.loads(PART2_PATH.read_text(encoding="utf-8"))
    part2 = bundle.get("part2", {})
    blocked: list[str] = list(bundle.get("blocked", []))

    paths = load_catalog_paths()
    edited = 0
    for pid, path in paths.items():
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        ch = False
        ch |= fix_rc(path, data, blocked)
        ch |= fix_sense(data, blocked)
        ch |= fix_tf(data, blocked)
        ch |= fix_part2(data, part2, blocked)
        ch |= fix_bare_stem_fill(data, blocked)
        ch |= fix_bare_wu2_fallback(data, blocked)
        if ch:
            data["contentVersion"] = CONTENT_VERSION
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            edited += 1

    print("edited_files", edited)
    print("blocked_count", len(blocked))
    for b in blocked:
        print("BLOCKED", b)
    return 0


if __name__ == "__main__":
    sys.exit(main())
