#!/usr/bin/env bash

set -e
set -x

# 0. postgres 설치
brew install postgresql@14
# 1. 임시 DB 생성, 끝나면 무조건 DB삭제
createdb test_k6
trap "dropdb test_k6" EXIT
# 1.1 pgvector 설치(벡터때문에)
brew install pgvector
psql -U postgres -d test_k6 -c "CREATE EXTENSION IF NOT EXISTS vector;"



# 2. 마이그레이션 (DB URL 환경변수 지정)
export DATABASE_URL="postgresql://postgres:password@localhost:5432/test_k6"
export PYTHONPATH="$(pwd):$PYTHONPATH"
alembic upgrade head

# 3. 더미 데이터 삽입
python app/backend_pre_test.py --db-url "$DATABASE_URL" --count 100

# 4. 대충 테스트 코드?

# 5. 테스트 끝난 뒤 임시 DB 삭제