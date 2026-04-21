from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from steward.services.auth import API_KEY_SCHEME, AuthError, RequestIdentity, authenticate_api_key


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    session_factory: async_sessionmaker[AsyncSession] = request.app.state.session_factory
    async with session_factory() as session:
        yield session


async def require_request_identity(
    request: Request,
    authorization: str | None = Header(default=None),
    session: AsyncSession = Depends(get_db_session),
) -> RequestIdentity:
    if authorization is None:
        raise _unauthorized("Missing Authorization header.")

    scheme, _, token = authorization.partition(" ")
    if scheme != API_KEY_SCHEME or not token:
        raise _unauthorized("Authorization must use Bearer authentication.")

    try:
        identity = await authenticate_api_key(
            session,
            token,
            request_id=request.state.request_id,
        )
    except AuthError as exc:
        raise _unauthorized(str(exc)) from exc

    request.state.identity = identity
    return identity


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": API_KEY_SCHEME},
    )
