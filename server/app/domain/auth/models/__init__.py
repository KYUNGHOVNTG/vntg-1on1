"""
Auth 도메인 SQLAlchemy 모델 (기존 DB 구조 기반)

기존에 생성된 테이블 구조에 맞춰 작성되었습니다:
- companies (회사)
- employees (직원)
- role_groups (역할 그룹)
- duty_role_mapping (직급-역할 매핑)
- user_social_auth (소셜 로그인)
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
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.app.core.database import Base


class Company(Base):
    """회사 정보 (기존 companies 테이블)"""

    __tablename__ = "companies"

    company_code: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    domain: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    use_yn: Mapped[str] = mapped_column(CHAR(1), default="Y", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    employees: Mapped[list["Employee"]] = relationship(
        back_populates="company"
    )


class Employee(Base):
    """직원 정보 (기존 employees 테이블)"""

    __tablename__ = "employees"

    emp_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_code: Mapped[int] = mapped_column(
        Integer, ForeignKey("companies.company_code"), nullable=False
    )
    emp_no: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    hire_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    dept_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pos_code_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duty_code_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    user_category: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    account_status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    use_yn: Mapped[str] = mapped_column(CHAR(1), default="Y", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    login_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    password: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # 추가 필드 (인증 관련)
    failed_login_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False, server_default="0")
    account_locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    password_changed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    company: Mapped["Company"] = relationship(
        back_populates="employees"
    )
    social_auths: Mapped[list["UserSocialAuth"]] = relationship(
        back_populates="employee", cascade="all, delete-orphan"
    )
    duty_role_mappings: Mapped[list["DutyRoleMapping"]] = relationship(
        back_populates="employee",
        primaryjoin="and_(Employee.duty_code_id==DutyRoleMapping.duty_code_id, Employee.company_code==DutyRoleMapping.company_code)",
        foreign_keys="[DutyRoleMapping.duty_code_id, DutyRoleMapping.company_code]",
        viewonly=True
    )


class RoleGroup(Base):
    """역할 그룹 (기존 role_groups 테이블)"""

    __tablename__ = "role_groups"

    role_group_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_code: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("companies.company_code"), nullable=True
    )
    role_group_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    use_yn: Mapped[str] = mapped_column(CHAR(1), default="Y", nullable=False)

    # Relationships
    duty_role_mappings: Mapped[list["DutyRoleMapping"]] = relationship(
        back_populates="role_group"
    )
    role_menu_maps: Mapped[list["RoleMenuMap"]] = relationship(
        back_populates="role_group"
    )


class DutyRoleMapping(Base):
    """직급-역할 매핑 (기존 duty_role_mapping 테이블)"""

    __tablename__ = "duty_role_mapping"

    mapping_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duty_code_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    role_group_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("role_groups.role_group_id"), nullable=True
    )
    use_yn: Mapped[str] = mapped_column(CHAR(1), default="Y", nullable=False)

    # Relationships
    role_group: Mapped["RoleGroup"] = relationship(back_populates="duty_role_mappings")
    employee: Mapped["Employee"] = relationship(
        viewonly=True,
        foreign_keys=[duty_code_id, company_code],
        primaryjoin="and_(DutyRoleMapping.duty_code_id==Employee.duty_code_id, DutyRoleMapping.company_code==Employee.company_code)"
    )


class Menu(Base):
    """메뉴 (기존 menus 테이블)"""

    __tablename__ = "menus"

    menu_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    menu_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    menu_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    parent_menu_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    menu_order: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    use_yn: Mapped[str] = mapped_column(CHAR(1), default="Y", nullable=False)

    # Relationships
    role_menu_maps: Mapped[list["RoleMenuMap"]] = relationship(back_populates="menu")


class RoleMenuMap(Base):
    """역할-메뉴 매핑 (기존 role_menu_map 테이블)"""

    __tablename__ = "role_menu_map"

    map_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role_group_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("role_groups.role_group_id"), nullable=True
    )
    menu_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("menus.menu_id"), nullable=True
    )
    use_yn: Mapped[str] = mapped_column(CHAR(1), default="Y", nullable=False)

    # Relationships
    role_group: Mapped["RoleGroup"] = relationship(back_populates="role_menu_maps")
    menu: Mapped["Menu"] = relationship(back_populates="role_menu_maps")


class UserSocialAuth(Base):
    """소셜 로그인 연동 (기존 user_social_auth 테이블)"""

    __tablename__ = "user_social_auth"

    social_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    emp_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("employees.emp_id"), nullable=True
    )
    provider: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    provider_user_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    use_yn: Mapped[str] = mapped_column(CHAR(1), default="Y", nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    employee: Mapped["Employee"] = relationship(back_populates="social_auths")


class RefreshToken(Base):
    """Refresh Token 저장소 (신규 테이블 - 필요시 생성)"""

    __tablename__ = "refresh_tokens"

    token_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    emp_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("employees.emp_id"), nullable=False
    )
    company_code: Mapped[int] = mapped_column(Integer, nullable=False)
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

    __table_args__ = (
        Index("idx_refresh_token_emp", "emp_id"),
        Index("idx_refresh_token_hash", "token_hash"),
        Index("idx_refresh_token_expires", "expires_at"),
        Index("idx_refresh_token_revoked", "is_revoked"),
    )


class LoginHistory(Base):
    """로그인 이력 (신규 테이블 - 필요시 생성)"""

    __tablename__ = "login_history"

    history_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    emp_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    company_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
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
        Index("idx_login_history_emp", "emp_id"),
        Index("idx_login_history_email", "company_code", "email"),
        Index("idx_login_history_created", "created_at"),
        Index("idx_login_history_success", "login_success"),
    )
