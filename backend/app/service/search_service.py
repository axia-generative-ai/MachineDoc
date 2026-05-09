from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import json
import httpx
from app.core.ai_client import call_ai_server
from app.schemas.search import AIQueryRequest
from app.crud.crud_error_code import error_code_repository
from app.crud.crud_search_history import search_history_repository

class SearchService:
    async def get_ai_diagnosis(self, db: Session, error_code: str, user_id: int):
        # 1. 초기 상태 설정
        ai_result = None
        search_status = "PENDING"
        raise_exception = False

        # 2. error_code 검증 로직
        db_error = error_code_repository.get_error_code_by_name(db, error_code.upper())
        try:
            if not db_error:
                search_status = "INVALID_CODE"
                raise ValueError("Unregistered error code")

            # 3. AI 서버 호출
            ai_result = await call_ai_server({"error_code": error_code})
            search_status = "COMPLETED"
            return ai_result
        except Exception as e:
            # 실패 상태 기록
            if search_status == "PENDING":
                search_status = "AI_ERROR"
            
            error_detail = str(e)
            ai_result = {"error": error_detail} # 실패 내용을 결과로 일단 담음
            raise_exception = True # 실패했으므로 최종적으로는 유저에게 에러를 알림. (저장 후 raise 예정)
        finally:
            # 4. 결과와 상관없이 무조건 검색 이력 저장
            search_history_repository.create_search_history(
                db, 
                user_id=user_id, 
                query=error_code, 
                result=json.dumps(ai_result),
                status=search_status
            )
            # 만약 위에서 에러가 발생했었다면 저장 후에 여기서 에러를 던짐.
            if raise_exception:
                if search_status == "INVALID_CODE":
                    raise HTTPException(status_code=404, detail="등록되지 않은 코드입니다.")
                raise HTTPException(status_code=503, detail="AI 분석 중 오류가 발생했습니다.")

    async def process_ai_query(self, db: Session, data: AIQueryRequest, user_id: int):
        # 1. 초기 상태 설정
        ai_result = None
        search_status = "PENDING"
        raise_exception = False
        
        # 2. 질의 문구 생성 (query로 사용될 내용)
        query_text = f"설비 {data.equipment_code} / {data.data_type} / 수치: {data.value}"

        try:
            # 3. AI 서버 호출 (실제 URL로 교체 필요)
            # 여기서는 예시로 httpx를 사용한 호출 구조를 유지합니다.
            async with httpx.AsyncClient() as client:
                # response = await client.post("AI_SERVER_URL", json=data.model_dump())
                # response.raise_for_status()
                # ai_result = response.json()
                
                # 테스트용 가상 응답
                ai_result = {"answer": f"{data.equipment_code}의 분석 결과입니다. 수치가 임계치를 초과했습니다."}
                search_status = "COMPLETED"
                return ai_result

        except Exception as e:
            # 실패 상태 및 내용 기록 준비
            search_status = "AI_ERROR"
            ai_result = {"error": str(e)}
            raise_exception = True
            
        finally:
            # 4. 결과와 상관없이 무조건 검색 이력 저장
            # 이 로직은 API 호출의 '성공/실패' 여부와 관계없이 DB에 기록을 남깁니다.
            search_history_repository.create_history(
                db, 
                user_id=user_id, 
                log_id=data.log_id,
                query=query_text,
                result=json.dumps(ai_result, ensure_ascii=False),
                status=search_status
            )

            # 에러가 발생했었다면 저장 완료 후 유저에게 예외 전달
            if raise_exception:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                    detail="AI 분석 요청 처리 중 오류가 발생하여 이력을 기록하고 중단했습니다."
                )
search_service = SearchService()
