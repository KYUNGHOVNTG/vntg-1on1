-- ============================================================================
-- Phase 1: 기본 로그인 마이그레이션
-- ============================================================================
-- employees 테이블에 인증 관련 컬럼 추가 및 신규 테이블 생성
-- ============================================================================

-- 1. employees 테이블에 인증 관련 컬럼 추가 (이미 없는 경우에만)
ALTER TABLE employees
ADD COLUMN IF NOT EXISTS failed_login_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS account_locked_until TIMESTAMP,
ADD COLUMN IF NOT EXISTS password_changed_at TIMESTAMP;

-- 2. refresh_tokens 테이블 생성
CREATE TABLE IF NOT EXISTS refresh_tokens (
    token_id SERIAL PRIMARY KEY,
    emp_id INTEGER NOT NULL,
    company_code INTEGER NOT NULL,
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    device_info VARCHAR(200),
    ip_address VARCHAR(45),
    user_agent TEXT,
    is_revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (emp_id) REFERENCES employees(emp_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_refresh_token_emp ON refresh_tokens(emp_id);
CREATE INDEX IF NOT EXISTS idx_refresh_token_hash ON refresh_tokens(token_hash);
CREATE INDEX IF NOT EXISTS idx_refresh_token_expires ON refresh_tokens(expires_at);
CREATE INDEX IF NOT EXISTS idx_refresh_token_revoked ON refresh_tokens(is_revoked);

COMMENT ON TABLE refresh_tokens IS 'Refresh Token 저장소';
COMMENT ON COLUMN refresh_tokens.token_hash IS 'Refresh Token의 SHA-256 해시값';

-- 3. login_history 테이블 생성
CREATE TABLE IF NOT EXISTS login_history (
    history_id SERIAL PRIMARY KEY,
    emp_id INTEGER,
    company_code INTEGER,
    email VARCHAR(100) NOT NULL,
    login_method VARCHAR(20) CHECK (login_method IN ('PASSWORD', 'GOOGLE', 'KAKAO', 'NAVER', 'MICROSOFT')),
    login_success BOOLEAN NOT NULL,
    failure_reason VARCHAR(200),
    ip_address VARCHAR(45),
    user_agent TEXT,
    device_info VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_login_history_emp ON login_history(emp_id);
CREATE INDEX IF NOT EXISTS idx_login_history_email ON login_history(company_code, email);
CREATE INDEX IF NOT EXISTS idx_login_history_created ON login_history(created_at);
CREATE INDEX IF NOT EXISTS idx_login_history_success ON login_history(login_success);

COMMENT ON TABLE login_history IS '로그인 이력 (감사 로그)';

-- 4. 완료 메시지
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Phase 1 Migration Completed!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Tables Created/Updated:';
    RAISE NOTICE '  - employees (컬럼 추가)';
    RAISE NOTICE '  - refresh_tokens (신규)';
    RAISE NOTICE '  - login_history (신규)';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Next Steps:';
    RAISE NOTICE '  1. 기존 사용자의 비밀번호를 BCRYPT로 해싱';
    RAISE NOTICE '  2. POST /api/v1/auth/login 엔드포인트 테스트';
    RAISE NOTICE '========================================';
END $$;
