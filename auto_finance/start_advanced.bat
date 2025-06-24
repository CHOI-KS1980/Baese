@echo off
echo 🚀 Auto Finance 고도화 시스템 시작
echo.

REM 가상환경 활성화 (있는 경우)
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM 의존성 설치 확인
echo 📦 의존성 확인 중...
pip install -r requirements.txt

REM 환경 변수 로드
if exist ".env" (
    echo ⚙️ 환경 변수 로드 중...
)

REM 시스템 실행
echo 🎯 Auto Finance 시스템 시작...
python main_advanced.py

pause
