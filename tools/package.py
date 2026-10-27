"""Build dist/hover_glossary-<version>.ankiaddon from addon/.

Rebuilds the glossary data first so the package always ships the current definitions.
Usage: python3 tools/package.py
"""

import glob
import json
import os
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "addon")
SKIP_DIRS = {"__pycache__"}
SKIP_FILES = {".DS_Store", "meta.json", os.path.join("user_files", "overrides.json")}

subprocess.run([sys.executable, os.path.join(ROOT, "tools", "build_data.py"),
                *sorted(glob.glob(os.path.join(ROOT, "data", "defs", "batch_*.jsonl"))),
                "-o", os.path.join(SRC, "web", "glossary_data.js")], check=True)

version = json.load(open(os.path.join(SRC, "manifest.json")))["human_version"]
os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
out = os.path.join(ROOT, "dist", f"hover_glossary-{version}.ankiaddon")
count = 0
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for dirpath, dirnames, filenames in os.walk(SRC):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, SRC)
            if rel in SKIP_FILES or name in SKIP_FILES:
                continue
            z.write(path, rel)  # .ankiaddon = zip of the add-on folder's contents, no top folder
            count += 1
    for name in ("LICENSE", "LICENSE-DEFINITIONS"):
        z.write(os.path.join(ROOT, name), name)
        count += 1
print(f"{out}: {count} files, {os.path.getsize(out) / 1e6:.2f} MB")
