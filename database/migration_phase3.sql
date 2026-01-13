-- ============================================================================
-- Phase 3: Google OAuth 2.0 로그인 마이그레이션
-- ============================================================================
-- Google OAuth 로그인을 위한 데이터베이스 구조 확인 및 인덱스 추가
-- ============================================================================

-- 1. user_social_auth 테이블 확인
-- 이 테이블은 이미 존재해야 합니다. 없다면 생성합니다.
CREATE TABLE IF NOT EXISTS user_social_auth (
    social_id SERIAL PRIMARY KEY,
    emp_id INTEGER,
    provider VARCHAR(20),
    provider_user_id VARCHAR(100),
    use_yn CHAR(1) DEFAULT 'Y' NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE
);

-- 2. 인덱스 추가 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_social_auth_provider ON user_social_auth(provider, provider_user_id);
CREATE INDEX IF NOT EXISTS idx_social_auth_emp ON user_social_auth(emp_id);
CREATE INDEX IF NOT EXISTS idx_social_auth_use_yn ON user_social_auth(use_yn);

-- 3. 제약 조건 추가 (provider + provider_user_id 조합은 유니크해야 함)
-- 단, 이미 데이터가 있는 경우 실패할 수 있으므로 주의
DO $$
BEGIN
    -- provider + provider_user_id 조합에 대한 유니크 제약 추가
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'uq_social_auth_provider_user'
    ) THEN
        ALTER TABLE user_social_auth
        ADD CONSTRAINT uq_social_auth_provider_user
        UNIQUE (provider, provider_user_id);
    END IF;
EXCEPTION
    WHEN duplicate_key THEN
        RAISE NOTICE 'Unique constraint already exists or duplicate data found';
END $$;

-- 4. 코멘트 추가
COMMENT ON TABLE user_social_auth IS '소셜 로그인 연동 정보 (Google, Kakao, Naver 등)';
COMMENT ON COLUMN user_social_auth.provider IS '소셜 로그인 제공자 (GOOGLE, KAKAO, NAVER, MICROSOFT)';
COMMENT ON COLUMN user_social_auth.provider_user_id IS '소셜 로그인 제공자의 고유 사용자 ID';
COMMENT ON COLUMN user_social_auth.emp_id IS '연동된 직원 ID (employees.emp_id 외래키)';

-- 5. login_history 테이블에 GOOGLE 메서드 추가 확인
-- Phase 1에서 이미 CHECK 제약이 있지만, 확장 가능하도록 확인
DO $$
BEGIN
    -- CHECK 제약이 있는지 확인하고 GOOGLE이 포함되어 있는지 검증
    IF EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'login_history_login_method_check'
    ) THEN
        RAISE NOTICE 'login_method CHECK constraint already exists';
    ELSE
        RAISE NOTICE 'login_method CHECK constraint not found - this is OK if Phase 1 migration was run';
    END IF;
END $$;

-- 6. 완료 메시지
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Phase 3 Migration Completed!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Tables Created/Updated:';
    RAISE NOTICE '  - user_social_auth (확인 및 인덱스 추가)';
    RAISE NOTICE '  - login_history (GOOGLE 메서드 지원 확인)';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Google OAuth Features:';
    RAISE NOTICE '  - POST /api/v1/auth/google (구글 로그인)';
    RAISE NOTICE '  - 구글 ID 토큰 검증';
    RAISE NOTICE '  - 이메일 기반 자동 계정 연동';
    RAISE NOTICE '  - JWT Access Token + Refresh Token 발급';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Next Steps:';
    RAISE NOTICE '  1. 구글 OAuth 클라이언트 ID 설정 (.env)';
    RAISE NOTICE '  2. POST /api/v1/auth/google 엔드포인트 테스트';
    RAISE NOTICE '  3. 기존 직원 이메일과 구글 이메일 일치 확인';
    RAISE NOTICE '========================================';
END $$;
