from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from steward.db.models import User
from steward.db.repositories import ApiKeyRepository, UserRepository

API_KEY_SCHEME = "Bearer"
API_KEY_NAMESPACE = "stwd"


class AuthError(Exception):
    """Raised when request authentication fails."""


@dataclass(slots=True, frozen=True)
class IssuedApiKey:
    key: str
    key_prefix: str
    user_id: str
    client_id: str | None
    description: str | None


@dataclass(slots=True, frozen=True)
class RequestIdentity:
    request_id: str
    user_id: str
    alias: str | None
    client_id: str | None
    api_key_id: int
    key_prefix: str
    is_admin: bool
    is_owner: bool


def hash_api_key(raw_key: str) -> str:
    digest = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def verify_api_key(raw_key: str, stored_hash: str) -> bool:
    return hmac.compare_digest(hash_api_key(raw_key), stored_hash)


def generate_api_key() -> tuple[str, str]:
    key_prefix = secrets.token_hex(6)
    secret = secrets.token_hex(24)
    raw_key = f"{API_KEY_NAMESPACE}.{key_prefix}.{secret}"
    return key_prefix, raw_key


def extract_key_prefix(raw_key: str) -> str:
    namespace, separator, remainder = raw_key.partition(".")
    if namespace != API_KEY_NAMESPACE or not separator:
        raise AuthError("Malformed API key.")

    key_prefix, separator, secret = remainder.partition(".")
    if not separator or not key_prefix or not secret:
        raise AuthError("Malformed API key.")
    return key_prefix


async def bootstrap_user(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    user_id: str,
    alias: str | None = None,
    is_admin: bool = False,
    is_owner: bool = False,
) -> User:
    async with session_factory() as session:
        repo = UserRepository(session)
        existing = await repo.get(user_id)
        if existing is not None:
            raise ValueError(f"User already exists: {user_id}")

        user = await repo.create(
            user_id=user_id,
            alias=alias,
            is_admin=is_admin,
            is_owner=is_owner,
        )
        await session.commit()
        return user


async def issue_api_key(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    user_id: str,
    client_id: str | None = None,
    description: str | None = None,
) -> IssuedApiKey:
    key_prefix, raw_key = generate_api_key()
    key_hash = hash_api_key(raw_key)

    async with session_factory() as session:
        users = UserRepository(session)
        api_keys = ApiKeyRepository(session)

        user = await users.get(user_id)
        if user is None:
            raise ValueError(f"Unknown user: {user_id}")

        await api_keys.create(
            user_id=user_id,
            key_prefix=key_prefix,
            key_hash=key_hash,
            client_id=client_id,
            description=description,
        )
        await session.commit()

    return IssuedApiKey(
        key=raw_key,
        key_prefix=key_prefix,
        user_id=user_id,
        client_id=client_id,
        description=description,
    )


async def revoke_api_key(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    key_prefix: str,
) -> None:
    async with session_factory() as session:
        api_keys = ApiKeyRepository(session)
        api_key = await api_keys.get_active_by_prefix(key_prefix)
        if api_key is None:
            raise ValueError(f"Unknown active API key: {key_prefix}")

        api_key.is_active = False
        api_key.revoked_at = datetime.now(UTC)
        await session.commit()


async def authenticate_api_key(
    session: AsyncSession,
    raw_key: str,
    *,
    request_id: str,
) -> RequestIdentity:
    key_prefix = extract_key_prefix(raw_key)
    api_keys = ApiKeyRepository(session)
    api_key = await api_keys.get_active_by_prefix(key_prefix)
    if api_key is None or not verify_api_key(raw_key, api_key.key_hash):
        raise AuthError("Invalid API key.")

    user = api_key.user
    return RequestIdentity(
        request_id=request_id,
        user_id=user.user_id,
        alias=user.alias,
        client_id=api_key.client_id,
        api_key_id=api_key.id,
        key_prefix=api_key.key_prefix,
        is_admin=user.is_admin,
        is_owner=user.is_owner,
    )
