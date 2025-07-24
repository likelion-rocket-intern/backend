from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form, Depends
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
from app.utils import storage
from app.schemas.resume import Keyword

#JobDescription
from app.worker.job_analysis import send_job_analysis_task 
from app.schemas.job_description import JobDescriptionRequest, JobTaskStatusResponse, JobAnalysisTaskResponse



router = APIRouter(tags=["resume"])

@router.post("/analysis")
async def upload_resume(
    current_user: CurrentUser,
    session: SessionDep,
    file: UploadFile = File(...),
    additional: str = Form(None),
    manualResume: str = Form(None),
)-> AnalysisResponse:
    try:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        original_filename = file.filename
        upload_filename = str(uuid.uuid4())
        filename = f"{current_user.id}_{timestamp}_{file.filename}"
        
        # Generate a unique task ID
        task_id = str(uuid.uuid4())
        
        # Read file content
        content = await file.read()
        
        # Upload directly to NCP Object Storage
        from io import BytesIO
        file_obj = BytesIO(content)
        file_url = storage.upload_resume(file_obj, upload_filename)
        if not file_url:
            raise HTTPException(
                status_code=500,
                detail="Failed to upload file to storage"
            )
        
        # Send for analysis
        send_resume_analysis.send(
            file_url=file_url, 
            original_filename=original_filename,
            upload_filename=upload_filename,
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
        resume = resume_service.get_by_id(session, resume_id, current_user.id)
        keywords = [
            Keyword(
                keyword=kw.keyword,
                similar_to=kw.similar_to,
                similarity=kw.similarity,
                frequency=kw.frequency
            ) for kw in resume.resume_keywords
        ]
        return ResumeDetailResponse(
            id=resume.id,
            user_id=resume.user_id,
            version=resume.version,
            original_filename=resume.original_filename,
            upload_filename=resume.upload_filename,
            file_url=resume.file_url,
            keywords=keywords,
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
                    file_path=resume.file_url,
                    keywords=[
                        Keyword(
                            keyword=kw.keyword,
                            similar_to=kw.similar_to,
                            similarity=float(kw.similarity),
                            frequency=kw.frequency
                        ) for kw in resume.resume_keywords
                    ],
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
