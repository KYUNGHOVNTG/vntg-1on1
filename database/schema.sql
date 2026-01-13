-- ============================================================================
-- PMS Authentication & Authorization Schema
-- ============================================================================
-- 멀티 테넌시(COMPANY_CODE 기반) + RBAC 지원 인증 시스템
-- 모든 키워드는 대문자, ID는 SERIAL, 상태값은 USE_YN('Y', 'N') 규칙 준수
-- ============================================================================

-- ============================================================================
-- 1. 회사(테넌트) 관리
-- ============================================================================

CREATE TABLE IF NOT EXISTS COMPANY (
    COMPANY_CODE VARCHAR(20) PRIMARY KEY,
    COMPANY_NAME VARCHAR(200) NOT NULL,
    BUSINESS_NO VARCHAR(20),
    REPRESENTATIVE VARCHAR(100),
    ADDRESS TEXT,
    PHONE VARCHAR(20),
    EMAIL VARCHAR(100),
    ESTABLISHED_DATE DATE,
    USE_YN CHAR(1) DEFAULT 'Y' CHECK (USE_YN IN ('Y', 'N')),
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CREATED_BY VARCHAR(50),
    UPDATED_BY VARCHAR(50)
);

CREATE INDEX idx_company_use_yn ON COMPANY(USE_YN);
CREATE INDEX idx_company_created_at ON COMPANY(CREATED_AT);

COMMENT ON TABLE COMPANY IS '회사(테넌트) 정보';
COMMENT ON COLUMN COMPANY.COMPANY_CODE IS '회사 코드 (멀티 테넌시 키)';
COMMENT ON COLUMN COMPANY.USE_YN IS '사용 여부 (Y/N)';

-- ============================================================================
-- 2. 사용자 계정 (직원 정보)
-- ============================================================================

CREATE TABLE IF NOT EXISTS USER_ACCOUNT (
    EMP_ID SERIAL PRIMARY KEY,
    COMPANY_CODE VARCHAR(20) NOT NULL,
    EMAIL VARCHAR(100) NOT NULL,
    PASSWORD_HASH VARCHAR(255),  -- NULL 허용 (OAuth 전용 계정)
    EMP_NO VARCHAR(50),  -- 사원번호
    EMP_NAME VARCHAR(100) NOT NULL,
    PHONE VARCHAR(20),
    MOBILE VARCHAR(20),
    DEPARTMENT_CODE VARCHAR(20),
    DUTY_CODE_ID INTEGER,  -- 직급 ID (RBAC에서 사용)
    POSITION_NAME VARCHAR(100),  -- 직위명
    JOIN_DATE DATE,
    RESIGN_DATE DATE,
    PROFILE_IMAGE_URL TEXT,
    LAST_LOGIN_AT TIMESTAMP,
    PASSWORD_CHANGED_AT TIMESTAMP,
    FAILED_LOGIN_COUNT INTEGER DEFAULT 0,
    ACCOUNT_LOCKED_UNTIL TIMESTAMP,
    USE_YN CHAR(1) DEFAULT 'Y' CHECK (USE_YN IN ('Y', 'N')),
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CREATED_BY VARCHAR(50),
    UPDATED_BY VARCHAR(50),

    FOREIGN KEY (COMPANY_CODE) REFERENCES COMPANY(COMPANY_CODE) ON DELETE CASCADE,
    UNIQUE (COMPANY_CODE, EMAIL)  -- 회사별 이메일 유일성
);

CREATE INDEX idx_user_company_email ON USER_ACCOUNT(COMPANY_CODE, EMAIL);
CREATE INDEX idx_user_emp_no ON USER_ACCOUNT(COMPANY_CODE, EMP_NO);
CREATE INDEX idx_user_use_yn ON USER_ACCOUNT(USE_YN);
CREATE INDEX idx_user_last_login ON USER_ACCOUNT(LAST_LOGIN_AT);

COMMENT ON TABLE USER_ACCOUNT IS '사용자 계정 (직원 정보)';
COMMENT ON COLUMN USER_ACCOUNT.EMP_ID IS '직원 ID (PK)';
COMMENT ON COLUMN USER_ACCOUNT.COMPANY_CODE IS '회사 코드 (멀티 테넌시 키)';
COMMENT ON COLUMN USER_ACCOUNT.PASSWORD_HASH IS 'BCRYPT 해시 비밀번호 (OAuth 전용 계정은 NULL)';
COMMENT ON COLUMN USER_ACCOUNT.DUTY_CODE_ID IS '직급 ID (RBAC 권한 결정)';
COMMENT ON COLUMN USER_ACCOUNT.FAILED_LOGIN_COUNT IS '로그인 실패 횟수 (5회 초과 시 계정 잠금)';

-- ============================================================================
-- 3. 소셜 로그인 연동 (OAuth)
-- ============================================================================

CREATE TABLE IF NOT EXISTS USER_SOCIAL_AUTH (
    SOCIAL_AUTH_ID SERIAL PRIMARY KEY,
    EMP_ID INTEGER NOT NULL,
    COMPANY_CODE VARCHAR(20) NOT NULL,
    PROVIDER VARCHAR(20) NOT NULL CHECK (PROVIDER IN ('GOOGLE', 'KAKAO', 'NAVER', 'MICROSOFT')),
    PROVIDER_ID VARCHAR(255) NOT NULL,  -- 제공자의 고유 사용자 ID
    PROVIDER_EMAIL VARCHAR(100),
    ACCESS_TOKEN TEXT,
    REFRESH_TOKEN TEXT,
    TOKEN_EXPIRES_AT TIMESTAMP,
    PROFILE_DATA JSONB,  -- 추가 프로필 정보 (JSON)
    USE_YN CHAR(1) DEFAULT 'Y' CHECK (USE_YN IN ('Y', 'N')),
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (EMP_ID) REFERENCES USER_ACCOUNT(EMP_ID) ON DELETE CASCADE,
    FOREIGN KEY (COMPANY_CODE) REFERENCES COMPANY(COMPANY_CODE) ON DELETE CASCADE,
    UNIQUE (COMPANY_CODE, PROVIDER, PROVIDER_ID)  -- 회사별 제공자 ID 유일성
);

CREATE INDEX idx_social_auth_emp ON USER_SOCIAL_AUTH(EMP_ID);
CREATE INDEX idx_social_auth_provider ON USER_SOCIAL_AUTH(COMPANY_CODE, PROVIDER, PROVIDER_ID);
CREATE INDEX idx_social_auth_use_yn ON USER_SOCIAL_AUTH(USE_YN);

COMMENT ON TABLE USER_SOCIAL_AUTH IS '소셜 로그인 연동 정보';
COMMENT ON COLUMN USER_SOCIAL_AUTH.PROVIDER IS '소셜 로그인 제공자 (GOOGLE, KAKAO, NAVER, MICROSOFT)';
COMMENT ON COLUMN USER_SOCIAL_AUTH.PROVIDER_ID IS '제공자의 고유 사용자 ID (sub, id 등)';
COMMENT ON COLUMN USER_SOCIAL_AUTH.PROFILE_DATA IS '추가 프로필 정보 (JSONB)';

-- ============================================================================
-- 4. RBAC - 역할(Role) 정의
-- ============================================================================

CREATE TABLE IF NOT EXISTS RBAC_ROLE (
    ROLE_ID SERIAL PRIMARY KEY,
    COMPANY_CODE VARCHAR(20) NOT NULL,
    ROLE_CODE VARCHAR(50) NOT NULL,  -- 예: ADMIN, MANAGER, EMPLOYEE
    ROLE_NAME VARCHAR(100) NOT NULL,
    DESCRIPTION TEXT,
    IS_SYSTEM_ROLE BOOLEAN DEFAULT FALSE,  -- 시스템 기본 역할 여부
    USE_YN CHAR(1) DEFAULT 'Y' CHECK (USE_YN IN ('Y', 'N')),
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CREATED_BY VARCHAR(50),
    UPDATED_BY VARCHAR(50),

    FOREIGN KEY (COMPANY_CODE) REFERENCES COMPANY(COMPANY_CODE) ON DELETE CASCADE,
    UNIQUE (COMPANY_CODE, ROLE_CODE)
);

CREATE INDEX idx_rbac_role_company ON RBAC_ROLE(COMPANY_CODE);
CREATE INDEX idx_rbac_role_code ON RBAC_ROLE(COMPANY_CODE, ROLE_CODE);

COMMENT ON TABLE RBAC_ROLE IS 'RBAC 역할 정의';
COMMENT ON COLUMN RBAC_ROLE.IS_SYSTEM_ROLE IS '시스템 기본 역할 (삭제 불가)';

-- ============================================================================
-- 5. RBAC - 권한(Permission) 정의
-- ============================================================================

CREATE TABLE IF NOT EXISTS RBAC_PERMISSION (
    PERMISSION_ID SERIAL PRIMARY KEY,
    PERMISSION_CODE VARCHAR(100) NOT NULL UNIQUE,  -- 예: user:read, user:write
    PERMISSION_NAME VARCHAR(100) NOT NULL,
    RESOURCE VARCHAR(50) NOT NULL,  -- 리소스 (user, project, performance 등)
    ACTION VARCHAR(20) NOT NULL,  -- 액션 (read, write, delete, approve 등)
    DESCRIPTION TEXT,
    IS_SYSTEM_PERMISSION BOOLEAN DEFAULT FALSE,
    USE_YN CHAR(1) DEFAULT 'Y' CHECK (USE_YN IN ('Y', 'N')),
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_rbac_perm_code ON RBAC_PERMISSION(PERMISSION_CODE);
CREATE INDEX idx_rbac_perm_resource ON RBAC_PERMISSION(RESOURCE, ACTION);

COMMENT ON TABLE RBAC_PERMISSION IS 'RBAC 권한 정의';
COMMENT ON COLUMN RBAC_PERMISSION.PERMISSION_CODE IS '권한 코드 (resource:action 형식)';

-- ============================================================================
-- 6. RBAC - 역할-권한 매핑
-- ============================================================================

CREATE TABLE IF NOT EXISTS RBAC_ROLE_PERMISSION (
    ROLE_PERMISSION_ID SERIAL PRIMARY KEY,
    ROLE_ID INTEGER NOT NULL,
    PERMISSION_ID INTEGER NOT NULL,
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CREATED_BY VARCHAR(50),

    FOREIGN KEY (ROLE_ID) REFERENCES RBAC_ROLE(ROLE_ID) ON DELETE CASCADE,
    FOREIGN KEY (PERMISSION_ID) REFERENCES RBAC_PERMISSION(PERMISSION_ID) ON DELETE CASCADE,
    UNIQUE (ROLE_ID, PERMISSION_ID)
);

CREATE INDEX idx_role_perm_role ON RBAC_ROLE_PERMISSION(ROLE_ID);
CREATE INDEX idx_role_perm_permission ON RBAC_ROLE_PERMISSION(PERMISSION_ID);

COMMENT ON TABLE RBAC_ROLE_PERMISSION IS 'RBAC 역할-권한 매핑';

-- ============================================================================
-- 7. RBAC - 사용자-역할 매핑
-- ============================================================================

CREATE TABLE IF NOT EXISTS RBAC_USER_ROLE (
    USER_ROLE_ID SERIAL PRIMARY KEY,
    EMP_ID INTEGER NOT NULL,
    ROLE_ID INTEGER NOT NULL,
    GRANTED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    GRANTED_BY VARCHAR(50),
    REVOKED_AT TIMESTAMP,
    REVOKED_BY VARCHAR(50),
    USE_YN CHAR(1) DEFAULT 'Y' CHECK (USE_YN IN ('Y', 'N')),

    FOREIGN KEY (EMP_ID) REFERENCES USER_ACCOUNT(EMP_ID) ON DELETE CASCADE,
    FOREIGN KEY (ROLE_ID) REFERENCES RBAC_ROLE(ROLE_ID) ON DELETE CASCADE,
    UNIQUE (EMP_ID, ROLE_ID)
);

CREATE INDEX idx_user_role_emp ON RBAC_USER_ROLE(EMP_ID);
CREATE INDEX idx_user_role_role ON RBAC_USER_ROLE(ROLE_ID);
CREATE INDEX idx_user_role_use_yn ON RBAC_USER_ROLE(USE_YN);

COMMENT ON TABLE RBAC_USER_ROLE IS 'RBAC 사용자-역할 매핑';

-- ============================================================================
-- 8. Refresh Token 저장소
-- ============================================================================

CREATE TABLE IF NOT EXISTS REFRESH_TOKEN (
    TOKEN_ID SERIAL PRIMARY KEY,
    EMP_ID INTEGER NOT NULL,
    COMPANY_CODE VARCHAR(20) NOT NULL,
    TOKEN_HASH VARCHAR(255) NOT NULL UNIQUE,  -- Refresh Token의 해시값
    EXPIRES_AT TIMESTAMP NOT NULL,
    DEVICE_INFO VARCHAR(200),  -- 디바이스 정보
    IP_ADDRESS VARCHAR(45),  -- IPv6 지원
    USER_AGENT TEXT,
    IS_REVOKED BOOLEAN DEFAULT FALSE,
    REVOKED_AT TIMESTAMP,
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (EMP_ID) REFERENCES USER_ACCOUNT(EMP_ID) ON DELETE CASCADE,
    FOREIGN KEY (COMPANY_CODE) REFERENCES COMPANY(COMPANY_CODE) ON DELETE CASCADE
);

CREATE INDEX idx_refresh_token_emp ON REFRESH_TOKEN(EMP_ID);
CREATE INDEX idx_refresh_token_hash ON REFRESH_TOKEN(TOKEN_HASH);
CREATE INDEX idx_refresh_token_expires ON REFRESH_TOKEN(EXPIRES_AT);
CREATE INDEX idx_refresh_token_revoked ON REFRESH_TOKEN(IS_REVOKED);

COMMENT ON TABLE REFRESH_TOKEN IS 'Refresh Token 저장소';
COMMENT ON COLUMN REFRESH_TOKEN.TOKEN_HASH IS 'Refresh Token의 SHA-256 해시값';

-- ============================================================================
-- 9. 로그인 이력 (Audit)
-- ============================================================================

CREATE TABLE IF NOT EXISTS LOGIN_HISTORY (
    HISTORY_ID SERIAL PRIMARY KEY,
    EMP_ID INTEGER,
    COMPANY_CODE VARCHAR(20),
    EMAIL VARCHAR(100) NOT NULL,
    LOGIN_METHOD VARCHAR(20) CHECK (LOGIN_METHOD IN ('PASSWORD', 'GOOGLE', 'KAKAO', 'NAVER', 'MICROSOFT')),
    LOGIN_SUCCESS BOOLEAN NOT NULL,
    FAILURE_REASON VARCHAR(200),
    IP_ADDRESS VARCHAR(45),
    USER_AGENT TEXT,
    DEVICE_INFO VARCHAR(200),
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (EMP_ID) REFERENCES USER_ACCOUNT(EMP_ID) ON DELETE SET NULL,
    FOREIGN KEY (COMPANY_CODE) REFERENCES COMPANY(COMPANY_CODE) ON DELETE SET NULL
);

CREATE INDEX idx_login_history_emp ON LOGIN_HISTORY(EMP_ID);
CREATE INDEX idx_login_history_email ON LOGIN_HISTORY(COMPANY_CODE, EMAIL);
CREATE INDEX idx_login_history_created ON LOGIN_HISTORY(CREATED_AT);
CREATE INDEX idx_login_history_success ON LOGIN_HISTORY(LOGIN_SUCCESS);

COMMENT ON TABLE LOGIN_HISTORY IS '로그인 이력 (감사 로그)';

-- ============================================================================
-- 10. 초기 데이터 INSERT (예시)
-- ============================================================================

-- 예시 회사 데이터
INSERT INTO COMPANY (COMPANY_CODE, COMPANY_NAME, USE_YN) VALUES
    ('VNTG', 'Vantage Corporation', 'Y'),
    ('DEMO', 'Demo Company', 'Y')
ON CONFLICT (COMPANY_CODE) DO NOTHING;

-- 시스템 기본 권한
INSERT INTO RBAC_PERMISSION (PERMISSION_CODE, PERMISSION_NAME, RESOURCE, ACTION, IS_SYSTEM_PERMISSION) VALUES
    ('user:read', '사용자 조회', 'user', 'read', TRUE),
    ('user:write', '사용자 생성/수정', 'user', 'write', TRUE),
    ('user:delete', '사용자 삭제', 'user', 'delete', TRUE),
    ('performance:read', '성과 조회', 'performance', 'read', TRUE),
    ('performance:write', '성과 작성/수정', 'performance', 'write', TRUE),
    ('performance:approve', '성과 승인', 'performance', 'approve', TRUE),
    ('admin:all', '시스템 관리', 'admin', 'all', TRUE)
ON CONFLICT (PERMISSION_CODE) DO NOTHING;

-- 시스템 기본 역할 (회사별)
INSERT INTO RBAC_ROLE (COMPANY_CODE, ROLE_CODE, ROLE_NAME, IS_SYSTEM_ROLE) VALUES
    ('VNTG', 'ADMIN', '시스템 관리자', TRUE),
    ('VNTG', 'MANAGER', '관리자', TRUE),
    ('VNTG', 'EMPLOYEE', '일반 직원', TRUE),
    ('DEMO', 'ADMIN', '시스템 관리자', TRUE),
    ('DEMO', 'MANAGER', '관리자', TRUE),
    ('DEMO', 'EMPLOYEE', '일반 직원', TRUE)
ON CONFLICT (COMPANY_CODE, ROLE_CODE) DO NOTHING;

-- 역할-권한 매핑 (ADMIN 역할에 모든 권한 부여)
INSERT INTO RBAC_ROLE_PERMISSION (ROLE_ID, PERMISSION_ID)
SELECT r.ROLE_ID, p.PERMISSION_ID
FROM RBAC_ROLE r
CROSS JOIN RBAC_PERMISSION p
WHERE r.ROLE_CODE = 'ADMIN'
ON CONFLICT (ROLE_ID, PERMISSION_ID) DO NOTHING;

-- 역할-권한 매핑 (EMPLOYEE 역할에 기본 권한 부여)
INSERT INTO RBAC_ROLE_PERMISSION (ROLE_ID, PERMISSION_ID)
SELECT r.ROLE_ID, p.PERMISSION_ID
FROM RBAC_ROLE r
CROSS JOIN RBAC_PERMISSION p
WHERE r.ROLE_CODE = 'EMPLOYEE'
  AND p.PERMISSION_CODE IN ('user:read', 'performance:read', 'performance:write')
ON CONFLICT (ROLE_ID, PERMISSION_ID) DO NOTHING;

-- 테스트용 관리자 계정 (비밀번호: admin123)
-- BCRYPT 해시: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYC5OwHbaHm
INSERT INTO USER_ACCOUNT (
    COMPANY_CODE, EMAIL, PASSWORD_HASH, EMP_NO, EMP_NAME,
    DUTY_CODE_ID, POSITION_NAME, USE_YN
) VALUES (
    'VNTG',
    'admin@vantage.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYC5OwHbaHm',
    'EMP001',
    '시스템 관리자',
    1,
    'CEO',
    'Y'
) ON CONFLICT (COMPANY_CODE, EMAIL) DO NOTHING;

-- 테스트 관리자에게 ADMIN 역할 부여
INSERT INTO RBAC_USER_ROLE (EMP_ID, ROLE_ID)
SELECT u.EMP_ID, r.ROLE_ID
FROM USER_ACCOUNT u
CROSS JOIN RBAC_ROLE r
WHERE u.EMAIL = 'admin@vantage.com'
  AND u.COMPANY_CODE = 'VNTG'
  AND r.ROLE_CODE = 'ADMIN'
  AND r.COMPANY_CODE = 'VNTG'
ON CONFLICT (EMP_ID, ROLE_ID) DO NOTHING;

-- ============================================================================
-- 유용한 View 정의
-- ============================================================================

-- 사용자 권한 조회 View
CREATE OR REPLACE VIEW V_USER_PERMISSIONS AS
SELECT
    u.EMP_ID,
    u.COMPANY_CODE,
    u.EMAIL,
    u.EMP_NAME,
    r.ROLE_CODE,
    r.ROLE_NAME,
    p.PERMISSION_CODE,
    p.RESOURCE,
    p.ACTION
FROM USER_ACCOUNT u
INNER JOIN RBAC_USER_ROLE ur ON u.EMP_ID = ur.EMP_ID AND ur.USE_YN = 'Y'
INNER JOIN RBAC_ROLE r ON ur.ROLE_ID = r.ROLE_ID AND r.USE_YN = 'Y'
INNER JOIN RBAC_ROLE_PERMISSION rp ON r.ROLE_ID = rp.ROLE_ID
INNER JOIN RBAC_PERMISSION p ON rp.PERMISSION_ID = p.PERMISSION_ID AND p.USE_YN = 'Y'
WHERE u.USE_YN = 'Y';

COMMENT ON VIEW V_USER_PERMISSIONS IS '사용자별 권한 조회 View';

-- ============================================================================
-- 인덱스 최적화를 위한 추가 복합 인덱스
-- ============================================================================

-- 로그인 쿼리 최적화
CREATE INDEX IF NOT EXISTS idx_user_login_lookup
ON USER_ACCOUNT(COMPANY_CODE, EMAIL, USE_YN)
WHERE USE_YN = 'Y';

-- 권한 조회 최적화
CREATE INDEX IF NOT EXISTS idx_user_role_active
ON RBAC_USER_ROLE(EMP_ID, ROLE_ID)
WHERE USE_YN = 'Y';

-- ============================================================================
-- 완료
-- ============================================================================

-- 스키마 생성 완료 메시지
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'PMS Authentication & Authorization Schema Created Successfully!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Tables Created:';
    RAISE NOTICE '  - COMPANY (회사/테넌트)';
    RAISE NOTICE '  - USER_ACCOUNT (사용자 계정)';
    RAISE NOTICE '  - USER_SOCIAL_AUTH (소셜 로그인)';
    RAISE NOTICE '  - RBAC_ROLE (역할)';
    RAISE NOTICE '  - RBAC_PERMISSION (권한)';
    RAISE NOTICE '  - RBAC_ROLE_PERMISSION (역할-권한 매핑)';
    RAISE NOTICE '  - RBAC_USER_ROLE (사용자-역할 매핑)';
    RAISE NOTICE '  - REFRESH_TOKEN (리프레시 토큰)';
    RAISE NOTICE '  - LOGIN_HISTORY (로그인 이력)';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Test Account:';
    RAISE NOTICE '  Email: admin@vantage.com';
    RAISE NOTICE '  Password: admin123';
    RAISE NOTICE '  Company: VNTG';
    RAISE NOTICE '========================================';
END $$;
