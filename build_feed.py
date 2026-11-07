#!/usr/bin/env python3
"""Build Bazar.bg XML from explicitly approved product records.

Source XML example was supplied by the owner for category 311.
Other categories need their own Bazar.bg field mapping.
No feed is generated while the catalog contains no approved items.
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
BASE_FIELDS = (
    "external_id", "title", "description", "category_id",
    "province_id", "city_id", "district_id", "phone",
    "images", "video", "type", "sizes", "condition",
    "delivery", "price", "price_type", "allow_offers",
    "hide_phone", "auto_renew"
)
REQUIRED = ("external_id", "title", "description", "category_id", "price")
TAG_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
LINK_RE = re.compile(r"https?://|www\.", re.I)


def check(item):
    sku = str(item.get("external_id", "(без код)"))
    for key in REQUIRED:
        if not str(item.get(key, "")).strip():
            raise ValueError(f"{sku}: липсва задължително поле {key}")
    if not str(item["category_id"]).isdigit():
        raise ValueError(f"{sku}: категорията трябва да има валиден числов ID")
    try:
        if Decimal(str(item["price"])) <= 0:
            raise ValueError("Цената трябва да е положителна")
    except InvalidOperation as exc:
        raise ValueError(f"{sku}: невалидна цена") from exc
    for field in ("title", "description"):
        if LINK_RE.search(str(item[field])):
            raise ValueError(f"{sku}: не добавяй външни линкове в {field}")
    images = item.get("images")
    if not isinstance(images, list) or not 1 <= len(images) <= 10:
        raise ValueError(f"{sku}: изискват се между 1 и 10 публични URL адреса на снимки")
    if not all(urlparse(u).scheme == "https" and urlparse(u).netloc for u in images):
        raise ValueError(f"{sku}: снимката трябва да има публичен HTTPS URL")
    extra = item.get("extra_fields", {})
    if not isinstance(extra, dict) or any(not TAG_RE.fullmatch(k) or k in BASE_FIELDS for k in extra):
        raise ValueError(f"{sku}: невалидни допълнителни XML полета")
    # Category values still require validation by Bazar importer during one-time setup.
    if not item.get("seller_approved"):
        raise ValueError(f"{sku}: липсва изрично одобрение за публикуване")


def build():
    document = json.loads((ROOT / "products.json").read_text(encoding="utf-8"))
    products = document.get("products", [])
    approved = [p for p in products if p.get("status") in ("approved", "approved_pending_import")]
    if not approved:
        print("Няма одобрени продукти. feed.xml не е създаден.", file=sys.stderr)
        return 2
    ids = [str(p.get("external_id")) for p in approved]
    if len(set(ids)) != len(ids):
        raise ValueError("Повтарящ се external_id")
    for p in approved:
        check(p)
    root = ET.Element("data")
    adverts = ET.SubElement(root, "adverts")
    for p in approved:
        advert = ET.SubElement(adverts, "advert")
        for field in BASE_FIELDS:
            value = p.get(field)
            if value is None or value == "":
                continue
            if field == "images":
                # Provisional multi-image encoding; importer mapping to be verified once.
                value = "|".join(value)
            ET.SubElement(advert, field).text = str(value)
        for field, value in p.get("extra_fields", {}).items():
            if value is not None and value != "":
                ET.SubElement(advert, field).text = str(value)
    ET.indent(root, space="  ")
    target = ROOT / "feed.xml"
    ET.ElementTree(root).write(target, encoding="utf-8", xml_declaration=True)
    print(f"Генериран feed.xml с {len(approved)} одобрени обяви")
    return 0


if __name__ == "__main__":
    sys.exit(build())
