#!/usr/bin/env python3
"""Read-only publishing readiness report; never approves or publishes anything."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def main():
    data=json.loads((ROOT/"products.json").read_text(encoding="utf-8"))
    categories=json.loads((ROOT/"category_registry.json").read_text(encoding="utf-8"))
    mappings=categories.get("mappings",{})
    products=data.get("products",[])
    print(f"Products: {len(products)}")
    seen=set()
    ready=0
    for p in products:
        sku=p.get("external_id","UNKNOWN")
        pending=[]
        if sku in seen: pending.append("duplicate_external_id")
        seen.add(sku)
        if not p.get("title"): pending.append("title")
        if not p.get("description"): pending.append("description")
        if not p.get("price"): pending.append("price")
        cat=str(p.get("category_id",""))
        if not cat or cat not in mappings: pending.append("category_mapping")
        elif mappings[cat].get("verification_status")!="verified": pending.append("category_fields_not_verified")
        if not p.get("category_fields_verified"): pending.append("category_fields_not_verified_for_product")
        if not p.get("images"): pending.append("public_photo_links")
        if p.get("status")!="approved": pending.append("seller_approval")
        print(f"{sku}: {'READY' if not pending else 'NOT_READY'}; pending={', '.join(pending)}")
        if not pending: ready+=1
    print(f"Publish-ready products: {ready}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
