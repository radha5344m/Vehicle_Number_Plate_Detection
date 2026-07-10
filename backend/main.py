"""Backend entry point for uvicorn.

Use ``python main.py`` (reads SENTINEL_API_PORT from backend/.env, default 8080).
If you prefer uvicorn directly, pass the same port explicitly:

    uvicorn main:app --reload --host 0.0.0.0 --port 8080
"""

from sentinel_anpr.bootstrap.app_entry import app, main

__all__ = ["app"]

if __name__ == "__main__":
    main()
