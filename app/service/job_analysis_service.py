import json
import logging
from typing import Dict, Any

from fastapi import HTTPException, status
from sqlmodel import Session

from app.models.user import User


from app.interface.llm_provider import LLMProviderInterface
from app.interface.prompt_generator import PromptGeneratorInterface
from app.interface.resume_vector_repository import ResumeVectorRepositoryInterface

from app.service.resume_service import resume_service



logger = logging.getLogger(__name__)


class JobAnalysisService:
    """
    RAG 파이프라인을 사용하여 이력서를 분석하는 서비스.
    의존성 주입을 통해 각 컴포넌트(DB, Vector Repo, Prompt Gen, LLM)를 받습니다.
    """

    def __init__(
        self,
        vector_repo: ResumeVectorRepositoryInterface,
        prompt_generator: PromptGeneratorInterface,
        llm_provider: LLMProviderInterface,
    ):
        self.vector_repo = vector_repo
        self.prompt_generator = prompt_generator
        self.llm_provider = llm_provider

    def analyze_job_fit(
        self,
        *,
        db: Session,
        resume_id: int,
        user: User,
        job_description: str,
    ) -> Dict[str, Any]:
        """
        주어진 이력서와 채용 공고의 직무 적합도를 RAG를 통해 분석합니다. 
        """
        logger.info(f"이력서 ID {resume_id}에 대한 직무 적합도 분석 시작...")
        
        # 이력서 소유권 확인 및 채용 공고 저장
        resume = resume_service.get_by_id(db=db, resume_id=resume_id, user_id=user.id)
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found or you do not have permission to access it."
            )

        # 1. 검색 (Retrieval): JD와 가장 관련성 높은 이력서 청크 검색
        relevant_chunks = self.vector_repo.search_similar_chunks(
            resume_id=resume_id, query=job_description, k=5
        )

		# 1-1. 유효성 검사: 검색된 청크가 없는 경우 예외 처리
        if not relevant_chunks:
            logger.warning(f"이력서 ID {resume_id}에 대한 임베딩된 청크를 찾을 수 없습니다.")
            raise HTTPException(
                status_code=404, detail=f"Resume(id={resume_id}) has no content to analyze."
            )
        
        # 2. 프롬프트 생성 (Augmented)
        prompt = self.prompt_generator.create_job_fit_prompt(
            job_description=job_description, resume_chunks=relevant_chunks
        )

        # 3. LLM 호출 (Generation)
        llm_response = self.llm_provider.invoke(prompt)

        # 4. 결과 정제 및 반환 (JSON 파싱)
        try:
            analysis_result = json.loads(llm_response)
            logger.info(f"이력서 ID {resume_id} 분석 완료.")
            return analysis_result
        except json.JSONDecodeError:
            logger.error("LLM 응답을 JSON으로 파싱하는 데 실패했습니다.", extra={"raw_response": llm_response})
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to parse LLM response into JSON."
            )