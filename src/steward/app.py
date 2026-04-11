from fastapi import FastAPI

from steward.api.routes import health


def create_app() -> FastAPI:
    """Build the FastAPI application instance."""
    app = FastAPI(
        title="Steward",
        version="0.1.0",
        description="Local inference queue manager and scheduler.",
    )
    app.include_router(health.router)
    return app


app = create_app()

