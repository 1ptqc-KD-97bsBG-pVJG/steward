from uuid import uuid4

from fastapi import FastAPI
from starlette.responses import Response

from steward.api.routes import auth, health
from steward.config import StewardConfig, load_config
from steward.db import create_session_factory


def create_app(config: StewardConfig | None = None) -> FastAPI:
    """Build the FastAPI application instance."""
    resolved_config = config or load_config()

    app = FastAPI(
        title="Steward",
        version="0.1.0",
        description="Local inference queue manager and scheduler.",
    )
    app.state.config = resolved_config
    app.state.session_factory = create_session_factory(resolved_config.database.url)

    @app.middleware("http")
    async def add_request_context(request, call_next) -> Response:
        request_id = request.headers.get("X-Request-Id", str(uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        return response

    app.include_router(health.router)
    app.include_router(auth.router)
    return app


app = create_app()
