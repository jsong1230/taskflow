# TaskFlow - Docker 설정 가이드

TaskFlow 프로젝트의 Docker 컨테이너화 및 배포 가이드입니다.

## 목차
- [개요](#개요)
- [개발 환경](#개발-환경)
- [프로덕션 환경](#프로덕션-환경)
- [Docker 이미지 최적화](#docker-이미지-최적화)
- [트러블슈팅](#트러블슈팅)

## 개요

### 아키텍처
```
┌─────────────────────────────────────────────┐
│              Nginx (Production)              │
│         Reverse Proxy & Load Balancer        │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
┌───────▼────────┐   ┌────────▼───────┐
│   Frontend     │   │    Backend     │
│   Next.js 15   │   │   FastAPI      │
│   Port: 3000   │   │   Port: 8000   │
└────────────────┘   └────────┬───────┘
                              │
                     ┌────────▼────────┐
                     │   PostgreSQL    │
                     │   Port: 5432    │
                     └─────────────────┘
```

### 컨테이너 구성
- **Database (PostgreSQL 16)**: 데이터 저장
- **Backend (FastAPI)**: REST API 서버
- **Frontend (Next.js 15)**: 사용자 인터페이스
- **Nginx (Production)**: 리버스 프록시 및 로드 밸런싱

## 개발 환경

### 사전 요구사항
- Docker Engine 24.0+
- Docker Compose 2.0+
- 최소 4GB RAM
- 10GB 디스크 공간

### 빠른 시작

1. **환경변수 설정**
```bash
# .env 파일 생성
cp .env.example .env

# 필요시 환경변수 수정
nano .env
```

2. **컨테이너 시작**
```bash
# 모든 서비스 시작 (백그라운드)
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그만 확인
docker-compose logs -f backend
```

3. **데이터베이스 마이그레이션**
```bash
# Alembic 마이그레이션 실행
docker-compose exec backend alembic upgrade head

# 마이그레이션 생성 (모델 변경 시)
docker-compose exec backend alembic revision --autogenerate -m "describe your changes"
```

4. **서비스 접근**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5433 (외부 접근용)

### 개발 모드 특징

- **핫 리로드**: 코드 변경 시 자동 재시작
- **볼륨 마운트**: 로컬 파일 시스템과 동기화
- **디버깅 지원**: 포트가 호스트에 노출됨
- **개발용 Dockerfile**: `Dockerfile.dev` 사용

### 유용한 명령어

```bash
# 컨테이너 상태 확인
docker-compose ps

# 특정 서비스 재시작
docker-compose restart backend

# 컨테이너 내부 접속
docker-compose exec backend bash
docker-compose exec frontend sh

# 로그 실시간 모니터링
docker-compose logs -f --tail=100

# 데이터베이스 접속
docker-compose exec db psql -U taskflow -d taskflow

# 컨테이너 중지
docker-compose stop

# 컨테이너 중지 및 삭제
docker-compose down

# 볼륨까지 모두 삭제 (주의: 데이터 손실!)
docker-compose down -v
```

## 프로덕션 환경

### 사전 준비

1. **환경변수 설정**
```bash
# .env.production 파일 생성
cp .env.production.example .env.production

# 프로덕션 환경변수 수정
nano .env.production
```

2. **SSL 인증서 준비** (HTTPS 사용 시)
```bash
# SSL 인증서 디렉토리 생성
mkdir -p nginx/ssl

# 인증서 복사 (Let's Encrypt, 상용 인증서 등)
cp /path/to/cert.pem nginx/ssl/
cp /path/to/key.pem nginx/ssl/

# 권한 설정
chmod 600 nginx/ssl/key.pem
```

3. **nginx.conf 수정**
```bash
# nginx/nginx.conf 파일에서 SSL 설정 주석 해제
# server_name을 실제 도메인으로 변경
nano nginx/nginx.conf
```

### 배포

1. **이미지 빌드**
```bash
# 프로덕션 이미지 빌드
docker-compose -f docker-compose.prod.yml build

# 캐시 없이 빌드 (클린 빌드)
docker-compose -f docker-compose.prod.yml build --no-cache
```

2. **서비스 시작**
```bash
# 프로덕션 모드로 시작
docker-compose -f docker-compose.prod.yml up -d

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f
```

3. **헬스 체크**
```bash
# 모든 서비스 상태 확인
docker-compose -f docker-compose.prod.yml ps

# 개별 헬스 체크
curl http://localhost/health                    # Nginx
curl http://localhost/api/v1/health            # Backend (through Nginx)
```

### 프로덕션 모드 특징

- **최적화된 이미지**: 멀티스테이지 빌드로 이미지 크기 최소화
- **리소스 제한**: CPU 및 메모리 제한 설정
- **보안 강화**: 비루트 사용자, 최소 권한 원칙
- **로그 관리**: 자동 로그 로테이션 (10MB, 최대 3개 파일)
- **헬스 체크**: 자동 컨테이너 상태 모니터링
- **리버스 프록시**: Nginx를 통한 부하 분산 및 SSL 종료

### 배포 체크리스트

- [ ] `.env.production` 파일에 프로덕션 설정 완료
- [ ] 강력한 `POSTGRES_PASSWORD` 설정
- [ ] 안전한 `JWT_SECRET_KEY` 생성 (openssl rand -hex 32)
- [ ] `BACKEND_CORS_ORIGINS`에 프로덕션 도메인 추가
- [ ] `NEXT_PUBLIC_API_URL` 프로덕션 URL로 설정
- [ ] `DEBUG=false` 설정
- [ ] SSL 인증서 설치 및 nginx 설정
- [ ] 방화벽 규칙 설정 (80, 443 포트만 외부 개방)
- [ ] 데이터베이스 백업 설정
- [ ] 모니터링 및 알림 설정
- [ ] 헬스 체크 엔드포인트 테스트

## Docker 이미지 최적화

### 백엔드 Dockerfile 특징

```dockerfile
# 멀티스테이지 빌드
FROM python:3.12-slim AS builder  # 빌드 단계
FROM python:3.12-slim AS runtime  # 런타임 단계
```

**최적화 포인트:**
- 멀티스테이지 빌드로 최종 이미지 크기 50% 감소
- 빌드 의존성과 런타임 의존성 분리
- Layer 캐싱: requirements.txt 먼저 복사
- 비루트 사용자(appuser) 사용
- 헬스 체크 내장
- 불필요한 패키지 제거

### 프론트엔드 Dockerfile 특징

```dockerfile
FROM node:20-alpine AS base      # 베이스
FROM base AS deps                # 의존성 설치
FROM base AS builder             # Next.js 빌드
FROM base AS runner              # 프로덕션 실행
```

**최적화 포인트:**
- 3단계 멀티스테이지 빌드
- Alpine Linux 사용 (이미지 크기 70% 감소)
- Standalone 출력 모드 (필요한 파일만 포함)
- 비루트 사용자(nextjs) 사용
- npm ci 사용 (재현 가능한 빌드)

### 이미지 크기 비교

```bash
# 이미지 크기 확인
docker images | grep taskflow

# 예상 크기:
# taskflow-backend:   ~250MB (최적화 전: ~500MB)
# taskflow-frontend:  ~150MB (최적화 전: ~500MB)
# postgres:16-alpine: ~250MB
```

### .dockerignore의 중요성

불필요한 파일을 제외하여 빌드 속도 향상 및 이미지 크기 감소:
- 개발 의존성 (node_modules, venv)
- 빌드 아티팩트 (.next, __pycache__)
- Git 및 IDE 설정
- 테스트 파일 및 문서

## 모니터링 및 관리

### 리소스 사용량 확인

```bash
# 실시간 리소스 모니터링
docker stats

# 특정 컨테이너만 모니터링
docker stats taskflow-backend taskflow-frontend
```

### 로그 관리

```bash
# 로그 파일 위치 확인
docker inspect taskflow-backend | grep LogPath

# 로그 크기 확인
du -sh /var/lib/docker/containers/*/

# 로그 정리 (프로덕션에서는 자동 로테이션 설정됨)
docker-compose logs --tail=0 -f  # 새 로그만 표시
```

### 백업 및 복원

```bash
# 데이터베이스 백업
docker-compose exec db pg_dump -U taskflow taskflow > backup_$(date +%Y%m%d_%H%M%S).sql

# 데이터베이스 복원
docker-compose exec -T db psql -U taskflow taskflow < backup_20240101_120000.sql

# 볼륨 백업
docker run --rm -v taskflow_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```

## 트러블슈팅

### 일반적인 문제

**문제: 포트가 이미 사용 중**
```bash
# 포트 사용 확인
lsof -i :8000
lsof -i :3000
lsof -i :5433

# 해결: .env 파일에서 포트 변경
BACKEND_PORT=8001
FRONTEND_PORT=3001
POSTGRES_PORT=5434
```

**문제: 데이터베이스 연결 실패**
```bash
# 데이터베이스 상태 확인
docker-compose exec db pg_isready -U taskflow

# 연결 테스트
docker-compose exec backend python -c "from app.core.database import engine; import asyncio; asyncio.run(engine.connect())"

# 로그 확인
docker-compose logs db
```

**문제: 프론트엔드가 백엔드에 연결되지 않음**
```bash
# 환경변수 확인
docker-compose exec frontend env | grep NEXT_PUBLIC_API_URL

# 네트워크 연결 테스트
docker-compose exec frontend wget -O- http://backend:8000/api/v1/health
```

**문제: 빌드 실패**
```bash
# 캐시 삭제 후 재빌드
docker-compose build --no-cache

# 개별 서비스 재빌드
docker-compose build --no-cache backend

# 빌드 로그 상세 확인
docker-compose build --progress=plain backend
```

### 컨테이너 디버깅

```bash
# 컨테이너 내부 조사
docker-compose exec backend bash
docker-compose exec frontend sh

# 컨테이너 로그 실시간 확인
docker-compose logs -f backend

# 헬스 체크 상태 확인
docker inspect --format='{{json .State.Health}}' taskflow-backend | jq

# 네트워크 문제 진단
docker-compose exec backend ping db
docker-compose exec frontend ping backend
```

### 성능 최적화

```bash
# 사용하지 않는 이미지 정리
docker image prune -a

# 중지된 컨테이너 정리
docker container prune

# 사용하지 않는 볼륨 정리 (주의!)
docker volume prune

# 전체 시스템 정리
docker system prune -a --volumes
```

## 보안 권장사항

1. **환경변수 보호**
   - `.env` 파일을 Git에 커밋하지 않기
   - 프로덕션 시크릿은 별도 시크릿 관리 도구 사용 (AWS Secrets Manager, HashiCorp Vault)

2. **네트워크 격리**
   - 프로덕션에서는 데이터베이스 포트를 호스트에 노출하지 않기
   - 커스텀 Docker 네트워크 사용

3. **이미지 보안**
   - 정기적으로 베이스 이미지 업데이트
   - 취약점 스캔: `docker scan taskflow-backend`
   - 비루트 사용자로 컨테이너 실행

4. **리소스 제한**
   - CPU 및 메모리 제한 설정하여 DoS 공격 방지
   - docker-compose.prod.yml에 리소스 제한 구성됨

## 참고 자료

- [Docker 공식 문서](https://docs.docker.com/)
- [Docker Compose 문서](https://docs.docker.com/compose/)
- [Next.js Docker 배포](https://nextjs.org/docs/deployment#docker-image)
- [FastAPI Docker 배포](https://fastapi.tiangolo.com/deployment/docker/)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [Nginx Docker Hub](https://hub.docker.com/_/nginx)

## 지원

문제가 발생하면 다음을 확인하세요:
1. 로그 확인: `docker-compose logs`
2. 헬스 체크 상태: `docker-compose ps`
3. 환경변수 설정: `.env` 파일 확인
4. GitHub Issues에 문의
