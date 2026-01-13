"""
Auth 도메인 Service (Phase 1: 기본 로그인)

일반 로그인 (ID/PW) 기능만 구현합니다.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from server.app.domain.auth.formatters import AuthFormatter
from server.app.domain.auth.providers import AuthProvider
from server.app.domain.auth.schemas import (
    AuthFormatterInput,
    AuthProviderInput,
    LoginRequest,
    LoginResponse,
)
from server.app.shared.base.service import BaseService
from server.app.shared.exceptions import (
    BusinessLogicException,
    UnauthorizedException,
)
from server.app.shared.types import ServiceResult
from server.app.shared.utils.jwt import (
    create_access_token,
    create_refresh_token,
    get_token_expiry,
    hash_token,
)
from server.app.shared.utils.password import hash_password, verify_password


class AuthService(BaseService[LoginRequest, LoginResponse]):
    """
    인증 서비스 (Phase 1)

    일반 로그인 (ID/Password)만 지원합니다.
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
            if not user.password:
                raise BusinessLogicException(
                    message="Password not set for this account",
                    details={"emp_id": user.emp_id}
                )

            # ⚠️ Phase 1: 평문 비교 (개발 단계)
            # TODO Phase 2: BCRYPT 해싱 추가
            password_valid = False

            # 먼저 BCRYPT 검증 시도
            if user.password.startswith("$2b$") or user.password.startswith("$2a$"):
                # BCRYPT 해시인 경우
                password_valid = verify_password(request.password, user.password)
            else:
                # 평문인 경우 (개발 환경)
                password_valid = (request.password == user.password)

            if not password_valid:
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
                "name": user.name
            })

            refresh_token = create_refresh_token(data={
                "sub": str(user.emp_id),
                "company_code": user.company_code,
                "emp_id": user.emp_id
            })

            # 5. Refresh Token 저장
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

    async def hash_user_password(self, emp_id: int, plain_password: str) -> bool:
        """
        사용자의 평문 비밀번호를 BCRYPT로 해싱합니다.

        Phase 2에서 사용할 유틸리티 함수입니다.

        Args:
            emp_id: 직원 ID
            plain_password: 평문 비밀번호

        Returns:
            bool: 성공 여부
        """
        try:
            provider_input = AuthProviderInput(emp_id=emp_id, company_code=0)
            provider_output = await self.provider.provide(provider_input)
            user = provider_output.user

            if not user:
                return False

            # 평문 비밀번호를 BCRYPT로 해싱
            hashed_password = hash_password(plain_password)
            user.password = hashed_password
            user.password_changed_at = datetime.utcnow()

            await self.db.commit()
            return True

        except Exception:
            return False
