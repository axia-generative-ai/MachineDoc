import httpx
from fastapi import HTTPException
from typing import Any, Dict

# AI 서버 주소 (나중에 config에서 관리하세요!)
AI_SERVER_URL = "http://localhost:8080"

async def call_ai_server(payload: Dict[str, Any]) -> Dict[str, Any]:
    # AI 서버가 완성될 때까지 임시로 가짜 데이터 리턴
    return {
        "status": "mock_success",
        "analysis": "AI 서버가 아직 준비되지 않아 테스트 데이터를 반환합니다.",
        "solution": "기계를 껐다 켜보세요."
    }
    
    """
    AI 서버와 비동기 통신을 담당하는 공통 함수
    :param payload: JSON으로 보낼 데이터 (딕셔너리)
    :return: AI 서버의 응답 결과
    """
    async with httpx.AsyncClient() as client:
        try:
            # json= 파라미터를 사용하면 자동으로 Content-Type이 application/json이 됩니다.
            response = await client.post(
                AI_SERVER_URL, 
                json=payload, 
                timeout=20.0  # AI 연산 시간을 고려해 넉넉히 설정
            )
            # 4xx, 5xx 에러 발생 시 예외 발생
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            # 서버는 응답했으나 에러인 경우 (예: 404, 500)
            raise HTTPException(status_code=e.response.status_code, detail=f"AI 서버 응답 오류: {e.response.text}")
        except httpx.RequestError as e:
            # 네트워크 문제나 주소가 잘못된 경우
            raise HTTPException(status_code=503, detail=f"AI 서버 연결 실패: {str(e)}")