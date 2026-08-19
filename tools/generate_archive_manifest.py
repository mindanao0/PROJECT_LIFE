#!/usr/bin/env python3
"""Generate spec/archive/manifest.json (REQ-S00-009).

Two digests are recorded and they mean different things:

  original_span_sha256  the ARCHIVE_BEGIN..ARCHIVE_END span exactly as it stood in
                        commit 26493b3, proving the recovered content is the real
                        archive and nothing was dropped
  file_sha256           the file as stored here, which differs by one documented
                        transformation (see transformations below)

file_sha256 is always read from disk, so it cannot go stale.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ARCHIVE = ROOT / "spec/archive/Plan_10_2_0_Historical_Archive.md"
OUT = ROOT / "spec/archive/manifest.json"
SOURCE_COMMIT = "26493b3"
SOURCE_FILE = "Evolution_Engine_Plan_10_2_2_Complete_Single_File_Canonical_Release.md"


def original_span() -> tuple[str, int] | tuple[None, None]:
    try:
        blob = subprocess.run(
            ["git", "show", f"{SOURCE_COMMIT}:{SOURCE_FILE}"],
            capture_output=True, text=True, cwd=ROOT, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None, None
    lines = blob.split("\n")
    begin = next(i for i, l in enumerate(lines) if l.strip() == "<!-- ARCHIVE_BEGIN -->")
    end = next(i for i, l in enumerate(lines) if l.strip() == "<!-- ARCHIVE_END -->")
    span = "\n".join(lines[begin:end + 1])
    return hashlib.sha256(span.encode()).hexdigest(), end - begin + 1


def main() -> int:
    if not ARCHIVE.exists():
        raise SystemExit(f"{ARCHIVE.relative_to(ROOT)} is missing")
    raw = ARCHIVE.read_bytes()
    span_digest, span_lines = original_span()

    manifest = {
        "archive_version": "10.2.0",
        "authority": "NON-NORMATIVE / SUPERSEDED",
        "file": str(ARCHIVE.relative_to(ROOT)),
        "recovered_from_commit": SOURCE_COMMIT,
        "deleted_at_commit": "cac1d52",
        "withdrawn_by": "CR-0001",
        "digest_algorithm": "SHA-256",
        "original_span_sha256": span_digest,
        "original_span_line_count": span_lines,
        "file_sha256": hashlib.sha256(raw).hexdigest(),
        "file_line_count": raw.decode("utf-8").count("\n"),
        "file_size_bytes": len(raw),
        "transformations": [
            "Absolute file:///Users/... links were flattened to plain text; they "
            "pointed at the original author's machine and resolved nowhere. This is "
            "why file_sha256 differs from original_span_sha256.",
        ],
    }
    OUT.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} — {manifest['file_line_count']} lines, "
          f"file digest {manifest['file_sha256'][:16]}...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
