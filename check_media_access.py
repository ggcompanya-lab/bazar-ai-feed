#!/usr/bin/env python3
"""Read-only test that the public Bazar image host serves actual JPEG bytes."""
import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent

def main():
    config = json.loads((ROOT / "media_config.json").read_text(encoding="utf-8"))
    url = config["test_media_url"]
    request = Request(url, headers={"User-Agent":"BazarAIFeed-ImageHealth/1.0"})
    with urlopen(request, timeout=20) as response:
        typ = response.headers.get("Content-Type", "")
        prefix = response.read(3)
        if response.status != 200 or not typ.startswith("image/") or prefix != b"\xff\xd8\xff":
            raise ValueError(f"Image inaccessible: HTTP {response.status}, {typ}, bytes={prefix!r}")
        print(f"Public image OK: HTTP {response.status} {typ}")
    return 0

if __name__ == "__main__":
    try: sys.exit(main())
    except Exception as e:
        print(f"Media host test failed: {e}", file=sys.stderr)
        sys.exit(1)
