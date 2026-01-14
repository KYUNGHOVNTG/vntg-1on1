"""
Auth API 엔드포인트 (Phase 2: 고도화)

인증 관련 API를 제공합니다.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.core.dependencies import get_db
from server.app.domain.auth.schemas import (
    ChangePasswordRequest,
    ChangePasswordResponse,
    CurrentUserResponse,
    GoogleLoginRequest,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RoleInfo,
    UserInfo,
)
from server.app.domain.auth.google_oauth_service import GoogleOAuthService
from server.app.domain.auth.service import AuthService
from server.app.shared.exceptions import ApplicationException
from server.app.shared.utils.jwt import verify_token

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="일반 로그인 (ID/Password)",
    description="""
    이메일과 비밀번호로 로그인합니다.

    **멀티 테넌시**: company_code (숫자)로 회사를 구분합니다.
    **인증 방식**: 평문 또는 BCRYPT 비밀번호 지원
    **응답**: Access Token + Refresh Token + 사용자 정보 + 권한 목록

    **테스트 계정**:
    - company_code: 100
    - email: cjhol2107@vntgcorp.com
    - password: HASHED_PW (또는 실제 비밀번호)

    **주의사항**:
    - 5회 로그인 실패 시 계정이 30분간 잠깁니다.
    - account_status가 'ACTIVE'이고 use_yn이 'Y'인 계정만 로그인 가능합니다.
    """,
)
async def login(
    request: LoginRequest,
    req: Request,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """일반 로그인 (ID/Password)"""
    service = AuthService(db=db)

    # IP 주소 및 User Agent 추출
    ip_address = req.client.host if req.client else None
    user_agent = req.headers.get("user-agent")

    result = await service.execute(
        request,
        ip_address=ip_address,
        user_agent=user_agent
    )

    if not result.success:
        raise ApplicationException(message=result.error or "Login failed", status_code=401)

    return result.data


@router.post(
    "/google",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="구글 OAuth 로그인",
    description="""
    구글 ID 토큰으로 로그인합니다.

    **멀티 테넌시**: company_code (숫자)로 회사를 구분합니다.
    **인증 방식**: Google OAuth 2.0 (ID Token)
    **응답**: Access Token + Refresh Token + 사용자 정보 + 권한 목록

    **프로세스**:
    1. 구글 ID 토큰을 검증합니다.
    2. user_social_auth 테이블에서 기존 연동을 조회합니다.
    3. 연동이 있으면 → 해당 직원으로 로그인
    4. 연동이 없으면 → 이메일로 직원을 찾아 연동 생성
    5. JWT 토큰을 발급합니다.

    **주의사항**:
    - 구글에 등록된 이메일이 employees 테이블에 존재해야 합니다.
    - use_yn='Y', account_status='ACTIVE'인 계정만 로그인 가능합니다.
    - 처음 구글 로그인 시 자동으로 계정이 연동됩니다.
    """,
)
async def google_login(
    request: GoogleLoginRequest,
    req: Request,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """구글 OAuth 로그인"""
    service = GoogleOAuthService(db=db)

    # IP 주소 및 User Agent 추출
    ip_address = req.client.host if req.client else None
    user_agent = req.headers.get("user-agent")

    result = await service.execute(
        request, ip_address=ip_address, user_agent=user_agent
    )

    if not result.success:
        raise ApplicationException(
            message=result.error or "Google login failed", status_code=401
        )

    return result.data


class HashPasswordRequest(BaseModel):
        emp_id: int
        plain_password: str

@router.post("/hash-password")
async def hash_password_utility(
    request: HashPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db=db)
    success = await service.hash_user_password(
        request.emp_id, request.plain_password
    )


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Access Token 갱신",
    description="""
    Refresh Token으로 새로운 Access Token을 발급받습니다.

    **유효 기간**:
    - Access Token: 30분
    - Refresh Token: 7일

    **보안**:
    - Refresh Token은 DB에 해시값으로 저장됩니다.
    - 폐기된 토큰은 사용할 수 없습니다.
    """,
)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> RefreshTokenResponse:
    """Access Token 갱신"""
    service = AuthService(db=db)

    # Service에 refresh_access_token 메서드가 있어야 합니다
    # 현재 Phase 1에서는 구현되지 않았으므로 간단히 구현
    from server.app.domain.auth.providers import AuthProvider
    from server.app.domain.auth.schemas import AuthProviderInput
    from server.app.shared.utils.jwt import create_access_token, hash_token, verify_token

    try:
        # Refresh Token 검증
        payload = verify_token(request.refresh_token, token_type="refresh")

        # DB에서 Refresh Token 확인
        provider = AuthProvider(db)
        token_hash = hash_token(request.refresh_token)
        stored_token = await provider.get_refresh_token_by_hash(token_hash)

        if not stored_token:
            raise ApplicationException(message="Invalid or revoked refresh token", status_code=401)

        # 사용자 조회
        emp_id = payload["emp_id"]
        company_code = payload["company_code"]

        provider_input = AuthProviderInput(
            company_code=company_code,
            emp_id=emp_id
        )
        provider_output = await provider.provide(provider_input)
        user = provider_output.user

        if not user:
            raise ApplicationException(message="User not found", status_code=401)

        # 새로운 Access Token 생성
        access_token = create_access_token(data={
            "sub": str(user.emp_id),
            "company_code": user.company_code,
            "emp_id": user.emp_id,
            "duty_code_id": user.duty_code_id,
            "permissions": provider_output.permissions,
            "email": user.email,
            "name": user.name
        })

        response = RefreshTokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=30 * 60  # 30분 (초 단위)
        )

        return response

    except Exception as e:
        raise ApplicationException(message=f"Token refresh failed: {str(e)}", status_code=401)


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="로그아웃",
    description="""
    로그아웃하고 Refresh Token을 폐기합니다.

    **프로세스**:
    1. Refresh Token을 DB에서 폐기 처리
    2. 클라이언트는 Access Token과 Refresh Token을 삭제해야 합니다.

    **주의사항**:
    - Access Token은 서버에서 폐기할 수 없습니다 (Stateless JWT).
    - 클라이언트에서 토큰을 삭제하는 것이 중요합니다.
    """,
)
async def logout(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> LogoutResponse:
    """로그아웃"""
    from server.app.domain.auth.providers import AuthProvider
    from server.app.shared.utils.jwt import hash_token

    try:
        provider = AuthProvider(db)
        token_hash = hash_token(request.refresh_token)
        await provider.revoke_refresh_token(token_hash)

        response = LogoutResponse(
            message="Successfully logged out",
            success=True
        )

        return response

    except Exception as e:
        raise ApplicationException(message=f"Logout failed: {str(e)}", status_code=400)


@router.get(
    "/me",
    response_model=CurrentUserResponse,
    status_code=status.HTTP_200_OK,
    summary="현재 사용자 정보 조회",
    description="""
    인증된 사용자의 정보를 조회합니다.

    **응답**:
    - 사용자 기본 정보
    - 역할(Role) 목록
    - 권한(Permission) 목록
    - 메뉴 권한

    **인증 필요**: Bearer Token (Authorization 헤더)
    """,
)
async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db),
) -> CurrentUserResponse:
    """현재 사용자 정보 조회"""
    if not authorization or not authorization.startswith("Bearer "):
        raise ApplicationException(message="Unauthorized", status_code=401)

    from server.app.domain.auth.providers import AuthProvider
    from server.app.domain.auth.schemas import AuthProviderInput

    # JWT에서 사용자 정보 추출
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token, token_type="access")
    emp_id = payload["emp_id"]
    company_code = payload["company_code"]

    # 사용자 정보 조회
    provider = AuthProvider(db)
    provider_input = AuthProviderInput(emp_id=emp_id, company_code=company_code)
    provider_output = await provider.provide(provider_input)

    if not provider_output.user:
        raise ApplicationException(message="User not found", status_code=404)

    user = provider_output.user

    # UserInfo 생성
    user_info = UserInfo(
        emp_id=user.emp_id,
        company_code=user.company_code,
        email=user.email,
        name=user.name,
        emp_no=user.emp_no,
        dept_id=user.dept_id,
        duty_code_id=user.duty_code_id,
        pos_code_id=user.pos_code_id,
        phone=user.phone,
        last_login_at=user.last_login_at,
        use_yn=user.use_yn,
    )

    # 메뉴 권한 조회
    menus = await provider.get_user_menus(user.duty_code_id, user.company_code)

    # 역할 정보 생성 (간단하게)
    roles = [
        RoleInfo(
            role_code=perm,
            role_name=perm,
            permissions=[perm]
        )
        for perm in provider_output.permissions
    ]

    response = CurrentUserResponse(
        user=user_info,
        roles=roles,
        permissions=provider_output.permissions,
    )

    # 메뉴 정보 추가 (response에 menus 필드가 있다면)
    # response.menus = menus

    return response


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Auth 서비스 헬스 체크",
    description="Auth 도메인의 상태를 확인합니다.",
)
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "service": "auth",
        "version": "Phase 3",
        "features": {
            "login": "enabled",
            "google_oauth": "enabled",
            "refresh_token": "enabled",
            "logout": "enabled",
            "me": "enabled",
            "hash_password": "enabled (dev only)",
        }
    }
