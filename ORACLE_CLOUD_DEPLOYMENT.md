# 🚀 오라클 클라우드 무료 버전 배포 가이드

이 문서는 Dean Agent Framework를 오라클 클라우드 인프라스트럭처(OCI) 무료 티어에 배포하는 방법을 설명합니다.

## 📋 사전 준비사항

### 1. 오라클 클라우드 계정 생성

- [오라클 클라우드](https://cloud.oracle.com/) 계정 생성
- 무료 티어 가입 (신용카드 정보 필요하지만 실제 요금 발생하지 않음)

### 2. API 키 준비

- **GEMINI_API_KEY**: Google AI Studio에서 발급
- **TAVILY_API_KEY**: Tavily 검색 API 키 (선택사항)
- **NOTION_API_KEY**: Notion API 키 (선택사항)

## 🏗️ 배포 방법

### 방법 1: Docker를 사용한 배포 (권장)

#### 1단계: Compute Instance 생성

1. OCI 콘솔에서 **Compute > Instances** 이동
2. **Create Instance** 클릭
3. 설정:
   - **Name**: `dean-agent-framework`
   - **Image**: Oracle Linux 8 또는 Ubuntu 20.04/22.04
   - **Shape**: VM.Standard.E2.1.Micro (무료 티어)
   - **Networking**: Public subnet 선택
   - **SSH keys**: 본인의 공개키 추가

#### 2단계: 보안 그룹 설정

1. **Networking > Virtual Cloud Networks** 이동
2. 보안 리스트에서 다음 규칙 추가:
   ```
   Inbound Rules:
   - Source: 0.0.0.0/0, Protocol: TCP, Port: 8000 (FastAPI)
   - Source: 0.0.0.0/0, Protocol: TCP, Port: 22 (SSH)
   - Source: 0.0.0.0/0, Protocol: TCP, Port: 8501 (Streamlit, 선택사항)
   ```

#### 3단계: 인스턴스 접속 및 설정

```bash
# SSH로 인스턴스 접속
ssh opc@<인스턴스_공용_IP>

# 시스템 업데이트
sudo yum update -y  # Oracle Linux
# 또는
sudo apt update && sudo apt upgrade -y  # Ubuntu

# Docker 설치
sudo yum install -y docker  # Oracle Linux
# 또는
sudo apt install -y docker.io  # Ubuntu

# Docker 서비스 시작
sudo systemctl start docker
sudo systemctl enable docker

# 현재 사용자를 docker 그룹에 추가
sudo usermod -aG docker opc

# 로그아웃 후 재접속하여 그룹 변경사항 적용
exit
ssh opc@<인스턴스_공용_IP>
```

#### 4단계: 애플리케이션 배포

```bash
# 프로젝트 클론
git clone <your-repository-url>
cd dean_agent_framework

# 환경 변수 설정
cp env.example .env
nano .env  # API 키들을 실제 값으로 수정

# Docker 이미지 빌드 및 실행
chmod +x deploy.sh
./deploy.sh
```

### 방법 2: 직접 설치 배포

#### 1단계: Python 환경 설정

```bash
# Python 3.11 설치 (Oracle Linux)
sudo yum install -y python3.11 python3.11-pip

# 가상환경 생성 및 활성화
python3.11 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

#### 2단계: 환경 변수 설정

```bash
# .env 파일 생성
cp env.example .env
nano .env  # API 키들을 실제 값으로 수정
```

#### 3단계: 데이터베이스 초기화

```bash
# Alembic 초기화 (필요한 경우)
alembic upgrade head

# 또는 간단한 방법으로 테이블 생성
python -c "from src.core.db import init_db; init_db()"
```

#### 4단계: 애플리케이션 실행

```bash
# 백그라운드에서 실행
nohup python app.py > app.log 2>&1 &

# 또는 systemd 서비스로 등록
sudo nano /etc/systemd/system/dean-agent.service
```

#### systemd 서비스 파일 예시:

```ini
[Unit]
Description=Dean Agent Framework
After=network.target

[Service]
Type=simple
User=opc
WorkingDirectory=/home/opc/dean_agent_framework
Environment=PATH=/home/opc/dean_agent_framework/venv/bin
ExecStart=/home/opc/dean_agent_framework/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 서비스 등록 및 시작
sudo systemctl daemon-reload
sudo systemctl enable dean-agent
sudo systemctl start dean-agent
```

## 🔧 추가 설정

### 1. Nginx 리버스 프록시 설정 (선택사항)

```bash
# Nginx 설치
sudo yum install -y nginx  # Oracle Linux
# 또는
sudo apt install -y nginx  # Ubuntu

# 설정 파일 생성
sudo nano /etc/nginx/sites-available/dean-agent
```

Nginx 설정 파일 내용:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 또는 인스턴스 IP

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# 설정 활성화
sudo ln -s /etc/nginx/sites-available/dean-agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 2. SSL 인증서 설정 (Let's Encrypt)

```bash
# Certbot 설치
sudo yum install -y certbot python3-certbot-nginx  # Oracle Linux
# 또는
sudo apt install -y certbot python3-certbot-nginx  # Ubuntu

# SSL 인증서 발급
sudo certbot --nginx -d your-domain.com
```

## 🚨 문제 해결

### 1. 포트 접근 문제

- 보안 그룹에서 포트 8000이 열려있는지 확인
- 방화벽 설정 확인: `sudo firewall-cmd --list-ports`

### 2. API 키 관련 오류

- `.env` 파일의 API 키가 올바른지 확인
- 환경 변수가 제대로 로드되었는지 확인: `echo $GEMINI_API_KEY`

### 3. 메모리 부족 오류

- 무료 티어 인스턴스는 1GB RAM으로 제한됨
- 필요시 `MAX_MESSAGES` 등 설정을 줄여서 메모리 사용량 최적화

### 4. 데이터베이스 연결 오류

- SQLite 파일 권한 확인: `chmod 664 app.db`
- 데이터베이스 파일 경로 확인

## 📊 모니터링

### 1. 로그 확인

```bash
# Docker 배포 시
docker logs dean-agent-app

# 직접 설치 시
tail -f app.log

# systemd 서비스 시
sudo journalctl -u dean-agent -f
```

### 2. 리소스 사용량 모니터링

```bash
# CPU 및 메모리 사용량
top
htop  # 설치된 경우

# 디스크 사용량
df -h

# 네트워크 연결 상태
netstat -tlnp
```

## 🔄 업데이트 및 백업

### 1. 애플리케이션 업데이트

```bash
# 코드 업데이트
git pull origin main

# Docker 재배포
./deploy.sh

# 또는 직접 설치 시 재시작
sudo systemctl restart dean-agent
```

### 2. 데이터베이스 백업

```bash
# SQLite 백업
cp app.db app.db.backup.$(date +%Y%m%d_%H%M%S)

# 정기 백업을 위한 cron 작업 설정
crontab -e
# 다음 라인 추가: 0 2 * * * cp /home/opc/dean_agent_framework/app.db /home/opc/backups/app.db.backup.$(date +\%Y\%m\%d_\%H\%M\%S)
```

## 🌐 접속 확인

배포 완료 후 다음 URL로 접속하여 정상 작동을 확인하세요:

- **API 상태**: `http://<인스턴스_IP>:8000/`
- **API 문서**: `http://<인스턴스_IP>:8000/docs`
- **헬스 체크**: `http://<인스턴스_IP>:8000/health`

## 💡 추가 팁

1. **도메인 연결**: 무료 도메인 서비스(Freenom, No-IP 등)를 사용하여 도메인 연결 가능
2. **CDN 사용**: Cloudflare 무료 플랜으로 성능 향상 가능
3. **모니터링**: OCI의 기본 모니터링 기능 활용
4. **백업**: 정기적인 데이터베이스 백업 설정 권장

이제 오라클 클라우드 무료 티어에서 Dean Agent Framework를 성공적으로 운영할 수 있습니다! 🎉
