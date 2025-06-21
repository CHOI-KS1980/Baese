#!/usr/bin/env python3
"""
🔧 카카오 API 키 없이도 테스트 가능한 간단 버전
웹훅 URL로 메시지를 전송하여 자동화 시스템 테스트
"""

import os
import requests
import json
from datetime import datetime
import pytz

# 한국시간 설정
KST = pytz.timezone('Asia/Seoul')

def send_webhook_message(webhook_url, message):
    """웹훅으로 메시지 전송"""
    try:
        payload = {
            "timestamp": datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S KST'),
            "message": message,
            "source": "배민 G라이더 자동화 시스템",
            "status": "test"
        }
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Baemin-Grider-Bot/1.0'
        }
        
        response = requests.post(webhook_url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ 웹훅 전송 성공!")
            print(f"📱 메시지: {message}")
            return True
        else:
            print(f"❌ 웹훅 전송 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 웹훅 오류: {e}")
        return False

def generate_test_message():
    """테스트 메시지 생성"""
    now = datetime.now(KST)
    
    message = f"""
🍕 배민 G라이더 자동화 시스템 테스트

⏰ 현재 시간: {now.strftime('%Y년 %m월 %d일 %H시 %M분')}
🇰🇷 시간대: 한국표준시 (KST)
🤖 상태: 정상 작동
🔧 테스트: 웹훅 연결 확인

━━━━━━━━━━━━━━━━━━━━━━━━
📊 G라이더 미션 현황 (테스트)
━━━━━━━━━━━━━━━━━━━━━━━━

🚀 오늘의 미션:
   • 아침 배송: 15건 완료
   • 점심 피크: 진행중
   • 저녁 준비: 대기중

🏆 현재 순위:
   🥇 1위: 김라이더 (127점)
   🥈 2위: 이배달 (98점) 
   🥉 3위: 박미션 (87점)

📈 오늘 통계:
   • 총 배송: 45건
   • 평점: 4.8/5.0
   • 보너스: +12,000원

━━━━━━━━━━━━━━━━━━━━━━━━
✅ 자동화 시스템이 정상 작동중입니다!
━━━━━━━━━━━━━━━━━━━━━━━━
    """.strip()
    
    return message

def main():
    """메인 실행 함수"""
    print("🚀 배민 G라이더 간단 테스트 시작!")
    print("━" * 50)
    
    # 환경변수에서 웹훅 URL 가져오기
    webhook_url = os.getenv('WEBHOOK_URL')
    
    if not webhook_url:
        print("❌ WEBHOOK_URL 환경변수가 설정되지 않았습니다!")
        print("💡 GitHub Secrets에서 WEBHOOK_URL을 설정해주세요.")
        print()
        print("🔧 설정 방법:")
        print("1. https://webhook.site/ 접속")
        print("2. 생성된 URL 복사")
        print("3. GitHub Secrets에 WEBHOOK_URL로 추가")
        return
    
    print(f"🌐 웹훅 URL: {webhook_url[:50]}...")
    print()
    
    # 테스트 메시지 생성
    test_message = generate_test_message()
    
    # 웹훅으로 메시지 전송
    print("📤 테스트 메시지 전송 중...")
    success = send_webhook_message(webhook_url, test_message)
    
    if success:
        print()
        print("🎉 테스트 성공!")
        print("📍 webhook.site 페이지에서 메시지 수신 확인하세요!")
        print()
        print("✅ 다음 단계:")
        print("1. webhook.site에서 메시지 확인")
        print("2. 카카오 API 키 설정 완료")
        print("3. 완전 자동화 활성화")
    else:
        print()
        print("❌ 테스트 실패!")
        print("🔍 WEBHOOK_URL 설정을 다시 확인해주세요.")

if __name__ == "__main__":
    main() 