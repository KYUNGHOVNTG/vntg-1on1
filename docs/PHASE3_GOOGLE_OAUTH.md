# Phase 3: Google OAuth 2.0 Integration

## 📌 개요

Phase 3에서는 **Google OAuth 2.0 로그인** 기능이 추가되었습니다.

기존 직원 계정(employees 테이블)을 구글 계정과 연동하여 로그인할 수 있습니다.

---

## 🎯 주요 기능

### 1. 구글 로그인 (POST /api/v1/auth/google)

- **구글 ID 토큰**을 사용하여 로그인
- **자동 계정 연동**: 구글 이메일과 employees.email이 일치하면 자동으로 연동
- **JWT 토큰 발급**: 일반 로그인과 동일하게 Access Token + Refresh Token 발급

### 2. 소셜 인증 연동 관리

- `user_social_auth` 테이블에 구글 계정 연동 정보 저장
- 한 직원이 여러 소셜 계정을 연동 가능 (Google, Kakao 등 - 향후 확장 가능)

---

## 📋 API 스펙

### POST /api/v1/auth/google

구글 ID 토큰으로 로그인합니다.

**Request Body:**

```json
{
  "company_code": 100,
  "google_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjI3...",
  "device_info": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
```

**Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "emp_id": 1,
    "company_code": 100,
    "email": "user@vntgcorp.com",
    "name": "홍길동",
    "emp_no": "EMP001",
    "dept_id": 10,
    "duty_code_id": 5,
    "pos_code_id": 3,
    "phone": "010-1234-5678",
    "last_login_at": "2024-01-15T10:30:00",
    "use_yn": "Y"
  },
  "permissions": ["role:manager", "menu:dashboard"]
}
```

**Error Responses:**

- **401 Unauthorized**: 구글 토큰이 유효하지 않음
- **400 Bad Request**: 이메일이 인증되지 않음
- **404 Not Found**: 해당 이메일을 가진 직원이 없음 (company_code 내)

---

## 🔄 로그인 프로세스

### 1. 처음 구글 로그인하는 경우 (계정 연동)

```
1. 클라이언트가 구글 ID 토큰을 POST /api/v1/auth/google에 전송
2. 서버가 구글 토큰을 검증 → 구글 사용자 정보 추출 (이메일, 이름, 구글 고유 ID 등)
3. user_social_auth 테이블에서 기존 연동 조회 → 없음
4. employees 테이블에서 구글 이메일로 직원 검색
5. 직원을 찾으면 → user_social_auth에 연동 정보 생성
6. JWT 토큰 발급 및 반환
```

### 2. 이미 연동된 구글 계정으로 로그인하는 경우

```
1. 클라이언트가 구글 ID 토큰을 POST /api/v1/auth/google에 전송
2. 서버가 구글 토큰을 검증 → 구글 사용자 정보 추출
3. user_social_auth 테이블에서 기존 연동 조회 → 있음!
4. 연동된 직원 정보 조회
5. JWT 토큰 발급 및 반환
```

---

## 🗄️ 데이터베이스 구조

### user_social_auth 테이블

| 컬럼              | 타입         | 설명                                  |
| ----------------- | ------------ | ------------------------------------- |
| social_id         | SERIAL (PK)  | 소셜 인증 고유 ID                     |
| emp_id            | INTEGER (FK) | 연동된 직원 ID (employees.emp_id)     |
| provider          | VARCHAR(20)  | 제공자 (GOOGLE, KAKAO, NAVER 등)      |
| provider_user_id  | VARCHAR(100) | 제공자의 고유 사용자 ID (예: 구글 sub) |
| use_yn            | CHAR(1)      | 사용 여부 ('Y' / 'N')                 |
| created_at        | TIMESTAMP    | 생성 시간                             |

**인덱스:**

- `idx_social_auth_provider`: (provider, provider_user_id) - 빠른 조회
- `idx_social_auth_emp`: (emp_id) - 직원별 연동 조회
- `uq_social_auth_provider_user`: (provider, provider_user_id) UNIQUE - 중복 방지

---

## 🧪 테스트 방법

### 1. 구글 ID 토큰 발급

프론트엔드에서 구글 로그인 버튼을 클릭하면 구글 OAuth 2.0 플로우가 시작됩니다.

**개발 테스트용 (Google OAuth Playground 사용):**

1. https://developers.google.com/oauthplayground 접속
2. 왼쪽에서 **Google OAuth2 API v2** 선택
3. `https://www.googleapis.com/auth/userinfo.email` 스코프 선택
4. "Authorize APIs" 클릭 → 구글 계정으로 로그인
5. Authorization code 받기
6. "Exchange authorization code for tokens" 클릭
7. **id_token** 값 복사 (이것이 구글 ID 토큰)

### 2. API 테스트

```bash
curl -X POST http://localhost:8000/api/v1/auth/google \
  -H "Content-Type: application/json" \
  -d '{
    "company_code": 100,
    "google_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjI3...",
    "device_info": "curl test"
  }'
```

### 3. 토큰 검증 확인

구글 ID 토큰을 검증하려면:

```bash
curl "https://oauth2.googleapis.com/tokeninfo?id_token=YOUR_GOOGLE_TOKEN"
```

응답 예시:

```json
{
  "sub": "1234567890",
  "email": "user@example.com",
  "email_verified": "true",
  "name": "홍길동",
  "picture": "https://lh3.googleusercontent.com/..."
}
```

---

## ⚙️ 환경 설정

### 선택적: Google OAuth Client ID 설정

프로덕션 환경에서는 `google-auth` 라이브러리를 사용하여 Client ID를 검증하는 것이 권장됩니다.

**requirements.txt에 추가:**

```txt
google-auth==2.23.0
```

**코드 수정 (google_oauth.py):**

`verify_google_token_with_google_auth()` 함수를 사용하도록 변경하고, Client ID를 설정에 추가:

```python
# server/app/core/config.py
class Settings(BaseSettings):
    # ... 기존 설정
    GOOGLE_OAUTH_CLIENT_ID: Optional[str] = None
```

---

## 🔐 보안 고려사항

### 1. 구글 토큰 검증

- 현재: Google의 `tokeninfo` API를 사용하여 검증
- 권장: 프로덕션에서는 `google-auth` 라이브러리 사용 (더 안전)

### 2. 이메일 인증 필수

- 구글 계정의 `email_verified`가 `true`인 경우에만 로그인 허용

### 3. 계정 잠금 정책

- 구글 로그인 실패 시에도 로그인 실패 기록 (`login_history`)
- 단, 비밀번호 실패와 달리 계정 잠금은 적용되지 않음

### 4. 멀티 테넌시

- `company_code`로 회사를 구분
- 같은 구글 계정이라도 다른 회사(company_code)에서는 별도 연동 필요

---

## 📊 로그 및 모니터링

### login_history 테이블

구글 로그인 시도는 `login_history` 테이블에 기록됩니다:

```sql
SELECT * FROM login_history
WHERE login_method = 'GOOGLE'
ORDER BY created_at DESC
LIMIT 10;
```

**컬럼:**

- `login_method`: 'GOOGLE'
- `login_success`: true (성공) / false (실패)
- `failure_reason`: 실패 시 사유 (예: "Invalid Google token", "User not found")
- `email`: 구글 이메일
- `ip_address`, `user_agent`, `device_info`: 로그인 컨텍스트

---

## 🚀 향후 확장 가능성

Phase 3는 Google OAuth만 구현했지만, 동일한 구조로 다른 소셜 로그인도 추가 가능합니다:

### 지원 가능한 제공자:

- ✅ **GOOGLE** (Phase 3 구현 완료)
- 🔜 **KAKAO** (카카오 로그인)
- 🔜 **NAVER** (네이버 로그인)
- 🔜 **MICROSOFT** (Microsoft 계정)

각 제공자별로:

1. `{provider}_oauth.py` 유틸리티 생성
2. `{Provider}OAuthService` 서비스 생성
3. `POST /api/v1/auth/{provider}` 엔드포인트 추가

---

## 📝 체크리스트

Phase 3 구현 완료 후 확인사항:

- [x] Google OAuth 스키마 정의 (`GoogleLoginRequest`, `GoogleUserInfo`)
- [x] 구글 토큰 검증 유틸리티 (`verify_google_token`)
- [x] GoogleOAuthService 구현
- [x] POST /api/v1/auth/google 엔드포인트 추가
- [x] user_social_auth 테이블 인덱스 추가
- [x] login_history에 GOOGLE 로그인 기록
- [x] 자동 계정 연동 로직 (이메일 매칭)
- [x] Phase 3 마이그레이션 스크립트 작성

---

## 🔧 트러블슈팅

### 1. "Invalid Google token" 오류

**원인**: 구글 ID 토큰이 만료되었거나 유효하지 않음

**해결**:

- 새로운 구글 ID 토큰을 발급받으세요
- 구글 토큰의 만료 시간은 약 1시간입니다

### 2. "No employee found with email" 오류

**원인**: 구글 이메일이 employees 테이블에 없음

**해결**:

- employees 테이블에 해당 이메일을 추가하세요
- company_code가 올바른지 확인하세요

```sql
SELECT * FROM employees
WHERE email = 'user@example.com' AND company_code = 100;
```

### 3. "Account is locked" 오류

**원인**: 계정이 잠겨있음 (비밀번호 5회 실패)

**해결**:

```sql
UPDATE employees
SET account_locked_until = NULL,
    failed_login_count = 0
WHERE email = 'user@example.com';
```

### 4. "Email not verified" 오류

**원인**: 구글 계정의 이메일이 인증되지 않음

**해결**:

- 구글 계정에서 이메일을 인증하세요
- 개발 환경에서는 테스트용 구글 계정을 사용하세요

---

## 📚 참고 자료

- [Google OAuth 2.0 문서](https://developers.google.com/identity/protocols/oauth2)
- [Google ID Token 검증](https://developers.google.com/identity/sign-in/web/backend-auth)
- [FastAPI OAuth2](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [httpx 문서](https://www.python-httpx.org/)

---

## 👨‍💻 작성자

**Phase 3 구현 완료: 2024-01-XX**

- Google OAuth 2.0 로그인
- 자동 계정 연동
- JWT 토큰 발급
- 로그인 이력 기록
