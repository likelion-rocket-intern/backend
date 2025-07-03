from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from fastapi.responses import Response
from app.api.deps import SessionDep, CurrentUser
from app.schemas.auth import KakaoLoginResponse, UserResponse
from app.service.auth import auth_service
from app.worker.resume_analysis import send_resume_analysis

router = APIRouter(tags=["resume"])


@router.post("/upload")
async def upload_resume(
    current_user: CurrentUser,
    session: SessionDep,
    file: UploadFile = File(...),
):
    """
    이력서 파일을 업로드하고 분석 작업을 큐에 추가합니다.
    """
    try:
        content = await file.read()
        
        # 분석 작업을 워커에게 전달
        send_resume_analysis.send(
            file_content=content,  # 바이너리 데이터 그대로 전달
            filename=file.filename,
            user_id=str(current_user.id),
        )
        
        return {
            "message": "Resume analysis started",
            "filename": file.filename,
            "status": "processing"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process resume: {str(e)}"
        )

