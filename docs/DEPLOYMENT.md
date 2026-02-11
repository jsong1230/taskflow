# TaskFlow 배포 가이드

## 목차
- [배포 개요](#배포-개요)
- [Docker Compose를 이용한 배포](#docker-compose를-이용한-배포)
- [환경변수 설정](#환경변수-설정)
- [데이터베이스 설정](#데이터베이스-설정)
- [프로덕션 환경 설정](#프로덕션-환경-설정)
- [HTTPS 설정](#https-설정)
- [성능 최적화](#성능-최적화)
- [백업 및 복구](#백업-및-복구)
- [모니터링](#모니터링)
- [트러블슈팅](#트러블슈팅)

---

## 배포 개요

TaskFlow는 Docker Compose를 이용하여 쉽게 배포할 수 있습니다. 프로덕션 환경에서는 다음 사항을 고려해야 합니다.

- **환경변수 보안**: JWT 비밀키, 데이터베이스 비밀번호 등
- **HTTPS 설정**: Nginx 또는 Caddy를 이용한 리버스 프록시
- **데이터베이스 백업**: 정기적인 백업 및 복구 전략
- **로깅 및 모니터링**: 에러 추적 및 성능 모니터링

---

## Docker Compose를 이용한 배포

### 1. 서버 준비

**최소 시스템 요구사항**
- CPU: 2 core
- RAM: 4GB
- Disk: 20GB
- OS: Ubuntu 20.04+ 또는 Debian 11+

**Docker 및 Docker Compose 설치**

```bash
# Docker 설치 (Ubuntu/Debian)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 현재 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER
newgrp docker

# 버전 확인
docker --version
docker-compose --version
```

### 2. 프로젝트 클론 및 설정

```bash
# 서버에 프로젝트 클론
git clone https://github.com/your-username/taskflow.git
cd taskflow

# 환경변수 파일 생성
cp .env.example .env
nano .env  # 또는 vim .env
```

### 3. 프로덕션 환경변수 설정

`.env` 파일을 수정하여 프로덕션 값을 설정합니다.

```bash
# Database
POSTGRES_USER=taskflow
POSTGRES_PASSWORD=CHANGE_THIS_TO_STRONG_PASSWORD
POSTGRES_DB=taskflow
DATABASE_URL=postgresql+asyncpg://taskflow:CHANGE_THIS_TO_STRONG_PASSWORD@db:5432/taskflow

# JWT
JWT_SECRET_KEY=CHANGE_THIS_TO_RANDOM_SECRET_KEY
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (프로덕션 도메인으로 변경)
BACKEND_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Frontend API URL (프로덕션 도메인으로 변경)
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

**비밀키 생성 방법**

```bash
# JWT 비밀키 생성 (랜덤 문자열)
openssl rand -hex 32

# 또는 Python으로 생성
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. 프로덕션 Docker Compose 파일

프로덕션 환경을 위한 `docker-compose.prod.yml` 파일을 생성합니다.

```yaml
# docker-compose.prod.yml
services:
  db:
    image: postgres:16-alpine
    restart: always
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - taskflow-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: always
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
    networks:
      - taskflow-network
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    restart: always
    env_file:
      - .env
    depends_on:
      - backend
    networks:
      - taskflow-network

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend
    networks:
      - taskflow-network

volumes:
  postgres_data:

networks:
  taskflow-network:
    driver: bridge
```

### 5. 서비스 시작

```bash
# 프로덕션 환경으로 빌드 및 시작
docker-compose -f docker-compose.prod.yml up -d --build

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f

# 특정 서비스 로그 확인
docker-compose -f docker-compose.prod.yml logs -f backend

# 서비스 상태 확인
docker-compose -f docker-compose.prod.yml ps
```

### 6. 데이터베이스 마이그레이션

```bash
# 백엔드 컨테이너에서 마이그레이션 실행
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

---

## 환경변수 설정

### 백엔드 환경변수

| 변수명 | 설명 | 기본값 | 필수 |
|--------|------|--------|------|
| `DATABASE_URL` | PostgreSQL 연결 URL | - | O |
| `JWT_SECRET_KEY` | JWT 서명 키 | - | O |
| `JWT_ALGORITHM` | JWT 알고리즘 | HS256 | X |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 토큰 만료 시간 (분) | 30 | X |
| `BACKEND_CORS_ORIGINS` | CORS 허용 오리진 (쉼표 구분) | http://localhost:3000 | O |

### 프론트엔드 환경변수

| 변수명 | 설명 | 기본값 | 필수 |
|--------|------|--------|------|
| `NEXT_PUBLIC_API_URL` | 백엔드 API URL | http://localhost:8000 | O |

### 데이터베이스 환경변수

| 변수명 | 설명 | 기본값 | 필수 |
|--------|------|--------|------|
| `POSTGRES_USER` | PostgreSQL 사용자명 | taskflow | O |
| `POSTGRES_PASSWORD` | PostgreSQL 비밀번호 | - | O |
| `POSTGRES_DB` | 데이터베이스 이름 | taskflow | O |

---

## 데이터베이스 설정

### PostgreSQL 튜닝

프로덕션 환경에서는 PostgreSQL 설정을 최적화해야 합니다.

```yaml
# docker-compose.prod.yml (db 서비스)
db:
  image: postgres:16-alpine
  command:
    - postgres
    - -c
    - max_connections=100
    - -c
    - shared_buffers=256MB
    - -c
    - effective_cache_size=1GB
    - -c
    - maintenance_work_mem=64MB
    - -c
    - checkpoint_completion_target=0.9
    - -c
    - wal_buffers=16MB
    - -c
    - default_statistics_target=100
```

### 데이터베이스 백업 설정

Docker volume을 이용한 자동 백업:

```bash
# 백업 스크립트 생성
cat > backup-db.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
mkdir -p $BACKUP_DIR

docker-compose -f docker-compose.prod.yml exec -T db \
  pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} | \
  gzip > ${BACKUP_DIR}/taskflow_${DATE}.sql.gz

# 30일 이상 된 백업 삭제
find ${BACKUP_DIR} -name "taskflow_*.sql.gz" -mtime +30 -delete

echo "Backup completed: taskflow_${DATE}.sql.gz"
EOF

chmod +x backup-db.sh
```

**cron으로 자동 백업 설정 (매일 새벽 2시)**

```bash
# crontab 편집
crontab -e

# 다음 줄 추가
0 2 * * * /path/to/taskflow/backup-db.sh >> /var/log/taskflow-backup.log 2>&1
```

---

## 프로덕션 환경 설정

### 프로덕션 Dockerfile (백엔드)

```dockerfile
# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY . .

# 비root 사용자 생성
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 포트 노출
EXPOSE 8000

# 시작 명령
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 프로덕션 Dockerfile (프론트엔드)

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# 의존성 설치
COPY package*.json ./
RUN npm ci --only=production

# 앱 빌드
COPY . .
RUN npm run build

# 프로덕션 이미지
FROM node:18-alpine

WORKDIR /app

# 빌드된 파일과 의존성 복사
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

# 비root 사용자 생성
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001
RUN chown -R nextjs:nodejs /app
USER nextjs

# 포트 노출
EXPOSE 3000

# 시작 명령
CMD ["npm", "start"]
```

---

## HTTPS 설정

### Nginx를 이용한 리버스 프록시

#### 1. Nginx 설정 파일

```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    # HTTP to HTTPS 리다이렉트
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            return 301 https://$host$request_uri;
        }
    }

    # HTTPS 설정
    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        # SSL 설정
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # API 프록시
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # 프론트엔드 프록시
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

#### 2. Let's Encrypt SSL 인증서 발급

```bash
# Certbot 설치
sudo apt install certbot python3-certbot-nginx

# SSL 인증서 발급
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 자동 갱신 테스트
sudo certbot renew --dry-run

# 자동 갱신 cron 설정 (이미 설치됨)
sudo systemctl status certbot.timer
```

또는 Docker를 이용한 Certbot:

```yaml
# docker-compose.prod.yml에 추가
certbot:
  image: certbot/certbot
  volumes:
    - ./nginx/ssl:/etc/letsencrypt
    - ./nginx/certbot:/var/www/certbot
  entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
```

```bash
# 초기 인증서 발급
docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  -d yourdomain.com -d www.yourdomain.com \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email
```

---

## 성능 최적화

### 1. 백엔드 최적화

#### Gunicorn과 Uvicorn 워커 사용

```dockerfile
# backend/Dockerfile
CMD ["gunicorn", "app.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
```

#### 데이터베이스 연결 풀 설정

```python
# app/core/database.py
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,           # 기본 연결 수
    max_overflow=40,        # 추가 연결 수
    pool_pre_ping=True,     # 연결 상태 확인
    pool_recycle=3600,      # 1시간마다 연결 재생성
)
```

#### 캐싱 (Redis)

추후 Redis를 추가하여 세션 및 쿼리 결과 캐싱을 구현할 수 있습니다.

```yaml
# docker-compose.prod.yml
redis:
  image: redis:7-alpine
  restart: always
  volumes:
    - redis_data:/data
  networks:
    - taskflow-network

volumes:
  redis_data:
```

### 2. 프론트엔드 최적화

#### Next.js 빌드 최적화

```javascript
// next.config.ts
const config = {
  output: 'standalone',
  compress: true,
  images: {
    domains: ['yourdomain.com'],
    formats: ['image/avif', 'image/webp'],
  },
  poweredByHeader: false,
};
```

#### 정적 파일 캐싱 (Nginx)

```nginx
# nginx/nginx.conf
location /_next/static {
    proxy_pass http://frontend;
    proxy_cache_valid 200 30d;
    add_header Cache-Control "public, max-age=2592000, immutable";
}

location /static {
    proxy_pass http://frontend;
    proxy_cache_valid 200 7d;
    add_header Cache-Control "public, max-age=604800";
}
```

---

## 백업 및 복구

### 백업 전략

#### 1. 데이터베이스 백업

```bash
# 수동 백업
docker-compose -f docker-compose.prod.yml exec db \
  pg_dump -U taskflow taskflow | gzip > taskflow_backup_$(date +%Y%m%d).sql.gz

# 원격 서버에 백업 전송 (rsync)
rsync -avz --delete /backups/ user@backup-server:/remote/backups/
```

#### 2. 애플리케이션 파일 백업

```bash
# .env 파일, 업로드 파일 등 백업
tar -czf taskflow_files_$(date +%Y%m%d).tar.gz .env nginx/ssl/ uploads/
```

### 복구 절차

#### 1. 데이터베이스 복구

```bash
# 백업 파일 압축 해제 및 복구
gunzip < taskflow_backup_20240115.sql.gz | \
  docker-compose -f docker-compose.prod.yml exec -T db \
  psql -U taskflow -d taskflow
```

#### 2. 서비스 재시작

```bash
docker-compose -f docker-compose.prod.yml restart
```

---

## 모니터링

### 로그 관리

#### 1. Docker 로그 확인

```bash
# 모든 서비스 로그
docker-compose -f docker-compose.prod.yml logs -f

# 특정 서비스 로그
docker-compose -f docker-compose.prod.yml logs -f backend

# 최근 100줄만 보기
docker-compose -f docker-compose.prod.yml logs --tail 100 backend

# 타임스탬프 포함
docker-compose -f docker-compose.prod.yml logs -f -t backend
```

#### 2. 로그 파일로 저장

```bash
# 로그를 파일로 리다이렉트
docker-compose -f docker-compose.prod.yml logs -f > /var/log/taskflow.log 2>&1 &
```

#### 3. 로그 로테이션

Docker의 로그 드라이버 설정:

```yaml
# docker-compose.prod.yml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "5"
```

### 헬스체크

#### 1. 백엔드 헬스체크 엔드포인트

```python
# app/api/v1/health.py
from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.get("/health/db")
async def db_health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)}
```

#### 2. 외부 모니터링 도구

**UptimeRobot, Pingdom 등을 이용한 모니터링**

- 엔드포인트: `https://yourdomain.com/api/v1/health`
- 체크 주기: 5분
- 알림: 이메일, Slack, SMS

### 에러 추적

추후 Sentry를 통합하여 에러 추적:

```python
# app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)
```

---

## 트러블슈팅

### 1. 서비스가 시작되지 않음

```bash
# 컨테이너 상태 확인
docker-compose -f docker-compose.prod.yml ps

# 특정 컨테이너 로그 확인
docker-compose -f docker-compose.prod.yml logs backend

# 컨테이너 재시작
docker-compose -f docker-compose.prod.yml restart backend

# 전체 재시작
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

### 2. 데이터베이스 연결 오류

```bash
# 데이터베이스 헬스체크
docker-compose -f docker-compose.prod.yml exec db pg_isready -U taskflow

# 데이터베이스 로그 확인
docker-compose -f docker-compose.prod.yml logs db

# 연결 테스트
docker-compose -f docker-compose.prod.yml exec db psql -U taskflow -d taskflow -c "SELECT 1;"
```

### 3. 디스크 공간 부족

```bash
# Docker 디스크 사용량 확인
docker system df

# 사용하지 않는 이미지, 컨테이너, 볼륨 삭제
docker system prune -a --volumes

# 특정 볼륨 삭제 (주의: 데이터 손실)
docker volume rm taskflow_postgres_data
```

### 4. 성능 저하

```bash
# CPU 및 메모리 사용량 확인
docker stats

# 데이터베이스 슬로우 쿼리 확인
docker-compose -f docker-compose.prod.yml exec db psql -U taskflow -d taskflow -c "
  SELECT query, calls, total_time, mean_time
  FROM pg_stat_statements
  ORDER BY mean_time DESC
  LIMIT 10;
"
```

### 5. SSL 인증서 문제

```bash
# 인증서 만료 확인
sudo certbot certificates

# 인증서 갱신
sudo certbot renew

# Nginx 설정 테스트
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# Nginx 재로드
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

---

## 업데이트 및 배포

### 무중단 배포

```bash
# 1. 새 코드 가져오기
git pull origin master

# 2. 이미지 빌드
docker-compose -f docker-compose.prod.yml build

# 3. 새 컨테이너로 교체 (무중단)
docker-compose -f docker-compose.prod.yml up -d --no-deps --build backend frontend

# 4. 마이그레이션 실행 (필요 시)
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# 5. 이전 이미지 정리
docker image prune -f
```

### 롤백

```bash
# 이전 버전으로 롤백
git checkout <previous-commit>
docker-compose -f docker-compose.prod.yml up -d --build

# 데이터베이스 마이그레이션 롤백
docker-compose -f docker-compose.prod.yml exec backend alembic downgrade -1
```

---

## 체크리스트

배포 전 체크리스트:

- [ ] 환경변수 보안 설정 완료 (JWT 비밀키, DB 비밀번호)
- [ ] CORS 설정 확인 (프로덕션 도메인)
- [ ] HTTPS 설정 완료 (SSL 인증서)
- [ ] 데이터베이스 백업 설정 완료
- [ ] 로그 로테이션 설정 완료
- [ ] 모니터링 설정 완료 (헬스체크)
- [ ] 방화벽 설정 (포트 80, 443만 오픈)
- [ ] 도메인 DNS 설정 완료

---

## 추가 자료

- **Docker 문서**: https://docs.docker.com/
- **Nginx 문서**: https://nginx.org/en/docs/
- **Let's Encrypt**: https://letsencrypt.org/
- **PostgreSQL 튜닝**: https://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server
