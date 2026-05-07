from fastapi import HTTPException
from sqlalchemy.orm import Session
import json
from app.core.ai_client import call_ai_server
from app.crud.crud_error_code import get_error_code_by_name
from app.crud.crud_search_history import create_search_history

class SearchService:
    async def get_ai_diagnosis(self, db: Session, error_code: str, user_id: int):
        # 1. 초기 상태 설정
        ai_result = None
        search_status = "PENDING"
        raise_exception = False

        # 2. error_code 검증 로직
        db_error = get_error_code_by_name(db, error_code.upper())
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
            create_search_history(
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

# 싱글톤으로 사용하기 위해 인스턴스 생성
search_service = SearchService()