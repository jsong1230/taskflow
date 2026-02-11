# TaskFlow API 명세서

## 문서 정보
- **버전**: v1
- **Base URL**: `http://localhost:8000/api/v1`
- **인증 방식**: Bearer JWT Token
- **응답 형식**: JSON

---

## 목차
- [인증](#인증)
- [프로젝트 API](#프로젝트-api)
- [태스크 API](#태스크-api)
- [댓글 API](#댓글-api)
- [에러 응답](#에러-응답)

---

## 인증

대부분의 API 엔드포인트는 JWT 토큰을 통한 인증이 필요합니다.

### 헤더 형식
```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

### 토큰 만료
- JWT 토큰 유효 기간: 30분 (기본값)
- 토큰 만료 시 401 Unauthorized 응답 반환

---

## 인증 API

### 1. 회원가입

사용자 계정을 생성합니다.

```http
POST /api/v1/auth/register
```

**Request Body**
```json
{
  "email": "user@example.com",
  "name": "홍길동",
  "password": "SecurePass123!"
}
```

**Validation Rules**
- `email`: 필수, 이메일 형식 (EmailStr)
- `name`: 필수, 문자열
- `password`: 필수, 문자열 (bcrypt로 해싱 저장)

**Response** (201 Created)
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "홍길동",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses**
- `400 Bad Request`: 이메일 형식 오류
- `422 Unprocessable Entity`: 이미 존재하는 이메일

---

### 2. 로그인

이메일과 비밀번호로 로그인하고 JWT 토큰을 발급받습니다.

```http
POST /api/v1/auth/login
```

**Request Body**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response** (200 OK)
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "홍길동",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "token": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
}
```

**Error Responses**
- `401 Unauthorized`: 잘못된 이메일 또는 비밀번호
  ```json
  {
    "detail": "이메일 또는 비밀번호가 올바르지 않습니다."
  }
  ```

---

### 3. 현재 사용자 정보 조회

로그인된 사용자의 정보를 조회합니다.

```http
GET /api/v1/auth/me
```

**Headers**
```http
Authorization: Bearer <access_token>
```

**Response** (200 OK)
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "홍길동",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses**
- `401 Unauthorized`: 토큰 없음 또는 유효하지 않은 토큰

---

## 프로젝트 API

### 1. 프로젝트 생성

새 프로젝트를 생성합니다. 생성자는 자동으로 owner 역할로 추가됩니다.

```http
POST /api/v1/projects/
```

**Headers**
```http
Authorization: Bearer <access_token>
```

**Request Body**
```json
{
  "name": "TaskFlow 개발",
  "description": "태스크 관리 애플리케이션 개발 프로젝트"
}
```

**Validation Rules**
- `name`: 필수, 최대 200자
- `description`: 선택, 최대 2000자 (기본값: "")

**Response** (201 Created)
```json
{
  "id": 1,
  "name": "TaskFlow 개발",
  "description": "태스크 관리 애플리케이션 개발 프로젝트",
  "owner_id": 1,
  "created_at": "2024-01-15T11:00:00Z"
}
```

---

### 2. 프로젝트 목록 조회

현재 사용자가 소유하거나 멤버로 속한 모든 프로젝트를 조회합니다.

```http
GET /api/v1/projects/
```

**Headers**
```http
Authorization: Bearer <access_token>
```

**Response** (200 OK)
```json
[
  {
    "id": 1,
    "name": "TaskFlow 개발",
    "description": "태스크 관리 애플리케이션 개발 프로젝트",
    "owner_id": 1,
    "created_at": "2024-01-15T11:00:00Z"
  },
  {
    "id": 2,
    "name": "마케팅 캠페인",
    "description": "2024 Q1 마케팅 캠페인",
    "owner_id": 2,
    "created_at": "2024-01-16T09:00:00Z"
  }
]
```

---

### 3. 프로젝트 상세 조회

프로젝트 정보와 멤버 목록을 조회합니다.

```http
GET /api/v1/projects/{project_id}
```

**Headers**
```http
Authorization: Bearer <access_token>
```

**Response** (200 OK)
```json
{
  "id": 1,
  "name": "TaskFlow 개발",
  "description": "태스크 관리 애플리케이션 개발 프로젝트",
  "owner_id": 1,
  "created_at": "2024-01-15T11:00:00Z",
  "members": [
    {
      "id": 1,
      "user_id": 1,
      "project_id": 1,
      "role": "owner"
    },
    {
      "id": 2,
      "user_id": 2,
      "project_id": 1,
      "role": "member"
    }
  ]
}
```

**Error Responses**
- `404 Not Found`: 프로젝트가 존재하지 않음
- `403 Forbidden`: 프로젝트 멤버가 아님

---

### 4. 프로젝트 수정

프로젝트 정보를 수정합니다. owner 또는 admin 역할만 가능합니다.

```http
PUT /api/v1/projects/{project_id}
```

**Headers**
```http
Authorization: Bearer <access_token>
```

**Request Body**
```json
{
  "name": "TaskFlow MVP 개발",
  "description": "MVP 버전 개발"
}
```

**Validation Rules**
- 모든 필드 선택 (부분 업데이트 가능)
- `name`: 최대 200자
- `description`: 최대 2000자

**Response** (200 OK)
```json
{
  "id": 1,
  "name": "TaskFlow MVP 개발",
  "description": "MVP 버전 개발",
  "owner_id": 1,
  "created_at": "2024-01-15T11:00:00Z"
}
```

**Error Responses**
- `403 Forbidden`: 수정 권한 없음 (member 역할)
  ```json
  {
    "detail": "프로젝트 수정 권한이 없습니다."
  }
  ```

---

### 5. 프로젝트 삭제

프로젝트를 삭제합니다. owner 역할만 가능합니다. CASCADE 삭제로 관련된 태스크, 댓글, 멤버십도 모두 삭제됩니다.

```http
DELETE /api/v1/projects/{project_id}
```

**Headers**
```http
Authorization: Bearer <access_token>
```

**Response** (204 No Content)
- Body 없음

**Error Responses**
- `403 Forbidden`: 삭제 권한 없음 (owner가 아님)
  ```json
  {
    "detail": "프로젝트 삭제 권한이 없습니다."
  }
  ```

---

### 6. 프로젝트 멤버 추가

프로젝트에 새 멤버를 추가합니다. owner 또는 admin 역할만 가능합니다.

```http
POST /api/v1/projects/{project_id}/members
```

**Headers**
```http
Authorization: Bearer <access_token>
```

**Request Body**
```json
{
  "user_id": 3,
  "role": "member"
}
```

**Validation Rules**
- `user_id`: 필수, 존재하는 사용자 ID
- `role`: 선택, "owner" | "admin" | "member" (기본값: "member")

**Response** (201 Created)
```json
{
  "id": 3,
  "user_id": 3,
  "project_id": 1,
  "role": "member"
}
```

**Error Responses**
- `403 Forbidden`: 멤버 추가 권한 없음
  ```json
  {
    "detail": "멤버 추가 권한이 없습니다."
  }
  ```
- `422 Unprocessable Entity`: 이미 멤버로 존재

---

## 태스크 API

### 1. 태스크 생성

프로젝트 내에 새 태스크를 생성합니다.

```http
POST /api/v1/projects/{project_id}/tasks
```

**Headers**
```http
Authorization: Bearer <access_token>
```

**Request Body**
```json
{
  "title": "API 설계",
  "description": "RESTful API 설계 및 문서화",
  "priority": "high",
  "assignee_id": 2
}
```

**Validation Rules**
- `title`: 필수, 최대 300자
- `description`: 선택, 최대 5000자 (기본값: "")
- `priority`: 선택, "low" | "medium" | "high" | "critical" (기본값: "medium")
- `assignee_id`: 선택, 프로젝트 멤버여야 함 (null 가능)

**Response** (201 Created)
```json
{
  "id": 1,
  "title": "API 설계",
  "description": "RESTful API 설계 및 문서화",
  "status": "todo",
  "priority": "high",
  "project_id": 1,
  "assignee_id": 2,
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2024-01-15T12:00:00Z"
}
```

**참고**
- 생성 시 `status`는 자동으로 "todo"로 설정됩니다.

---

### 2. 태스크 목록 조회

프로젝트의 태스크 목록을 필터링 및 정렬하여 조회합니다.

```http
GET /api/v1/projects/{project_id}/tasks
```

**Headers**
```http
Authorization: Bearer <access_token>
```

**Query Parameters**
| 파라미터 | 타입 | 필수 | 설명 | 기본값 |
|----------|------|------|------|--------|
| status | string | X | 상태 필터 ("todo", "in_progress", "done") | - |
| priority | string | X | 우선순위 필터 ("low", "medium", "high", "critical") | - |
| assignee_id | integer | X | 담당자 ID 필터 | - |
| sort_by | string | X | 정렬 기준 ("created_at", "updated_at", "title", "priority", "status") | "created_at" |
| sort_order | string | X | 정렬 순서 ("asc", "desc") | "desc" |

**예시**
```http
GET /api/v1/projects/1/tasks?status=in_progress&priority=high&sort_by=created_at&sort_order=desc
```

**Response** (200 OK)
```json
[
  {
    "id": 1,
    "title": "API 설계",
    "description": "RESTful API 설계 및 문서화",
    "status": "in_progress",
    "priority": "high",
    "project_id": 1,
    "assignee_id": 2,
    "created_at": "2024-01-15T12:00:00Z",
    "updated_at": "2024-01-15T14:30:00Z"
  },
  {
    "id": 5,
    "title": "데이터베이스 마이그레이션",
    "description": "Alembic 마이그레이션 스크립트 작성",
    "status": "in_progress",
    "priority": "high",
    "project_id": 1,
    "assignee_id": 1,
    "created_at": "2024-01-15T13:00:00Z",
    "updated_at": "2024-01-15T13:00:00Z"
  }
]
```

---

### 3. 태스크 상세 조회

특정 태스크의 상세 정보를 조회합니다.

```http
GET /api/v1/projects/{project_id}/tasks/{task_id}
```

**Headers**
```http
Authorization: Bearer <access_token>
```

**Response** (200 OK)
```json
{
  "id": 1,
  "title": "API 설계",
  "description": "RESTful API 설계 및 문서화",
  "status": "in_progress",
  "priority": "high",
  "project_id": 1,
  "assignee_id": 2,
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2024-01-15T14:30:00Z"
}
```

**Error Responses**
- `404 Not Found`: 태스크가 존재하지 않음
  ```json
  {
    "detail": "태스크를 찾을 수 없습니다."
  }
  ```

---

### 4. 태스크 수정

태스크 정보를 수정합니다. 모든 필드는 선택 사항입니다.

```http
PUT /api/v1/projects/{project_id}/tasks/{task_id}
```

**Headers**
```http
Authorization: Bearer <access_token>
```

**Request Body**
```json
{
  "title": "API 설계 및 구현",
  "description": "RESTful API 설계, 문서화 및 구현",
  "status": "done",
  "priority": "critical",
  "assignee_id": 3
}
```

**Validation Rules**
- 모든 필드 선택 (부분 업데이트 가능)
- `title`: 최대 300자
- `description`: 최대 5000자
- `status`: "todo" | "in_progress" | "done"
- `priority`: "low" | "medium" | "high" | "critical"
- `assignee_id`: 프로젝트 멤버여야 함 (null 가능)

**Response** (200 OK)
```json
{
  "id": 1,
  "title": "API 설계 및 구현",
  "description": "RESTful API 설계, 문서화 및 구현",
  "status": "done",
  "priority": "critical",
  "project_id": 1,
  "assignee_id": 3,
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2024-01-15T16:00:00Z"
}
```

**Error Responses**
- `404 Not Found`: 태스크가 존재하지 않음

---

### 5. 태스크 상태 변경

태스크의 상태만 변경합니다. 드래그 앤 드롭 칸반 보드에서 주로 사용됩니다.

```http
PATCH /api/v1/projects/{project_id}/tasks/{task_id}/status
```

**Headers**
```http
Authorization: Bearer <access_token>
```

**Request Body**
```json
{
  "status": "done"
}
```

**Validation Rules**
- `status`: 필수, "todo" | "in_progress" | "done"

**Response** (200 OK)
```json
{
  "id": 1,
  "title": "API 설계",
  "description": "RESTful API 설계 및 문서화",
  "status": "done",
  "priority": "high",
  "project_id": 1,
  "assignee_id": 2,
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2024-01-15T16:30:00Z"
}
```

---

### 6. 태스크 삭제

태스크를 삭제합니다. CASCADE 삭제로 관련된 댓글도 모두 삭제됩니다.

```http
DELETE /api/v1/projects/{project_id}/tasks/{task_id}
```

**Headers**
```http
Authorization: Bearer <access_token>
```

**Response** (204 No Content)
- Body 없음

**Error Responses**
- `404 Not Found`: 태스크가 존재하지 않음

---

## 댓글 API

### 1. 댓글 생성

태스크에 댓글을 작성합니다.

```http
POST /api/v1/projects/{project_id}/tasks/{task_id}/comments
```

**Headers**
```http
Authorization: Bearer <access_token>
```

**Request Body**
```json
{
  "content": "API 설계 초안을 검토했습니다. 수정 사항이 있습니다."
}
```

**Validation Rules**
- `content`: 필수, 텍스트

**Response** (201 Created)
```json
{
  "id": 1,
  "content": "API 설계 초안을 검토했습니다. 수정 사항이 있습니다.",
  "task_id": 1,
  "author_id": 3,
  "created_at": "2024-01-15T17:00:00Z"
}
```

**Error Responses**
- `404 Not Found`: 태스크가 존재하지 않음

---

### 2. 댓글 목록 조회

태스크의 모든 댓글을 시간순으로 조회합니다.

```http
GET /api/v1/projects/{project_id}/tasks/{task_id}/comments
```

**Headers**
```http
Authorization: Bearer <access_token>
```

**Response** (200 OK)
```json
[
  {
    "id": 1,
    "content": "API 설계 초안을 검토했습니다. 수정 사항이 있습니다.",
    "task_id": 1,
    "author_id": 3,
    "created_at": "2024-01-15T17:00:00Z"
  },
  {
    "id": 2,
    "content": "수정 완료했습니다.",
    "task_id": 1,
    "author_id": 2,
    "created_at": "2024-01-15T17:30:00Z"
  }
]
```

**Error Responses**
- `404 Not Found`: 태스크가 존재하지 않음

---

## 에러 응답

### 공통 에러 형식

모든 에러는 다음 형식을 따릅니다:

```json
{
  "detail": "에러 메시지 설명"
}
```

### HTTP 상태 코드

| 코드 | 의미 | 설명 |
|------|------|------|
| 200 | OK | 성공 (조회, 수정) |
| 201 | Created | 성공 (생성) |
| 204 | No Content | 성공 (삭제, 응답 본문 없음) |
| 400 | Bad Request | 잘못된 요청 (유효성 검증 실패) |
| 401 | Unauthorized | 인증 필요 또는 토큰 유효하지 않음 |
| 403 | Forbidden | 권한 없음 (접근 거부) |
| 404 | Not Found | 리소스 없음 |
| 422 | Unprocessable Entity | 처리 불가능 (비즈니스 로직 오류, 중복 등) |
| 500 | Internal Server Error | 서버 오류 |

### 예시

**401 Unauthorized - 토큰 없음**
```json
{
  "detail": "Not authenticated"
}
```

**403 Forbidden - 권한 없음**
```json
{
  "detail": "프로젝트 멤버가 아닙니다."
}
```

**404 Not Found - 리소스 없음**
```json
{
  "detail": "태스크를 찾을 수 없습니다."
}
```

**422 Unprocessable Entity - 중복**
```json
{
  "detail": "이미 존재하는 이메일입니다."
}
```

---

## 데이터 타입 정리

### TaskStatus
```typescript
type TaskStatus = "todo" | "in_progress" | "done";
```

### TaskPriority
```typescript
type TaskPriority = "low" | "medium" | "high" | "critical";
```

### ProjectRole
```typescript
type ProjectRole = "owner" | "admin" | "member";
```

---

## API 테스트 예시

### curl을 이용한 테스트

**회원가입**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "테스트",
    "password": "testpass123"
  }'
```

**로그인**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

**프로젝트 생성 (토큰 필요)**
```bash
curl -X POST http://localhost:8000/api/v1/projects/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "name": "테스트 프로젝트",
    "description": "테스트용 프로젝트입니다."
  }'
```

**태스크 생성**
```bash
curl -X POST http://localhost:8000/api/v1/projects/1/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{
    "title": "테스트 태스크",
    "description": "테스트용 태스크",
    "priority": "high"
  }'
```

---

## 추가 정보

### 자동 생성 문서

FastAPI는 자동으로 Swagger UI와 ReDoc을 제공합니다.

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

개발 중에는 위 URL에서 대화형으로 API를 테스트할 수 있습니다.

### CORS 설정

프론트엔드 개발을 위해 CORS가 설정되어 있습니다.
- 기본값: `http://localhost:3000`
- 환경변수 `BACKEND_CORS_ORIGINS`로 변경 가능 (쉼표로 구분하여 여러 origin 허용)

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| v1.0 | 2024-02-11 | 초기 API 문서 작성 |
