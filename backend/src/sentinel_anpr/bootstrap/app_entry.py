"""Application entry point."""

import uvicorn

from sentinel_anpr.infrastructure.config.settings import get_settings
from sentinel_anpr.interfaces.rest_api.app.create_app import create_app

app = create_app()


def _should_enable_reload(settings) -> bool:
    """Disable auto-reload with SQLite — reload spawns a second process and locks the DB."""
    if settings.env != "development":
        return False
    return not settings.database_url.strip().lower().startswith("sqlite")


def main() -> None:
    """Run the API server."""
    settings = get_settings()
    uvicorn.run(
        "sentinel_anpr.bootstrap.app_entry:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=_should_enable_reload(settings),
    )


if __name__ == "__main__":
    main()
