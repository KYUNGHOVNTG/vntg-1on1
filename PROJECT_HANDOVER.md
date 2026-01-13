# 프로젝트 인수인계 문서 (Project Handover)

> 이 문서는 AI 어시스턴트가 이 프로젝트를 이해하고 새로운 기능을 개발할 수 있도록 작성된 인수인계 문서입니다.

**작성일**: 2026-01-13
**대상**: Gemini, GPT, Claude 등 AI 개발 어시스턴트
**목적**: 프로젝트 컨텍스트 제공 및 신규 기능 개발 가이드

---

## 📋 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [기술 스택](#2-기술-스택)
3. [아키텍처 핵심](#3-아키텍처-핵심)
4. [프로젝트 구조](#4-프로젝트-구조)
5. [핵심 개념](#5-핵심-개념)
6. [개발 워크플로우](#6-개발-워크플로우)
7. [새 도메인 추가 방법](#7-새-도메인-추가-방법)
8. [코드 예시](#8-코드-예시)
9. [환경 설정](#9-환경-설정)
10. [테스트 & 배포](#10-테스트--배포)
11. [주의사항](#11-주의사항)
12. [문제 해결](#12-문제-해결)

---

## 1. 프로젝트 개요

### 1.1 프로젝트 정보
- **이름**: AI 데이터 분석 웹 서비스 템플릿 (vntg-1on1)
- **목적**: 확장 가능하고 유지보수하기 쉬운 엔터프라이즈급 풀스택 웹 애플리케이션 템플릿
- **핵심 가치**: **"유지보수성 최우선" 및 "모듈화"**

### 1.2 주요 특징
- **도메인 플러그인 구조**: 새로운 비즈니스 도메인을 독립적으로 추가 가능
- **계층화된 아키텍처**: Router → Service → Provider/Calculator → Formatter
- **타입 안전성**: Pydantic v2 + SQLAlchemy 2.0 + TypeScript
- **비동기 최적화**: async/await 기반 고성능
- **운영 준비 완료**: Request ID 로깅, Health Check, 전역 에러/로딩 처리

### 1.3 현재 구현 상태
- ✅ 백엔드 인프라 완료 (FastAPI, SQLAlchemy 2.0, Pydantic v2)
- ✅ 프론트엔드 인프라 완료 (React 19, Zustand, Tailwind 4)
- ✅ 인증 도메인 (auth) 구현 완료 (Google OAuth 2.0, RBAC)
- ✅ 샘플 도메인 (examples/sample_domain) 참고용 구현 완료
- 🔄 프론트엔드 UI 컴포넌트 일부 미완성 (Button, Card, Input 등 TODO 항목 존재)

---

## 2. 기술 스택

### 2.1 백엔드 (Python 3.12)
| 기술 | 버전 | 용도 |
|------|------|------|
| FastAPI | 0.109.0 | 고성능 비동기 REST API 프레임워크 |
| SQLAlchemy | 2.0.25 (async) | ORM, 비동기 DB 접근 |
| asyncpg | 0.29.0 | PostgreSQL 비동기 드라이버 |
| Pydantic | v2.5.3 | 런타임 데이터 검증, 스키마 정의 |
| python-jose | 3.3.0 | JWT 토큰 인증 |
| passlib | 1.7.4 | 비밀번호 해싱 |
| Alembic | 1.13.1 | 데이터베이스 마이그레이션 |
| pytest | 7.4.4 | 테스트 프레임워크 |

### 2.2 프론트엔드 (TypeScript 5.9)
| 기술 | 버전 | 용도 |
|------|------|------|
| React | 19.2.0 | UI 프레임워크 |
| Vite | 7.2.4 | 빌드 도구 (빠른 HMR) |
| TypeScript | 5.9.3 | 타입 안전성 |
| Tailwind CSS | 4.1.18 | 유틸리티 우선 CSS |
| Zustand | 5.0.9 | 경량 상태 관리 |
| Axios | 1.13.2 | HTTP 클라이언트 |
| React Router DOM | 7.12.0 | SPA 라우팅 |
| Framer Motion | 12.25.0 | 애니메이션 |
| Lucide React | 0.562.0 | 아이콘 시스템 |

### 2.3 데이터베이스 & 인프라
- **Database**: PostgreSQL (asyncpg 사용)
- **Authentication**: JWT (python-jose) + Google OAuth 2.0
- **Authorization**: RBAC (Role-Based Access Control)
- **Logging**: Request ID 추적, 구조화된 로깅

---

## 3. 아키텍처 핵심

### 3.1 계층화된 아키텍처 (Layered Architecture)

```
┌─────────────────────────────────────────┐
│  Client (React)                          │
└────────────────┬────────────────────────┘
                 │ HTTP Request
                 ▼
┌─────────────────────────────────────────┐
│  Router Layer (FastAPI)                  │  ← HTTP 요청/응답 처리
│  • Pydantic 검증                         │
│  • Service 호출                          │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Service Layer (Facade + Template)      │  ← 비즈니스 로직 조율
│  • Provider/Calculator/Formatter 조율   │
│  • 트랜잭션 관리                         │
│  • 권한 검증                             │
└───┬──────────────────┬──────────────────┘
    │                  │
    ▼                  ▼
┌─────────────┐  ┌────────────────┐  ┌──────────────┐
│  Provider   │  │  Calculator    │  │  Formatter   │
│  (Data)     │  │  (Logic)       │  │  (Output)    │
│             │  │                │  │              │
│  • DB 쿼리  │  │  • 순수 계산   │  │  • 응답 변환 │
│  • API 호출 │  │  • 알고리즘    │  │  • 마스킹    │
│  • 파일 I/O │  │  • 통계 분석   │  │  • 포맷팅    │
└─────────────┘  └────────────────┘  └──────────────┘
```

### 3.2 핵심 디자인 패턴

| 패턴 | 적용 위치 | 목적 |
|------|-----------|------|
| **Facade** | Service | Provider/Calculator/Formatter의 복잡성을 숨김 |
| **Template Method** | BaseService | 비즈니스 로직 흐름 정의 (before_execute, execute, after_execute) |
| **Strategy** | Provider | 다양한 데이터 소스 전략 캡슐화 (DB, API, 파일, 캐시) |
| **Adapter** | Formatter | 내부 데이터 → API 응답 형식 변환 |
| **Dependency Injection** | 전체 | FastAPI `Depends()`, 생성자 주입으로 결합도 감소 |
| **Singleton** | ApiClient (프론트) | 단일 Axios 인스턴스로 일관된 API 통신 |

### 3.3 핵심 원칙

#### SOLID 원칙 준수
- **S (Single Responsibility)**: 각 클래스는 하나의 책임만 (Provider는 데이터 조회만, Calculator는 계산만)
- **O (Open/Closed)**: BaseService/Provider 등 확장 가능, 수정 불필요
- **L (Liskov Substitution)**: 모든 Service는 BaseService로 대체 가능
- **I (Interface Segregation)**: Pydantic 스키마로 명확한 인터페이스 정의
- **D (Dependency Inversion)**: 구체적 구현이 아닌 추상화(Base 클래스)에 의존

#### 추가 원칙
- **DRY (Don't Repeat Yourself)**: 공통 로직은 `shared/` 또는 `core/`로 추출
- **KISS (Keep It Simple, Stupid)**: 과도한 엔지니어링 금지
- **YAGNI (You Aren't Gonna Need It)**: 필요한 기능만 구현

---

## 4. 프로젝트 구조

### 4.1 전체 구조
```
vntg-1on1/
├── 📁 server/                     # 백엔드 (FastAPI)
│   ├── main.py                    # FastAPI 진입점
│   └── app/
│       ├── core/                  # 핵심 인프라
│       │   ├── config.py          # 환경 설정
│       │   ├── database.py        # SQLAlchemy 엔진/세션
│       │   ├── dependencies.py    # FastAPI DI
│       │   ├── logging.py         # Request ID 로깅
│       │   ├── middleware.py      # Request ID 미들웨어
│       │   └── routers.py         # Health, Version 엔드포인트
│       ├── shared/                # 공유 컴포넌트
│       │   ├── base/              # Base 클래스들
│       │   │   ├── service.py     # BaseService
│       │   │   ├── provider.py    # BaseProvider
│       │   │   ├── calculator.py  # BaseCalculator
│       │   │   └── formatter.py   # BaseFormatter
│       │   ├── exceptions/        # 커스텀 예외
│       │   └── types/             # ServiceResult, DTOs
│       ├── domain/                # 비즈니스 도메인
│       │   └── auth/              # 인증 도메인 (구현 완료)
│       │       ├── service.py
│       │       ├── models/
│       │       ├── schemas/
│       │       ├── providers/
│       │       └── formatters/
│       ├── examples/              # 참고용 예제
│       │   └── sample_domain/     # 샘플 도메인 (템플릿)
│       └── api/v1/                # API 레이어
│           ├── router.py          # 라우터 통합
│           └── endpoints/         # 도메인별 엔드포인트
│
├── 📁 client/                     # 프론트엔드 (React)
│   └── src/
│       ├── main.tsx               # React 진입점
│       ├── App.tsx                # 메인 앱 컴포넌트
│       ├── core/                  # 핵심 인프라
│       │   ├── api/               # apiClient 싱글톤
│       │   ├── errors/            # ErrorBoundary
│       │   ├── loading/           # LoadingOverlay
│       │   ├── hooks/             # useApi, useDebounce
│       │   ├── layout/            # Header, Sidebar, MainLayout
│       │   ├── store/             # useAuthStore (전역)
│       │   └── ui/                # Button, Card, Input (재사용)
│       └── domains/               # 도메인별 기능
│           └── sample/            # 샘플 도메인
│               ├── api.ts         # API 호출
│               ├── store.ts       # Zustand 스토어
│               ├── types.ts       # TypeScript 타입
│               ├── components/    # 도메인 컴포넌트
│               └── pages/         # 도메인 페이지
│
├── 📁 tests/                      # 테스트
│   ├── unit/
│   └── integration/
│
├── README.md                      # 프로젝트 개요
├── ARCHITECTURE.md                # 상세 아키텍처 문서
├── DEVELOPMENT_GUIDE.md           # 개발 가이드
├── claude_rules.md                # Claude Code 규칙 (간결)
├── PROJECT_HANDOVER.md            # 이 문서
└── .cursorrules                   # Cursor AI 규칙
```

### 4.2 도메인 구조 (중요!)

**백엔드 도메인 구조** (`server/app/domain/{domain}/`):
```
{domain}/
├── service.py           # Service 클래스 (BaseService 상속)
├── models/              # SQLAlchemy 모델
│   └── __init__.py
├── schemas/             # Pydantic Request/Response
│   └── __init__.py
├── providers/           # 데이터 조회 (BaseProvider 상속)
│   └── __init__.py
├── calculators/         # 비즈니스 로직 (BaseCalculator 상속)
│   └── __init__.py
└── formatters/          # 응답 포맷팅 (BaseFormatter 상속)
    └── __init__.py
```

**프론트엔드 도메인 구조** (`client/src/domains/{domain}/`):
```
{domain}/
├── api.ts               # API 호출 함수
├── store.ts             # Zustand 스토어
├── types.ts             # TypeScript 타입
├── components/          # 도메인 전용 컴포넌트
│   ├── {Domain}Form.tsx
│   ├── {Domain}List.tsx
│   └── index.ts
├── pages/               # 도메인 페이지 (라우팅 대상)
│   ├── {Domain}Page.tsx
│   └── index.ts
└── index.ts             # 내보내기
```

---

## 5. 핵심 개념

### 5.1 Base 클래스 시스템

#### BaseService
```python
from typing import TypeVar, Generic
from server.app.shared.types import ServiceResult

TRequest = TypeVar("TRequest")
TResponse = TypeVar("TResponse")

class BaseService(Generic[TRequest, TResponse]):
    """
    모든 Service의 베이스 클래스
    - Template Method 패턴 구현
    - before_execute, execute, after_execute 훅 제공
    """
    async def execute(self, request: TRequest) -> ServiceResult[TResponse]:
        await self.before_execute(request)
        await self.validate_request(request)
        await self.check_permissions(request)

        # 하위 클래스에서 구현
        result = await self._execute_business_logic(request)

        await self.after_execute(request, result)
        return result
```

#### BaseProvider
```python
class BaseProvider(Generic[TInput, TOutput]):
    """
    데이터 조회 전략을 캡슐화
    - provide() 메서드 구현 필수
    - 하위 클래스: DatabaseProvider, APIProvider, FileProvider
    """
    async def provide(self, input_data: TInput) -> TOutput:
        raise NotImplementedError
```

#### BaseCalculator
```python
class BaseCalculator(Generic[TInput, TOutput]):
    """
    순수 계산 로직
    - calculate() 메서드 구현 필수
    - Side Effect 절대 금지 (DB, API 접근 불가)
    """
    async def calculate(self, input_data: TInput) -> TOutput:
        raise NotImplementedError
```

#### BaseFormatter
```python
class BaseFormatter(Generic[TInput, TOutput]):
    """
    내부 데이터 → API 응답 변환
    - format() 메서드 구현 필수
    """
    async def format(self, input_data: TInput) -> TOutput:
        raise NotImplementedError
```

### 5.2 ServiceResult 패턴

```python
from dataclasses import dataclass
from typing import Generic, TypeVar, Optional

T = TypeVar("T")

@dataclass
class ServiceResult(Generic[T]):
    """Service 실행 결과를 명시적으로 표현"""
    success: bool
    data: Optional[T] = None
    error: Optional[Exception] = None
    message: Optional[str] = None

    @classmethod
    def success(cls, data: T, message: str = "Success") -> "ServiceResult[T]":
        return cls(success=True, data=data, message=message)

    @classmethod
    def fail(cls, error: Exception, message: str = "Failed") -> "ServiceResult[T]":
        return cls(success=False, error=error, message=message)
```

### 5.3 커스텀 예외 계층

```python
class ApplicationException(Exception):
    """모든 애플리케이션 예외의 베이스"""
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}

class ValidationException(ApplicationException):
    """400: 입력 검증 실패"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=400, details=details)

class NotFoundException(ApplicationException):
    """404: 리소스를 찾을 수 없음"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=404, details=details)

class BusinessLogicException(ApplicationException):
    """422: 비즈니스 규칙 위반"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=422, details=details)
```

---

## 6. 개발 워크플로우

### 6.1 환경 설정

#### 백엔드
```bash
# 1. 가상환경 생성 & 활성화
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경 변수 설정
cp .env.example .env
# .env 파일 수정 (DATABASE_URL 등)

# 4. 서버 실행
python -m server.main
# → http://localhost:8000
# → http://localhost:8000/docs (Swagger UI)
```

#### 프론트엔드
```bash
cd client

# 1. 의존성 설치
npm install

# 2. 개발 서버 실행
npm run dev
# → http://localhost:3000
```

### 6.2 코드 품질 관리

```bash
# 백엔드
black server/            # 코드 포맷팅
isort server/            # Import 정렬
ruff check server/       # 린팅
mypy server/             # 타입 체크
pytest --cov=server      # 테스트 + 커버리지

# 프론트엔드
cd client
npm run lint             # ESLint
npx tsc --noEmit         # 타입 체크
npm run build            # 빌드 테스트
```

### 6.3 Git 워크플로우

```bash
# Feature 브랜치 생성
git checkout -b feature/payment-domain

# 작업 후 커밋
git add .
git commit -m "feat: Add payment domain"

# 메인 브랜치 최신 변경사항 반영
git fetch origin
git rebase origin/main

# Push
git push origin feature/payment-domain

# Pull Request 생성 → 리뷰 → 머지
```

---

## 7. 새 도메인 추가 방법

### 7.1 백엔드 (예: `payment` 도메인)

#### 단계 1: 디렉토리 생성
```bash
mkdir -p server/app/domain/payment/{models,schemas,providers,calculators,formatters}
touch server/app/domain/payment/__init__.py
touch server/app/domain/payment/service.py
```

#### 단계 2: SQLAlchemy 모델 정의
`server/app/domain/payment/models/__init__.py`:
```python
from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from server.app.core.database import Base

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(20))
```

#### 단계 3: Pydantic 스키마 정의
`server/app/domain/payment/schemas/__init__.py`:
```python
from pydantic import BaseModel, Field
from decimal import Decimal

class PaymentRequest(BaseModel):
    user_id: int = Field(..., gt=0)
    amount: Decimal = Field(..., gt=0)

class PaymentResponse(BaseModel):
    transaction_id: str
    status: str
    amount: float
```

#### 단계 4-6: Provider, Calculator, Formatter 구현
(각각 BaseProvider, BaseCalculator, BaseFormatter 상속)

#### 단계 7: Service 구현
`server/app/domain/payment/service.py`:
```python
from server.app.shared.base import BaseService
from server.app.shared.types import ServiceResult

class PaymentService(BaseService[PaymentRequest, PaymentResponse]):
    def __init__(self, db: AsyncSession):
        super().__init__()
        self.provider = PaymentDataProvider(db)
        self.calculator = PaymentCalculator()
        self.formatter = PaymentResponseFormatter()

    async def execute(self, request: PaymentRequest) -> ServiceResult[PaymentResponse]:
        data = await self.provider.provide(...)
        result = await self.calculator.calculate(...)
        response = await self.formatter.format(...)
        return ServiceResult.success(response)
```

#### 단계 8-9: API 엔드포인트 & 라우터 등록
`server/app/api/v1/endpoints/payment.py`:
```python
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/payment", tags=["payment"])

@router.post("/process", response_model=PaymentResponse)
async def process_payment(request: PaymentRequest, db = Depends(get_db)):
    service = PaymentService(db)
    result = await service.execute(request)
    return result.data
```

`server/app/api/v1/router.py`에 등록:
```python
from server.app.api.v1.endpoints import payment
api_router.include_router(payment.router)
```

### 7.2 프론트엔드 (예: `payment` 도메인)

#### 단계 1-2: 디렉토리 & 타입 정의
```bash
mkdir -p client/src/domains/payment/{components,pages}
```

`client/src/domains/payment/types.ts`:
```typescript
export interface PaymentRequest {
  user_id: number;
  amount: number;
}

export interface PaymentResponse {
  transaction_id: string;
  status: string;
  amount: number;
}
```

#### 단계 3: API 모듈
`client/src/domains/payment/api.ts`:
```typescript
import { apiClient } from '@/core/api';

export async function processPayment(data: PaymentRequest): Promise<PaymentResponse> {
  return apiClient.post<PaymentResponse>('/v1/payment/process', data);
}
```

#### 단계 4: Zustand 스토어
`client/src/domains/payment/store.ts`:
```typescript
import { create } from 'zustand';

interface PaymentState {
  payments: Payment[];
  setPayments: (payments: Payment[]) => void;
}

export const usePaymentStore = create<PaymentState>((set) => ({
  payments: [],
  setPayments: (payments) => set({ payments }),
}));
```

#### 단계 5-6: 컴포넌트 & 페이지
`client/src/domains/payment/pages/PaymentPage.tsx`:
```tsx
import { MainLayout } from '@/core/layout';
import { PaymentForm, PaymentList } from '../components';

export const PaymentPage: React.FC = () => (
  <MainLayout>
    <h1 className="text-3xl font-bold">결제 관리</h1>
    <PaymentForm />
    <PaymentList />
  </MainLayout>
);
```

#### 단계 7: 라우팅 등록
`client/src/App.tsx`:
```tsx
<Route path="/payment" element={<PaymentPage />} />
```

---

## 8. 코드 예시

### 8.1 완전한 Service 예시

```python
# server/app/domain/payment/service.py
from sqlalchemy.ext.asyncio import AsyncSession
from server.app.shared.base import BaseService
from server.app.shared.types import ServiceResult
from server.app.shared.exceptions import BusinessLogicException

class PaymentService(BaseService[PaymentRequest, PaymentResponse]):
    """결제 서비스"""

    def __init__(self, db: AsyncSession):
        super().__init__()
        self.db = db
        self.provider = PaymentDataProvider(db)
        self.calculator = PaymentCalculator()
        self.formatter = PaymentResponseFormatter()

    async def execute(self, request: PaymentRequest) -> ServiceResult[PaymentResponse]:
        try:
            # 1. 검증
            await self.validate_request(request)

            # 2. Provider: 데이터 조회
            user_data = await self.provider.provide({
                "user_id": request.user_id,
                "payment_method_id": request.payment_method_id
            })

            # 3. Calculator: 비즈니스 로직 (수수료 계산, 한도 검증)
            calc_result = await self.calculator.calculate({
                "amount": request.amount,
                "user_data": user_data,
                "currency": request.currency
            })

            # 4. 비즈니스 규칙 검증
            if calc_result["exceeds_limit"]:
                raise BusinessLogicException(
                    message="결제 한도 초과",
                    details={"limit": calc_result["daily_limit"]}
                )

            # 5. Formatter: 응답 포맷팅
            response = await self.formatter.format({
                "payment_result": calc_result,
                "request": request
            })

            return ServiceResult.success(response)

        except Exception as e:
            return await self.handle_error(e)

    async def validate_request(self, request: PaymentRequest) -> None:
        if request.amount <= 0:
            raise ValidationException("결제 금액은 0보다 커야 합니다")
```

### 8.2 완전한 React 컴포넌트 예시

```tsx
// client/src/domains/payment/components/PaymentForm.tsx
import React, { useState } from 'react';
import { Button, Input, Card } from '@/core/ui';
import { usePaymentStore } from '../store';
import { processPayment } from '../api';
import { LoadingManager } from '@/core/loading';
import { handleApiError } from '@/core/errors';

interface PaymentFormProps {
  userId: number;
}

export const PaymentForm: React.FC<PaymentFormProps> = ({ userId }) => {
  const [amount, setAmount] = useState('');
  const { addPayment } = usePaymentStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    LoadingManager.show('결제 처리 중...');
    try {
      const result = await processPayment({
        user_id: userId,
        amount: parseFloat(amount),
      });

      addPayment(result);
      setAmount(''); // 폼 초기화
      alert('결제가 완료되었습니다!');
    } catch (error) {
      const message = handleApiError(error);
      alert(message);
    } finally {
      LoadingManager.hide();
    }
  };

  return (
    <Card>
      <form onSubmit={handleSubmit} className="space-y-4">
        <h2 className="text-xl font-semibold text-gray-900">결제</h2>
        <Input
          label="금액"
          type="number"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          placeholder="결제 금액 입력"
          required
        />
        <Button type="submit" variant="primary">
          결제하기
        </Button>
      </form>
    </Card>
  );
};
```

---

## 9. 환경 설정

### 9.1 백엔드 환경 변수 (`.env`)

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=True

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google OAuth (if using)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback

# Logging
LOG_LEVEL=INFO
```

### 9.2 프론트엔드 환경 변수 (`.env`)

```bash
# API Base URL
VITE_API_BASE_URL=http://localhost:8000/api

# Google OAuth
VITE_GOOGLE_CLIENT_ID=your-google-client-id
```

---

## 10. 테스트 & 배포

### 10.1 테스트 작성

#### 백엔드 단위 테스트
```python
# tests/unit/payment/test_payment_calculator.py
import pytest
from decimal import Decimal
from server.app.domain.payment.calculators import PaymentCalculator

@pytest.mark.asyncio
async def test_calculate_fee_credit_card():
    calculator = PaymentCalculator()

    result = await calculator.calculate({
        "amount": Decimal("100000"),
        "payment_type": "credit_card",
        "user_tier": "silver"
    })

    assert result["fee"] == Decimal("3000")
    assert result["final_amount"] == Decimal("103000")
```

#### 백엔드 통합 테스트
```python
# tests/integration/payment/test_payment_service.py
@pytest.mark.asyncio
async def test_payment_service_success(async_db: AsyncSession):
    service = PaymentService(db=async_db)

    request = PaymentRequest(
        user_id=1,
        payment_method_id=1,
        amount=50000
    )

    result = await service.execute(request)

    assert result.success
    assert result.data.status == "approved"
```

### 10.2 배포

#### 백엔드 (Docker)
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY server/ server/
CMD ["python", "-m", "server.main"]
```

#### 프론트엔드 (Vercel/Netlify)
```bash
cd client
npm run build  # dist/ 폴더 생성
# dist/ 폴더를 Vercel/Netlify에 배포
```

---

## 11. 주의사항

### 11.1 절대 금지 사항

1. **절차지향 함수 금지**: 백엔드 비즈니스 로직은 반드시 클래스 기반
2. **직접 DB 접근 금지**: Service에서 직접 쿼리 작성 금지 (Provider로 위임)
3. **Calculator에서 DB 접근 금지**: 순수 함수만 (Side Effect 금지)
4. **직접 axios 호출 금지**: 프론트엔드에서 `apiClient` 사용 필수
5. **인라인 스타일 금지**: React에서 Tailwind CSS 사용
6. **타입 힌트 생략 금지**: Python, TypeScript 모두 명시적 타입 선언

### 11.2 보안 주의사항

- **비밀번호 해싱**: passlib 사용
- **JWT 토큰**: python-jose 사용, 만료 시간 설정
- **민감정보 마스킹**: Formatter에서 카드 번호, 이메일 마스킹
- **SQL Injection 방지**: ORM 사용, 직접 쿼리 금지
- **XSS 방지**: 사용자 입력 검증, React는 기본적으로 XSS 방지

### 11.3 성능 주의사항

- **N+1 문제**: `selectinload()`, `joinedload()` 사용
- **페이지네이션**: 대량 데이터는 반드시 페이지네이션
- **캐싱**: Provider 레벨에서 캐싱 (Redis 등)
- **비동기 일관성**: async/await 일관되게 사용

---

## 12. 문제 해결

### 12.1 자주 발생하는 에러

#### `ImportError: cannot import name ...`
- **원인**: 순환 import
- **해결**: `from typing import TYPE_CHECKING` 사용
  ```python
  from typing import TYPE_CHECKING
  if TYPE_CHECKING:
      from payment.models import Payment
  ```

#### `AttributeError: 'AsyncSession' object has no attribute 'query'`
- **원인**: SQLAlchemy 1.x 문법 사용
- **해결**: SQLAlchemy 2.0 문법으로 변경
  ```python
  # ❌ 1.x
  db.query(User).filter(User.id == user_id).first()

  # ✅ 2.0
  result = await db.execute(select(User).where(User.id == user_id))
  user = result.scalar_one_or_none()
  ```

#### `Module not found: Can't resolve '@/core/ui'`
- **원인**: Path alias 설정 누락
- **해결**: `vite.config.ts` 확인
  ```typescript
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  }
  ```

### 12.2 디버깅 팁

#### 백엔드
```python
# Request ID로 로그 추적
logger.info("Debug message", extra={"request_id": request.state.request_id})

# Pydantic 검증 에러 디버깅
try:
    request = PaymentRequest(**data)
except ValidationError as e:
    print(e.json())
```

#### 프론트엔드
```typescript
// Axios 인터셉터에서 디버깅
apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response:', response);
    return response;
  }
);
```

---

## 📚 추가 참고 문서

- **`README.md`**: 프로젝트 개요 및 빠른 시작
- **`ARCHITECTURE.md`**: 상세 아키텍처 & 디자인 패턴
- **`DEVELOPMENT_GUIDE.md`**: 도메인 추가 상세 체크리스트
- **`claude_rules.md`**: Claude Code 규칙 (간결 버전)
- **`server/README.md`**: 백엔드 상세 가이드
- **`client/README.md`**: 프론트엔드 상세 가이드

---

## 🎯 신규 기능 개발 시작하기

### 예시: "결제(payment) 도메인" 개발 요청

**당신에게 주어진 작업**:
> "결제 기능을 추가해주세요. 사용자가 결제 수단을 선택하고, 금액을 입력하면 수수료를 자동으로 계산하여 결제를 처리하는 기능입니다."

**개발 순서**:

1. **이 문서 읽기**: 프로젝트 구조, 아키텍처 이해 ✅
2. **도메인 설계**: ERD, API 명세서 작성
3. **백엔드 구현**:
   - models → schemas → providers → calculators → formatters → service → router
4. **프론트엔드 구현**:
   - types → api → store → components → pages → routing
5. **테스트 & 검증**: 단위 테스트, 통합 테스트, E2E 테스트
6. **코드 품질**: black, isort, ruff, mypy, eslint 실행
7. **커밋 & PR**: Git 워크플로우 따라 PR 생성

---

**이제 당신은 이 프로젝트를 완벽히 이해했습니다! 🚀**

**질문이 있거나 새로운 기능을 개발해야 한다면, 이 문서를 참고하여 작업을 시작하세요.**
