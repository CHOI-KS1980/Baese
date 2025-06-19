#!/bin/bash

echo "🚀 GitHub에 G라이더 자동화 시스템 업로드"
echo "========================================"

# GitHub 저장소 URL 입력 받기
echo "📝 GitHub 저장소 URL을 입력하세요:"
echo "예: https://github.com/username/g-rider-automation.git"
read -p "URL: " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "❌ 저장소 URL이 입력되지 않았습니다."
    exit 1
fi

echo "📁 현재 폴더: $(pwd)"

# 기존 원격 저장소 제거 (있다면)
git remote remove origin 2>/dev/null || true

# 새 원격 저장소 추가
echo "🔗 GitHub 저장소 연결 중..."
git remote add origin "$REPO_URL"

# 브랜치 이름 확인 및 설정
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "🔄 브랜치를 main으로 변경 중..."
    git branch -M main
fi

# GitHub에 푸시
echo "📤 코드 업로드 중..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo "✅ 코드 업로드 완료!"
    echo "🌐 저장소 확인: ${REPO_URL%.git}"
    echo ""
    echo "📋 다음 단계:"
    echo "1. GitHub 저장소 → Settings → Secrets and variables → Actions"
    echo "2. New repository secret 클릭하여 토큰 추가"
    echo "3. Actions 탭에서 자동 실행 확인"
else
    echo "❌ 업로드 실패. GitHub 계정 로그인 상태를 확인하세요."
    echo "💡 해결 방법:"
    echo "   git config --global user.name \"Your Name\""
    echo "   git config --global user.email \"your.email@example.com\""
fi 