#!/usr/bin/env python3
"""Generate spec/schema_manifest.json (REQ-S15-003).

Registry order, filename, $id, schema version and the SHA-256 of the real bytes
of all 26 canonical schemas. Digests are read from disk, never carried forward,
so a stale entry is impossible by construction. REQ-S16-002 forbids placeholder
hashes and the same rule is applied here.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA_DIR = ROOT / "schemas"
OUT = ROOT / "spec/schema_manifest.json"


def main() -> int:
    files = sorted(SCHEMA_DIR.glob("*.schema.json"))
    if len(files) != 26:
        raise SystemExit(f"expected 26 canonical schemas, found {len(files)}")

    entries = []
    for order, path in enumerate(files, 1):
        raw = path.read_bytes()
        schema = json.loads(raw.decode("utf-8"))
        entries.append({
            "registry_order": order,
            "filename": path.name,
            "schema_id": schema["$id"],
            "title": schema.get("title", ""),
            "schema_version": schema["$schema"],
            "size_bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
        })

    manifest = {
        "manifest_version": "10.2.2",
        "generated_by": "tools/generate_schema_manifest.py",
        "digest_algorithm": "SHA-256",
        "digest_source": "raw file bytes on disk",
        "total_schemas": len(entries),
        "schemas": entries,
    }
    OUT.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} with {len(entries)} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
