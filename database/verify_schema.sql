-- ============================================================================
-- Schema Verification Script for Supabase
-- ============================================================================
-- Supabase SQL Editor에서 실행하여 employees 테이블 스키마를 확인합니다
-- ============================================================================

-- 1. employees 테이블의 모든 컬럼 확인
SELECT
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'employees'
ORDER BY ordinal_position;

-- 2. employees 테이블에 필요한 인증 컬럼들이 있는지 확인
SELECT
    CASE
        WHEN EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'employees' AND column_name = 'failed_login_count')
        THEN 'EXISTS'
        ELSE 'MISSING'
    END AS failed_login_count_status,
    CASE
        WHEN EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'employees' AND column_name = 'account_locked_until')
        THEN 'EXISTS'
        ELSE 'MISSING'
    END AS account_locked_until_status,
    CASE
        WHEN EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'employees' AND column_name = 'password_changed_at')
        THEN 'EXISTS'
        ELSE 'MISSING'
    END AS password_changed_at_status;

-- 3. 테스트 사용자 데이터 확인
SELECT
    emp_id,
    company_code,
    email,
    name,
    use_yn,
    account_status,
    CASE
        WHEN password IS NOT NULL AND password != '' THEN 'SET (' || substring(password, 1, 10) || '...)'
        ELSE 'NULL'
    END AS password_status,
    failed_login_count,
    account_locked_until,
    password_changed_at
FROM employees
WHERE company_code = 100 AND email = 'cjhol2107@vntgcorp.com';

-- 4. companies 테이블 확인
SELECT * FROM companies WHERE company_code = 100;

-- 5. 간단한 쿼리 테스트 (모델에서 사용하는 것과 동일)
SELECT emp_id, company_code, email, name, use_yn, account_status
FROM employees
WHERE company_code = 100
  AND email = 'cjhol2107@vntgcorp.com'
  AND use_yn = 'Y'
  AND account_status = 'ACTIVE';
