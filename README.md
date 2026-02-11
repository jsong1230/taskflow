# TaskFlow

**팀 협업을 위한 칸반 보드 태스크 관리 웹 애플리케이션**

TaskFlow는 팀 프로젝트의 태스크를 직관적인 칸반 보드로 관리할 수 있는 웹 애플리케이션입니다. 드래그 앤 드롭으로 태스크 상태를 변경하고, 댓글로 소통하며, 대시보드에서 프로젝트 진행 상황을 한눈에 파악할 수 있습니다.

---

## ✨ 주요 기능

### 🎯 대시보드
- 전체 프로젝트 및 태스크 현황 요약
- 내게 배정된 태스크 목록
- 프로젝트별 완료율 진행 바

### 📋 칸반 보드
- **드래그 앤 드롭**으로 태스크 상태 변경 (Todo → In Progress → Done)
- 3가지 상태 컬럼 (Todo, In Progress, Done)
- 태스크 카드에 우선순위 뱃지 및 담당자 표시

### ✏️ 태스크 관리
- 태스크 생성, 수정, 삭제
- 제목, 설명, 상태, 우선순위(낮음/보통/높음/긴급) 설정
- 담당자 배정
- 태스크별 댓글 작성 및 조회

### 👥 프로젝트 관리
- 프로젝트 생성 및 관리
- 프로젝트 멤버 초대 (Owner/Admin/Member 역할)
- 프로젝트별 태스크 분리 관리

### 🔐 사용자 인증
- 회원가입 및 로그인 (JWT 기반)
- 비밀번호 암호화 (bcrypt)

---

## 🛠 기술 스택

### 백엔드
- **Python 3.12**
- **FastAPI** - 고성능 비동기 웹 프레임워크
- **SQLAlchemy 2.0** - ORM (async 지원)
- **Alembic** - 데이터베이스 마이그레이션
- **PostgreSQL 16** - 관계형 데이터베이스
- **JWT (python-jose)** - 인증/인가
- **bcrypt (passlib)** - 비밀번호 해싱

### 프론트엔드
- **Next.js 15 (App Router)** - React 프레임워크
- **TypeScript** - 타입 안정성
- **Tailwind CSS** - 유틸리티 우선 CSS 프레임워크
- **HTML5 Drag and Drop API** - 드래그 앤 드롭 (외부 라이브러리 없음)

### 인프라
- **Docker & Docker Compose** - 컨테이너화 및 로컬 개발 환경

---

## 📁 프로젝트 구조

```
taskflow/
├── backend/                    # FastAPI 백엔드
│   ├── app/
│   │   ├── api/               # API 라우터
│   │   │   └── v1/
│   │   │       ├── auth.py    # 인증 API
│   │   │       ├── projects.py # 프로젝트/태스크/댓글 API
│   │   │       └── health.py  # 헬스체크
│   │   ├── core/              # 설정, 보안, 의존성
│   │   ├── models/            # SQLAlchemy 모델
│   │   ├── schemas/           # Pydantic 스키마
│   │   ├── services/          # 비즈니스 로직
│   │   └── tests/             # 테스트
│   ├── alembic/               # 마이그레이션 파일
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/                   # Next.js 프론트엔드
│   ├── app/
│   │   ├── dashboard/         # 대시보드 페이지
│   │   ├── projects/          # 프로젝트 목록 & 칸반 보드
│   │   ├── login/             # 로그인 페이지
│   │   └── register/          # 회원가입 페이지
│   ├── components/
│   │   ├── kanban/            # 칸반 보드 컴포넌트
│   │   └── dashboard/         # 대시보드 컴포넌트
│   ├── lib/
│   │   └── api.ts             # API 클라이언트
│   ├── types/
│   │   └── api.ts             # TypeScript 타입 정의
│   ├── package.json
│   └── Dockerfile
│
├── docs/                       # 문서
│   └── plans/                 # 구현 계획 문서
├── docker-compose.yml
├── .env.example
├── CLAUDE.md                  # 프로젝트 가이드라인
└── README.md
```

---

## 🚀 시작하기

### 사전 요구사항

- **Docker** 및 **Docker Compose** 설치
- (또는) **Python 3.12+**, **Node.js 18+**, **PostgreSQL 16**

### 1. 환경변수 설정

```bash
# 루트 디렉토리에서
cp .env.example .env

# 환경변수 편집 (필요한 경우)
# - DATABASE_URL
# - JWT_SECRET_KEY
# - NEXT_PUBLIC_API_URL
```

### 2. Docker Compose로 실행 (권장)

```bash
# 전체 스택 실행 (PostgreSQL + Backend + Frontend)
docker compose up -d

# 로그 확인
docker compose logs -f

# 중지
docker compose down
```

**접속 URL:**
- 프론트엔드: http://localhost:3000
- 백엔드 API: http://localhost:8000
- API 문서: http://localhost:8000/docs

### 3. 로컬 개발 환경 (Docker 없이)

#### 백엔드 실행

```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 데이터베이스 마이그레이션
alembic upgrade head

# 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 프론트엔드 실행

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

---

## 📖 사용 방법

### 1. 회원가입 및 로그인
1. http://localhost:3000/register 에서 계정 생성
2. 로그인하여 JWT 토큰 발급

### 2. 프로젝트 생성
1. **대시보드** (`/dashboard`) 또는 **프로젝트 목록** (`/projects`) 페이지에서 "새 프로젝트" 버튼 클릭
2. 프로젝트 이름 및 설명 입력

### 3. 칸반 보드 사용
1. 프로젝트 카드를 클릭하여 칸반 보드 진입
2. 각 컬럼의 **"+ 태스크 추가"** 버튼으로 태스크 생성
3. 태스크 카드를 **드래그하여 다른 컬럼으로 이동** (상태 변경)
4. 태스크 카드를 **클릭**하여 상세 정보 보기/수정

### 4. 태스크 상세 관리
- **제목/설명** 인라인 편집
- **상태/우선순위** 드롭다운으로 변경
- **댓글** 작성 및 조회
- **태스크 삭제**

### 5. 대시보드 확인
- `/dashboard`에서 전체 프로젝트 현황 요약 확인
- 내게 배정된 태스크 목록 확인
- 프로젝트별 진행률 확인

---

## 🗄️ 데이터베이스 스키마

### 주요 테이블

#### `users` - 사용자
- id, email (unique), hashed_password, name, created_at

#### `projects` - 프로젝트
- id, name, description, owner_id (FK → users), created_at

#### `project_members` - 프로젝트 멤버십
- id, user_id (FK → users), project_id (FK → projects), role (owner/admin/member)
- UniqueConstraint(user_id, project_id)

#### `tasks` - 태스크
- id, title, description, status (todo/in_progress/done), priority (low/medium/high/critical)
- project_id (FK → projects), assignee_id (FK → users, nullable)
- created_at, updated_at

#### `comments` - 댓글
- id, content, task_id (FK → tasks), author_id (FK → users), created_at

---

## 🔌 API 엔드포인트

### 인증 (`/api/v1/auth`)
- `POST /register` - 회원가입
- `POST /login` - 로그인 (JWT 발급)
- `GET /me` - 현재 사용자 정보

### 프로젝트 (`/api/v1/projects`)
- `POST /` - 프로젝트 생성
- `GET /` - 내 프로젝트 목록
- `GET /{project_id}` - 프로젝트 상세
- `PUT /{project_id}` - 프로젝트 수정
- `DELETE /{project_id}` - 프로젝트 삭제
- `POST /{project_id}/members` - 멤버 추가

### 태스크 (`/api/v1/projects/{project_id}/tasks`)
- `POST /` - 태스크 생성
- `GET /` - 태스크 목록 (필터/정렬 지원)
- `GET /{task_id}` - 태스크 상세
- `PUT /{task_id}` - 태스크 수정
- `PATCH /{task_id}/status` - 태스크 상태 변경
- `DELETE /{task_id}` - 태스크 삭제

### 댓글 (`/api/v1/projects/{project_id}/tasks/{task_id}/comments`)
- `POST /` - 댓글 작성
- `GET /` - 댓글 목록

**전체 API 문서**: http://localhost:8000/docs (Swagger UI)

---

## 🧪 테스트

### 백엔드 테스트

```bash
cd backend

# 전체 테스트 실행
pytest -v

# 특정 테스트 실행
pytest app/tests/test_health.py -v

# 커버리지 포함
pytest --cov=app --cov-report=html
```

---

## 🎨 주요 기능 상세

### 드래그 앤 드롭 구현
- **HTML5 Drag and Drop API** 사용 (외부 라이브러리 없음)
- **낙관적 업데이트(Optimistic Update)**: 즉시 UI 변경 → 서버 요청 → 실패 시 자동 롤백
- 부드러운 시각적 피드백

### 상태 관리
- React hooks (`useState`, `useEffect`)
- 로컬 상태: UI 및 모달 상태
- 서버 상태: API 데이터 (fetch 후 캐싱)

### 권한 관리
- JWT Bearer 토큰 기반 인증
- 프로젝트 멤버십 역할 (Owner/Admin/Member)
- API 레벨에서 권한 검증 (`get_project_member` dependency)

---

## 🔒 보안 고려사항

- ✅ 비밀번호 bcrypt 해싱
- ✅ JWT 토큰 기반 인증
- ✅ SQL Injection 방어 (SQLAlchemy 파라미터화된 쿼리)
- ✅ CORS 설정
- ✅ 환경변수로 민감 정보 관리
- ⚠️ HTTPS 사용 권장 (프로덕션 환경)
- ⚠️ Rate Limiting 추가 권장

---

## 📝 코딩 컨벤션

### 백엔드 (Python)
- **PEP 8** 스타일 가이드
- Type hints 필수
- `snake_case` (함수/변수), `PascalCase` (클래스)
- async/await 패턴

### 프론트엔드 (TypeScript)
- **ESLint + Prettier**
- 함수형 컴포넌트
- `camelCase` (함수/변수), `PascalCase` (컴포넌트/타입)
- Server Components 우선, 필요시 Client Components

### Git Commit
- **Conventional Commits** 형식
  - `feat:` - 새로운 기능
  - `fix:` - 버그 수정
  - `refactor:` - 코드 리팩토링
  - `docs:` - 문서 수정
  - `test:` - 테스트 추가/수정
  - `chore:` - 빌드, 설정 수정

---

## 🚧 향후 개선 사항

- [ ] 실시간 협업 (WebSocket)
- [ ] 태스크 검색 및 고급 필터링
- [ ] 파일 첨부 기능
- [ ] 마감일 알림
- [ ] 활동 로그 (Activity Feed)
- [ ] 다크 모드
- [ ] 모바일 앱 (React Native)
- [ ] 이메일 알림
- [ ] 태스크 템플릿
- [ ] 커스텀 컬럼 상태

---

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feat/amazing-feature`)
5. Open a Pull Request

---

## 📄 라이센스

This project is licensed under the MIT License.

---

## 👨‍💻 개발자

**TaskFlow Team**

- 문의: taskflow@example.com
- GitHub Issues: [Issues](https://github.com/yourusername/taskflow/issues)

---

## 🙏 감사의 말

- [FastAPI](https://fastapi.tiangolo.com/)
- [Next.js](https://nextjs.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)

---

**Happy Task Managing! 🎯**
