#!/usr/bin/env python3
"""
🌉 카카오톡 브리지 서버
webhook.site → 카카오톡으로 메시지 전달
GitHub Actions에서 전송된 메시지를 실제 카카오톡으로 전송
"""

import os
import json
import requests
import time
from datetime import datetime
import pytz

# 한국시간 설정
KST = pytz.timezone('Asia/Seoul')

def send_to_kakao_with_rest_api(access_token, message):
    """카카오 REST API로 나에게 보내기"""
    try:
        url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # 카카오톡 메시지 템플릿
        template = {
            "object_type": "text",
            "text": message,
            "link": {
                "web_url": "https://github.com/CHOI-KS1980/baemin",
                "mobile_web_url": "https://github.com/CHOI-KS1980/baemin"
            }
        }
        
        data = {
            "template_object": json.dumps(template)
        }
        
        response = requests.post(url, headers=headers, data=data, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ 카카오톡 전송 성공!")
            return True
        else:
            print(f"❌ 카카오톡 전송 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 카카오톡 전송 오류: {e}")
        return False

def check_webhook_site_and_forward():
    """webhook.site에서 새 메시지를 확인하고 카카오톡으로 전달"""
    
    # 설정값들
    webhook_url = "https://webhook.site/token/dbf3ed6e-e7ca-4430-be5a-19fb1fb1ba57/requests"
    access_token = "3f2716744254c8c199bd05c59b84142b"  # 실제 액세스 토큰으로 변경 필요
    
    print("🌉 카카오톡 브리지 서버 시작!")
    print("━" * 50)
    print(f"📡 모니터링: {webhook_url}")
    print(f"📱 전송대상: 카카오톡 (나에게 보내기)")
    print("━" * 50)
    
    last_check_time = datetime.now(KST)
    
    try:
        while True:
            print(f"🔍 {datetime.now(KST).strftime('%H:%M:%S')} - 새 메시지 확인 중...")
            
            # webhook.site API로 최근 요청 확인
            try:
                response = requests.get(webhook_url, timeout=10)
                
                if response.status_code == 200:
                    requests_data = response.json()
                    
                    if requests_data.get('data'):
                        # 가장 최근 요청 확인
                        latest_request = requests_data['data'][0]
                        request_time = datetime.fromisoformat(latest_request['created_at'].replace('Z', '+00:00')).astimezone(KST)
                        
                        # 마지막 확인 시간 이후의 새 메시지인지 확인
                        if request_time > last_check_time:
                            print("📨 새로운 메시지 발견!")
                            
                            # 요청 내용에서 메시지 추출
                            content = latest_request.get('content', '{}')
                            if isinstance(content, str):
                                try:
                                    content = json.loads(content)
                                except:
                                    pass
                            
                            message = content.get('message', '메시지 내용을 찾을 수 없음')
                            
                            print(f"💬 메시지 미리보기: {message[:100]}...")
                            
                            # 카카오톡으로 전송
                            success = send_to_kakao_with_rest_api(access_token, message)
                            
                            if success:
                                print("🎉 카카오톡 전송 완료!")
                            else:
                                print("❌ 카카오톡 전송 실패!")
                            
                            last_check_time = request_time
                        
                else:
                    print(f"⚠️ webhook.site API 오류: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ 모니터링 오류: {e}")
            
            # 30초마다 확인
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n👋 브리지 서버를 종료합니다.")

def manual_test():
    """수동 테스트"""
    print("🧪 수동 카카오톡 전송 테스트")
    print("━" * 30)
    
    access_token = input("📝 카카오 액세스 토큰을 입력하세요: ").strip()
    
    if not access_token:
        print("❌ 액세스 토큰이 필요합니다!")
        return
    
    test_message = f"""🍕 배민 G라이더 브리지 테스트

⏰ 테스트 시간: {datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')}
🌉 방법: webhook.site → 카카오톡 브리지
✅ 상태: 수동 테스트

━━━━━━━━━━━━━━━━━━━━━━━━
📊 G라이더 미션 현황 (테스트)
━━━━━━━━━━━━━━━━━━━━━━━━

🚀 오늘의 미션:
   • 아침 배송: 완료 ✅
   • 점심 피크: 진행중 🔥
   • 저녁 준비: 대기중 ⏰

🏆 현재 순위:
   🥇 1위: 김라이더 (127점)
   🥈 2위: 이배달 (98점)
   🥉 3위: 박미션 (87점)

✅ 브리지 서버 정상 작동!
━━━━━━━━━━━━━━━━━━━━━━━━"""

    success = send_to_kakao_with_rest_api(access_token, test_message)
    
    if success:
        print("🎉 테스트 성공! 카카오톡을 확인하세요!")
    else:
        print("❌ 테스트 실패!")

if __name__ == "__main__":
    print("🌉 카카오톡 브리지 서버")
    print("━" * 50)
    print("1. 자동 모니터링 시작")
    print("2. 수동 테스트")
    print("0. 종료")
    
    choice = input("\n📝 선택 (0-2): ").strip()
    
    if choice == "1":
        check_webhook_site_and_forward()
    elif choice == "2":
        manual_test()
    else:
        print("👋 종료합니다.") 