from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine
from app.db.base import Base

from app.api.v1.endpoints import dashboard, auth, users, search, manual, log, notification, websocket, prompts

app = FastAPI(title="FactoryGuard API",
    description="스마트 팩토리 보안 및 관리 시스템을 위한 백엔드 API 문서입니다.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True, # 필수!
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["대시보드"])

app.include_router(auth.router, prefix="/api/v1/auth", tags=["인증"])

app.include_router(users.router, prefix="/api/v1/users", tags=["유저"])

app.include_router(search.router, prefix="/api/v1/search", tags=["검색"])

app.include_router(manual.router, prefix="/api/v1/manual", tags=["매뉴얼"])

app.include_router(log.router, prefix="/api/v1/log", tags=["로그"])

app.include_router(notification.router, prefix="/api/v1/notifications", tags=["알림"])

app.include_router(prompts.router, prefix="/api/v1/prompts", tags=["프롬프트 관리"])

app.include_router(websocket.router, prefix="/ws/v1", tags=["웹소켓"])
