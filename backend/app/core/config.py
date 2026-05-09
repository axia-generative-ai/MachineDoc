import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def _resolve_manual_dir() -> Path:
    """매뉴얼 PDF 디렉토리 자동 탐지.

    우선순위:
      1. env `MANUAL_DIR` 명시값 (절대/상대 모두 OK)
      2. 레포 루트 추정: backend/app/core/config.py → parents[3] = repo 루트
      3. CWD 기준 `ai-service/manuals/` 또는 `../ai-service/manuals/` 폴백
      4. 위 모두 실패 시 `./uploads/`로 자동 생성
    """
    env_value = os.getenv("MANUAL_DIR")
    if env_value:
        path = Path(env_value).expanduser().resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path

    here = Path(__file__).resolve()
    candidates = [
        here.parents[3] / "ai-service" / "manuals",
        Path.cwd() / "ai-service" / "manuals",
        Path.cwd().parent / "ai-service" / "manuals",
    ]
    for cand in candidates:
        if cand.is_dir():
            return cand.resolve()

    # 최후 폴백: backend 작업 디렉토리에 uploads/ 자동 생성
    fallback = (here.parents[2] / "uploads").resolve()
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback


_MANUAL_DIR = _resolve_manual_dir()


class Settings:
    PROJECT_NAME: str = "Smart Factory RAG Project"
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))
    MANUAL_URL: str = str(_MANUAL_DIR) + os.sep


config = Settings()
