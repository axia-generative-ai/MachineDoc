"""Admin-only proxy to ai-service prompt CRUD."""

from typing import List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api import deps
from app.core.ai_client import AI_SERVER_URL
from app.models.user import User

router = APIRouter()


class PromptOut(BaseModel):
    key: str
    content: str
    description: Optional[str] = None
    updated_at: Optional[str] = None


class PromptUpsert(BaseModel):
    content: str = Field(..., min_length=1)
    description: Optional[str] = None


def _ai_url(path: str) -> str:
    return f"{AI_SERVER_URL.rstrip('/')}{path}"


@router.get(
    "",
    summary="전체 프롬프트 조회 (관리자 전용)",
    response_model=List[PromptOut],
)
async def list_prompts(admin_user: User = Depends(deps.get_current_admin_user)):
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(_ai_url("/api/v1/prompts"))
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text[:200])
    return resp.json()


@router.get(
    "/{key}",
    summary="단일 프롬프트 조회 (관리자 전용)",
    response_model=PromptOut,
)
async def get_prompt(key: str, admin_user: User = Depends(deps.get_current_admin_user)):
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(_ai_url(f"/api/v1/prompts/{key}"))
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail=f"prompt '{key}' not found")
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text[:200])
    return resp.json()


@router.put(
    "/{key}",
    summary="프롬프트 등록/수정 (관리자 전용)",
    response_model=PromptOut,
)
async def upsert_prompt(
    key: str,
    body: PromptUpsert,
    admin_user: User = Depends(deps.get_current_admin_user),
):
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.put(_ai_url(f"/api/v1/prompts/{key}"), json=body.model_dump())
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text[:200])
    return resp.json()