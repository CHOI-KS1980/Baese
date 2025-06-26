@echo off
echo ========================================
echo  심플 배민 통합 제어센터 - 간편 배포
echo ========================================
echo.

echo 1. Surge CLI 설치중...
npm install -g surge

echo.
echo 2. 사이트 배포중...
surge . simple-baemin-control.surge.sh

echo.
echo 배포 완료!
echo URL: https://simple-baemin-control.surge.sh
pause 