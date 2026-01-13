"""
Auth API 엔드포인트 (Phase 1: 기본 로그인)

인증 관련 API를 제공합니다.
"""

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.core.dependencies import get_db
from server.app.domain.auth.schemas import LoginRequest, LoginResponse
from server.app.domain.auth.service import AuthService
from server.app.shared.exceptions import ApplicationException

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
        "features": {
            "login": "enabled",
            "oauth": "disabled (Phase 2)",
            "refresh_token": "enabled",
        }
    }
