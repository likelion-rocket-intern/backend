# backend
dev
uvicorn app.main:app --reload

cd ../backend && curl http://localhost:8000/api/v1/openapi.json > openapi.json

cd ../frontend && npx openapi-typescript ../backend/openapi.json -o ./src/app/lib/schema.ts

모델(테이블 구조) 변경할 때마다 새로운 마이그레이션 파일 생성:
Apply to page.tsx
Run
"
예를 들어:
alembic revision --autogenerate -m "create users table"
alembic revision --autogenerate -m "add email column"
alembic revision --autogenerate -m "create posts table"
그 다음부터는 prestart.sh가 실행될 때 alembic upgrade head 명령어로 자동으로 마이그레이션이 적용됩니다.
정리하면:
마이그레이션 파일 생성 → 수동 (모델 변경할 때마다)
마이그레이션 적용 → 자동 (서버 시작할 때마다)
현재는 users 테이블을 위한 마이그레이션 파일을 먼저 생성해야 합니다. 생성하시겠습니까?

alembic revision --autogenerate -m "create users table"

alembic upgrade head

# 1. 가상환경 생성
python -m venv .venv

# 2. 가상환경 활성화 (MacOS/Linux의 경우)
source .venv/bin/activate

# 3. 빌드 그레이들
uv pip install -e . 

# 4-1. DB 버전업
alembic revision --autogenerate -m "create users table"

# 4-2. DB 마이그레이션 
alembic upgrade head

# 5. 서버실행
uvicorn app.main:app --reload

# 6. dramatiq 워커실행
./scripts/worker-start.sh
or
dramatiq app.worker.resume_analysis app.worker.__init__ --processes 2 --threads 4

# 6. 도커 빌드 & 실행
docker build -t ll-rocket-backend . && docker run ll-rocket-backend

