#!/bin/bash

# 오라클 클라우드 배포 스크립트

echo "🚀 오라클 클라우드 배포 시작..."

# 1. 환경 변수 확인
echo "📋 환경 변수 확인 중..."
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ GEMINI_API_KEY가 설정되지 않았습니다."
    exit 1
fi

if [ -z "$TAVILY_API_KEY" ]; then
    echo "⚠️  TAVILY_API_KEY가 설정되지 않았습니다."
fi

if [ -z "$NOTION_API_KEY" ]; then
    echo "⚠️  NOTION_API_KEY가 설정되지 않았습니다."
fi

# 2. Docker 이미지 빌드
echo "🔨 Docker 이미지 빌드 중..."
docker build -t dean-agent-framework .

if [ $? -ne 0 ]; then
    echo "❌ Docker 이미지 빌드 실패"
    exit 1
fi

# 3. 기존 컨테이너 정리
echo "🧹 기존 컨테이너 정리 중..."
docker stop dean-agent-app 2>/dev/null || true
docker rm dean-agent-app 2>/dev/null || true

# 4. 새 컨테이너 실행
echo "🚀 새 컨테이너 실행 중..."
docker run -d \
    --name dean-agent-app \
    -p 8000:8000 \
    -e GEMINI_API_KEY="$GEMINI_API_KEY" \
    -e TAVILY_API_KEY="$TAVILY_API_KEY" \
    -e NOTION_API_KEY="$NOTION_API_KEY" \
    -e HOST=0.0.0.0 \
    -e PORT=8000 \
    -v $(pwd)/app.db:/app/app.db \
    --restart unless-stopped \
    dean-agent-framework

if [ $? -eq 0 ]; then
    echo "✅ 배포 완료!"
    echo "🌐 애플리케이션 URL: http://localhost:8000"
    echo "📚 API 문서: http://localhost:8000/docs"
    echo "🔍 컨테이너 상태 확인: docker logs dean-agent-app"
else
    echo "❌ 배포 실패"
    exit 1
fi
