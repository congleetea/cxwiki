#!/usr/bin/env python3
"""Validate generated HTML pages, local links, images, and shared assets."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def local_targets(page: Path) -> list[tuple[str, Path]]:
    text = page.read_text(encoding="utf-8")
    values = re.findall(r"(?:href|src)\s*=\s*['\"]([^'\"]+)['\"]", text, flags=re.I)
    targets: list[tuple[str, Path]] = []
    for raw in values:
        url = urlsplit(raw)
        if url.scheme or url.netloc or raw.startswith("/") or not url.path:
            continue
        target = (page.parent / unquote(url.path)).resolve()
        targets.append((raw, target))
    return targets


def main() -> int:
    if not SITE.exists():
        print("site/ does not exist; run python scripts/build_blog.py first", file=sys.stderr)
        return 1
    errors: list[str] = []
    pages = ([ROOT / "index.html"] if (ROOT / "index.html").exists() else []) + sorted(SITE.rglob("*.html"))
    if not pages:
        errors.append("site contains no HTML pages")
    for page in pages:
        text = page.read_text(encoding="utf-8")
        relative = page.relative_to(ROOT)
        if "<title>" not in text:
            errors.append(f"{relative}: missing <title>")
        is_redirect = "http-equiv=\"refresh\"" in text.lower()
        refresh = re.search(r"<meta[^>]+http-equiv=\"refresh\"[^>]+url=([^\"'>]+)", text, flags=re.I)
        if refresh:
            redirect_target = (page.parent / unquote(urlsplit(refresh.group(1).strip()).path)).resolve()
            if redirect_target == page.resolve():
                errors.append(f"{relative}: redirect points to itself")
        if not is_redirect and "assets/style.css" not in text and "../assets/style.css" not in text and "../../assets/style.css" not in text and "../../../assets/style.css" not in text:
            errors.append(f"{relative}: missing shared stylesheet")
        if not is_redirect and "<h1" not in text:
            errors.append(f"{relative}: missing main heading")
        for raw, target in local_targets(page):
            if not target.exists():
                errors.append(f"{relative}: broken local target {raw}")
        if re.search(r"(?:href|src)=['\"][^'\"]+\.md(?:[#?\"]|$)", text):
            errors.append(f"{relative}: generated page still points to Markdown")
    for asset in (SITE / "assets/style.css", SITE / "assets/blog.js"):
        if not asset.exists():
            errors.append(f"missing asset {asset.relative_to(SITE)}")
    images = list((SITE / "wiki" / "imgs").glob("*.png")) + list((SITE / "wiki" / "imgs").glob("*.svg"))
    if not images:
        errors.append("no copied image assets")
    for snapshot in (ROOT / "raw" / "codes").glob("*/snapshot.json"):
        copied = SITE / "raw" / "codes" / snapshot.parent.name
        if not copied.exists():
            errors.append(f"missing copied code snapshot {copied.relative_to(SITE)}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"checked {len(pages)} HTML pages and {len(images)} image assets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
