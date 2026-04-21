from __future__ import annotations

from fastapi import APIRouter, Depends

from steward.api.dependencies import require_request_identity
from steward.services.auth import RequestIdentity

router = APIRouter(tags=["auth"])


@router.get("/v1/whoami")
async def whoami(
    identity: RequestIdentity = Depends(require_request_identity),
) -> dict[str, object]:
    return {
        "request_id": identity.request_id,
        "user_id": identity.user_id,
        "alias": identity.alias,
        "client_id": identity.client_id,
        "api_key_id": identity.api_key_id,
        "key_prefix": identity.key_prefix,
        "is_admin": identity.is_admin,
        "is_owner": identity.is_owner,
    }
