from fastapi import FastAPI

from steward.api.routes import health
from steward.config import StewardConfig, load_config


def create_app(config: StewardConfig | None = None) -> FastAPI:
    """Build the FastAPI application instance."""
    resolved_config = config or load_config()

    app = FastAPI(
        title="Steward",
        version="0.1.0",
        description="Local inference queue manager and scheduler.",
    )
    app.state.config = resolved_config
    app.include_router(health.router)
    return app


app = create_app()
