# SSL 인증서 디렉토리

이 디렉토리는 프로덕션 환경에서 HTTPS를 위한 SSL/TLS 인증서를 저장하는 곳입니다.

## 인증서 설치 방법

### 1. Let's Encrypt (무료)

```bash
# Certbot 설치 (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install certbot

# 인증서 발급 (standalone 모드)
sudo certbot certonly --standalone -d taskflow.example.com -d www.taskflow.example.com

# 생성된 인증서 복사
sudo cp /etc/letsencrypt/live/taskflow.example.com/fullchain.pem ./cert.pem
sudo cp /etc/letsencrypt/live/taskflow.example.com/privkey.pem ./key.pem

# 권한 설정
chmod 644 cert.pem
chmod 600 key.pem
```

### 2. 상용 인증서

상용 인증서 제공업체(예: DigiCert, Comodo)에서 발급받은 인증서를 다음과 같이 배치:

```bash
# 인증서 파일 복사
cp /path/to/your/certificate.crt ./cert.pem
cp /path/to/your/private-key.key ./key.pem

# 중간 인증서가 있는 경우 병합
cat certificate.crt intermediate.crt > cert.pem

# 권한 설정
chmod 644 cert.pem
chmod 600 key.pem
```

### 3. 자체 서명 인증서 (개발/테스트용)

```bash
# OpenSSL로 자체 서명 인증서 생성
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout key.pem \
  -out cert.pem \
  -subj "/C=KR/ST=Seoul/L=Seoul/O=TaskFlow/CN=localhost"

# 권한 설정
chmod 644 cert.pem
chmod 600 key.pem
```

## 필요한 파일

프로덕션 배포 시 다음 파일들이 필요합니다:

- `cert.pem` - SSL 인증서 (공개키)
- `key.pem` - Private Key (비밀키)
- `dhparam.pem` (선택사항) - Diffie-Hellman 파라미터

### DH 파라미터 생성 (선택사항, 보안 강화)

```bash
openssl dhparam -out dhparam.pem 2048
```

## nginx.conf 설정

인증서를 설치한 후 `nginx/nginx.conf` 파일에서 SSL 관련 설정의 주석을 해제하세요:

```nginx
# HTTPS 서버 블록 주석 해제
listen 443 ssl http2;
ssl_certificate /etc/nginx/ssl/cert.pem;
ssl_certificate_key /etc/nginx/ssl/key.pem;
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;
ssl_prefer_server_ciphers on;

# DH 파라미터 (생성한 경우)
ssl_dhparam /etc/nginx/ssl/dhparam.pem;
```

## 인증서 갱신

### Let's Encrypt 자동 갱신

```bash
# Cron job으로 자동 갱신 설정
sudo crontab -e

# 매일 오전 3시에 인증서 갱신 체크
0 3 * * * certbot renew --quiet && docker-compose -f /opt/taskflow/docker-compose.prod.yml restart nginx
```

### 수동 갱신

```bash
# 인증서 갱신
sudo certbot renew

# 새 인증서 복사
sudo cp /etc/letsencrypt/live/taskflow.example.com/fullchain.pem ./cert.pem
sudo cp /etc/letsencrypt/live/taskflow.example.com/privkey.pem ./key.pem

# Nginx 재시작
docker-compose -f docker-compose.prod.yml restart nginx
```

## 보안 체크리스트

- [ ] Private key 파일 권한이 600인지 확인
- [ ] 인증서 만료일 확인
- [ ] 자동 갱신 설정 확인
- [ ] SSL Labs에서 보안 등급 테스트: https://www.ssllabs.com/ssltest/
- [ ] HSTS(HTTP Strict Transport Security) 헤더 설정 고려

## 주의사항

- **절대 Git에 커밋하지 마세요!**: Private key가 유출되면 보안이 무력화됩니다.
- `.gitignore`에 `*.pem`, `*.key`, `*.crt` 가 포함되어 있는지 확인하세요.
- 인증서와 키 파일은 별도의 안전한 곳에 백업하세요.

## 테스트

인증서 설치 후 다음 명령으로 테스트:

```bash
# SSL 인증서 정보 확인
openssl x509 -in cert.pem -text -noout

# SSL 연결 테스트
openssl s_client -connect taskflow.example.com:443 -servername taskflow.example.com

# 온라인 SSL 테스트
# https://www.ssllabs.com/ssltest/analyze.html?d=taskflow.example.com
```
