from fastapi import APIRouter, Depends, Query
from app.service.saved_manual_service import manual_service
from app.models.user import User
from sqlalchemy.orm import Session
from app.api import deps
from typing import List
from app.schemas.manual import SearchManual
from fastapi.responses import FileResponse

router = APIRouter()

@router.get(
    "/search", 
    summary="설비 매뉴얼 통합 조회", 
    response_model=List[SearchManual]
)
async def search_equipment_manual(
    equipment_code: str = Query(None, description="조회할 설비 코드 혹은 설비명 (예: M-101)", examples="M-101"),
    category: str = Query(None, description="매뉴얼 카테고리 (예: 점검, 수리)", examples="test_category"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    설비명과 카테고리를 이용해 관련 매뉴얼을 조회합니다.
    
    1. **DB 우선 조회**: 입력된 카테고리가 있다면 시스템 내 저장된 공식 매뉴얼을 먼저 검색합니다.
    2. **AI 추천 전환**: 카테고리가 없거나 DB 검색 결과가 없는 경우, AI 서버가 설비명과 카테고리를 분석하여 유사 매뉴얼 정보를 추천합니다.
    3. **데이터 출처 표시**: 응답의 **source** 필드를 통해 데이터가 DB(database)인지 AI(ai_recommendation)인지 확인할 수 있습니다.

    - **equipment_code**: 설비 식별 코드 (AI 추천 시 활용)
    - **category**: 매뉴얼 분류 (DB 검색 및 AI 분석 키워드)
    - **auth**: 로그인한 사용자만 접근 가능
    """
    result = await manual_service.get_equipment_manual(db, equipment_code, category)
    return result["data"]

@router.get(
    "/{manual_id}", 
    summary="매뉴얼 파일 보기/다운로드",
    response_class=FileResponse,
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "PDF 파일이 성공적으로 반환됩니다."
        },
        404: {"description": "요청한 ID의 매뉴얼이 DB에 없거나 실제 파일이 서버에 존재하지 않습니다."},
        500: {"description": "파일 읽기 중 서버 내부 오류가 발생했습니다."}
    }
)
async def view_manual_file(
    manual_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    지정한 ID에 해당하는 매뉴얼 PDF 파일을 서버에서 직접 스트리밍하여 반환합니다.
    
    ### 🛠 동작 방식
    1. **권한 확인**: 유효한 토큰을 가진 사용자만 접근 가능합니다.
    2. **파일 매핑**: 전달받은 **manual_id**를 기반으로 내부 저장소의 실제 PDF 경로를 조회합니다.
    3. **스트리밍 응답**: 파일을 메모리에 적재하지 않고 **FileResponse**를 통해 스트림 형태로 전송하여 대용량 파일도 안정적으로 처리합니다.
    
    ### 💡 프론트엔드 활용 팁
    * **바로 보기**: 브라우저의 새 탭이나 &lt;iframe&gt; 등을 통해 이 API 주소를 호출하면 PDF 뷰어가 자동으로 실행됩니다.
    * **다운로드**: HTML의 &lt;a&gt; 태그에 **download** 속성을 부여하여 호출하면 서버에서 설정한 파일명으로 즉시 다운로드됩니다.
    """
    return manual_service.get_manual_file_response(db, manual_id)