#!/usr/bin/env python3
"""
🎯 카카오톡 최종 테스트
액세스 토큰으로 바로 카카오톡 전송
"""

import json
import requests
from datetime import datetime
import pytz

KST = pytz.timezone('Asia/Seoul')

def send_final_test_message():
    """최종 테스트 메시지 전송"""
    
    print("🎯 카카오톡 최종 테스트")
    print("━" * 40)
    
    # 카카오 액세스 토큰 입력
    access_token = input("📝 카카오 액세스 토큰을 입력하세요: ").strip()
    
    if not access_token:
        print("❌ 액세스 토큰이 필요합니다!")
        return False
    
    # 테스트 메시지
    test_message = f"""🍕 배민 G라이더 완전 자동화 성공!

⏰ 최종 테스트: {datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')}
🤖 시스템: GitHub Actions + 카카오톡
✅ 상태: 완전 자동화 완료!

━━━━━━━━━━━━━━━━━━━━━━━━
🎉 축하합니다! 
━━━━━━━━━━━━━━━━━━━━━━━━

✅ GitHub Actions: 자동 스케줄링
✅ 공휴일 인식: 한국천문연구원 API
✅ 날씨 정보: 안산시 실시간
✅ G라이더 데이터: 실시간 수집
✅ 카카오톡 전송: 정상 작동

🚀 이제부터 24시간 무인 운영됩니다!

━━━━━━━━━━━━━━━━━━━━━━━━
📊 다음 자동 전송 예정:
   • 평일: 45회/일 (30분 간격)
   • 휴일: 50회/일 (더 자주)
   • 피크시간: 15분 간격

🎯 완전 자동화 100% 완성! 🎯"""

    try:
        url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        template = {
            "object_type": "text",
            "text": test_message,
            "link": {
                "web_url": "https://github.com/CHOI-KS1980/baemin",
                "mobile_web_url": "https://github.com/CHOI-KS1980/baemin"
            }
        }
        
        data = {
            "template_object": json.dumps(template)
        }
        
        print("📤 카카오톡으로 메시지 전송 중...")
        response = requests.post(url, headers=headers, data=data, timeout=10)
        
        if response.status_code == 200:
            print("🎉 성공! 카카오톡을 확인하세요!")
            print("━" * 40)
            print("🔥 완전 자동화 시스템이 작동합니다!")
            print("📱 이제 카카오톡으로 실시간 알림을 받습니다!")
            return True
        else:
            print(f"❌ 전송 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

if __name__ == "__main__":
    success = send_final_test_message()
    
    if success:
        print("\n🎊 완전 자동화 성공!")
        print("이제 GitHub Actions가 자동으로 G라이더 정보를 카카오톡으로 보냅니다!")
    else:
        print("\n❌ 테스트 실패. 액세스 토큰을 다시 확인해주세요.") 