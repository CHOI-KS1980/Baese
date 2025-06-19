#!/bin/bash

echo "🚀 G라이더 자동화 시스템 시작"
echo "================================"

# 현재 경로 확인
echo "📁 실행 경로: $(pwd)"

# Python 가상환경 활성화 (있다면)
if [ -d "venv" ]; then
    echo "🐍 가상환경 활성화 중..."
    source venv/bin/activate
fi

# 필요한 패키지 설치
echo "📦 패키지 의존성 확인 중..."
pip3 install -q requests beautifulsoup4 schedule selenium webdriver-manager python-dotenv

# 백그라운드에서 스케줄러 실행
echo "⏰ 백그라운드 스케줄러 시작..."
nohup python3 kakao_scheduled_sender.py > kakao_automation.log 2>&1 &

# PID 저장
echo $! > kakao_automation.pid

echo "✅ 자동화 시스템이 백그라운드에서 실행 중입니다!"
echo "📊 로그 확인: tail -f kakao_automation.log"
echo "⏹️ 중지 방법: kill \$(cat kakao_automation.pid)"
echo "📅 전송 시간: 08:00, 10:30, 12:00, 14:30, 18:00, 20:30, 22:00"

# 상태 확인
sleep 3
if ps -p $(cat kakao_automation.pid) > /dev/null; then
    echo "🟢 프로세스 정상 실행 중 (PID: $(cat kakao_automation.pid))"
else
    echo "🔴 프로세스 시작 실패 - 로그를 확인하세요"
fi 