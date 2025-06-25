#!/bin/bash
echo "🚀 Auto Finance 고도화 시스템 시작"
echo

# 가상환경 활성화 (있는 경우)
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# 의존성 설치 확인
echo "📦 의존성 확인 중..."
pip install -r requirements.txt

# 환경 변수 로드
if [ -f ".env" ]; then
    echo "⚙️ 환경 변수 로드 중..."
    export $(cat .env | xargs)
fi

# 시스템 실행
echo "🎯 Auto Finance 시스템 시작..."
python main_advanced.py
