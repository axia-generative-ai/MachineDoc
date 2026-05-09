import os
import shutil
from uuid import uuid4
from fastapi import HTTPException
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.core.ai_client import call_ai_server
from app.crud.crud_saved_manual import manual_repository
from fastapi.responses import FileResponse
from app.core.config import config
from app.schemas.manual import ManualCreate, ManualCreateInternal
from app.crud.crud_error_code import error_code_repository
from typing import List

class ManualService:
    async def get_equipment_manual(self, db, equipment_code, category):
        manuals = []
        source = "database"

        # 1. 카테고리가 입력되었을 때만 DB 조회 실행
        if category:
            manuals = manual_repository.get_manuals_by_category(db, category=category)
        else:
            manuals = manual_repository.get_manuals(db)
        
        # 2. 결과가 빈 리스트이거나 카테고리가 없는 경우 AI 서버로 전환
        if not manuals:
            source = "ai_recommendation"
            try:
                # AI 서버에는 설비명과 카테고리를 모두 전달하여 최적의 추천을 받음
                ai_payload = {
                    "request_type": "manual_search",
                    "equipment_code": equipment_code,
                    "category": category
                }
                ai_response = await call_ai_server(ai_payload)
                
                # AI 결과를 manuals 포맷에 맞춰 리턴 (구조는 AI 서버 응답에 따라 조정)
                return {
                    "source": source,
                    "query_info": {"equipment": equipment_code, "category": category},
                    "data": ai_response
                }
                
            except Exception as e:
                # AI 서버도 응답하지 못할 경우
                raise HTTPException(
                    status_code=503, 
                    detail="매뉴얼을 찾을 수 없으며, 추천 서버와의 통신에 실패했습니다."
                )

        # 3. DB에 데이터가 있는 경우 결과 반환
        return {
            "source": source,
            "data": manuals
        }
    
    def get_manual_file_response(self, db, manual_id):
        # 1. DB에서 매뉴얼 정보 조회
        manual = manual_repository.get_manual_by_id(db, manual_id)
        
        if not manual:
            raise HTTPException(status_code=404, detail="매뉴얼을 찾을 수 없습니다.")
        
        # 2. 실제 파일 경로 확인 (DB에는 파일 시스템 경로가 저장되어 있다고 가정)
        if os.path.isabs(manual.file_url):
            file_path = manual.file_url
        else:
            file_path = os.path.join("/code/static/data", manual.file_url)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="실제 매뉴얼 파일이 서버에 존재하지 않습니다.")

        # 3. FileResponse로 반환
        # filename은 다운로드 시 기본 파일명이 됩니다.
        return FileResponse(
            path=file_path, 
            media_type="application/pdf",
            filename=f"{manual.title}_{manual.version}.pdf"
        )
    
    async def upload_manual_process(
        self, 
        db: Session, 
        manual_in: ManualCreate, 
        error_codes: List[str], 
        file: UploadFile, 
        user_id: int
    ):
        # 1. 파일 저장 경로 설정 및 물리적 저장
        # 컨테이너 내부 경로 기준입니다.
        upload_dir = "/code/static/data"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_extension = os.path.splitext(file.filename)[1]
        safe_filename = f"{uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, safe_filename)

        try:
            # 실제 파일 저장 (I/O)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"서버에 파일을 저장하는 중 오류가 발생했습니다: {str(e)}")

        # 2. DB 트랜잭션 시작
        try:
            # 내부용 DTO 생성 (manual_in 데이터 + 서버 생성 데이터)
            manual_internal = ManualCreateInternal(
                **manual_in.model_dump(),
                user_id=user_id,
                file_url=file_path
            )

            # [Step A] 매뉴얼 메타데이터 저장 (ManualRepo)
            new_manual = manual_repository.create(db, manual_internal)

            # [Step B] 에러 코드 리스트 저장 (ErrorCodeRepo)
            if error_codes:
                error_code_repository.create_multiple(
                    db, 
                    manual_id=new_manual.manual_id, 
                    codes=error_codes
                )

            # 모든 작업이 성공하면 DB에 최종 반영
            db.commit()
            db.refresh(new_manual)
            
            return new_manual

        except Exception as e:
            # DB 작업 중 하나라도 실패하면 롤백 (원자성 보장)
            db.rollback()
            
            # DB 저장에 실패했으므로 이미 저장된 물리 파일도 삭제하여 찌꺼기를 남기지 않음
            if os.path.exists(file_path):
                os.remove(file_path)
                
            raise HTTPException(status_code=500, detail=f"데이터베이스 기록 중 오류가 발생했습니다: {str(e)}")

manual_service = ManualService()
