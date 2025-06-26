@echo off
echo =============================================
echo    심플 배민 통합 제어 센터 - Netlify 배포
echo =============================================
echo.

echo 1. Netlify CLI 설치 중...
npm install -g netlify-cli

echo.
echo 2. Netlify 계정 연결...
echo 브라우저가 열리면 GitHub 계정으로 로그인하세요.
netlify login

echo.
echo 3. 사이트 배포 중...
netlify deploy --prod --dir .

echo.
echo ✅ 배포 완료! 
echo 제공된 URL로 접속하여 사이트를 확인하세요.
echo.
pause 