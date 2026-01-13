"""
Google OAuth 2.0 유틸리티

구글 ID 토큰 검증 및 사용자 정보 추출 기능을 제공합니다.
"""

import httpx
from typing import Optional

from server.app.domain.auth.schemas import GoogleUserInfo
from server.app.shared.exceptions import ApplicationException


async def verify_google_token(token: str) -> GoogleUserInfo:
    """
    구글 ID 토큰을 검증하고 사용자 정보를 반환합니다.

    Args:
        token: 구글 ID 토큰 (JWT)

    Returns:
        GoogleUserInfo: 구글 사용자 정보

    Raises:
        ApplicationException: 토큰이 유효하지 않은 경우

    Note:
        Google의 tokeninfo 엔드포인트를 사용하여 토큰을 검증합니다.
        프로덕션 환경에서는 google-auth 라이브러리 사용을 권장합니다.
    """
    try:
        # Google tokeninfo API를 사용하여 토큰 검증
        # https://oauth2.googleapis.com/tokeninfo?id_token={token}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://oauth2.googleapis.com/tokeninfo",
                params={"id_token": token},
                timeout=10.0
            )

            if response.status_code != 200:
                raise ApplicationException(
                    message="Invalid Google token",
                    status_code=401,
                    details={"error": response.text}
                )

            token_info = response.json()

            # 이메일 인증 여부 확인
            if not token_info.get("email_verified"):
                raise ApplicationException(
                    message="Email not verified",
                    status_code=400,
                    details={"email": token_info.get("email")}
                )

            # GoogleUserInfo 객체 생성
            user_info = GoogleUserInfo(
                sub=token_info["sub"],
                email=token_info["email"],
                email_verified=token_info.get("email_verified", False),
                name=token_info.get("name"),
                given_name=token_info.get("given_name"),
                family_name=token_info.get("family_name"),
                picture=token_info.get("picture"),
                locale=token_info.get("locale")
            )

            return user_info

    except httpx.TimeoutException:
        raise ApplicationException(
            message="Google token verification timeout",
            status_code=504,
            details={"error": "Request to Google API timed out"}
        )
    except httpx.HTTPError as e:
        raise ApplicationException(
            message="Failed to verify Google token",
            status_code=500,
            details={"error": str(e)}
        )
    except KeyError as e:
        raise ApplicationException(
            message="Invalid token response format",
            status_code=400,
            details={"missing_field": str(e)}
        )
    except Exception as e:
        raise ApplicationException(
            message=f"Google OAuth error: {str(e)}",
            status_code=500
        )


async def verify_google_token_with_google_auth(token: str, client_id: Optional[str] = None) -> GoogleUserInfo:
    """
    google-auth 라이브러리를 사용한 토큰 검증 (프로덕션 권장)

    Args:
        token: 구글 ID 토큰
        client_id: Google OAuth Client ID (선택)

    Returns:
        GoogleUserInfo: 구글 사용자 정보

    Note:
        이 함수를 사용하려면 `google-auth` 패키지가 필요합니다:
        pip install google-auth

        프로덕션 환경에서는 이 방식을 권장합니다.
    """
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests

        # 토큰 검증
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            client_id  # None이면 client_id 검증 스킵
        )

        # 이메일 인증 확인
        if not idinfo.get("email_verified"):
            raise ApplicationException(
                message="Email not verified",
                status_code=400
            )

        # GoogleUserInfo 객체 생성
        user_info = GoogleUserInfo(
            sub=idinfo["sub"],
            email=idinfo["email"],
            email_verified=idinfo.get("email_verified", False),
            name=idinfo.get("name"),
            given_name=idinfo.get("given_name"),
            family_name=idinfo.get("family_name"),
            picture=idinfo.get("picture"),
            locale=idinfo.get("locale")
        )

        return user_info

    except ImportError:
        raise ApplicationException(
            message="google-auth library not installed",
            status_code=500,
            details={"hint": "pip install google-auth"}
        )
    except ValueError as e:
        raise ApplicationException(
            message="Invalid Google token",
            status_code=401,
            details={"error": str(e)}
        )
    except Exception as e:
        raise ApplicationException(
            message=f"Google OAuth error: {str(e)}",
            status_code=500
        )
