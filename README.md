<div align="center">
	<img width="25%" alt="tech_fit_logo" src="https://github.com/user-attachments/assets/e527c1c5-80f9-4956-94c8-bf60ba5cedc9">


# TechFit
> AI 이력서 평가 및 적성 검사 시스템
 
수강생의 이력서를 AI가 분석하여 역량 기반 정량 평가 및 인사담당자의 성향에 맞는 인재 추천 서비스


[<img src="https://img.shields.io/badge/-readme.md-important?style=flat&logoColor=white" />](https://github.com/ocy-likelion/AI_resume_1_backend/blob/main/README.md) [![Repository](https://img.shields.io/badge/Repository-%23121011.svg?style=flat&logo=github&logoColor=white)](https://github.com/ocy-likelion/AI_resume_1_backend) [![tech_fit deploy](https://github.com/likelion-rocket-intern/backend/actions/workflows/deploy.yml/badge.svg)](https://github.com/likelion-rocket-intern/backend/actions/workflows/deploy.yml)
 

<img width="100%" alt="image" src="https://github.com/user-attachments/assets/a05b918c-e1e2-4394-bd59-fb24b9bc277f" />


</div>


## 설치 및 실행 방법

다음의 환경에서 준비해주세요
- Python 3.10 이상
- uv
- Docker 및 Docker Compose
- PostgreSQL 데이터베이스 (pgvector 확장 활성화 필요)



### 프로젝트 설정

```
git clone https://github.com/likelion-rocket-intern/backend
cd backend
```

### 의존 서비스 실행
```
# Docker 네트워크 생성
docker network create resume_matching
```
```
# Redis 컨테이너 실행
docker run -d --name ll-redis \
  --network=resume_matching \
  -p 6379:6379 \
  --restart unless-stopped \
  redis
```
```
# PostgreSQL (+ PGVvector) 컨테이너 실행
docker run -d   --name ll-pgvector\
  --network=resume_matching \
  -e POSTGRES_USER=myuser \
  -e POSTGRES_PASSWORD=1234 \
  -e POSTGRES_DB=ll_rocket \
  -p 5432:5432 \
  --restart unless-stopped \
  pgvector/pgvector:pg17
```
```
# PGVector 확장 활성화
sleep 5
docker exec -it ll-pgvector psql -U myuser -d ll_rocket -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Python 가상환경 및 의존성 설치
```
# 가상환경 활성화
uv venv
source .venv/bin/activate
```
```
# 의존성 설치
uv sync

# DB 마이그레이션
alembic upgrade head
```

### 사전 세팅 실행
다음 스크립트를 실행하여 DB 테이블 및 초기 데이터를 주입합니다.
```
./scripts/prestart.sh
```

### 어플리케이션 실행
```
# 터미널 1: FastAPI 서버 실행


# FastAPI 서버 실행
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

```
# 터미널 2: Dramatiq 워커 실행 (백그라운드 작업 처리)

# Dramatiq 워커 실행
./scripts/worker-start.sh

```

## 아키텍처

```mermaid
flowchart TD
    subgraph "클라이언트"
        C1[브라우저/모바일]:::client
    end

    subgraph "애플리케이션 계층"
        direction LR
        subgraph "API 게이트웨이"
            A1[FastAPI Service]:::api_gateway
            A2[내부 라우터]:::api_gateway
            A3[인증]:::api_gateway
        end

        subgraph "비즈니스 로직"
            direction TB
            S1[Service 계층]:::service_layer
        end

        subgraph "데이터 접근"
            D1[CRUD 계층]:::data_access
            D2[Repository 계층]:::data_access
        end

        subgraph "모델 & 스키마"
            M1[Pydantic/SQLModel 모델]:::models_schemas
            M2[API 스키마]:::models_schemas
        end

        subgraph "코어 클라이언트"
            CC1[Postgres Client & 세션]:::core_clients
            CC2[Redis Client & 큐 설정]:::core_clients
            CC3[core security/config]:::core_clients
        end

        subgraph "인터페이스 & Provider"
            I1[LLM Provider Interface]:::interfaces
            I2[Embedding Provider Interface]:::interfaces
            I3[Prompt Generator Interface]:::interfaces
            I4[이력서 Vector Repository Interface]:::interfaces

            P1[LLM Provider]:::providers
            P2[Embedding Provider]:::providers
            P3[Prompt Generator]:::providers
        end

        subgraph "백그라운드 워커"
            W1[Dramatiq 워커]:::worker
        end

        subgraph "유틸리티 모듈"
            U1[크롤러]:::utilities
        end
    end

    subgraph "데이터 저장소 & 캐시"
        DB1[(PostgreSQL + pgvector)]:::database
        C2[(Redis)]:::cache_queue
    end

    subgraph "외부 서비스"
        E1[소셜 로그인 <br/> Provider]:::external_service
        E2[LLM 엔드포인트]:::external_service
    end

    %% 관계 & 상호작용
    C1 --"HTTP 요청"--> A1
    A1 --"요청 라우팅"--> A2
    A2 --"인증 처리"--> A3
    A3 --"인증 수행"--> E1

    A2 --"위임"--> S1
    S1 --"동기 작업"--> D1
    S1 --"동기 작업"--> D2
    S1 --"사용"--> M1
    S1 --"사용"--> M2
    S1 --"사용"--> I1
    S1 --"사용"--> I2
    S1 --"사용"--> I3
    S1 --"사용"--> I4
    S1 --"사용"--> U1
    S1 --"태스크 대기열에 추가"--> C2

    D1 --"CRUD 작업"--> DB1
    D2 --"데이터 접근"--> DB1
    D2 --"사용"--> I4
    CC1 --"연결"--> DB1
    CC2 --"연결"--> C2

    C2 --"트리거"--> W1
    W1 --"호출"--> P1
    W1 --"호출"--> P2
    W1 --"호출"--> P3
    W1 --"결과 저장"--> DB1

    I1 --"구현"--> P1
    I2 --"구현"--> P2
    I3 --"구현"--> P3

    P1 --"호출"--> E2
    P2 --"호출"--> E2
    P3 --"호출"--> E2

    W1 --"상태 업데이트"--> A1
    C1 --"상태 폴링"--> A1

    %% 스타일링
    classDef client fill:#ADD8E6,stroke:#318CE7,stroke-width:2px;
    classDef api_gateway fill:#90EE90,stroke:#228B22,stroke-width:2px;
    classDef service_layer fill:#FFD700,stroke:#DAA520,stroke-width:2px;
    classDef data_access fill:#DA70D6,stroke:#9370DB,stroke-width:2px;
    classDef models_schemas fill:#B0E0E6,stroke:#6495ED,stroke-width:2px;
    classDef core_clients fill:#DDA0DD,stroke:#8B008B,stroke-width:2px;
    classDef interfaces fill:#FFFF00,stroke:#BDB76B,stroke-width:2px;
    classDef providers fill:#FFA07A,stroke:#FF8C00,stroke-width:2px;
    classDef worker fill:#FF6347,stroke:#CD5C5C,stroke-width:2px;
    classDef utilities fill:#AFEEEE,stroke:#40E0D0,stroke-width:2px;
    classDef database fill:#87CEEB,stroke:#4682B4,stroke-width:2px;
    classDef cache_queue fill:#FFDAB9,stroke:#F4A460,stroke-width:2px;
    classDef external_service fill:#FFC0CB,stroke:#FF69B4,stroke-width:2px;
    classDef observability fill:#D3D3D3,stroke:#A9A9A9,stroke-width:2px;
    classDef infra_code fill:#C0C0C0,stroke:#808080,stroke-width:2px;


```
## API

<div align="center">
	
자세한 사항은 FastAPI Docs를 참고해주세요.

( FastAPI 서버 구동 후 [`http://localhost:8000/docs/`](http://localhost:8000/docs/) )

| **기능** | **메서드** | **엔드포인트** | **설명** |
| --- | --- | --- | --- |
| **시스템** | GET | **`/metrics`** | 시스템 메트릭 조회 |
|  | GET | **`/health`** | 서버 상태 확인 |
| **인증** | GET | **`/api/v1/auth/kakao/login`** | 카카오 로그인 페이지로 리디렉션 |
|  | GET | **`/api/v1/auth/kakao/callback`** | 카카오 인증 콜백 처리 |
|  | GET | **`/api/v1/auth/logout`** | 로그아웃 |
|  | GET | **`/api/v1/auth/me`** | 현재 로그인된 사용자 정보 조회 |
| **이력서** | POST | **`/api/v1/resume/analysis`** | 이력서 업로드 및 분석 요청 |
|  | GET | **`/api/v1/resume/task/{task_id}`** | 이력서 분석 작업 상태 확인 |
|  | GET | **`/api/v1/resume/{resume_id}`** | 특정 이력서 정보 조회 |
|  | DELETE | **`/api/v1/resume/{resume_id}`** | 특정 이력서 삭제 |
|  | GET | **`/api/v1/resume/`** | 전체 이력서 목록 조회 |
| **진로탐색** | GET | **`/api/v1/jinro/user`** | 사용자의 진로 테스트 결과 조회 |
|  | GET | **`/api/v1/jinro/user/latest`** | 사용자의 최신 진로 테스트 결과 |
|  | GET | **`/api/v1/jinro/test-questions-v1`** | 진로 테스트 질문지 조회 (v1) |
|  | POST | **`/api/v1/jinro/test-report-v1`** | 진로 테스트 결과 제출 (v1) |
|  | GET | **`/api/v1/jinro/{id}`** | 특정 진로 테스트 결과 ID로 조회 |
| **JD 분석** | POST | **`/api/v1/jd/analyze`** | 이력서 기반 JD(채용공고) 분석 요청 |
|  | GET | **`/api/v1/jd/task/{task_id}`** | JD 분석 작업 상태 확인 |
| **크롤러** | GET | **`/api/v1/crawler/`** | 크롤러 정보 조회 (내부용 추정) |

</div>

## 기술 스택

<div align="center">

| 영역         | 기술 스택                                                                 |
|--------------|--------------------------------------------------------------------------|
| **백엔드 (Backend)** | Python (3.10+), FastAPI, Pydantic, SQLModel |
| **AI / LLM & 자연어 처리 (NLP)** | LangChain, Sentence-Transformers, <br/> Gensim (Word2Vec), HuggingFace,<br/> PyTorch, Numpy, Pandas |
| **데이터베이스** | PostgreSQL, pgvector, Alembic |
| **인프라 및 배포** | Docker , Docker Compose |
| **비동기 처리** | Redis, Dramatiq, ThreadPool |
| **개발 환경 및 도구** | Git, Github, uv, MyPy, Pytest, Ruff|

</div>

