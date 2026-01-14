-- ============================================================================
-- Seed Data for Testing Auth Endpoints
-- ============================================================================
-- 테스트용 초기 데이터 (회사, 직원, 역할 그룹)
-- ============================================================================

-- 1. 회사 데이터 삽입
INSERT INTO companies (company_code, company_name, domain, use_yn, created_at, updated_at)
VALUES (100, 'VNTG CORP', 'vntgcorp.com', 'Y', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT (company_code) DO UPDATE SET
    company_name = EXCLUDED.company_name,
    domain = EXCLUDED.domain,
    updated_at = CURRENT_TIMESTAMP;

-- 2. 직원 데이터 삽입 (비밀번호: test123)
-- bcrypt hash for 'test123': $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqNqB6kOqi
INSERT INTO employees (
    emp_id, company_code, emp_no, email, name, phone, hire_date,
    dept_id, pos_code_id, duty_code_id, user_category, account_status,
    use_yn, created_at, login_id, password, last_login_at,
    failed_login_count, account_locked_until, password_changed_at
)
VALUES (
    1, 100, 'V001', 'cjhol2107@vntgcorp.com', '최경호', NULL, NULL,
    1, 4, 7, 'INTERNAL', 'ACTIVE',
    'Y', CURRENT_TIMESTAMP, 'cjhol2107',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqNqB6kOqi',
    NULL, 0, NULL, CURRENT_TIMESTAMP
)
ON CONFLICT (emp_id) DO UPDATE SET
    email = EXCLUDED.email,
    password = EXCLUDED.password,
    account_status = EXCLUDED.account_status,
    use_yn = EXCLUDED.use_yn,
    failed_login_count = 0,
    account_locked_until = NULL;

INSERT INTO employees (
    emp_id, company_code, emp_no, email, name, phone, hire_date,
    dept_id, pos_code_id, duty_code_id, user_category, account_status,
    use_yn, created_at, login_id, password, last_login_at,
    failed_login_count, account_locked_until, password_changed_at
)
VALUES (
    2, 100, 'V002', 'user2@vntgcorp.com', '사원2', NULL, NULL,
    1, 1, 6, 'INTERNAL', 'ACTIVE',
    'Y', CURRENT_TIMESTAMP, 'user2',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqNqB6kOqi',
    NULL, 0, NULL, CURRENT_TIMESTAMP
)
ON CONFLICT (emp_id) DO UPDATE SET
    email = EXCLUDED.email,
    password = EXCLUDED.password,
    account_status = EXCLUDED.account_status,
    use_yn = EXCLUDED.use_yn,
    failed_login_count = 0,
    account_locked_until = NULL;

INSERT INTO employees (
    emp_id, company_code, emp_no, email, name, phone, hire_date,
    dept_id, pos_code_id, duty_code_id, user_category, account_status,
    use_yn, created_at, login_id, password, last_login_at,
    failed_login_count, account_locked_until, password_changed_at
)
VALUES (
    3, 100, 'V003', 'user3@vntgcorp.com', '사원3', NULL, NULL,
    1, 1, 6, 'INTERNAL', 'ACTIVE',
    'Y', CURRENT_TIMESTAMP, 'user3',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqNqB6kOqi',
    NULL, 0, NULL, CURRENT_TIMESTAMP
)
ON CONFLICT (emp_id) DO UPDATE SET
    email = EXCLUDED.email,
    password = EXCLUDED.password,
    account_status = EXCLUDED.account_status,
    use_yn = EXCLUDED.use_yn,
    failed_login_count = 0,
    account_locked_until = NULL;

-- 3. 시퀀스 업데이트 (다음 emp_id가 4부터 시작하도록)
SELECT setval('employees_emp_id_seq', (SELECT MAX(emp_id) FROM employees), true);

-- 4. 역할 그룹 데이터 삽입 (선택 사항)
INSERT INTO role_groups (role_group_id, company_code, role_group_name, use_yn)
VALUES
    (1, 100, '관리자', 'Y'),
    (2, 100, '일반 사용자', 'Y')
ON CONFLICT (role_group_id) DO UPDATE SET
    role_group_name = EXCLUDED.role_group_name,
    use_yn = EXCLUDED.use_yn;

SELECT setval('role_groups_role_group_id_seq', (SELECT MAX(role_group_id) FROM role_groups), true);

-- 5. 완료 메시지
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Seed Data Inserted Successfully!';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Test Accounts:';
    RAISE NOTICE '  - Email: cjhol2107@vntgcorp.com';
    RAISE NOTICE '    Password: test123';
    RAISE NOTICE '    Company Code: 100';
    RAISE NOTICE '';
    RAISE NOTICE '  - Email: user2@vntgcorp.com';
    RAISE NOTICE '    Password: test123';
    RAISE NOTICE '    Company Code: 100';
    RAISE NOTICE '';
    RAISE NOTICE '  - Email: user3@vntgcorp.com';
    RAISE NOTICE '    Password: test123';
    RAISE NOTICE '    Company Code: 100';
    RAISE NOTICE '========================================';
END $$;
