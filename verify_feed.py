#!/usr/bin/env python3
"""Validate generated feed and locally hosted product JPEG files.

This verifies GitHub Pages deployment artifacts, not Bazar acceptance.
"""
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlparse
from build_feed import ACTIVE_STATUSES

ROOT = Path(__file__).resolve().parent
PUBLIC_HOST = "ggcompanya-lab.github.io"
PUBLIC_PREFIX = "/bazar-ai-feed/"

def main():
    catalog = json.loads((ROOT / "products.json").read_text(encoding="utf-8"))
    live = [p for p in catalog["products"] if p.get("status") in ACTIVE_STATUSES]
    root = ET.parse(ROOT / "feed.xml").getroot()
    ads = root.findall("./adverts/advert")
    if len(ads) != len(live):
        raise ValueError(f"Count mismatch: {len(ads)} XML ads, {len(live)} approved products")
    by_id = {p["external_id"]: p for p in live}
    seen = set()
    for ad in ads:
        sid = ad.findtext("external_id")
        if sid not in by_id or sid in seen:
            raise ValueError("Duplicate or unapproved advert in feed")
        seen.add(sid)
        product = by_id[sid]
        if ad.findtext("price") != str(product["price"]):
            raise ValueError(f"{sid}: price mismatch")
        if ad.findtext("category_id") != str(product["category_id"]):
            raise ValueError(f"{sid}: category mismatch")
        urls = ad.findtext("images", "").split("|")
        if urls != product["images"]:
            raise ValueError(f"{sid}: photo mismatch")
        for url in urls:
            u = urlparse(url)
            if u.scheme != "https" or u.netloc != PUBLIC_HOST or not u.path.startswith(PUBLIC_PREFIX):
                raise ValueError(f"{sid}: all photos must be hosted on our GitHub Pages HTTPS origin")
            rel = unquote(u.path[len(PUBLIC_PREFIX):])
            candidate = (ROOT / rel).resolve()
            if not candidate.is_relative_to(ROOT) or not candidate.is_file():
                raise ValueError(f"{sid}: missing image file: {rel}")
            if candidate.stat().st_size > 50 * 1024 * 1024 or candidate.stat().st_size == 0:
                raise ValueError(f"{sid}: invalid image file size: {rel}")
            with candidate.open("rb") as fh:
                if fh.read(3) != b"\xff\xd8\xff":
                    raise ValueError(f"{sid}: not a JPEG: {rel}")
        print(f"{sid}: XML and {len(urls)} original image files verified")
    if len(seen) != len(by_id):
        raise ValueError("Some approved products are missing from XML")
    print("Feed structure and image assets OK. Bazar import remains a separate step.")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, ET.ParseError) as exc:
        print(f"VALIDATION FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
