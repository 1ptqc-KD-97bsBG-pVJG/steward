from __future__ import annotations

import asyncio
from pathlib import Path

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession

from steward.db.migration import upgrade_database
from steward.db.models import ApiKey, Job, JobEvent, ServiceState, User
from steward.db.repositories import (
    ApiKeyRepository,
    JobEventRepository,
    JobRepository,
    ServiceStateRepository,
    UserRepository,
)
from steward.db.session import create_session_factory, make_sync_url


def test_upgrade_database_creates_expected_tables(tmp_path: Path) -> None:
    database_url = f"sqlite+aiosqlite:///{tmp_path / 'steward.db'}"

    upgrade_database(database_url)

    engine = inspect_database(database_url)
    assert sorted(engine.get_table_names()) == [
        "alembic_version",
        "api_keys",
        "job_events",
        "jobs",
        "service_state",
        "users",
    ]


def test_repositories_round_trip_entities(tmp_path: Path) -> None:
    database_url = f"sqlite+aiosqlite:///{tmp_path / 'steward.db'}"
    upgrade_database(database_url)

    asyncio.run(exercise_repositories(database_url))


def inspect_database(database_url: str):
    from sqlalchemy import create_engine

    engine = create_engine(make_sync_url(database_url))
    return inspect(engine)


async def exercise_repositories(database_url: str) -> None:
    session_factory = create_session_factory(database_url)

    async with session_factory() as session:
        await create_records(session)
        await session.commit()

    async with session_factory() as session:
        user = await session.get(User, "owner")
        api_key = await session.get(ApiKey, 1)
        job = await session.get(Job, "job-1")
        event = await session.get(JobEvent, 1)
        state = await session.get(ServiceState, "mode")

        assert user is not None
        assert user.alias == "Owner"
        assert api_key is not None
        assert api_key.client_id == "openclaw-wsl"
        assert job is not None
        assert job.requested_model == "qwen/qwen3-coder-next"
        assert event is not None
        assert event.event_type == "job_received"
        assert state is not None
        assert state.value == {"mode": "running"}


async def create_records(session: AsyncSession) -> None:
    users = UserRepository(session)
    api_keys = ApiKeyRepository(session)
    jobs = JobRepository(session)
    events = JobEventRepository(session)
    service_state = ServiceStateRepository(session)

    await users.create(user_id="owner", alias="Owner", is_admin=True, is_owner=True)
    await api_keys.create(
        user_id="owner",
        key_prefix="stwd_owner",
        key_hash="hashed-key-material",
        client_id="openclaw-wsl",
        description="OpenClaw WSL client",
    )
    await jobs.create(
        job_id="job-1",
        user_id="owner",
        state="queued",
        task_class="interactive_light",
        requested_model="qwen/qwen3-coder-next",
        request_payload={"messages": [{"role": "user", "content": "hello"}]},
        tooling_expected=False,
        input_chars_estimate=5,
        max_output_tokens=64,
        priority_score=100.0,
    )
    await events.create(
        job_id="job-1",
        event_type="job_received",
        state="queued",
        details={"source": "test"},
    )
    await service_state.put(key="mode", value={"mode": "running"})
