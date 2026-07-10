"""Application entry point."""

import uvicorn

from sentinel_anpr.infrastructure.config.settings import get_settings
from sentinel_anpr.interfaces.rest_api.app.create_app import create_app

app = create_app()


def main() -> None:
    """Run the API server."""
    settings = get_settings()
    uvicorn.run(
        "sentinel_anpr.bootstrap.app_entry:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.env == "development",
    )


if __name__ == "__main__":
    main()
