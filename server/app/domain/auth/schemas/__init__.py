"""
Auth 도메인 Pydantic 스키마

인증 관련 Request/Response 스키마를 정의합니다.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ====================
# Common Base Models
# ====================


class UserBase(BaseModel):
    """사용자 기본 정보"""

    emp_id: int = Field(..., description="직원 ID")
    company_code: int = Field(..., description="회사 코드 (숫자)")
    email: str = Field(..., description="이메일")
    name: str = Field(..., description="직원 이름")
    emp_no: Optional[str] = Field(None, description="사원번호")
    dept_id: Optional[int] = Field(None, description="부서 ID")
    duty_code_id: Optional[int] = Field(None, description="직급 ID")
    pos_code_id: Optional[int] = Field(None, description="직책 ID")


class UserInfo(UserBase):
    """사용자 상세 정보"""

    phone: Optional[str] = Field(None, description="전화번호")
    mobile: Optional[str] = Field(None, description="휴대폰번호")
    profile_image_url: Optional[str] = Field(None, description="프로필 이미지 URL")
    join_date: Optional[datetime] = Field(None, description="입사일")
    last_login_at: Optional[datetime] = Field(None, description="마지막 로그인 시간")
    use_yn: str = Field("Y", description="사용 여부")

    model_config = ConfigDict(from_attributes=True)


class PermissionInfo(BaseModel):
    """권한 정보"""

    permission_code: str = Field(..., description="권한 코드 (예: user:read)")
    resource: str = Field(..., description="리소스 (예: user)")
    action: str = Field(..., description="액션 (예: read)")

    model_config = ConfigDict(from_attributes=True)


class RoleInfo(BaseModel):
    """역할 정보"""

    role_code: str = Field(..., description="역할 코드")
    role_name: str = Field(..., description="역할 이름")
    permissions: list[str] = Field(default_factory=list, description="권한 코드 목록")

    model_config = ConfigDict(from_attributes=True)


# ====================
# Request Schemas
# ====================


class LoginRequest(BaseModel):
    """일반 로그인 요청"""

    company_code: int = Field(..., description="회사 코드 (숫자)")
    email: EmailStr = Field(..., description="이메일")
    password: str = Field(..., description="비밀번호", min_length=1, max_length=100)
    device_info: Optional[str] = Field(None, description="디바이스 정보")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "company_code": 100,
                "email": "cjhol2107@vntgcorp.com",
                "password": "test123",
                "device_info": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            }
        }
    )


class GoogleLoginRequest(BaseModel):
    """구글 OAuth 로그인 요청"""

    company_code: str = Field(..., description="회사 코드", min_length=1, max_length=20)
    google_token: str = Field(..., description="구글 ID 토큰 (JWT)")
    device_info: Optional[str] = Field(None, description="디바이스 정보")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "company_code": "VNTG",
                "google_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjI3...",
                "device_info": "Mozilla/5.0"
            }
        }
    )


class RefreshTokenRequest(BaseModel):
    """Refresh Token 갱신 요청"""

    refresh_token: str = Field(..., description="Refresh Token")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    )


class LogoutRequest(BaseModel):
    """로그아웃 요청"""

    refresh_token: Optional[str] = Field(None, description="Refresh Token (선택)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    )


class ChangePasswordRequest(BaseModel):
    """비밀번호 변경 요청"""

    current_password: str = Field(..., description="현재 비밀번호")
    new_password: str = Field(..., description="새 비밀번호", min_length=8, max_length=100)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "current_password": "oldpassword123",
                "new_password": "NewSecurePassword!@#123"
            }
        }
    )


# ====================
# Response Schemas
# ====================


class LoginResponse(BaseModel):
    """로그인 응답"""

    access_token: str = Field(..., description="Access Token (JWT)")
    refresh_token: str = Field(..., description="Refresh Token (JWT)")
    token_type: str = Field("bearer", description="토큰 타입")
    expires_in: int = Field(..., description="Access Token 만료 시간 (초)")
    user: UserInfo = Field(..., description="사용자 정보")
    permissions: list[str] = Field(default_factory=list, description="권한 코드 목록")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {
                    "emp_id": 1,
                    "company_code": "VNTG",
                    "email": "admin@vantage.com",
                    "emp_name": "시스템 관리자",
                    "emp_no": "EMP001",
                    "duty_code_id": 1,
                    "position_name": "CEO"
                },
                "permissions": ["user:read", "user:write", "admin:all"]
            }
        }
    )


class RefreshTokenResponse(BaseModel):
    """Token 갱신 응답"""

    access_token: str = Field(..., description="새로운 Access Token")
    token_type: str = Field("bearer", description="토큰 타입")
    expires_in: int = Field(..., description="만료 시간 (초)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }
    )


class LogoutResponse(BaseModel):
    """로그아웃 응답"""

    message: str = Field(..., description="응답 메시지")
    success: bool = Field(True, description="성공 여부")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Successfully logged out",
                "success": True
            }
        }
    )


class ChangePasswordResponse(BaseModel):
    """비밀번호 변경 응답"""

    message: str = Field(..., description="응답 메시지")
    success: bool = Field(True, description="성공 여부")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Password changed successfully",
                "success": True
            }
        }
    )


class CurrentUserResponse(BaseModel):
    """현재 사용자 정보 응답"""

    user: UserInfo = Field(..., description="사용자 정보")
    roles: list[RoleInfo] = Field(default_factory=list, description="역할 목록")
    permissions: list[str] = Field(default_factory=list, description="권한 코드 목록")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user": {
                    "emp_id": 1,
                    "company_code": "VNTG",
                    "email": "admin@vantage.com",
                    "emp_name": "시스템 관리자"
                },
                "roles": [
                    {
                        "role_code": "ADMIN",
                        "role_name": "시스템 관리자",
                        "permissions": ["admin:all"]
                    }
                ],
                "permissions": ["admin:all", "user:read", "user:write"]
            }
        }
    )


# ====================
# Internal Data Transfer Objects
# ====================


class AuthProviderInput(BaseModel):
    """AuthProvider 입력 데이터"""

    company_code: str
    email: Optional[str] = None
    google_id: Optional[str] = None
    emp_id: Optional[int] = None


class AuthProviderOutput(BaseModel):
    """AuthProvider 출력 데이터"""

    user: Optional[Any] = None  # UserAccount 모델
    permissions: list[str] = Field(default_factory=list)
    social_auth: Optional[Any] = None  # UserSocialAuth 모델

    model_config = ConfigDict(arbitrary_types_allowed=True)


class AuthFormatterInput(BaseModel):
    """AuthFormatter 입력 데이터"""

    user: Any  # UserAccount 모델
    access_token: str
    refresh_token: str
    permissions: list[str]

    model_config = ConfigDict(arbitrary_types_allowed=True)


# ====================
# Google OAuth Response (from Google API)
# ====================


class GoogleUserInfo(BaseModel):
    """구글 사용자 정보 (Google API 응답)"""

    sub: str = Field(..., description="구글 고유 ID")
    email: str = Field(..., description="이메일")
    email_verified: bool = Field(..., description="이메일 인증 여부")
    name: Optional[str] = Field(None, description="이름")
    given_name: Optional[str] = Field(None, description="이름")
    family_name: Optional[str] = Field(None, description="성")
    picture: Optional[str] = Field(None, description="프로필 사진 URL")
    locale: Optional[str] = Field(None, description="로케일")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sub": "1234567890",
                "email": "user@example.com",
                "email_verified": True,
                "name": "홍길동",
                "given_name": "길동",
                "family_name": "홍",
                "picture": "https://lh3.googleusercontent.com/...",
                "locale": "ko"
            }
        }
    )
