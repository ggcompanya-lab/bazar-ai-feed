import json
import unittest
from pathlib import Path
from copy import deepcopy
from build_feed import approved_products, validate

ROOT = Path(__file__).resolve().parent
CATALOG = json.loads((ROOT / "products.json").read_text(encoding="utf-8"))
CATS = json.loads((ROOT / "category_registry.json").read_text(encoding="utf-8"))["mappings"]

class FeedTests(unittest.TestCase):
    def test_current_catalog_has_no_duplicate_codes(self):
        codes = [p["external_id"] for p in CATALOG["products"]]
        self.assertEqual(len(codes), len(set(codes)))

    def test_drafts_are_not_exported(self):
        item = deepcopy(CATALOG["products"][0])
        item["status"] = "draft"
        self.assertEqual(approved_products({"products": [item]}), [])

    def test_approval_is_mandatory(self):
        item = deepcopy(CATALOG["products"][0])
        item["seller_approved"] = False
        with self.assertRaises(ValueError):
            validate(item, CATS)

    def test_invalid_price_rejected(self):
        item = deepcopy(CATALOG["products"][0])
        item["price"] = "NaN"
        with self.assertRaises(ValueError):
            validate(item, CATS)

    def test_unknown_category_rejected(self):
        item = deepcopy(CATALOG["products"][0])
        item["category_id"] = "999999999"
        with self.assertRaises(ValueError):
            validate(item, CATS)

    def test_duplicate_code_rejected(self):
        p = deepcopy(CATALOG["products"][0])
        with self.assertRaises(ValueError):
            approved_products({"products": [p, deepcopy(p)]})

if __name__ == "__main__":
    unittest.main()
