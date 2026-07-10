"""Backend entry point for uvicorn.

Use ``python main.py`` (reads SENTINEL_API_PORT from backend/.env, default 8080).
If you prefer uvicorn directly, pass the same port explicitly:

    uvicorn main:app --reload --host 0.0.0.0 --port 8080
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure ``src/`` is importable when the package is not installed (e.g. fresh CI).
_SRC = Path(__file__).resolve().parent / "src"
if _SRC.is_dir():
    src_path = str(_SRC)
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

from sentinel_anpr.bootstrap.app_entry import app, main

__all__ = ["app"]

if __name__ == "__main__":
    main()
