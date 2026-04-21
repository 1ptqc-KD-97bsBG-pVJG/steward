from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from steward.db.models import ApiKey, Job, JobEvent, ServiceState, User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        user_id: str,
        alias: str | None = None,
        is_admin: bool = False,
        is_owner: bool = False,
    ) -> User:
        user = User(user_id=user_id, alias=alias, is_admin=is_admin, is_owner=is_owner)
        self.session.add(user)
        await self.session.flush()
        return user

    async def get(self, user_id: str) -> User | None:
        return await self.session.get(User, user_id)


class ApiKeyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        user_id: str,
        key_prefix: str,
        key_hash: str,
        client_id: str | None = None,
        description: str | None = None,
    ) -> ApiKey:
        api_key = ApiKey(
            user_id=user_id,
            key_prefix=key_prefix,
            key_hash=key_hash,
            client_id=client_id,
            description=description,
        )
        self.session.add(api_key)
        await self.session.flush()
        return api_key

    async def get_active_by_prefix(self, key_prefix: str) -> ApiKey | None:
        statement = (
            select(ApiKey)
            .options(selectinload(ApiKey.user))
            .where(
                ApiKey.key_prefix == key_prefix,
                ApiKey.is_active.is_(True),
                ApiKey.revoked_at.is_(None),
            )
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def revoke(self, api_key: ApiKey) -> ApiKey:
        api_key.is_active = False
        api_key.revoked_at = api_key.updated_at
        await self.session.flush()
        return api_key


class JobRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        job_id: str,
        user_id: str,
        state: str,
        task_class: str,
        client_id: str | None = None,
        requested_model: str | None = None,
        request_payload: dict[str, Any] | None = None,
        tooling_expected: bool = False,
        input_chars_estimate: int | None = None,
        max_output_tokens: int | None = None,
        priority_score: float = 0.0,
    ) -> Job:
        job = Job(
            id=job_id,
            user_id=user_id,
            state=state,
            task_class=task_class,
            client_id=client_id,
            requested_model=requested_model,
            request_payload=request_payload,
            tooling_expected=tooling_expected,
            input_chars_estimate=input_chars_estimate,
            max_output_tokens=max_output_tokens,
            priority_score=priority_score,
        )
        self.session.add(job)
        await self.session.flush()
        return job


class JobEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        job_id: str,
        event_type: str,
        state: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> JobEvent:
        event = JobEvent(job_id=job_id, event_type=event_type, state=state, details=details)
        self.session.add(event)
        await self.session.flush()
        return event


class ServiceStateRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def put(self, *, key: str, value: dict[str, Any]) -> ServiceState:
        state = await self.session.get(ServiceState, key)
        if state is None:
            state = ServiceState(key=key, value=value)
            self.session.add(state)
        else:
            state.value = value
        await self.session.flush()
        return state

    async def get(self, key: str) -> ServiceState | None:
        return await self.session.get(ServiceState, key)
