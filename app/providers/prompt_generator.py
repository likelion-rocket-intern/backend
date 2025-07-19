from typing import List

from app.interface.prompt_generator import PromptGeneratorInterface
from langchain_core.documents import Document


class AnalysisPromptGenerator(PromptGeneratorInterface):
    """
    이력서 분석을 위한 프롬프트 생성기 구현체.
    """

    def create_job_fit_prompt(
        self, job_description: str, resume_chunks: List[Document]
    ) -> str:
        context = "\n---\n".join([chunk.page_content for chunk in resume_chunks])

        prompt_template = f"""
You are a top-tier IT headhunter and career consultant in South Korea. Your primary language is Korean. Your task is to conduct a detailed analysis comparing a candidate's resume against a job description.

**1. 채용공고 (Job Description):**
{job_description}



**2. 이력서 핵심 내용 (Relevant Resume Excerpts):**
{context}


**3. 좋은 분석의 예시 (Example of a GOOD Analysis):**
This is the high-quality, structured JSON output I expect. All text values must be in Korean.
```json
{{
  "job_summary": {{
    "name": "AI 백엔드 개발자",
    "skill": [
    "생성형 AI 플랫폼 활용 Application 설계 및 개발",
    "정형 또는 비정형 데이터 수집 및 처리 파이프라인 설계 및 구현",
    "Python, Golang을 이용한 서비스 구축 및 유지보수",
    "MLOps 구축 및 운영을 통한 모델 서빙 및 배포 자동화"
    ]
  }},
  "job_keywords": ["RAG", "LLM", "FastAPI", "AWS", "Python"],
  "resume_keywords": ["FastAPI", "Docker", "RAG", "LangChain", "LLM"],
  "resume_strengths": [
    {{
      "keyword": "RAG 파이프라인 개발",
      "evidence": "이력서의 'RAG 기반 AI 이력서 분석 시스템 개발' 프로젝트 경험이 채용공고의 우대사항 "RAG 기반 AI 시스템 설계 및 구현 경험을 보유하신 분"과 부합해요!"
    }},
    {{
      "keyword": "FastAPI 기반 서버 개발",
      "evidence": "이력서에 명시된 'FastAPI를 이용한 고성능 API 서버 개발 및 MSA 환경 배포' 이 해당 직무에 관한 "백엔드 아키텍처 설계 및 운영 (On-Premise 및 Cloud 환경)"에 부합해요!"
    }}
  ],
  "resume_weaknesses": [
    {{
      "keyword": "특정 클라우드 서비스 경험",
      "evidence": "채용공고에 AWS ElasticBeanstalk이 언급되어 있으나, 이력서에는 포괄적인 AWS 경험만 기재되어 있어해당 서비스에 대한 구체적인 경험을 개선하면 좋을 것 같아요!."
    }}
  ],
    "overall_assessment": {{
    "score": 85,
    "summary": "AI 백엔드 개발자 직무에 매우 적합해보여요! 특히 LLM과 RAG 파이프라인 구축한 경험이 핵심 자격요건과 일치하고, FastAPI 및 Docker 활용 능력 또한 실무에 즉시 기여할 수 있는 수준이라고 보여집니다."
  }}
}}
```

**4. 평가 기준 (Scoring Rubric):**
Use the following rubric to determine the job fit score. Be strict and objective.
- **90-100 (매우 높음):** 모든 핵심 자격요건을 충족하며, 구체적이고 증명 가능한 경험을 다수 보유함.
- **70-89 (높음):** 대부분의 핵심 자격요건을 충족하지만, 일부 경험이 부족하거나 간접적임.
- **50-69 (보통):** 일부 핵심 자격요건을 충족하지만, 여러 부분에서 불일치가 발견됨.
- **Below 50 (낮음):** 핵심 자격요건과 경험의 관련성이 매우 낮음.


**5. 당신의 임무 (Your Task):**
Based on the provided information, perform the following steps and generate a single, valid JSON object as your final output. **All responses MUST be in Korean.**

a. **Summarize Job & Extract Keywords:** First, read the job description. Extract the job title (`name`) and a list of key duties (`skill`). Then, extract a list of important technical keywords (`job_keywords`).
b. **Extract Resume Keywords:** Read the resume excerpts and extract a list of key technical keywords (`resume_keywords`).
c. **Analyze Strengths & Weaknesses:** Objectively compare the job description and resume.
   - Identify **up to 3** key strengths. **If no clear strengths are found, return an empty array `[]`.**
   - Identify **up to 2** key weaknesses. **If no clear weaknesses are found, return an empty array `[]`.**
   - For each, specify the `keyword` and provide `evidence` or reasoning.
d. **Final Evaluation:** Provide an overall assessment, including a job fit `score` based on the rubric and a concise `summary`.
e. **Format as JSON:** Combine all the analysis into a single JSON object that strictly follows the structure provided in the example above. Do not add any text or explanations outside of the JSON structure.

"""
        return prompt_template