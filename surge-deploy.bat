@echo off
echo =============================================
echo    심플 배민 통합 제어 센터 - Surge 배포
echo =============================================
echo.

echo 1. Surge CLI 설치 중...
npm install -g surge

echo.
echo 2. 사이트 배포 중...
echo 이메일과 비밀번호를 입력하세요 (처음 사용시)
surge . simple-baemin-control.surge.sh

echo.
echo ✅ 배포 완료!
echo 접속 URL: https://simple-baemin-control.surge.sh
echo.
pause 