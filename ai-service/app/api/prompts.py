"""Admin-facing prompt CRUD.

The shared `prompts` table holds editable LLM prompt skeletons. Backend
proxies to these endpoints so admins can hot-edit the RAG prompt without
redeploying ai-service.
"""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.prompt_service import prompt_service

router = APIRouter(prefix="/api/v1/prompts", tags=["프롬프트 관리"])


class PromptOut(BaseModel):
    key: str
    content: str
    description: Optional[str] = None
    updated_at: Optional[str] = None


class PromptUpsert(BaseModel):
    content: str = Field(..., min_length=1)
    description: Optional[str] = None


@router.get("", response_model=List[PromptOut], summary="전체 프롬프트 조회")
def list_prompts() -> List[PromptOut]:
    return [
        PromptOut(key=r.key, content=r.content, description=r.description, updated_at=r.updated_at)
        for r in prompt_service.list_all()
    ]


@router.get("/{key}", response_model=PromptOut, summary="단일 프롬프트 조회")
def get_prompt(key: str) -> PromptOut:
    rows = [r for r in prompt_service.list_all() if r.key == key]
    if not rows:
        raise HTTPException(status_code=404, detail=f"prompt '{key}' not found")
    r = rows[0]
    return PromptOut(key=r.key, content=r.content, description=r.description, updated_at=r.updated_at)


@router.put("/{key}", response_model=PromptOut, summary="프롬프트 등록/수정")
def upsert_prompt(key: str, body: PromptUpsert) -> PromptOut:
    r = prompt_service.upsert(key, body.content, description=body.description)
    return PromptOut(key=r.key, content=r.content, description=r.description, updated_at=r.updated_at)
