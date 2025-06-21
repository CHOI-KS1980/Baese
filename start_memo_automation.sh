#!/bin/bash
# 카카오톡 나에게 보내기 자동화 시스템 시작 스크립트

echo "🤖 카카오톡 나에게 보내기 자동화 시스템"
echo "================================================"

# 가상환경 확인 및 활성화 (선택사항)
if [ -d "venv" ]; then
    echo "📁 가상환경 활성화..."
    source venv/bin/activate
fi

# 필요한 패키지 설치 확인
echo "📦 패키지 확인 중..."
python3 -c "import schedule, requests, dotenv, pyperclip, pytz" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 필요한 패키지가 설치되지 않았습니다."
    echo "📦 다음 명령어로 설치하세요:"
    echo "   pip install -r requirements_memo.txt"
    exit 1
fi

# 환경변수 파일 확인
if [ ! -f ".env" ]; then
    echo "❌ .env 파일이 없습니다."
    echo "🔧 create_env_for_memo.py를 먼저 실행하세요."
    exit 1
fi

# 카카오톡 자동화 시스템 실행
echo "🚀 카카오톡 자동화 시스템 시작..."
python3 kakao_memo_automation.py

echo "👋 시스템이 종료되었습니다."
