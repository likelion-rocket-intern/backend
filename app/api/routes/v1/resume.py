from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from fastapi.responses import Response
from app.api.deps import SessionDep, CurrentUser
from app.schemas.auth import KakaoLoginResponse, UserResponse
from app.service.auth import auth_service
from app.service.resume_service import resume_service
from app.worker.resume_analysis import send_resume_analysis, get_task_status
from pathlib import Path
from datetime import datetime
import uuid
from app.schemas.resume import AnalysisResponse, TaskStatusResponse, ResumeDetailResponse, ResumeListResponse
from app.schemas.status import TaskStatus


router = APIRouter(tags=["resume"])

UPLOAD_DIR = Path("uploads/resumes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/analysis")
async def upload_resume(
    current_user: CurrentUser,
    session: SessionDep,
    file: UploadFile = File(...),
)-> AnalysisResponse:
    try:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{current_user.id}_{timestamp}_{file.filename}"
        file_path = UPLOAD_DIR / filename

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Generate a unique task ID
        task_id = str(uuid.uuid4())

        # parse_resume = resume_service.process_resume_with_embeddings(file_path, file.filename)
        # result = resume_service.process_and_save_resume(
        #     db=session,
        #     file_path=str(file_path),
        #     filename=file.filename,
        #     resume_id=1  # 테스트용
        # )
        
        send_resume_analysis.send(
            file_path=str(file_path),
            filename=file.filename,
            user_id=current_user.id,
            task_id=task_id,
        )
        
        return AnalysisResponse(
            message="Resume analysis started",
            filename=file.filename,
            status=TaskStatus.PENDING,
            task_id=task_id
        )
    
    except Exception as e:
        # 에러 발생 시 저장된 파일 삭제
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process resume: {str(e)}"
        )


@router.get("/task/{task_id}")
async def check_task_status(
    task_id: str,
    current_user: CurrentUser,
    session: SessionDep,
)-> TaskStatusResponse:
    """
    주어진 task_id로 이력서 분석 작업의 상태를 확인합니다.
    """
    try:
        task_data = get_task_status(task_id)
        return TaskStatusResponse(
            task_id=task_id,
            status=task_data["status"],
            result=task_data["result"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check task status: {str(e)}"
        )

@router.get("/{resume_id}", response_model=ResumeDetailResponse)
async def get_resume(
    resume_id: int,
    current_user: CurrentUser,
    session: SessionDep,
) -> ResumeDetailResponse:
    try:
        resume = resume_service.get_by_id(session, resume_id)
        return ResumeDetailResponse(
            id=resume.id,
            user_id=resume.user_id,
            version=resume.version,
            file_path=resume.file_path,
            analysis_result=resume.analysis_result,
            created_at=resume.created_at
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get resume: {str(e)}")

@router.get("/", response_model=ResumeListResponse)
async def get_resume_list(
    current_user: CurrentUser,
    session: SessionDep,
) -> ResumeListResponse:
    try:
        resume_list = resume_service.get_by_user_id(session, current_user.id)
        return ResumeListResponse(
            resumes=[
                ResumeDetailResponse(
                    id=resume.id,
                    user_id=resume.user_id,
                    version=resume.version,
                    file_path=resume.file_path,
                    analysis_result=resume.analysis_result,
                    created_at=resume.created_at
                )
                for resume in resume_list
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get resume list: {str(e)}")

@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: int,
    current_user: CurrentUser,
    session: SessionDep,
):
    try:
        resume_service.delete(session, resume_id)
        return {"message": "Resume deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete resume: {str(e)}")