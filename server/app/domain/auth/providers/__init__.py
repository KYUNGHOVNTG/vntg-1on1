"""
Auth 도메인 Provider

사용자 인증 데이터 조회를 담당합니다.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from server.app.domain.auth.models import (
    LoginHistory,
    RbacPermission,
    RbacRole,
    RbacRolePermission,
    RbacUserRole,
    RefreshToken,
    UserAccount,
    UserSocialAuth,
)
from server.app.domain.auth.schemas import AuthProviderInput, AuthProviderOutput
from server.app.shared.base.provider import BaseProvider
from server.app.shared.exceptions import NotFoundException


class AuthProvider(BaseProvider[AuthProviderInput, AuthProviderOutput]):
    """
    인증 데이터 조회 Provider

    사용자 계정, 권한, 소셜 인증 정보를 조회합니다.
    """

    def __init__(self, db: AsyncSession):
        super().__init__()
        self.db = db

    async def provide(self, input_data: AuthProviderInput) -> AuthProviderOutput:
        """
        인증 데이터를 조회합니다.

        Args:
            input_data: 조회 조건 (company_code + email 또는 emp_id)

        Returns:
            AuthProviderOutput: 사용자 정보, 권한, 소셜 인증 정보

        Raises:
            NotFoundException: 사용자를 찾을 수 없는 경우
        """
        user = None
        permissions = []
        social_auth = None

        # 사용자 조회
        if input_data.email:
            user = await self.get_user_by_email(
                company_code=input_data.company_code,
                email=input_data.email
            )
        elif input_data.emp_id:
            user = await self.get_user_by_id(
                emp_id=input_data.emp_id,
                company_code=input_data.company_code
            )

        # 사용자 권한 조회
        if user:
            permissions = await self.get_user_permissions(user.emp_id)

        # 소셜 인증 조회 (필요시)
        if input_data.google_id:
            social_auth = await self.get_social_auth(
                company_code=input_data.company_code,
                provider="GOOGLE",
                provider_id=input_data.google_id
            )

        return AuthProviderOutput(
            user=user,
            permissions=permissions,
            social_auth=social_auth
        )

    async def get_user_by_email(
        self,
        company_code: str,
        email: str
    ) -> Optional[UserAccount]:
        """
        이메일로 사용자를 조회합니다.

        Args:
            company_code: 회사 코드
            email: 이메일

        Returns:
            UserAccount | None: 사용자 정보
        """
        stmt = (
            select(UserAccount)
            .where(
                UserAccount.company_code == company_code,
                UserAccount.email == email,
                UserAccount.use_yn == "Y"
            )
            .options(
                joinedload(UserAccount.user_roles).joinedload(RbacUserRole.role)
            )
        )
        result = await self.db.execute(stmt)
        user = result.unique().scalar_one_or_none()
        return user

    async def get_user_by_id(
        self,
        emp_id: int,
        company_code: str
    ) -> Optional[UserAccount]:
        """
        직원 ID로 사용자를 조회합니다.

        Args:
            emp_id: 직원 ID
            company_code: 회사 코드

        Returns:
            UserAccount | None: 사용자 정보
        """
        stmt = (
            select(UserAccount)
            .where(
                UserAccount.emp_id == emp_id,
                UserAccount.company_code == company_code,
                UserAccount.use_yn == "Y"
            )
            .options(
                joinedload(UserAccount.user_roles).joinedload(RbacUserRole.role)
            )
        )
        result = await self.db.execute(stmt)
        user = result.unique().scalar_one_or_none()
        return user

    async def get_user_permissions(self, emp_id: int) -> list[str]:
        """
        사용자의 권한 목록을 조회합니다.

        Args:
            emp_id: 직원 ID

        Returns:
            list[str]: 권한 코드 목록 (예: ["user:read", "user:write"])
        """
        stmt = (
            select(RbacPermission.permission_code)
            .join(RbacRolePermission, RbacRolePermission.permission_id == RbacPermission.permission_id)
            .join(RbacRole, RbacRole.role_id == RbacRolePermission.role_id)
            .join(RbacUserRole, RbacUserRole.role_id == RbacRole.role_id)
            .where(
                RbacUserRole.emp_id == emp_id,
                RbacUserRole.use_yn == "Y",
                RbacRole.use_yn == "Y",
                RbacPermission.use_yn == "Y"
            )
            .distinct()
        )
        result = await self.db.execute(stmt)
        permissions = [row[0] for row in result.all()]
        return permissions

    async def get_social_auth(
        self,
        company_code: str,
        provider: str,
        provider_id: str
    ) -> Optional[UserSocialAuth]:
        """
        소셜 인증 정보를 조회합니다.

        Args:
            company_code: 회사 코드
            provider: 제공자 (GOOGLE, KAKAO 등)
            provider_id: 제공자 고유 ID

        Returns:
            UserSocialAuth | None: 소셜 인증 정보
        """
        stmt = (
            select(UserSocialAuth)
            .where(
                UserSocialAuth.company_code == company_code,
                UserSocialAuth.provider == provider,
                UserSocialAuth.provider_id == provider_id,
                UserSocialAuth.use_yn == "Y"
            )
            .options(joinedload(UserSocialAuth.user))
        )
        result = await self.db.execute(stmt)
        social_auth = result.unique().scalar_one_or_none()
        return social_auth

    async def update_last_login(self, emp_id: int) -> None:
        """
        마지막 로그인 시간을 업데이트합니다.

        Args:
            emp_id: 직원 ID
        """
        stmt = (
            select(UserAccount)
            .where(UserAccount.emp_id == emp_id)
        )
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            user.last_login_at = datetime.utcnow()
            user.failed_login_count = 0
            user.account_locked_until = None
            await self.db.commit()

    async def increment_failed_login(self, emp_id: int) -> int:
        """
        로그인 실패 횟수를 증가시킵니다.

        5회 실패 시 계정을 30분간 잠급니다.

        Args:
            emp_id: 직원 ID

        Returns:
            int: 실패 횟수
        """
        stmt = (
            select(UserAccount)
            .where(UserAccount.emp_id == emp_id)
        )
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            user.failed_login_count += 1

            # 5회 이상 실패 시 계정 잠금 (30분)
            if user.failed_login_count >= 5:
                from datetime import timedelta
                user.account_locked_until = datetime.utcnow() + timedelta(minutes=30)

            await self.db.commit()
            return user.failed_login_count

        return 0

    async def save_refresh_token(
        self,
        emp_id: int,
        company_code: str,
        token_hash: str,
        expires_at: datetime,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> RefreshToken:
        """
        Refresh Token을 저장합니다.

        Args:
            emp_id: 직원 ID
            company_code: 회사 코드
            token_hash: 토큰 해시값
            expires_at: 만료 시간
            device_info: 디바이스 정보
            ip_address: IP 주소
            user_agent: User Agent

        Returns:
            RefreshToken: 저장된 토큰 정보
        """
        refresh_token = RefreshToken(
            emp_id=emp_id,
            company_code=company_code,
            token_hash=token_hash,
            expires_at=expires_at,
            device_info=device_info,
            ip_address=ip_address,
            user_agent=user_agent,
            is_revoked=False
        )
        self.db.add(refresh_token)
        await self.db.commit()
        await self.db.refresh(refresh_token)
        return refresh_token

    async def get_refresh_token_by_hash(self, token_hash: str) -> Optional[RefreshToken]:
        """
        Refresh Token을 해시값으로 조회합니다.

        Args:
            token_hash: 토큰 해시값

        Returns:
            RefreshToken | None: 토큰 정보
        """
        stmt = (
            select(RefreshToken)
            .where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > datetime.utcnow()
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke_refresh_token(self, token_hash: str) -> None:
        """
        Refresh Token을 폐기합니다.

        Args:
            token_hash: 토큰 해시값
        """
        stmt = (
            select(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
        )
        result = await self.db.execute(stmt)
        token = result.scalar_one_or_none()

        if token:
            token.is_revoked = True
            token.revoked_at = datetime.utcnow()
            await self.db.commit()

    async def log_login_attempt(
        self,
        company_code: str,
        email: str,
        login_method: str,
        success: bool,
        emp_id: Optional[int] = None,
        failure_reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        device_info: Optional[str] = None
    ) -> None:
        """
        로그인 시도를 기록합니다.

        Args:
            company_code: 회사 코드
            email: 이메일
            login_method: 로그인 방법 (PASSWORD, GOOGLE 등)
            success: 성공 여부
            emp_id: 직원 ID (성공 시)
            failure_reason: 실패 사유
            ip_address: IP 주소
            user_agent: User Agent
            device_info: 디바이스 정보
        """
        history = LoginHistory(
            emp_id=emp_id,
            company_code=company_code,
            email=email,
            login_method=login_method,
            login_success=success,
            failure_reason=failure_reason,
            ip_address=ip_address,
            user_agent=user_agent,
            device_info=device_info
        )
        self.db.add(history)
        await self.db.commit()

    async def create_social_auth(
        self,
        emp_id: int,
        company_code: str,
        provider: str,
        provider_id: str,
        provider_email: str,
        profile_data: Optional[dict] = None
    ) -> UserSocialAuth:
        """
        소셜 인증 연동을 생성합니다.

        Args:
            emp_id: 직원 ID
            company_code: 회사 코드
            provider: 제공자 (GOOGLE, KAKAO 등)
            provider_id: 제공자 고유 ID
            provider_email: 제공자 이메일
            profile_data: 프로필 데이터 (JSON)

        Returns:
            UserSocialAuth: 소셜 인증 정보
        """
        social_auth = UserSocialAuth(
            emp_id=emp_id,
            company_code=company_code,
            provider=provider,
            provider_id=provider_id,
            provider_email=provider_email,
            profile_data=profile_data,
            use_yn="Y"
        )
        self.db.add(social_auth)
        await self.db.commit()
        await self.db.refresh(social_auth)
        return social_auth
