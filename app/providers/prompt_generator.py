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
You are a highly experienced senior tech recruiter and career consultant. Your task is to analyze the provided resume excerpts and determine the candidate's suitability for a specific job description.

**1. Job Description:**
```
{job_description}
```

**2. Relevant Resume Excerpts:**
```
{context}
```


**3. Example of a GOOD Analysis (Few-shot Example):**
Here is an example of the kind of high-quality, structured analysis I expect.
```json
{{
  "overall_assessment": {{
    "score": 85,
    "summary": "해당 이력서는 시니어 백엔드 엔지니어 직무에 매우 적합합니다. 마이크로서비스 아키텍처(MSA) 및 클라우드 플랫폼(AWS)과 같은 핵심 요구 사항에 대한 풍부한 경험을 보유하고 있으며, 구체적인 프로젝트 사례를 바탕으로 검증된 역량을 갖추고 있습니다."
  }},
  "strengths": [
    {{"strength": "깊은 MSA 경험", "evidence": "단일 애플리케이션을 20개가 넘는 마이크로서비스로 전환하는 작업을 주도했으며, 해당 업무의 핵심 요구 사항과 직접적으로 일치했습니다."}},
    {{"strength": "AWS 활용", "evidence": "'프로젝트 A' 설명에 언급된 대로 EC2, S3, RDS, Lambda를 포함한 광범위한 AWS 서비스를 활용했습니다."}}
  ],
  "areas_for_improvement": [
    {{"area": "적은 NoSQL 활용 경험", "reasoning": "현재 이력서에는 주로 PostgreSQL과 같은 RDBMS 관련 경험이 나열되어 있습니다. 직무 내용에 DynamoDB 관련 내용이 언급되어 있으므로, NoSQL 관련 경험이 있다면 강조하는 것이 좋습니다."}}
  ]
}}
```

**4. Your Task:**
Based on the resume excerpts, provide a comprehensive analysis of the candidate's job fit. Follow these instructions precisely:

a. **Overall Assessment:** Start with a summary of your overall assessment, including a job fit score from 1 to 100.
b. **Key Strengths:** Identify and list up to 3 key strengths of the candidate that are highly relevant to the job description. For each strength, provide a specific example or evidence from the resume.
c. **Areas for Improvement:** Identify and list up to 2 areas where the candidate's experience or skills seem less aligned with the job description. Frame this as constructive feedback.

**5. Output Format:**
Provide your analysis in a structured JSON format, just like the example provided in section 3. Do not add any text or explanations outside of the JSON structure.
Ensure your output is a single, valid JSON object.

{{
  "overall_assessment": {{
    "score": <integer, 1-100>,
    "summary": "<string>"
  }},
  "strengths": [
    {{"strength": "<string>", "evidence": "<string>"}},
    ...
  ],
  "areas_for_improvement": [
    {{"area": "<string>", "reasoning": "<string>"}},
    ...
  ]
}}
"""
        return prompt_template