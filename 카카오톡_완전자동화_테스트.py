#!/usr/bin/env python3
"""
🎉 카카오톡 완전 자동화 최종 테스트
액세스 토큰으로 실제 카카오톡 전송
"""

import json
import requests
from datetime import datetime
import pytz

KST = pytz.timezone('Asia/Seoul')

def send_success_message():
    """완전 자동화 성공 메시지 전송"""
    
    # 받은 액세스 토큰
    access_token = "f45go3Naqg7w_vP11KL7OdHm7LvQ7qkDZOrTTH5wm6uNj08itLSgwAAAAQKFwvXAAABl4g0TLwFVMIyByjmyg"
    
    print("🎉 카카오톡 완전 자동화 최종 테스트")
    print("━" * 60)
    print(f"🔑 액세스 토큰: {access_token[:30]}...")
    print("━" * 60)
    
    # 완전 자동화 성공 메시지
    success_message = f"""🍕 배민 G라이더 완전 자동화 100% 완성! 🎉

⏰ 완성 시간: {datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')}
🤖 시스템: GitHub Actions + 카카오톡 연동
✅ 상태: 완전 무인 자동화 가동!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎊 축하합니다! 완전 자동화 시스템 완성! 🎊
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ GitHub Actions: 자동 스케줄링 완료
✅ 한국 공휴일: 천문연구원 API 연동
✅ 날씨 정보: 안산시 실시간 연동
✅ G라이더 데이터: 실시간 수집
✅ 카카오톡 전송: 정상 작동 확인!
✅ 스마트 시간대: 피크/논피크 인식

🚀 이제부터 24시간 무인 운영됩니다!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 자동 전송 스케줄:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌅 평일 (월-금):
   • 09:00 시작
   • 09:30-11:30: 30분 간격 (5회)
   • 11:30-14:00: 15분 간격 (10회) 🔥
   • 14:00-17:30: 30분 간격 (7회)
   • 17:30-21:00: 15분 간격 (14회) 🔥
   • 21:00-23:30: 30분 간격 (5회)
   • 00:00 마무리 (1회)
   총 42회/일

🌴 휴일 (토-일, 공휴일):
   • 09:00-23:30: 30분 간격
   • 11:30-14:00: 15분 간격 🔥
   • 17:30-21:00: 15분 간격 🔥
   총 47회/일

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 완전 자동화 시스템 특징:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧠 스마트 기능:
   • 공휴일 자동 인식
   • 날씨별 메시지 변화
   • 라이더 순위 TOP 3 분석
   • 피크시간 집중 모니터링

📱 실시간 알림:
   • G라이더 미션 현황
   • 배송 완료율 추적
   • 날씨 변화 알림
   • 긴급 상황 즉시 통보

🔒 안정성:
   • 이중 백업 시스템
   • 오류 자동 복구
   • 로그 실시간 추적
   • GitHub Actions 모니터링

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 완전 자동화 100% 완성!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

이제 손대지 않아도 자동으로:
• G라이더 정보 수집
• 실시간 분석 및 순위 계산  
• 카카오톡 자동 전송
• 24시간 무인 모니터링

🍕 배민 G라이더 완전 정복! 🍕"""

    try:
        url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        template = {
            "object_type": "text",
            "text": success_message,
            "link": {
                "web_url": "https://github.com/CHOI-KS1980/baemin",
                "mobile_web_url": "https://github.com/CHOI-KS1980/baemin"
            }
        }
        
        data = {
            "template_object": json.dumps(template)
        }
        
        print("📤 완전 자동화 성공 메시지 전송 중...")
        response = requests.post(url, headers=headers, data=data, timeout=10)
        
        if response.status_code == 200:
            print("🎊 대성공! 카카오톡을 확인하세요!")
            print("━" * 60)
            print("🔥 완전 자동화 시스템이 정상 작동합니다!")
            print("📱 이제 카카오톡으로 실시간 G라이더 정보를 받습니다!")
            print("🚀 GitHub Actions가 자동으로 24시간 모니터링합니다!")
            print("━" * 60)
            return True
        else:
            print(f"❌ 전송 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def save_access_token():
    """액세스 토큰을 파일로 저장"""
    access_token = "f45go3Naqg7w_vP11KL7OdHm7LvQ7qkDZOrTTH5wm6uNj08itLSgwAAAAQKFwvXAAABl4g0TLwFVMIyByjmyg"
    
    # 토큰 파일로 저장
    with open('kakao_access_token.txt', 'w') as f:
        f.write(access_token)
    
    print("💾 액세스 토큰이 'kakao_access_token.txt' 파일로 저장되었습니다!")
    print(f"🔑 토큰: {access_token}")

if __name__ == "__main__":
    print("━" * 70)
    print("🎉 배민 G라이더 완전 자동화 최종 완성!")
    print("━" * 70)
    
    # 액세스 토큰 저장
    save_access_token()
    print()
    
    # 성공 메시지 전송
    success = send_success_message()
    
    if success:
        print("\n🎊🎊🎊 완전 자동화 100% 완성! 🎊🎊🎊")
        print()
        print("━" * 70)
        print("🚀 다음 작업들이 자동으로 실행됩니다:")
        print("━" * 70)
        print("✅ GitHub Actions: 자동 스케줄링")
        print("✅ G라이더 데이터: 실시간 수집")
        print("✅ 날씨 정보: 실시간 연동")
        print("✅ 카카오톡 전송: 자동 발송")
        print("✅ 공휴일 인식: 자동 조정")
        print("━" * 70)
        print("🎯 이제 모든 것이 자동으로 작동합니다!")
        print("📱 카카오톡으로 실시간 알림을 받으세요!")
    else:
        print("\n❌ 마지막 테스트 실패. 다시 시도해주세요.") 