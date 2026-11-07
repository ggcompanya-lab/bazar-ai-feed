#!/usr/bin/env python3
"""Validate XML and images before deployment (not a Bazar import confirmation)."""
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen
from build_feed import ACTIVE_STATUSES

ROOT = Path(__file__).resolve().parent
PUBLIC_HOST = "ggcompanya-lab.github.io"
PUBLIC_PREFIX = "/bazar-ai-feed/"
WP_HOST = "bazaraiphotos.wordpress.com"
WP_PREFIX = "/wp-content/uploads/"


def check_photo(url, sku):
    u = urlparse(url)
    if u.scheme != "https" or u.username or u.password or u.query or u.fragment:
        raise ValueError(f"{sku}: invalid photo URL")
    if u.netloc == PUBLIC_HOST and u.path.startswith(PUBLIC_PREFIX):
        relative = unquote(u.path[len(PUBLIC_PREFIX):])
        f = (ROOT / relative).resolve()
        if not f.is_relative_to(ROOT) or not f.is_file():
            raise ValueError(f"{sku}: photo file missing: {relative}")
        if not 0 < f.stat().st_size <= 50 * 1024 * 1024:
            raise ValueError(f"{sku}: invalid file size: {relative}")
        with f.open("rb") as src:
            if src.read(3) != b"\xff\xd8\xff":
                raise ValueError(f"{sku}: bad JPEG bytes: {relative}")
    elif u.netloc == WP_HOST and u.path.startswith(WP_PREFIX):
        request = Request(url, headers={"User-Agent": "BazarAIFeed/1.0"})
        with urlopen(request, timeout=20) as response:
            if response.status != 200 or not response.headers.get("Content-Type", "").startswith("image/"):
                raise ValueError(f"{sku}: external image is not reachable")
            if response.read(3) != b"\xff\xd8\xff":
                raise ValueError(f"{sku}: external image is not a JPEG")
    else:
        raise ValueError(f"{sku}: image origin not approved: {u.netloc}")


def main():
    data = json.loads((ROOT / "products.json").read_text(encoding="utf-8"))
    approved = [p for p in data.get("products", []) if p.get("status") in ACTIVE_STATUSES]
    ads = ET.parse(ROOT / "feed.xml").getroot().findall("./adverts/advert")
    if len(ads) != len(approved):
        raise ValueError(f"Mismatch: {len(ads)} XML ads versus {len(approved)} approved")
    by_id = {p["external_id"]: p for p in approved}
    seen = set()
    for ad in ads:
        sku = ad.findtext("external_id")
        if sku not in by_id or sku in seen:
            raise ValueError("Unexpected/duplicate approved product")
        seen.add(sku)
        item = by_id[sku]
        for key in ("price", "category_id", "title"):
            if ad.findtext(key) != str(item[key]):
                raise ValueError(f"{sku}: mismatch in {key}")
        images = ad.findtext("images", "").split("|")
        if images != item["images"]:
            raise ValueError(f"{sku}: photo URLs not in sync")
        for url in images:
            check_photo(url, sku)
        print(f"{sku}: verified {len(images)} JPEG images and XML record")
    print("All approved XML records validated; Bazar acceptance is still separate.")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"VALIDATION FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
