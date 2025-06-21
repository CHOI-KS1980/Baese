#!/usr/bin/env python3
"""
🔧 헤더 설정 없이도 작동하는 웹훅 테스트
카카오 i 오픈빌더 헤더 설정이 어려울 때 사용
"""

import requests
import json
from datetime import datetime

def test_webhook_without_headers():
    """헤더 없이 웹훅 테스트"""
    
    print("🔧 헤더 없는 웹훅 테스트 시작!")
    print("━" * 50)
    
    # webhook.site URL (실제 URL로 변경 필요)
    webhook_url = input("📝 webhook.site URL을 입력하세요: ").strip()
    
    if not webhook_url:
        print("❌ URL이 입력되지 않았습니다!")
        return
    
    # 테스트 메시지 데이터
    test_data = {
        "message": """
🍕 배민 G라이더 헤더없이 테스트

⏰ 테스트 시간: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
🤖 상태: 헤더 없는 전송 테스트
🔧 방법: POST 요청 (Content-Type 자동)

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

✅ 헤더 없는 웹훅 전송 성공!
        """.strip(),
        "timestamp": datetime.now().isoformat(),
        "source": "baemin-grider-automation",
        "test_mode": True,
        "header_test": "no_content_type_header"
    }
    
    try:
        print(f"📤 웹훅 전송 중... URL: {webhook_url[:50]}...")
        
        # 방법 1: JSON으로 전송 (헤더 자동 설정)
        response1 = requests.post(webhook_url, json=test_data, timeout=10)
        print(f"✅ 방법1 (json=) 결과: {response1.status_code}")
        
        # 방법 2: 데이터로 전송
        response2 = requests.post(webhook_url, data=json.dumps(test_data), timeout=10)
        print(f"✅ 방법2 (data=) 결과: {response2.status_code}")
        
        # 방법 3: 폼 데이터로 전송
        form_data = {"message": test_data["message"]}
        response3 = requests.post(webhook_url, data=form_data, timeout=10)
        print(f"✅ 방법3 (form) 결과: {response3.status_code}")
        
        print()
        print("🎉 모든 방법으로 테스트 완료!")
        print("📍 webhook.site 페이지에서 메시지 수신을 확인하세요!")
        print()
        print("💡 카카오 i 오픈빌더 설정:")
        print("   - 헤더 설정 없이도 작동할 수 있습니다")
        print("   - URL만 정확히 입력하면 됩니다")
        
    except Exception as e:
        print(f"❌ 웹훅 전송 오류: {e}")
        print("🔍 URL을 다시 확인해주세요.")

def show_kakao_simple_setup():
    """카카오 오픈빌더 간단 설정 방법"""
    print()
    print("🤖 카카오 i 오픈빌더 간단 설정법:")
    print("━" * 50)
    print("1. 스킬 추가 시 최소한의 정보만 입력:")
    print("   - 스킬명: G라이더알림")
    print("   - URL: webhook.site URL")
    print("   - 메소드: POST (기본값)")
    print()
    print("2. 헤더 설정 찾기:")
    print("   - '고급 설정' 클릭")
    print("   - '헤더 추가' 버튼 찾기")
    print("   - Key: Content-Type")
    print("   - Value: application/json")
    print()
    print("3. 헤더 설정이 없다면:")
    print("   - 헤더 없이도 작동 가능!")
    print("   - URL만 정확히 설정하면 됨")
    print("━" * 50)

if __name__ == "__main__":
    test_webhook_without_headers()
    show_kakao_simple_setup() 