from sqlalchemy.orm import Session
from app.models.search_history import SearchHistory

class CRUDSearchHistory:
    def create_search_history(self, db: Session, *, user_id: int, query: str, result: str, status: str):
        """
        검색 이력을 DB에 저장합니다.
        성공(COMPLETED)뿐만 아니라 AI 에러(AI_ERROR), 유효하지 않은 코드(INVALID_CODE) 등
        서비스 단에서 넘겨준 상태값을 그대로 기록합니다.
        """
        db_obj = SearchHistory(
            user_id=user_id,
            query=query,
            result_content=result,  # AI 응답 혹은 에러 메시지(JSON 문자열)
            status=status           # 서비스 단에서 판단한 상태값
        )
        
        try:
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            db.rollback()
            # DB 저장 자체에 문제가 생겼을 때의 예외 처리
            print(f"SearchHistory 저장 실패: {e}")
            raise e

search_history_repository = CRUDSearchHistory()