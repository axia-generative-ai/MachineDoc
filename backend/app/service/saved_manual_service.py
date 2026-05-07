import os
import json
from fastapi import HTTPException
from app.core.ai_client import call_ai_server
from app.crud.crud_saved_manual import get_manuals_by_category, get_manual_by_id
from app.core.ai_client import call_ai_server
from fastapi.responses import FileResponse
from app.core.config import config

class ManualService:
    async def get_equipment_manual(self, db, equipment_code, category):
        manuals = []
        source = "database"

        # 1. 카테고리가 입력되었을 때만 DB 조회 실행
        if category:
            manuals = get_manuals_by_category(db, category=category)
        
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
        manual = get_manual_by_id(db, manual_id)
        
        if not manual:
            raise HTTPException(status_code=404, detail="매뉴얼을 찾을 수 없습니다.")
        
        # 2. 실제 파일 경로 확인 (DB에는 파일 시스템 경로가 저장되어 있다고 가정)
        file_path = config.MANUAL_URL + manual.file_url  # 예: "/data/manuals/m101_v1.pdf"
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="실제 매뉴얼 파일이 서버에 존재하지 않습니다.")

        # 3. FileResponse로 반환
        # filename은 다운로드 시 기본 파일명이 됩니다.
        return FileResponse(
            path=file_path, 
            media_type="application/pdf",
            filename=f"{manual.title}_{manual.version}.pdf"
        )

manual_service = ManualService()