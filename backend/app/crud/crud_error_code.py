from sqlalchemy.orm import Session
from app.models.error_code import ErrorCode

# 1. 에러 코드 존재 여부 확인
def get_error_code_by_name(db: Session, code_name: str):
    return db.query(ErrorCode).filter(ErrorCode.code_name == code_name).first()