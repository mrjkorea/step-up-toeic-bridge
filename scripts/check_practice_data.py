#!/usr/bin/env python3
"""Fail publish if practice data still references workbook page scans or vague stubs."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(ROOT, "data")
PHOTOS = os.path.join(ROOT, "assets", "photos")

PAGE_REF = re.compile(r"page-\d+\.(?:jpe?g|png)|/rc-pages/|rc-pages/", re.I)
VAGUE = re.compile(r"see the book page", re.I)
ALLOWED_PHOTO = re.compile(
    r"^(basic|intermediate|advanced)/(at/q\d+|p1-s\d\d/q0[1-6]|p1-s\d\d/(wu1|wu2|lp1|lp2))\.(?:png|jpe?g)$",
    re.I,
)


def check(assets_only: bool = False) -> int:
    errors: list[str] = []

    for dirpath, _, files in os.walk(PHOTOS):
        for name in files:
            if re.match(r"page-\d+\.(jpe?g|png)$", name, re.I):
                errors.append(f"workbook page file on disk: {os.path.join(dirpath, name)}")

    if assets_only:
        if errors:
            print("check_practice_data: FAIL (assets)", len(errors), file=sys.stderr)
            for e in errors[:50]:
                print(" ", e, file=sys.stderr)
            return 1
        print("check_practice_data: OK (assets only)")
        return 0

    for path in _iter_practice_json():
        rel = os.path.relpath(path, ROOT)
        d = json.load(open(path, encoding="utf-8"))
        pid = d.get("practiceId", os.path.basename(path)[:-5])
        if d.get("bookPages"):
            errors.append(f"{pid}: bookPages must be removed ({rel})")
        if d.get("pageImage"):
            errors.append(f"{pid}: practice pageImage banned ({rel})")
        for i, it in enumerate(d.get("items") or []):
            loc = f"{pid} item {it.get('id','?')} ({rel})"
            if it.get("blocked"):
                continue
            prompt = it.get("prompt") or it.get("stem") or ""
            if VAGUE.search(prompt):
                errors.append(f"{loc}: prompt still says 'see the book page'")
            for field in ("photo", "pageImage", "passageImage"):
                ref = it.get(field)
                if ref and PAGE_REF.search(str(ref)):
                    errors.append(f"{loc}: {field}={ref!r} is a full workbook page")
            pp = it.get("passagePage")
            if pp is not None and str(pp).strip() != "":
                errors.append(f"{loc}: passagePage={pp!r} banned (use passage text)")
            if it.get("passageNote"):
                errors.append(f"{loc}: passageNote OCR stub must be removed")
            ref = it.get("photo")
            if ref and not PAGE_REF.search(str(ref)):
                if not ALLOWED_PHOTO.match(str(ref).replace("\\", "/")):
                    errors.append(
                        f"{loc}: photo {ref!r} not in allowlist (AT or p1 TYS crops only)"
                    )
            for x in it.get("photos") or []:
                if PAGE_REF.search(str(x)):
                    errors.append(f"{loc}: photos[] has page scan {x!r}")

    if errors:
        print("check_practice_data: FAIL", len(errors), "issue(s)", file=sys.stderr)
        for e in errors[:200]:
            print(" ", e, file=sys.stderr)
        if len(errors) > 200:
            print(f"  ... and {len(errors)-200} more", file=sys.stderr)
        return 1
    print("check_practice_data: OK")
    return 0


def _iter_practice_json():
    for level in ("basic", "intermediate", "advanced"):
        for skill in ("lc", "rc"):
            d = os.path.join(DATA, level, skill)
            if not os.path.isdir(d):
                continue
            for name in sorted(os.listdir(d)):
                if name.endswith(".json"):
                    yield os.path.join(d, name)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--assets-only",
        action="store_true",
        help="Only fail if page-*.jpg/png files remain under assets/photos",
    )
    args = ap.parse_args()
    sys.exit(check(assets_only=args.assets_only))
