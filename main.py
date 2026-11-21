# Passport v2 entrypoint.
# The artwork itself is already rendered: entry.png sits right beside this
# file (draw.py produced it). This script only checks that the render is a
# genuine 1024x1024 JPEG under 1 MiB and drops a copy where the grader
# wants it. It never writes into the repo itself, because the grader mounts
# the repo read-only and hands us a writable output folder instead.
# Output folder priority: argv[1] first, then MAKEFUN_OUTPUT_DIR, then an
# "out" folder next to this script. No relative paths from the cwd.

import os
import shutil
import sys
from pathlib import Path

from PIL import Image

RENDER_NAME = "entry.png"
MAX_BYTES = 1024 * 1024
EXPECTED_SIZE = (1024, 1024)
JPEG_MAGIC = b"\xff\xd8\xff"


def fail(reason):
    print(f"entrypoint error: {reason}", file=sys.stderr)
    return 1


def locate_render():
    here = Path(__file__).resolve().parent
    return here / RENDER_NAME


def check_render(path):
    if not path.is_file():
        return f"missing render file: {path}"
    blob = path.read_bytes()
    if len(blob) >= MAX_BYTES:
        return f"render is {len(blob)} bytes, over the 1 MiB limit"
    if blob[:3] != JPEG_MAGIC:
        return "render does not start with JPEG magic bytes"
    with Image.open(path) as shot:
        if shot.size != EXPECTED_SIZE:
            return f"render is {shot.size[0]}x{shot.size[1]}, expected 1024x1024"
        if shot.format != "JPEG":
            return f"render format is {shot.format}, expected JPEG"
    return None


def pick_output_dir():
    if len(sys.argv) > 1 and sys.argv[1]:
        return Path(sys.argv[1])
    env_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip()
    if env_dir:
        return Path(env_dir)
    return Path(__file__).resolve().parent / "out"


def main():
    render = locate_render()
    problem = check_render(render)
    if problem is not None:
        return fail(problem)
    target_dir = pick_output_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    destination = target_dir / RENDER_NAME
    shutil.copyfile(render, destination)
    copied = destination.stat().st_size
    print(f"copied entry.png ({copied} bytes) to {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
