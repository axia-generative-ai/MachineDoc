from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text  # SQL 구문을 직접 실행하기 위해 필요
from app.core.database import get_db
from app.core.config import config
from app.db.session import engine
from app.db.base import Base

from app.api.v1.endpoints import auth, users, search, manual


app = FastAPI(title="FactoryGuard API",
    description="스마트 팩토리 보안 및 관리 시스템을 위한 백엔드 API 문서입니다.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["인증"])

app.include_router(users.router, prefix="/api/v1/users", tags=["유저"])

app.include_router(search.router, prefix="/api/v1/search", tags=["검색"])

app.include_router(manual.router, prefix="/api/v1/manual", tags=["매뉴얼"])
