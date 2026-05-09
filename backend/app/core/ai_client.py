import os
from typing import Any, Dict

import httpx
from fastapi import HTTPException


AI_SERVER_URL = os.getenv("AI_SERVICE_URL", "http://host.docker.internal:8001")


async def call_ai_server(payload: Dict[str, Any]) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{AI_SERVER_URL}/api/v1/search",
                json=payload,
                timeout=180.0,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"AI server response error: {e.response.text}",
            ) from e
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"AI server connection failed: {str(e)}",
            ) from e
