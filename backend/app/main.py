from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text  # SQL 구문을 직접 실행하기 위해 필요
from app.core.database import get_db
from app.core.config import config

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": config.PROJECT_NAME}

# DB 연결 상태 확인 API
@app.get("/db-check")
def check_db_connection(db: Session = Depends(get_db)):
    try:
        # DB에 '1'을 조회하는 아주 가벼운 쿼리를 날려봅니다.
        result = db.execute(text("SELECT 1")).fetchone()
        
        if result:
            return {"status": "success", "message": "데이터베이스 연결이 완벽합니다!"}
            
    except Exception as e:
        # 연결 실패 시 에러 메시지 반환
        raise HTTPException(
            status_code=500, 
            detail={"status": "error", "detail": str(e)}
        )