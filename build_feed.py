#!/usr/bin/env python3
"""Build the Bazar.bg XML feed from seller-approved inventory only.

Only fields in the seller's Bazar.bg sample feed are emitted. This is
publishing preparation, not evidence that Bazar accepted the listing.
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
ACTIVE_STATUSES = {"approved", "approved_pending_import", "live"}
FIELDS = (
    "external_id", "title", "description", "category_id",
    "province_id", "city_id", "district_id", "phone",
    "images", "video", "type", "sizes", "condition",
    "delivery", "price", "price_type", "allow_offers",
    "hide_phone", "auto_renew"
)
REQUIRED = ("external_id", "title", "description", "category_id", "price")
FIELD_NAME = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$")
LINK = re.compile(r"https?://|www\.", re.I)


def approved_products(data):
    items = data.get("products")
    if not isinstance(items, list):
        raise ValueError("products трябва да бъде списък")
    ids = [str(p.get("external_id", "")).strip() for p in items]
    if any(not sid for sid in ids) or len(set(ids)) != len(ids):
        raise ValueError("Липсват или се повтарят external_id стойности")
    return [p for p in items if p.get("status") in ACTIVE_STATUSES]


def validate(item, known_categories):
    sku = item["external_id"]
    if item.get("seller_approved") is not True:
        raise ValueError(f"{sku}: липсва изрично одобрение от продавача")
    for key in REQUIRED:
        if not str(item.get(key, "")).strip():
            raise ValueError(f"{sku}: липсва {key}")
    if str(item["category_id"]) not in known_categories:
        raise ValueError(f"{sku}: непозната категория {item['category_id']} — провери я")
    for key in ("title", "description"):
        if LINK.search(str(item[key])):
            raise ValueError(f"{sku}: външни линкове в {key} не са позволени")
    try:
        price = Decimal(str(item["price"]))
    except InvalidOperation as exc:
        raise ValueError(f"{sku}: невалидна цена") from exc
    if not price.is_finite() or price <= 0 or price.as_tuple().exponent < -2:
        raise ValueError(f"{sku}: цената трябва да е положителна с до два десетични знака")
    if item.get("currency", "EUR") != "EUR":
        raise ValueError(f"{sku}: настройката за валута се нуждае от ръчна проверка")
    images = item.get("images")
    if not isinstance(images, list) or not 1 <= len(images) <= 10:
        raise ValueError(f"{sku}: очакват се 1–10 снимки")
    for url in images:
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
            raise ValueError(f"{sku}: невалиден HTTPS адрес на снимка")
    extra = item.get("extra_fields", {})
    if not isinstance(extra, dict):
        raise ValueError(f"{sku}: extra_fields трябва да е обект")
    if any(not FIELD_NAME.fullmatch(k) or k in FIELDS for k in extra):
        raise ValueError(f"{sku}: невалидно/повтарящо се XML поле в extra_fields")


def main():
    data = json.loads((ROOT / "products.json").read_text(encoding="utf-8"))
    cats = json.loads((ROOT / "category_registry.json").read_text(encoding="utf-8"))
    active = approved_products(data)
    if not active and not data.get("allow_empty_feed", False):
        print("Стоп: няма активни обяви. Празен feed се допуска само при allow_empty_feed=true.", file=sys.stderr)
        return 2
    for p in active:
        validate(p, cats.get("mappings", {}))
    root = ET.Element("data")
    adverts = ET.SubElement(root, "adverts")
    for p in sorted(active, key=lambda x: str(x["external_id"])):
        ad = ET.SubElement(adverts, "advert")
        for field in FIELDS:
            value = p.get(field, "")
            if value is None:
                value = ""
            if field == "images":
                # Seller's example has one <images> field.
                # Pipe joining is provisionally used; validate once with Bazar importer.
                value = "|".join(value)
            ET.SubElement(ad, field).text = str(value)
        for field, value in sorted(p.get("extra_fields", {}).items()):
            if value is not None and value != "":
                ET.SubElement(ad, field).text = str(value)
    ET.indent(root, space="  ")
    ET.ElementTree(root).write(ROOT / "feed.xml", xml_declaration=True, encoding="utf-8")
    print(f"Generated {len(active)} approved adverts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
