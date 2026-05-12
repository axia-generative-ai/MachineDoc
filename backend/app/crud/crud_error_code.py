from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.error_code import ErrorCode
from typing import List

class CRUDErrorCode:
    # 1. 에러 코드 존재 여부 확인 (case-insensitive — 벤더 코드가 mixed case: oH, COM.E 등)
    def get_error_code_by_name(self, db: Session, code_name: str):
        return (
            db.query(ErrorCode)
            .filter(func.lower(ErrorCode.code_name) == code_name.lower())
            .first()
        )

    def create_multiple(self, db: Session, manual_id: int, codes: List[str]):
        for code_str in codes:
            new_error_code = ErrorCode(
                manual_id=manual_id,
                code_name=code_str,
            )
            db.add(new_error_code)

error_code_repository = CRUDErrorCode()