"""split_social_id_field

Revision ID: f6ac25e53064
Revises: 93b6bf9aba2c
Create Date: 2025-07-04 10:23:37.107015

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column, text
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'f6ac25e53064'
down_revision = '93b6bf9aba2c'
branch_labels = None
depends_on = None


def upgrade():
    # 1. 새로운 컬럼 추가
    op.add_column('users', sa.Column('social_type', sa.String(), nullable=True))
    op.add_column('users', sa.Column('new_social_id', sa.String(), nullable=True))
    
    # 2. 기존 데이터 변환 - PostgreSQL의 split_part 함수 사용
    op.execute(text("""
        UPDATE users 
        SET social_type = split_part(social_id, '_', 1),
            new_social_id = split_part(social_id, '_', 2)
    """))
    
    # 3. 기존 social_id 컬럼 삭제하고 new_social_id를 social_id로 이름 변경
    op.drop_column('users', 'social_id')
    op.alter_column('users', 'new_social_id', new_column_name='social_id')
    
    # 4. NOT NULL 제약 조건 추가
    op.alter_column('users', 'social_type', nullable=False)
    op.alter_column('users', 'social_id', nullable=False)
    
    # 5. 인덱스 추가
    op.create_index(op.f('ix_users_social_type'), 'users', ['social_type'])
    op.create_index(op.f('ix_users_social_id'), 'users', ['social_id'])


def downgrade():
    # 인덱스 삭제
    op.drop_index(op.f('ix_users_social_id'))
    op.drop_index(op.f('ix_users_social_type'))
    
    # 임시 컬럼 추가
    op.add_column('users', sa.Column('old_social_id', sa.String(), nullable=True))
    
    # 데이터 다시 합치기
    op.execute(text("""
        UPDATE users 
        SET old_social_id = social_type || '_' || social_id
    """))
    
    # 새 컬럼들 삭제하고 old_social_id를 social_id로 이름 변경
    op.drop_column('users', 'social_type')
    op.drop_column('users', 'social_id')
    op.alter_column('users', 'old_social_id', new_column_name='social_id')
    
    # unique 인덱스 다시 생성
    op.create_index('ix_users_social_id', 'users', ['social_id'], unique=True)
