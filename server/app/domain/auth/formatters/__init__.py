"""
Auth 도메인 Formatter

인증 응답 데이터를 포맷팅합니다.
"""

from server.app.domain.auth.schemas import (
    AuthFormatterInput,
    LoginResponse,
    UserInfo,
)
from server.app.shared.base.formatter import BaseFormatter
from server.app.shared.utils.jwt import ACCESS_TOKEN_EXPIRE_MINUTES


class AuthFormatter(BaseFormatter[AuthFormatterInput, LoginResponse]):
    """
    인증 응답 Formatter

    로그인 성공 시 응답 데이터를 포맷팅합니다.
    """

    async def format(self, input_data: AuthFormatterInput) -> LoginResponse:
        """
        로그인 응답 데이터를 포맷팅합니다.

        Args:
            input_data: 사용자 정보, 토큰, 권한

        Returns:
            LoginResponse: 포맷팅된 로그인 응답
        """
        user = input_data.user

        # UserInfo 생성
        user_info = UserInfo(
            emp_id=user.emp_id,
            company_code=user.company_code,
            email=user.email,
            emp_name=user.emp_name,
            emp_no=user.emp_no,
            department_code=user.department_code,
            duty_code_id=user.duty_code_id,
            position_name=user.position_name,
            phone=user.phone,
            mobile=user.mobile,
            profile_image_url=user.profile_image_url,
            join_date=user.join_date,
            last_login_at=user.last_login_at,
            use_yn=user.use_yn
        )

        # LoginResponse 생성
        response = LoginResponse(
            access_token=input_data.access_token,
            refresh_token=input_data.refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # 초 단위로 변환
            user=user_info,
            permissions=input_data.permissions
        )

        return response
