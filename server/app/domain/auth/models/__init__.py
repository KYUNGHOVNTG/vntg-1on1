"""
Auth 도메인 SQLAlchemy 모델

멀티 테넌시(COMPANY_CODE)와 RBAC를 지원하는 인증 모델입니다.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    CHAR,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.app.core.database import Base


class Company(Base):
    """회사(테넌트) 정보"""

    __tablename__ = "company"

    company_code: Mapped[str] = mapped_column(String(20), primary_key=True)
    company_name: Mapped[str] = mapped_column(String(200), nullable=False)
    business_no: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    representative: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    established_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    use_yn: Mapped[str] = mapped_column(
        CHAR(1), default="Y", nullable=False, server_default="Y"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    created_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    users: Mapped[list["UserAccount"]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("use_yn IN ('Y', 'N')", name="ck_company_use_yn"),
        Index("idx_company_use_yn", "use_yn"),
    )


class UserAccount(Base):
    """사용자 계정 (직원 정보)"""

    __tablename__ = "user_account"

    emp_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_code: Mapped[str] = mapped_column(
        String(20), ForeignKey("company.company_code", ondelete="CASCADE"), nullable=False
    )
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    emp_no: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    emp_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    mobile: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    department_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    duty_code_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    position_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    join_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    resign_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    profile_image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    password_changed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    failed_login_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    account_locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    use_yn: Mapped[str] = mapped_column(
        CHAR(1), default="Y", nullable=False, server_default="Y"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    created_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    company: Mapped["Company"] = relationship(back_populates="users")
    social_auths: Mapped[list["UserSocialAuth"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    user_roles: Mapped[list["RbacUserRole"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("use_yn IN ('Y', 'N')", name="ck_user_use_yn"),
        Index("idx_user_company_email", "company_code", "email", unique=True),
        Index("idx_user_emp_no", "company_code", "emp_no"),
        Index("idx_user_use_yn", "use_yn"),
    )


class UserSocialAuth(Base):
    """소셜 로그인 연동 정보"""

    __tablename__ = "user_social_auth"

    social_auth_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    emp_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_account.emp_id", ondelete="CASCADE"), nullable=False
    )
    company_code: Mapped[str] = mapped_column(
        String(20), ForeignKey("company.company_code", ondelete="CASCADE"), nullable=False
    )
    provider: Mapped[str] = mapped_column(String(20), nullable=False)
    provider_id: Mapped[str] = mapped_column(String(255), nullable=False)
    provider_email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    access_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    profile_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    use_yn: Mapped[str] = mapped_column(
        CHAR(1), default="Y", nullable=False, server_default="Y"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user: Mapped["UserAccount"] = relationship(back_populates="social_auths")

    __table_args__ = (
        CheckConstraint(
            "provider IN ('GOOGLE', 'KAKAO', 'NAVER', 'MICROSOFT')",
            name="ck_social_auth_provider",
        ),
        CheckConstraint("use_yn IN ('Y', 'N')", name="ck_social_auth_use_yn"),
        Index("idx_social_auth_emp", "emp_id"),
        Index(
            "idx_social_auth_provider",
            "company_code",
            "provider",
            "provider_id",
            unique=True,
        ),
    )


class RbacRole(Base):
    """RBAC 역할 정의"""

    __tablename__ = "rbac_role"

    role_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_code: Mapped[str] = mapped_column(
        String(20), ForeignKey("company.company_code", ondelete="CASCADE"), nullable=False
    )
    role_code: Mapped[str] = mapped_column(String(50), nullable=False)
    role_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_system_role: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    use_yn: Mapped[str] = mapped_column(
        CHAR(1), default="Y", nullable=False, server_default="Y"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    created_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    role_permissions: Mapped[list["RbacRolePermission"]] = relationship(
        back_populates="role", cascade="all, delete-orphan"
    )
    user_roles: Mapped[list["RbacUserRole"]] = relationship(
        back_populates="role", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("use_yn IN ('Y', 'N')", name="ck_role_use_yn"),
        Index("idx_rbac_role_company", "company_code"),
        Index("idx_rbac_role_code", "company_code", "role_code", unique=True),
    )


class RbacPermission(Base):
    """RBAC 권한 정의"""

    __tablename__ = "rbac_permission"

    permission_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    permission_code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    permission_name: Mapped[str] = mapped_column(String(100), nullable=False)
    resource: Mapped[str] = mapped_column(String(50), nullable=False)
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_system_permission: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    use_yn: Mapped[str] = mapped_column(
        CHAR(1), default="Y", nullable=False, server_default="Y"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    role_permissions: Mapped[list["RbacRolePermission"]] = relationship(
        back_populates="permission", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("use_yn IN ('Y', 'N')", name="ck_permission_use_yn"),
        Index("idx_rbac_perm_code", "permission_code"),
        Index("idx_rbac_perm_resource", "resource", "action"),
    )


class RbacRolePermission(Base):
    """RBAC 역할-권한 매핑"""

    __tablename__ = "rbac_role_permission"

    role_permission_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("rbac_role.role_id", ondelete="CASCADE"), nullable=False
    )
    permission_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("rbac_permission.permission_id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    created_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    role: Mapped["RbacRole"] = relationship(back_populates="role_permissions")
    permission: Mapped["RbacPermission"] = relationship(back_populates="role_permissions")

    __table_args__ = (
        Index("idx_role_perm_role", "role_id"),
        Index("idx_role_perm_permission", "permission_id"),
        Index("idx_role_perm_unique", "role_id", "permission_id", unique=True),
    )


class RbacUserRole(Base):
    """RBAC 사용자-역할 매핑"""

    __tablename__ = "rbac_user_role"

    user_role_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    emp_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_account.emp_id", ondelete="CASCADE"), nullable=False
    )
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("rbac_role.role_id", ondelete="CASCADE"), nullable=False
    )
    granted_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    granted_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    revoked_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    use_yn: Mapped[str] = mapped_column(
        CHAR(1), default="Y", nullable=False, server_default="Y"
    )

    # Relationships
    user: Mapped["UserAccount"] = relationship(back_populates="user_roles")
    role: Mapped["RbacRole"] = relationship(back_populates="user_roles")

    __table_args__ = (
        CheckConstraint("use_yn IN ('Y', 'N')", name="ck_user_role_use_yn"),
        Index("idx_user_role_emp", "emp_id"),
        Index("idx_user_role_role", "role_id"),
        Index("idx_user_role_unique", "emp_id", "role_id", unique=True),
    )


class RefreshToken(Base):
    """Refresh Token 저장소"""

    __tablename__ = "refresh_token"

    token_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    emp_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_account.emp_id", ondelete="CASCADE"), nullable=False
    )
    company_code: Mapped[str] = mapped_column(
        String(20), ForeignKey("company.company_code", ondelete="CASCADE"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    device_info: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    user: Mapped["UserAccount"] = relationship(back_populates="refresh_tokens")

    __table_args__ = (
        Index("idx_refresh_token_emp", "emp_id"),
        Index("idx_refresh_token_hash", "token_hash"),
        Index("idx_refresh_token_expires", "expires_at"),
        Index("idx_refresh_token_revoked", "is_revoked"),
    )


class LoginHistory(Base):
    """로그인 이력 (감사 로그)"""

    __tablename__ = "login_history"

    history_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    emp_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("user_account.emp_id", ondelete="SET NULL"), nullable=True
    )
    company_code: Mapped[Optional[str]] = mapped_column(
        String(20), ForeignKey("company.company_code", ondelete="SET NULL"), nullable=True
    )
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    login_method: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    login_success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    failure_reason: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    device_info: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "login_method IN ('PASSWORD', 'GOOGLE', 'KAKAO', 'NAVER', 'MICROSOFT')",
            name="ck_login_method",
        ),
        Index("idx_login_history_emp", "emp_id"),
        Index("idx_login_history_email", "company_code", "email"),
        Index("idx_login_history_created", "created_at"),
        Index("idx_login_history_success", "login_success"),
    )
