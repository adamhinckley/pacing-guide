#!/usr/bin/env python3
"""Write version.json from the content hash of shipped app files."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "version.json"
SOURCE_FILES = [
    ROOT / "index.html",
    ROOT / "pacing-data.js",
    ROOT / "pacing-lib.js",
    ROOT / "sw.js",
    ROOT / "site.webmanifest",
]


def main() -> None:
    digest = hashlib.sha256()
    for path in SOURCE_FILES:
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    version = digest.hexdigest()[:12]
    OUT_PATH.write_text(
        json.dumps({"version": version}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUT_PATH} (version {version})")


if __name__ == "__main__":
    main()
