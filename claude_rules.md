# Claude Code Rules

> 이 프로젝트는 **"유지보수성 최우선" 및 "모듈화"** 원칙을 따르는 FastAPI + React 19 풀스택 애플리케이션입니다.

---

## 🚫 절대 금지 (NEVER DO)

1. **절차지향 함수 금지**: 백엔드 비즈니스 로직은 반드시 클래스 기반 (BaseService, BaseProvider, BaseCalculator, BaseFormatter 상속)
2. **직접 DB 접근 금지**: Service에서 직접 DB 쿼리 작성 금지 (Provider로 위임)
3. **직접 axios 호출 금지**: 프론트엔드에서 `axios` 직접 import 금지 (apiClient 사용)
4. **인라인 스타일 금지**: React에서 `style={{ ... }}` 사용 금지 (Tailwind CSS 사용)
5. **타입 힌트 생략 금지**: Python, TypeScript 모두 명시적 타입 선언 필수
6. **도메인 간 직접 의존 금지**: 한 도메인이 다른 도메인의 Service 직접 호출 금지

---

## 📂 폴더 구조

### 백엔드
```
server/app/
├── core/              # 인프라 (database, logging, middleware, dependencies)
├── shared/            # 공통 컴포넌트
│   ├── base/          # BaseService, BaseProvider, BaseCalculator, BaseFormatter
│   ├── exceptions/    # 커스텀 예외 (ValidationException, NotFoundException 등)
│   └── types/         # ServiceResult, PaginatedResult
├── domain/            # 비즈니스 도메인
│   └── {domain}/
│       ├── service.py       # Service (BaseService 상속)
│       ├── models/          # SQLAlchemy 모델
│       ├── schemas/         # Pydantic 스키마
│       ├── providers/       # 데이터 조회 (BaseProvider 상속)
│       ├── calculators/     # 비즈니스 로직 (BaseCalculator 상속)
│       └── formatters/      # 응답 포맷팅 (BaseFormatter 상속)
└── api/v1/endpoints/  # FastAPI 라우터
```

### 프론트엔드
```
client/src/
├── core/              # 공통 인프라
│   ├── api/           # apiClient 싱글톤
│   ├── store/         # 전역 상태 (useAuthStore)
│   ├── ui/            # 재사용 UI 컴포넌트 (Button, Card, Input)
│   ├── layout/        # 레이아웃 (Header, Sidebar, MainLayout)
│   ├── hooks/         # 커스텀 훅 (useApi, useDebounce)
│   ├── errors/        # ErrorBoundary, ApiErrorHandler
│   └── loading/       # LoadingOverlay, LoadingManager
└── domains/           # 도메인별 기능
    └── {domain}/
        ├── api.ts         # API 호출 함수
        ├── store.ts       # Zustand 스토어
        ├── types.ts       # TypeScript 타입
        ├── components/    # 도메인 컴포넌트
        └── pages/         # 도메인 페이지
```

---

## 🏗️ 레이어 책임

### 백엔드 계층
| 레이어 | 역할 | 규칙 |
|--------|------|------|
| **Router** | HTTP 요청/응답, Pydantic 검증 | 비즈니스 로직 금지, Service만 호출 |
| **Service** | Provider/Calculator/Formatter 조율, 트랜잭션 관리 | 반드시 BaseService 상속, execute() 구현 |
| **Provider** | DB/API/파일 접근, 데이터 조회 | 반드시 BaseProvider 상속, 계산 로직 금지 |
| **Calculator** | 순수 계산 로직 (Side Effect 금지) | 반드시 BaseCalculator 상속, DB 접근 금지 |
| **Formatter** | 내부 데이터 → API 응답 변환 | 반드시 BaseFormatter 상속, 비즈니스 로직 금지 |

**데이터 흐름**: Router → Service → Provider → Calculator → Formatter → Router

---

## 💻 코드 스타일

### Python
```python
# ✅ 권장: 클래스 기반 Service
class PaymentService(BaseService[PaymentRequest, PaymentResponse]):
    def __init__(self, db: AsyncSession):
        super().__init__()
        self.db = db
        self.provider = PaymentDataProvider(db)
        self.calculator = PaymentCalculator()
        self.formatter = PaymentResponseFormatter()

    async def execute(self, request: PaymentRequest) -> ServiceResult[PaymentResponse]:
        # 1. Provider: 데이터 조회
        data = await self.provider.provide(...)
        # 2. Calculator: 비즈니스 로직
        result = await self.calculator.calculate(...)
        # 3. Formatter: 응답 포맷팅
        response = await self.formatter.format(...)
        return ServiceResult.success(response)

# ❌ 금지: 절차지향 함수
async def process_payment(db, request):
    user = await db.execute(...)  # 직접 DB 접근 금지
    ...
```

### TypeScript
```tsx
// ✅ 권장: apiClient + Zustand + Tailwind
import { apiClient } from '@/core/api';
import { usePaymentStore } from '../store';

export const PaymentForm: React.FC = () => {
  const { addPayment } = usePaymentStore();

  const handleSubmit = async () => {
    const result = await apiClient.post('/v1/payment/process', data);
    addPayment(result);
  };

  return (
    <div className="flex flex-col gap-4 p-4 bg-white rounded-lg shadow-md">
      {/* Tailwind CSS */}
    </div>
  );
};

// ❌ 금지: 직접 axios 사용 + 인라인 스타일
import axios from 'axios';  // 금지!
<div style={{ display: 'flex' }}>  {/* 금지! */}
```

---

## 🎨 공통 UI 컴포넌트 (필수 사용)

**디자인 요청 시 항상 먼저 공통 컴포넌트를 사용하세요!**

모든 프론트엔드 개발 시 `@/core/ui`의 공통 컴포넌트를 **최우선**으로 사용하여 일관된 디자인을 유지합니다.

### 사용 가능한 컴포넌트

```tsx
import {
  // Form Components
  Button, Input, Textarea, Select, Checkbox, Radio, RadioGroup,
  // Layout Components
  Card, CardHeader, CardBody, CardFooter,
  Modal, ModalHeader, ModalBody, ModalFooter,
  // Feedback Components
  Badge, Alert
} from '@/core/ui';
```

### 디자인 가이드라인 (2026 모던 핀테크)

- **색상**: Indigo(Primary), Slate(Secondary), Emerald(Success), Red(Danger)
- **둥근 모서리**: `rounded-xl`, `rounded-2xl` (부드러운 느낌)
- **그림자**: `shadow-sm`, `shadow-md` (은은한 깊이감)
- **간격**: 4px 단위 (`gap-2`, `p-4`, `mb-6`)
- **애니메이션**: `transition-all duration-200` (부드러운 전환)
- **호버 효과**: 밝기 변화 + 약간의 scale 변화

### 컴포넌트 예시

```tsx
// ✅ 권장: 공통 컴포넌트 사용
import { Button, Input, Card, Modal } from '@/core/ui';

export const UserForm = () => (
  <Card>
    <CardHeader>User Information</CardHeader>
    <CardBody>
      <Input label="Email" type="email" required />
      <Input label="Name" placeholder="Enter name" />
      <Button variant="primary" size="md">Submit</Button>
    </CardBody>
  </Card>
);

// ❌ 금지: 커스텀 스타일 컴포넌트 직접 생성
const CustomButton = () => (
  <button style={{ padding: '10px' }}>...</button>  // 금지!
);
```

### 컴포넌트별 사용법

```tsx
// Button
<Button variant="primary|secondary|outline|ghost|danger" size="sm|md|lg" isLoading>
  Click me
</Button>

// Input
<Input label="Email" type="email" error="Invalid email" helperText="example@email.com" />

// Select
<Select label="Country" options={[{value: 'kr', label: 'Korea'}]} />

// Checkbox
<Checkbox label="Agree to terms" />

// Radio
<RadioGroup label="Plan">
  <Radio name="plan" value="free" label="Free" />
  <Radio name="plan" value="pro" label="Pro" helperText="$29/month" />
</RadioGroup>

// Badge
<Badge variant="success|warning|danger|info" size="sm|md|lg" dot>Active</Badge>

// Alert
<Alert variant="success|warning|danger|info" title="Success" onClose={handleClose}>
  Payment completed!
</Alert>

// Modal
<Modal isOpen={isOpen} onClose={onClose} size="sm|md|lg|xl|full">
  <ModalHeader onClose={onClose}>Title</ModalHeader>
  <ModalBody>Content</ModalBody>
  <ModalFooter>
    <Button onClick={onClose}>Close</Button>
  </ModalFooter>
</Modal>
```

---

## 🛡️ 타입 안전성

### Python
- **모든 함수/메서드에 타입 힌트 명시**: `def foo(x: int) -> str:`
- **Pydantic v2 스키마 사용**: Request/Response는 BaseModel 상속
- **SQLAlchemy 2.0 타입**: `Mapped[int] = mapped_column(...)`

### TypeScript
- **`any` 타입 사용 금지**: 불가피한 경우 `unknown` 사용 후 타입 가드
- **명시적 인터페이스**: `interface PaymentRequest { ... }`
- **제네릭 활용**: `Promise<PaymentResponse>`, `create<PaymentState>(...)`

---

## 📝 로깅 & 예외 처리

### 로깅
```python
from server.app.core.logging import get_logger
logger = get_logger(__name__)

# Request ID 자동 포함
logger.info("Payment processed", extra={
    "request_id": request.state.request_id,
    "user_id": user.id,
    "amount": amount
})
```

### 예외 처리
```python
# ✅ 커스텀 예외 사용
from server.app.shared.exceptions import (
    ValidationException,      # 400: 입력 검증 실패
    NotFoundException,        # 404: 리소스 없음
    BusinessLogicException,   # 422: 비즈니스 규칙 위반
    ExternalServiceException  # 502: 외부 서비스 오류
)

raise NotFoundException(
    message="사용자를 찾을 수 없습니다",
    details={"user_id": user_id}
)

# ❌ 일반 Exception 사용 금지
raise Exception("사용자를 찾을 수 없습니다")  # 금지!
```

---

## 🎨 Tailwind CSS

### 권장 패턴
```tsx
// ✅ Tailwind 유틸리티 클래스
<button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
  클릭
</button>

// ✅ cn() 유틸리티로 조건부 클래스
import { cn } from '@/utils/cn';

<button className={cn(
  'px-4 py-2 rounded-lg',
  variant === 'primary' && 'bg-blue-600 text-white',
  disabled && 'opacity-50 cursor-not-allowed'
)}>

// ❌ 인라인 스타일 금지
<button style={{ padding: '8px 16px' }}>  {/* 금지! */}
```

---

## ⚡ 빠른 참조

### 백엔드 명령어
```bash
# 서버 실행
python -m server.main

# 코드 품질
black server/ && isort server/ && ruff check server/

# 타입 체크
mypy server/

# 테스트
pytest --cov=server
```

### 프론트엔드 명령어
```bash
cd client
npm run dev        # 개발 서버
npm run build      # 프로덕션 빌드
npm run lint       # ESLint 검사
```

### 새 도메인 추가 (핵심만)
1. **백엔드**: `server/app/domain/{domain}/` 생성 → models → schemas → providers → calculators → formatters → service → router 등록
2. **프론트엔드**: `client/src/domains/{domain}/` 생성 → types → api → store → components → pages → 라우팅 등록

---

## 📚 참고 문서

- `README.md`: 프로젝트 개요 & 빠른 시작
- `ARCHITECTURE.md`: 상세 아키텍처 & 디자인 패턴
- `DEVELOPMENT_GUIDE.md`: 도메인 추가 상세 체크리스트
- `server/README.md`: 백엔드 상세 가이드
- `client/README.md`: 프론트엔드 상세 가이드

---

**기억하세요**: 이 규칙을 따르면 여러 명이 동시에 작업해도 충돌 없이 깔끔한 코드를 유지할 수 있습니다! 🚀
