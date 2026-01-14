"""
JWT 토큰 생성 및 검증 유틸리티

멀티 테넌시(COMPANY_CODE)와 RBAC 권한 정보를 포함하는 JWT 토큰을 생성하고 검증합니다.
"""

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt

from server.app.core.config import settings
from server.app.shared.exceptions import UnauthorizedException


def create_access_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Access Token을 생성합니다.

    JWT Payload에 포함되는 정보:
        - sub: 사용자 ID (EMP_ID)
        - company_code: 회사 코드 (멀티 테넌시)
        - emp_id: 직원 ID
        - duty_code_id: 직급 ID
        - permissions: 권한 목록 (list[str])
        - email: 이메일
        - emp_name: 직원 이름
        - exp: 만료 시간
        - iat: 발급 시간

    Args:
        data: 토큰에 포함할 데이터
        expires_delta: 만료 시간 (기본값: 30분)

    Returns:
        str: JWT Access Token

    Example:
        >>> token = create_access_token({
        ...     "sub": "1",
        ...     "company_code": "VNTG",
        ...     "emp_id": 1,
        ...     "duty_code_id": 1,
        ...     "permissions": ["user:read", "user:write"],
        ...     "email": "admin@vantage.com",
        ...     "emp_name": "관리자"
        ... })
    """
    to_encode = data.copy()

    # 만료 시간 설정
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    })

    # JWT 토큰 생성
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Refresh Token을 생성합니다.

    JWT Payload에 포함되는 정보:
        - sub: 사용자 ID (EMP_ID)
        - company_code: 회사 코드
        - emp_id: 직원 ID
        - exp: 만료 시간
        - iat: 발급 시간

    Args:
        data: 토큰에 포함할 데이터
        expires_delta: 만료 시간 (기본값: 7일)

    Returns:
        str: JWT Refresh Token

    Example:
        >>> token = create_refresh_token({
        ...     "sub": "1",
        ...     "company_code": "VNTG",
        ...     "emp_id": 1
        ... })
    """
    to_encode = data.copy()

    # 만료 시간 설정
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh"
    })

    # JWT 토큰 생성
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> dict[str, Any]:
    """
    JWT 토큰을 검증하고 페이로드를 반환합니다.

    Args:
        token: JWT 토큰 문자열
        token_type: 토큰 타입 ("access" 또는 "refresh")

    Returns:
        dict: 디코딩된 페이로드

    Raises:
        UnauthorizedException: 토큰이 유효하지 않거나 만료된 경우

    Example:
        >>> payload = verify_token(token, "access")
        >>> print(payload["company_code"])
        VNTG
    """
    try:
        # JWT 디코딩
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

        # 토큰 타입 확인
        if payload.get("type") != token_type:
            raise UnauthorizedException(
                message=f"Invalid token type. Expected '{token_type}', got '{payload.get('type')}'",
                details={"expected": token_type, "actual": payload.get("type")}
            )

        # 필수 필드 확인
        if token_type == "access":
            required_fields = ["sub", "company_code", "emp_id"]
        else:  # refresh
            required_fields = ["sub", "company_code", "emp_id"]

        for field in required_fields:
            if field not in payload:
                raise UnauthorizedException(
                    message=f"Missing required field: {field}",
                    details={"field": field}
                )

        return payload

    except JWTError as e:
        raise UnauthorizedException(
            message="Invalid or expired token",
            details={"error": str(e)}
        )


def decode_token_without_verification(token: str) -> Optional[dict[str, Any]]:
    """
    토큰을 검증하지 않고 디코딩합니다. (디버깅 용도)

    주의: 실제 인증에는 사용하지 마세요!

    Args:
        token: JWT 토큰 문자열

    Returns:
        dict | None: 디코딩된 페이로드 (실패 시 None)

    Example:
        >>> payload = decode_token_without_verification(token)
        >>> print(payload)
    """
    try:
        return jwt.decode(token, options={"verify_signature": False})
    except JWTError:
        return None


def hash_token(token: str) -> str:
    """
    토큰을 SHA-256으로 해시합니다.

    Refresh Token을 데이터베이스에 저장할 때 사용합니다.

    Args:
        token: JWT 토큰 문자열

    Returns:
        str: SHA-256 해시 문자열 (hex)

    Example:
        >>> token_hash = hash_token(refresh_token)
        >>> # DB에 저장: INSERT INTO REFRESH_TOKEN (TOKEN_HASH) VALUES (token_hash)
    """
    return hashlib.sha256(token.encode()).hexdigest()


def get_token_expiry(token: str) -> Optional[datetime]:
    """
    토큰의 만료 시간을 반환합니다.

    Args:
        token: JWT 토큰 문자열

    Returns:
        datetime | None: 만료 시간 (UTC, 실패 시 None)

    Example:
        >>> expiry = get_token_expiry(token)
        >>> print(f"Token expires at: {expiry}")
    """
    payload = decode_token_without_verification(token)
    if payload and "exp" in payload:
        return datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    return None
