import os
import httpx
from fastapi import HTTPException
from typing import Any, Dict

AI_SERVER_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8001")

async def call_ai_server(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    AI 서버(ai-service)의 /api/v1/search 로 위임.
    payload: {"error_code": "...", "equipment_id"?: "..."}
    응답: {"status", "analysis", "solution"}
    """
    url = f"{AI_SERVER_URL.rstrip('/')}/api/v1/search"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"AI 서버 응답 오류: {e.response.text}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"AI 서버 연결 실패: {str(e)}")
