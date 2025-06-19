#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
카카오 i 오픈빌더 웹훅 URL 테스트 스크립트

사용법:
python test_webhook.py https://your-webhook-url-here
"""

import sys
import requests
import json

def test_webhook(webhook_url):
    """카카오 i 오픈빌더 웹훅 URL 테스트"""
    
    # 테스트 메시지 페이로드
    payload = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": "🔧 웹훅 연결 테스트 성공! 자동 전송 시스템이 정상 작동합니다! ✅"
                    }
                }
            ]
        }
    }
    
    try:
        print(f"🔍 웹훅 URL 테스트 중: {webhook_url}")
        
        response = requests.post(
            webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📊 응답 상태 코드: {response.status_code}")
        print(f"📋 응답 헤더: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ 성공! 웹훅 URL이 정상 작동합니다!")
            print("🎉 이제 GitHub Secrets에 이 URL을 설정하세요!")
            return True
        else:
            print(f"❌ 실패! HTTP {response.status_code}")
            print(f"📝 응답 내용: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"💥 연결 오류: {e}")
        print("🔧 URL이 올바른지 확인해주세요")
        return False

def main():
    if len(sys.argv) != 2:
        print("사용법: python test_webhook.py https://your-webhook-url-here")
        print("\n예시:")
        print("python test_webhook.py https://chatbot-api.kakao.com/v1/skill/12345678-abcd-efgh")
        sys.exit(1)
    
    webhook_url = sys.argv[1]
    
    print("🚀 카카오 i 오픈빌더 웹훅 테스트 시작")
    print("=" * 50)
    
    success = test_webhook(webhook_url)
    
    print("=" * 50)
    if success:
        print("🎯 결론: 웹훅 URL이 정상 작동합니다!")
        print("👉 다음 단계: GitHub Secrets에 WEBHOOK_URL 설정")
    else:
        print("🔧 결론: 웹훅 URL 설정을 다시 확인해주세요")
        print("👉 카카오 i 오픈빌더 → 스킬 → URL 필드 재확인")

if __name__ == "__main__":
    main() 