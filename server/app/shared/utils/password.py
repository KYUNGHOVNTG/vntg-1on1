"""
비밀번호 암호화 및 검증 유틸리티

BCRYPT를 사용하여 비밀번호를 안전하게 해싱하고 검증합니다.
"""

from passlib.context import CryptContext

# BCRYPT 컨텍스트 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    비밀번호를 BCRYPT로 해싱합니다.

    Args:
        password: 평문 비밀번호

    Returns:
        str: BCRYPT 해시 문자열

    Example:
        >>> hashed = hash_password("mypassword123")
        >>> print(hashed)
        $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYC5OwHbaHm
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    평문 비밀번호와 해시값을 비교하여 일치 여부를 확인합니다.

    Args:
        plain_password: 평문 비밀번호
        hashed_password: BCRYPT 해시 문자열

    Returns:
        bool: 비밀번호 일치 여부 (True/False)

    Example:
        >>> hashed = hash_password("mypassword123")
        >>> verify_password("mypassword123", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)


def needs_update(hashed_password: str) -> bool:
    """
    해시 알고리즘 업데이트가 필요한지 확인합니다.

    Args:
        hashed_password: BCRYPT 해시 문자열

    Returns:
        bool: 업데이트 필요 여부

    Example:
        >>> hashed = hash_password("mypassword123")
        >>> needs_update(hashed)
        False
    """
    return pwd_context.needs_update(hashed_password)
