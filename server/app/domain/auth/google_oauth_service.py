"""
Google OAuth Service (Phase 3)

구글 OAuth 로그인 기능을 제공합니다.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from server.app.domain.auth.formatters import AuthFormatter
from server.app.domain.auth.providers import AuthProvider
from server.app.domain.auth.schemas import (
    AuthFormatterInput,
    AuthProviderInput,
    GoogleLoginRequest,
    LoginResponse,
)
from server.app.shared.base.service import BaseService
from server.app.shared.exceptions import (
    ApplicationException,
    BusinessLogicException,
    UnauthorizedException,
)
from server.app.shared.types import ServiceResult
from server.app.shared.utils.google_oauth import verify_google_token
from server.app.shared.utils.jwt import (
    create_access_token,
    create_refresh_token,
    get_token_expiry,
    hash_token,
)


class GoogleOAuthService(BaseService[GoogleLoginRequest, LoginResponse]):
    """
    Google OAuth 로그인 서비스

    구글 ID 토큰을 검증하고 사용자를 인증합니다.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.provider = AuthProvider(db)
        self.formatter = AuthFormatter()

    async def execute(
        self, request: GoogleLoginRequest, **kwargs
    ) -> ServiceResult[LoginResponse]:
        """
        Google OAuth 로그인

        Args:
            request: 구글 로그인 요청 (company_code, google_token)
            **kwargs: ip_address, user_agent 등 추가 컨텍스트

        Returns:
            ServiceResult[LoginResponse]: 로그인 응답 (토큰 + 사용자 정보)

        Raises:
            UnauthorizedException: 인증 실패
            BusinessLogicException: 사용자 없음 등

        프로세스:
        1. 구글 토큰 검증 → 구글 사용자 정보 추출
        2. user_social_auth 테이블에서 연동 정보 조회
        3. 연동 정보 있음 → 기존 사용자 로그인
        4. 연동 정보 없음 → 이메일로 사용자 조회 → 연동 생성
        5. JWT 토큰 생성 및 반환
        """
        try:
            # 1. 구글 토큰 검증
            try:
                google_user = await verify_google_token(request.google_token)
            except ApplicationException as e:
                # 로그인 실패 기록
                await self.provider.log_login_attempt(
                    company_code=request.company_code,
                    email="unknown",
                    login_method="GOOGLE",
                    success=False,
                    failure_reason=f"Invalid Google token: {e.message}",
                    ip_address=kwargs.get("ip_address"),
                    user_agent=kwargs.get("user_agent"),
                    device_info=request.device_info,
                )
                raise UnauthorizedException(
                    message="Invalid Google token",
                    details={"error": e.message},
                )

            # 2. user_social_auth 테이블에서 기존 연동 조회
            provider_input = AuthProviderInput(
                company_code=request.company_code, google_id=google_user.sub
            )
            provider_output = await self.provider.provide(provider_input)
            social_auth = provider_output.social_auth

            user = None

            if social_auth:
                # 3. 기존 연동이 있는 경우 → 연결된 사용자 조회
                user_input = AuthProviderInput(
                    company_code=request.company_code, emp_id=social_auth.emp_id
                )
                user_output = await self.provider.provide(user_input)
                user = user_output.user
                permissions = user_output.permissions
            else:
                # 4. 기존 연동이 없는 경우 → 이메일로 사용자 찾기
                email_input = AuthProviderInput(
                    company_code=request.company_code, email=google_user.email
                )
                email_output = await self.provider.provide(email_input)
                user = email_output.user
                permissions = email_output.permissions

                if not user:
                    # 사용자를 찾을 수 없음
                    await self.provider.log_login_attempt(
                        company_code=request.company_code,
                        email=google_user.email,
                        login_method="GOOGLE",
                        success=False,
                        failure_reason="User not found with this email",
                        ip_address=kwargs.get("ip_address"),
                        user_agent=kwargs.get("user_agent"),
                        device_info=request.device_info,
                    )
                    raise BusinessLogicException(
                        message=f"No employee found with email {google_user.email} in company {request.company_code}",
                        details={
                            "company_code": request.company_code,
                            "email": google_user.email,
                            "hint": "Please contact your administrator to register this email",
                        },
                    )

                # 5. 구글 계정과 직원 연동 생성
                await self.provider.create_social_auth(
                    emp_id=user.emp_id,
                    provider="GOOGLE",
                    provider_user_id=google_user.sub,
                    profile_data={
                        "email": google_user.email,
                        "name": google_user.name,
                        "picture": google_user.picture,
                    },
                )

            # 6. 계정 상태 확인
            if not user:
                raise UnauthorizedException(
                    message="User not found or inactive",
                    details={"company_code": request.company_code},
                )

            # 7. 계정 잠김 확인
            if user.account_locked_until and user.account_locked_until > datetime.utcnow():
                raise BusinessLogicException(
                    message="Account is locked due to multiple failed login attempts",
                    details={"locked_until": user.account_locked_until.isoformat()},
                )

            # 8. JWT 토큰 생성
            access_token = create_access_token(
                data={
                    "sub": str(user.emp_id),
                    "company_code": user.company_code,
                    "emp_id": user.emp_id,
                    "duty_code_id": user.duty_code_id,
                    "permissions": permissions,
                    "email": user.email,
                    "name": user.name,
                }
            )

            refresh_token = create_refresh_token(
                data={
                    "sub": str(user.emp_id),
                    "company_code": user.company_code,
                    "emp_id": user.emp_id,
                }
            )

            # 9. Refresh Token 저장
            token_hash = hash_token(refresh_token)
            expires_at = get_token_expiry(refresh_token)

            if expires_at:
                await self.provider.save_refresh_token(
                    emp_id=user.emp_id,
                    company_code=user.company_code,
                    token_hash=token_hash,
                    expires_at=expires_at,
                    device_info=request.device_info,
                    ip_address=kwargs.get("ip_address"),
                    user_agent=kwargs.get("user_agent"),
                )

            # 10. 마지막 로그인 시간 업데이트
            await self.provider.update_last_login(user.emp_id)

            # 11. 로그인 성공 기록
            await self.provider.log_login_attempt(
                company_code=request.company_code,
                email=user.email,
                login_method="GOOGLE",
                success=True,
                emp_id=user.emp_id,
                ip_address=kwargs.get("ip_address"),
                user_agent=kwargs.get("user_agent"),
                device_info=request.device_info,
            )

            # 12. 응답 포맷팅
            formatter_input = AuthFormatterInput(
                user=user,
                access_token=access_token,
                refresh_token=refresh_token,
                permissions=permissions,
            )
            response = await self.formatter.format(formatter_input)

            return ServiceResult.ok(response)

        except (UnauthorizedException, BusinessLogicException) as e:
            return ServiceResult.fail(e.message)
        except Exception as e:
            return ServiceResult.fail(f"Google OAuth login failed: {str(e)}")
