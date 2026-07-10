#!/usr/bin/env python3
"""Build the React frontend and copy the Vite dist into backend/static/frontend.

Used for single-service deployments (e.g. Render web service) where the API and
SPA share the same origin, so ``VITE_API_BASE_URL`` can remain empty.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parent
FRONTEND_DIR = REPO_ROOT / "frontend"
DIST_DIR = FRONTEND_DIR / "dist"
TARGET_DIR = BACKEND_DIR / "static" / "frontend"


def _run(command: list[str], *, cwd: Path, env: dict[str, str]) -> None:
    print(f"+ {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=cwd, env=env, check=True)


def main() -> int:
    package_json = FRONTEND_DIR / "package.json"
    if not package_json.is_file():
        print(f"Frontend not found at {FRONTEND_DIR}", file=sys.stderr)
        return 1

    env = os.environ.copy()
    env.setdefault("VITE_API_BASE_URL", "")
    env.setdefault("VITE_APP_ENV", "production")

    _run(["npm", "ci"], cwd=FRONTEND_DIR, env=env)
    _run(["npm", "run", "build"], cwd=FRONTEND_DIR, env=env)

    if not (DIST_DIR / "index.html").is_file():
        print(f"Build did not produce {DIST_DIR / 'index.html'}", file=sys.stderr)
        return 1

    if TARGET_DIR.exists():
        shutil.rmtree(TARGET_DIR)
    shutil.copytree(DIST_DIR, TARGET_DIR)
    print(f"Frontend bundle ready at {TARGET_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
