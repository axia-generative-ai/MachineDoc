from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import config

# 도커 환경이므로 db 호스트 사용
SQLALCHEMY_DATABASE_URL = config.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모든 모델이 상속받을 기본 클래스
Base = declarative_base()

# API 엔드포인트에서 DB 연결이 필요할 때 'Depends(get_db)'로 사용합니다.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() # 요청이 끝나면 자동으로 연결을 닫아줌 (메모리 누수 방지)