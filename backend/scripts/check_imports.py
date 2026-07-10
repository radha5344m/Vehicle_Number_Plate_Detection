"""Verify all sentinel_anpr modules import without ModuleNotFoundError."""

from __future__ import annotations

import importlib
import pkgutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import sentinel_anpr  # noqa: E402

errors: list[tuple[str, str]] = []
count = 0

for mod in pkgutil.walk_packages(sentinel_anpr.__path__, sentinel_anpr.__name__ + "."):
    if mod.name.endswith(".placeholder"):
        continue
    count += 1
    try:
        importlib.import_module(mod.name)
    except ModuleNotFoundError as exc:
        errors.append((mod.name, str(exc)))

if errors:
    print("MODULE NOT FOUND ERRORS:")
    for name, message in errors:
        print(f"  {name}: {message}")
    raise SystemExit(1)

print(f"OK: {count} modules imported without ModuleNotFoundError")
