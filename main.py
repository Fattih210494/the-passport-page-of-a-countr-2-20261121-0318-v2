"""Deliver the finished passport spread to the grader.

draw.py renders entry.png (a JPEG) next to this file. This entrypoint
only checks that the picture is a genuine JPEG under the 1 MiB cap,
then copies it into the folder the harness reads (MAKEFUN_OUTPUT_DIR,
or ./out when unset). Pure standard library: the sandbox needs
nothing beyond Python 3.13.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

LIMIT = 1_048_576
MAGIC = b"\xff\xd8\xff"


def find_picture() -> Path:
    return Path(__file__).resolve().with_name("entry.png")


def target_folder() -> Path:
    override = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if override:
        return Path(override)
    return Path(__file__).resolve().parent / "out"


def read_picture(picture: Path) -> bytes:
    if not picture.is_file():
        raise SystemExit(f"entry picture missing: {picture}")
    data = picture.read_bytes()
    if data[:3] != MAGIC:
        raise SystemExit(f"{picture} is not a JPEG (bad magic bytes)")
    if len(data) > LIMIT:
        raise SystemExit(
            f"{picture} is {len(data)} bytes, over the {LIMIT}-byte cap")
    return data


def deliver() -> int:
    payload = read_picture(find_picture())
    folder = target_folder()
    folder.mkdir(parents=True, exist_ok=True)
    dest = folder / "entry.png"
    shutil.copyfile(find_picture(), dest)
    print(f"wrote {dest} ({len(payload)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(deliver())
