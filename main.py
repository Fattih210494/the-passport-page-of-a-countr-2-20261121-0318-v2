#!/usr/bin/env python3
"""Entrypoint for the Republic of Sorrelia passport spread.

This script draws nothing by itself. The artwork lives in entry.png,
rendered by draw.py. This entrypoint only proves the rendered image
is present and well-formed, then places a copy in the output
directory so the make.fun harness can pick it up.

Checks performed: the file exists, is a real JPEG, measures exactly
1024 by 1024 pixels, and stays under one mebibyte.
"""

import sys
from pathlib import Path

from PIL import Image

EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
MAX_BYTES = 1024 * 1024


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def main(argv: list[str]) -> int:
    here = Path(__file__).resolve().parent
    source = here / "entry.png"
    if not source.is_file():
        fail(f"entry.png not found next to {__file__}")
    size = source.stat().st_size
    if size >= MAX_BYTES:
        fail(f"entry.png is {size} bytes, over the 1 MiB limit")
    try:
        with Image.open(source) as picture:
            picture.verify()
        with Image.open(source) as picture:
            width, height = picture.size
            fmt = picture.format
    except Exception as exc:  # unreadable or truncated image
        fail(f"entry.png could not be read as an image: {exc}")
    if fmt != "JPEG":
        fail(f"entry.png is {fmt}, expected JPEG")
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        fail(f"entry.png is {width}x{height}, expected 1024x1024")
    target_dir = Path(argv[1]) if len(argv) > 1 else Path("out")
    target_dir.mkdir(parents=True, exist_ok=True)
    destination = target_dir / "entry.png"
    destination.write_bytes(source.read_bytes())
    print(f"wrote {destination} ({destination.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
