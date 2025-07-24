from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import Response

import uuid

from app.api.deps import SessionDep, CurrentUser
from app.schemas.total import TotalRequest, TotalResponse
from app.schemas.job_description import JobDescriptionRequest, JobAnalysisTaskResponse
from app.schemas.job_description import JobTaskStatusResponse
from app.worker import job_analysis


router = APIRouter(tags=["jd"])

#JobDescription
@router.post("/{resume_id}/analyze", response_model=JobAnalysisTaskResponse)
async def request_job_analysis(
    resume_id: int,
    job_description_request: JobDescriptionRequest,
    current_user: CurrentUser,
) -> JobAnalysisTaskResponse:
    """
    주어진 이력서(resume_id)와 채용 공고를 RAG 기반으로 분석합니다.
    """
    task_id = str(uuid.uuid4())

    try:
        job_analysis.send_job_analysis_task.send(
            task_id=task_id,
            user_id=current_user.id,
            resume_id=resume_id,
            job_request=job_description_request.model_dump()
        )

        return JobAnalysisTaskResponse(task_id=task_id,  message="Job description analysis has been successfully requested. Please check the status using the task_id.")

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze resume with job description: {str(e)}"
        )
    
@router.get("/task/{task_id}", response_model=JobTaskStatusResponse)
async def check_job_task_status(
    task_id: str,
    current_user: CurrentUser,
    session: SessionDep
):
    """
    특정 이력서에 속한 작업의 상태와 결과를 조회합니다.
    """

    # Redis에서 작업 상태를 가져옴
    task_data = job_analysis.get_task_status(task_id)
    if not task_data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_data['task_id'] = task_id

    return JobTaskStatusResponse(**task_data)