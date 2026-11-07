#!/usr/bin/env python3
"""Read-only catalog report. Never marks a product published in Bazar."""
import json
from pathlib import Path
from build_feed import ACTIVE_STATUSES, approved_products, validate

ROOT = Path(__file__).resolve().parent

def main():
    data = json.loads((ROOT / "products.json").read_text(encoding="utf-8"))
    registry = json.loads((ROOT / "category_registry.json").read_text(encoding="utf-8"))
    mappings = registry.get("mappings", {})
    ready = approved_products(data)
    print(f"В каталога има {len(data.get('products', []))} продукта, от които {len(ready)} са одобрени за feed.")
    for p in data.get("products", []):
        sku = p["external_id"]
        if p.get("status") not in ACTIVE_STATUSES:
            print(f"{sku}: ЧЕРНОВА/НЕАКТИВЕН — не се включва.")
            continue
        validate(p, mappings)
        cat = mappings[str(p["category_id"])]
        if cat.get("verification_status") != "verified":
            print(f"{sku}: XML ГОТОВ, НО ИМПОРТЪТ В BAZAR ОЩЕ НЕ Е ПРОВЕРЕН.")
        else:
            print(f"{sku}: XML ГОТОВ — успешното публикуване в Bazar трябва да се потвърди отделно.")
    print("Проверката не променя никакви обяви.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
