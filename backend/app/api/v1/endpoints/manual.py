from fastapi import APIRouter, Depends, Query, UploadFile, File, Form
from app.service.saved_manual_service import manual_service
from app.models.user import User
from sqlalchemy.orm import Session
from app.api import deps
from typing import List
from app.schemas.manual import SearchManual, ManualCreate, ManualResponse
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

@router.post(
    "/upload", 
    status_code=201,
    response_model=ManualResponse,
    summary="신규 매뉴얼 업로드"
)
async def upload_manual(
    title: str = Form(..., description="매뉴얼의 제목", examples=["2026 스마트팩토리 컨베이어 점검 매뉴얼"]),
    category: str = Form(..., description="설비 분류 또는 카테고리", examples=["점검"]),
    version: str = Form(..., description="매뉴얼 버전", examples=["v1.0.2"]),
    error_codes: List[str] = Form(..., description="매뉴역과 연결될 에러 코드 리스트", examples=[["E0001", "E0023"]]),
    file: UploadFile = File(..., description="업로드할 PDF 파일"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_admin_user)
):
    """
    관리자 권한으로 새로운 PDF 매뉴얼과 관련 에러 코드들을 서버에 등록합니다.

    - **파일 저장**: 서버 내 /static/data 경로에 고유한 파일명으로 저장됩니다.
    - **에러 코드**: 여러 개의 에러 코드를 리스트 형태로 입력하면 해당 매뉴얼과 자동으로 매핑됩니다.
    - **권한**: 관리자(Admin) 계정만 호출 가능합니다.

    매뉴얼 업로드 프로세스:
    1. 파일 시스템에 PDF 저장
    2. 매뉴얼 메타데이터 저장
    3. 에러 코드 관계 매핑 저장
    """
    # 매뉴얼 기본 정보 DTO 생성
    manual_in = ManualCreate(title=title, category=category, version=version)
    
    # 서비스에 매뉴얼 DTO와 에러 코드 리스트를 각각 전달
    return await manual_service.upload_manual_process(
        db, 
        manual_in=manual_in, 
        error_codes=error_codes, 
        file=file, 
        user_id=current_user.user_id
    )