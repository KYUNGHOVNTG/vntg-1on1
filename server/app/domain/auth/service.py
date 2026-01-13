"""
Auth 도메인 Service

인증 비즈니스 로직을 처리합니다.
- 일반 로그인 (ID/Password)
- 구글 OAuth 2.0 로그인
- 토큰 갱신
- 비밀번호 변경
"""

from datetime import datetime
from typing import Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.core.config import settings
from server.app.domain.auth.formatters import AuthFormatter
from server.app.domain.auth.providers import AuthProvider
from server.app.domain.auth.schemas import (
    AuthFormatterInput,
    AuthProviderInput,
    ChangePasswordRequest,
    ChangePasswordResponse,
    GoogleLoginRequest,
    GoogleUserInfo,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
)
from server.app.shared.base.service import BaseService
from server.app.shared.exceptions import (
    BusinessLogicException,
    ExternalServiceException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)
from server.app.shared.types import ServiceResult
from server.app.shared.utils.jwt import (
    create_access_token,
    create_refresh_token,
    get_token_expiry,
    hash_token,
    verify_token,
)
from server.app.shared.utils.password import hash_password, verify_password


class AuthService(BaseService[LoginRequest, LoginResponse]):
    """
    인증 서비스

    사용자 로그인, 토큰 발급, 권한 검증을 담당합니다.
    """

    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.provider = AuthProvider(db)
        self.formatter = AuthFormatter()

    async def execute(self, request: LoginRequest, **kwargs) -> ServiceResult[LoginResponse]:
        """
        일반 로그인 (ID/Password)

        Args:
            request: 로그인 요청 (company_code, email, password)
            **kwargs: ip_address, user_agent 등 추가 컨텍스트

        Returns:
            ServiceResult[LoginResponse]: 로그인 응답 (토큰 + 사용자 정보)

        Raises:
            UnauthorizedException: 인증 실패
            BusinessLogicException: 계정 잠김 등
        """
        try:
            # 1. 사용자 조회
            provider_input = AuthProviderInput(
                company_code=request.company_code,
                email=request.email
            )
            provider_output = await self.provider.provide(provider_input)
            user = provider_output.user

            if not user:
                # 로그인 실패 기록
                await self.provider.log_login_attempt(
                    company_code=request.company_code,
                    email=request.email,
                    login_method="PASSWORD",
                    success=False,
                    failure_reason="User not found",
                    ip_address=kwargs.get("ip_address"),
                    user_agent=kwargs.get("user_agent"),
                    device_info=request.device_info
                )
                raise UnauthorizedException(
                    message="Invalid email or password",
                    details={"company_code": request.company_code, "email": request.email}
                )

            # 2. 계정 잠김 확인
            if user.account_locked_until and user.account_locked_until > datetime.utcnow():
                raise BusinessLogicException(
                    message="Account is locked due to multiple failed login attempts",
                    details={"locked_until": user.account_locked_until.isoformat()}
                )

            # 3. 비밀번호 검증
            if not user.password_hash:
                raise BusinessLogicException(
                    message="This account uses social login. Please use Google login.",
                    details={"provider": "GOOGLE"}
                )

            if not verify_password(request.password, user.password_hash):
                # 실패 횟수 증가
                await self.provider.increment_failed_login(user.emp_id)

                # 로그인 실패 기록
                await self.provider.log_login_attempt(
                    company_code=request.company_code,
                    email=request.email,
                    login_method="PASSWORD",
                    success=False,
                    emp_id=user.emp_id,
                    failure_reason="Invalid password",
                    ip_address=kwargs.get("ip_address"),
                    user_agent=kwargs.get("user_agent"),
                    device_info=request.device_info
                )

                raise UnauthorizedException(
                    message="Invalid email or password",
                    details={"company_code": request.company_code, "email": request.email}
                )

            # 4. 토큰 생성
            access_token = create_access_token(data={
                "sub": str(user.emp_id),
                "company_code": user.company_code,
                "emp_id": user.emp_id,
                "duty_code_id": user.duty_code_id,
                "permissions": provider_output.permissions,
                "email": user.email,
                "emp_name": user.emp_name
            })

            refresh_token = create_refresh_token(data={
                "sub": str(user.emp_id),
                "company_code": user.company_code,
                "emp_id": user.emp_id
            })

            # 5. Refresh Token 저장
            token_hash = hash_token(refresh_token)
            expires_at = get_token_expiry(refresh_token)
            await self.provider.save_refresh_token(
                emp_id=user.emp_id,
                company_code=user.company_code,
                token_hash=token_hash,
                expires_at=expires_at,
                device_info=request.device_info,
                ip_address=kwargs.get("ip_address"),
                user_agent=kwargs.get("user_agent")
            )

            # 6. 마지막 로그인 시간 업데이트
            await self.provider.update_last_login(user.emp_id)

            # 7. 로그인 성공 기록
            await self.provider.log_login_attempt(
                company_code=request.company_code,
                email=request.email,
                login_method="PASSWORD",
                success=True,
                emp_id=user.emp_id,
                ip_address=kwargs.get("ip_address"),
                user_agent=kwargs.get("user_agent"),
                device_info=request.device_info
            )

            # 8. 응답 포맷팅
            formatter_input = AuthFormatterInput(
                user=user,
                access_token=access_token,
                refresh_token=refresh_token,
                permissions=provider_output.permissions
            )
            response = await self.formatter.format(formatter_input)

            return ServiceResult.ok(response)

        except (UnauthorizedException, BusinessLogicException) as e:
            return ServiceResult.fail(e.message)
        except Exception as e:
            return ServiceResult.fail(f"Login failed: {str(e)}")

    async def google_login(
        self,
        request: GoogleLoginRequest,
        **kwargs
    ) -> ServiceResult[LoginResponse]:
        """
        구글 OAuth 2.0 로그인

        Args:
            request: 구글 로그인 요청 (google_token)
            **kwargs: ip_address, user_agent 등 추가 컨텍스트

        Returns:
            ServiceResult[LoginResponse]: 로그인 응답 (토큰 + 사용자 정보)

        Raises:
            UnauthorizedException: 구글 토큰 검증 실패
            NotFoundException: 직원 정보 없음
        """
        try:
            # 1. 구글 토큰 검증 및 사용자 정보 조회
            google_user_info = await self._verify_google_token(request.google_token)

            if not google_user_info:
                raise UnauthorizedException(
                    message="Invalid Google token",
                    details={"token": "verification_failed"}
                )

            # 2. 소셜 인증 정보 조회
            provider_input = AuthProviderInput(
                company_code=request.company_code,
                google_id=google_user_info.sub
            )
            provider_output = await self.provider.provide(provider_input)
            social_auth = provider_output.social_auth

            user = None

            # 3-1. 기존 소셜 인증이 있는 경우
            if social_auth:
                user = social_auth.user
            else:
                # 3-2. 최초 로그인: 이메일로 직원 정보 찾기
                provider_input = AuthProviderInput(
                    company_code=request.company_code,
                    email=google_user_info.email
                )
                provider_output = await self.provider.provide(provider_input)
                user = provider_output.user

                if not user:
                    # 직원 정보가 없으면 로그인 불가
                    await self.provider.log_login_attempt(
                        company_code=request.company_code,
                        email=google_user_info.email,
                        login_method="GOOGLE",
                        success=False,
                        failure_reason="Employee not found",
                        ip_address=kwargs.get("ip_address"),
                        user_agent=kwargs.get("user_agent"),
                        device_info=request.device_info
                    )
                    raise NotFoundException(
                        message=f"No employee found with email {google_user_info.email} in company {request.company_code}",
                        details={"email": google_user_info.email, "company_code": request.company_code}
                    )

                # 소셜 인증 연동 생성
                await self.provider.create_social_auth(
                    emp_id=user.emp_id,
                    company_code=request.company_code,
                    provider="GOOGLE",
                    provider_id=google_user_info.sub,
                    provider_email=google_user_info.email,
                    profile_data={
                        "name": google_user_info.name,
                        "given_name": google_user_info.given_name,
                        "family_name": google_user_info.family_name,
                        "picture": google_user_info.picture,
                        "locale": google_user_info.locale
                    }
                )

            # 4. 권한 조회
            permissions = await self.provider.get_user_permissions(user.emp_id)

            # 5. 토큰 생성
            access_token = create_access_token(data={
                "sub": str(user.emp_id),
                "company_code": user.company_code,
                "emp_id": user.emp_id,
                "duty_code_id": user.duty_code_id,
                "permissions": permissions,
                "email": user.email,
                "emp_name": user.emp_name
            })

            refresh_token = create_refresh_token(data={
                "sub": str(user.emp_id),
                "company_code": user.company_code,
                "emp_id": user.emp_id
            })

            # 6. Refresh Token 저장
            token_hash = hash_token(refresh_token)
            expires_at = get_token_expiry(refresh_token)
            await self.provider.save_refresh_token(
                emp_id=user.emp_id,
                company_code=user.company_code,
                token_hash=token_hash,
                expires_at=expires_at,
                device_info=request.device_info,
                ip_address=kwargs.get("ip_address"),
                user_agent=kwargs.get("user_agent")
            )

            # 7. 마지막 로그인 시간 업데이트
            await self.provider.update_last_login(user.emp_id)

            # 8. 로그인 성공 기록
            await self.provider.log_login_attempt(
                company_code=request.company_code,
                email=user.email,
                login_method="GOOGLE",
                success=True,
                emp_id=user.emp_id,
                ip_address=kwargs.get("ip_address"),
                user_agent=kwargs.get("user_agent"),
                device_info=request.device_info
            )

            # 9. 응답 포맷팅
            formatter_input = AuthFormatterInput(
                user=user,
                access_token=access_token,
                refresh_token=refresh_token,
                permissions=permissions
            )
            response = await self.formatter.format(formatter_input)

            return ServiceResult.ok(response)

        except (UnauthorizedException, NotFoundException, BusinessLogicException) as e:
            return ServiceResult.fail(e.message)
        except Exception as e:
            return ServiceResult.fail(f"Google login failed: {str(e)}")

    async def refresh_access_token(
        self,
        request: RefreshTokenRequest
    ) -> ServiceResult[RefreshTokenResponse]:
        """
        Refresh Token으로 Access Token 갱신

        Args:
            request: Refresh Token

        Returns:
            ServiceResult[RefreshTokenResponse]: 새로운 Access Token

        Raises:
            UnauthorizedException: Refresh Token 무효
        """
        try:
            # 1. Refresh Token 검증
            payload = verify_token(request.refresh_token, token_type="refresh")

            # 2. DB에서 Refresh Token 확인
            token_hash = hash_token(request.refresh_token)
            stored_token = await self.provider.get_refresh_token_by_hash(token_hash)

            if not stored_token:
                raise UnauthorizedException(
                    message="Invalid or revoked refresh token",
                    details={"token": "not_found"}
                )

            # 3. 사용자 조회
            emp_id = payload["emp_id"]
            company_code = payload["company_code"]

            provider_input = AuthProviderInput(
                company_code=company_code,
                emp_id=emp_id
            )
            provider_output = await self.provider.provide(provider_input)
            user = provider_output.user

            if not user:
                raise UnauthorizedException(
                    message="User not found",
                    details={"emp_id": emp_id}
                )

            # 4. 새로운 Access Token 생성
            access_token = create_access_token(data={
                "sub": str(user.emp_id),
                "company_code": user.company_code,
                "emp_id": user.emp_id,
                "duty_code_id": user.duty_code_id,
                "permissions": provider_output.permissions,
                "email": user.email,
                "emp_name": user.emp_name
            })

            response = RefreshTokenResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=30 * 60  # 30분 (초 단위)
            )

            return ServiceResult.ok(response)

        except UnauthorizedException as e:
            return ServiceResult.fail(e.message)
        except Exception as e:
            return ServiceResult.fail(f"Token refresh failed: {str(e)}")

    async def logout(
        self,
        request: Optional[str] = None
    ) -> ServiceResult[LogoutResponse]:
        """
        로그아웃 (Refresh Token 폐기)

        Args:
            request: Refresh Token (선택)

        Returns:
            ServiceResult[LogoutResponse]: 로그아웃 결과
        """
        try:
            if request:
                token_hash = hash_token(request)
                await self.provider.revoke_refresh_token(token_hash)

            response = LogoutResponse(
                message="Successfully logged out",
                success=True
            )

            return ServiceResult.ok(response)

        except Exception as e:
            return ServiceResult.fail(f"Logout failed: {str(e)}")

    async def change_password(
        self,
        request: ChangePasswordRequest,
        emp_id: int
    ) -> ServiceResult[ChangePasswordResponse]:
        """
        비밀번호 변경

        Args:
            request: 현재 비밀번호 + 새 비밀번호
            emp_id: 직원 ID (인증된 사용자)

        Returns:
            ServiceResult[ChangePasswordResponse]: 비밀번호 변경 결과

        Raises:
            UnauthorizedException: 현재 비밀번호 불일치
            ValidationException: 새 비밀번호 유효성 검증 실패
        """
        try:
            # 1. 사용자 조회
            provider_input = AuthProviderInput(emp_id=emp_id, company_code="")
            provider_output = await self.provider.provide(provider_input)
            user = provider_output.user

            if not user:
                raise NotFoundException(
                    message="User not found",
                    details={"emp_id": emp_id}
                )

            # 2. 현재 비밀번호 검증
            if not user.password_hash:
                raise BusinessLogicException(
                    message="This account uses social login. Password cannot be changed.",
                    details={"provider": "GOOGLE"}
                )

            if not verify_password(request.current_password, user.password_hash):
                raise UnauthorizedException(
                    message="Current password is incorrect",
                    details={"emp_id": emp_id}
                )

            # 3. 새 비밀번호 유효성 검증
            if len(request.new_password) < 8:
                raise ValidationException(
                    message="Password must be at least 8 characters long",
                    details={"min_length": 8}
                )

            # 4. 비밀번호 해시 및 업데이트
            user.password_hash = hash_password(request.new_password)
            user.password_changed_at = datetime.utcnow()
            await self.db.commit()

            response = ChangePasswordResponse(
                message="Password changed successfully",
                success=True
            )

            return ServiceResult.ok(response)

        except (UnauthorizedException, NotFoundException, ValidationException, BusinessLogicException) as e:
            return ServiceResult.fail(e.message)
        except Exception as e:
            return ServiceResult.fail(f"Password change failed: {str(e)}")

    async def _verify_google_token(self, google_token: str) -> Optional[GoogleUserInfo]:
        """
        구글 ID 토큰을 검증하고 사용자 정보를 반환합니다.

        Args:
            google_token: 구글 ID 토큰 (JWT)

        Returns:
            GoogleUserInfo | None: 구글 사용자 정보

        Raises:
            ExternalServiceException: 구글 API 호출 실패
        """
        try:
            # Google의 tokeninfo 엔드포인트를 사용하여 토큰 검증
            url = f"https://oauth2.googleapis.com/tokeninfo?id_token={google_token}"

            async with httpx.AsyncClient() as client:
                response = await client.get(url)

                if response.status_code != 200:
                    return None

                data = response.json()

                # 클라이언트 ID 검증 (설정된 경우)
                if settings.GOOGLE_CLIENT_ID:
                    if data.get("aud") != settings.GOOGLE_CLIENT_ID:
                        raise ExternalServiceException(
                            message="Invalid Google client ID",
                            details={"aud": data.get("aud")}
                        )

                # GoogleUserInfo로 변환
                user_info = GoogleUserInfo(
                    sub=data.get("sub"),
                    email=data.get("email"),
                    email_verified=data.get("email_verified", False),
                    name=data.get("name"),
                    given_name=data.get("given_name"),
                    family_name=data.get("family_name"),
                    picture=data.get("picture"),
                    locale=data.get("locale")
                )

                return user_info

        except httpx.HTTPError as e:
            raise ExternalServiceException(
                message=f"Failed to verify Google token: {str(e)}",
                details={"error": str(e)}
            )
