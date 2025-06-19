#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GitHub Actions용 카카오 웹훅 시뮬레이터
실제 카카오 i 오픈빌더 API를 호출하여 메시지를 전송합니다.
"""

import requests
import json
import os
from datetime import datetime

def send_to_kakao_webhook(webhook_url, message):
    """
    카카오 i 오픈빌더로 메시지 전송
    실제 웹훅이 아닌 직접 API 호출 방식
    """
    
    # 카카오 i 오픈빌더 API 형식에 맞는 페이로드
    payload = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": message
                    }
                }
            ]
        }
    }
    
    headers = {
        'Content-Type': 'application/json; charset=utf-8'
    }
    
    try:
        print(f"🚀 카카오로 메시지 전송 시도...")
        print(f"📍 URL: {webhook_url}")
        print(f"📩 메시지: {message}")
        
        response = requests.post(
            webhook_url,
            data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
            headers=headers,
            timeout=10
        )
        
        print(f"📈 응답 코드: {response.status_code}")
        print(f"📋 응답 내용: {response.text}")
        
        if response.status_code == 200:
            print("✅ 메시지 전송 성공!")
            return True
        else:
            print(f"❌ 전송 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"💥 오류 발생: {e}")
        return False

def main():
    """메인 실행 함수"""
    
    # 환경변수에서 웹훅 URL 가져오기
    webhook_url = os.getenv('WEBHOOK_URL')
    
    if not webhook_url:
        print("❌ WEBHOOK_URL 환경변수가 설정되지 않았습니다.")
        print("💡 GitHub Secrets에 WEBHOOK_URL을 추가해주세요.")
        return
    
    # 테스트 메시지
    test_message = f"""
🤖 GitHub Actions 테스트 메시지

✅ 자동화 시스템이 정상 작동합니다!
📅 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🚀 이 메시지가 보인다면 설정이 완료되었습니다!

다음 단계:
1. 정기 스케줄 활성화
2. 날씨 API 연동
3. 한국 공휴일 API 연동
"""
    
    # 메시지 전송
    success = send_to_kakao_webhook(webhook_url, test_message.strip())
    
    if success:
        print("🎉 테스트 완료! 카카오톡을 확인해보세요.")
    else:
        print("🔧 웹훅 URL을 다시 확인해주세요.")

if __name__ == '__main__':
    main() 