from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import Response
from app.api.deps import SessionDep, CurrentUser
from app.schemas.total import TotalRequest, TotalResponse

router = APIRouter(tags=["total"])
@router.post("/")
async def analyze_totl(
  current_user: CurrentUser,
  session: SessionDep,
  request: TotalRequest,
)-> TotalResponse:
  return TotalResponse(
    Strengths="",
    Weaknesses=""
  )