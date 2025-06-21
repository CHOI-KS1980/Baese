#!/usr/bin/env python3
"""
🍕 카카오톡 직접 전송 시스템
webhook.site 없이 바로 카카오톡으로 메시지 전송
"""

import os
import json
import requests
from datetime import datetime
import pytz

# 한국시간 설정
KST = pytz.timezone('Asia/Seoul')

def get_kakao_access_token(rest_api_key):
    """카카오 액세스 토큰 발급 URL 생성"""
    auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri=https://localhost&response_type=code"
    print(f"🔗 다음 URL에서 인증 코드를 받으세요:")
    print(f"{auth_url}")
    print()
    print("📝 인증 후 redirect URL에서 'code=' 뒤의 값을 복사하세요!")
    
    return input("📋 인증 코드를 입력하세요: ").strip()

def exchange_code_for_token(rest_api_key, auth_code):
    """인증 코드를 액세스 토큰으로 교환"""
    token_url = "https://kauth.kakao.com/oauth/token"
    
    data = {
        'grant_type': 'authorization_code',
        'client_id': rest_api_key,
        'redirect_uri': 'https://localhost',
        'code': auth_code
    }
    
    response = requests.post(token_url, data=data)
    
    if response.status_code == 200:
        token_info = response.json()
        access_token = token_info['access_token']
        print(f"✅ 액세스 토큰 발급 성공!")
        print(f"🔑 토큰 (처음 10자리): {access_token[:10]}...")
        return access_token
    else:
        print(f"❌ 토큰 발급 실패: {response.status_code}")
        print(f"응답: {response.text}")
        return None

def send_kakao_message(access_token, message):
    """카카오톡 나에게 보내기"""
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
    
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 200:
        print(f"✅ 카카오톡 메시지 전송 성공!")
        return True
    else:
        print(f"❌ 메시지 전송 실패: {response.status_code}")
        print(f"응답: {response.text}")
        return False

def send_to_openchat(access_token, chat_id, message):
    """카카오톡 오픈채팅방에 메시지 전송"""
    # 오픈채팅방 메시지 전송은 별도 API 필요
    # 일단 나에게 보내기로 테스트
    print(f"📱 오픈채팅방 ID: {chat_id}")
    print(f"💬 메시지를 나에게 보내기로 테스트합니다...")
    
    return send_kakao_message(access_token, f"[배민 G라이더 → {chat_id}]\n\n{message}")

def generate_test_message():
    """G라이더 테스트 메시지 생성"""
    now = datetime.now(KST)
    
    message = f"""🍕 배민 G라이더 실제 전송 테스트!

⏰ 전송시간: {now.strftime('%Y년 %m월 %d일 %H시 %M분')}
🚀 전송방법: 카카오 REST API 직접 호출
✅ 상태: webhook.site 없이 직접 전송

━━━━━━━━━━━━━━━━━━━━━━━━
📊 G라이더 미션 현황 (실제)
━━━━━━━━━━━━━━━━━━━━━━━━

🔥 실시간 알림:
   • 아침 배송: 완료
   • 점심 피크: 진행중  
   • 저녁 준비: 대기중

🏆 TOP 라이더:
   🥇 김라이더 (127점)
   🥈 이배달 (98점)
   🥉 박미션 (87점)

📈 실시간 통계:
   • 총 주문: 156건
   • 완료률: 94.2%
   • 평균 별점: 4.7★

━━━━━━━━━━━━━━━━━━━━━━━━
✅ 카카오톡 직접 전송 성공!
🤖 배민 G라이더 자동화 시스템
━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    return message

def main():
    """메인 실행 함수"""
    print("🍕 카카오톡 직접 전송 테스트")
    print("━" * 50)
    
    # REST API 키 입력
    rest_api_key = input("📝 카카오 REST API 키를 입력하세요: ").strip()
    
    if not rest_api_key:
        print("❌ REST API 키가 필요합니다!")
        return
    
    print("\n🔐 카카오 인증 절차를 시작합니다...")
    
    # 인증 코드 받기
    auth_code = get_kakao_access_token(rest_api_key)
    
    if not auth_code:
        print("❌ 인증 코드가 필요합니다!")
        return
    
    # 액세스 토큰 발급
    access_token = exchange_code_for_token(rest_api_key, auth_code)
    
    if not access_token:
        print("❌ 액세스 토큰 발급 실패!")
        return
    
    # 오픈채팅방 ID 입력
    chat_id = input("📝 오픈채팅방 ID를 입력하세요 (또는 Enter로 나에게 보내기): ").strip()
    
    if not chat_id:
        chat_id = "나에게_보내기"
    
    # 테스트 메시지 생성
    test_message = generate_test_message()
    
    print("\n📤 카카오톡 메시지 전송 중...")
    print("━" * 30)
    
    # 메시지 전송
    success = send_to_openchat(access_token, chat_id, test_message)
    
    if success:
        print("\n🎉 카카오톡 전송 성공!")
        print("📱 카카오톡에서 메시지를 확인하세요!")
        print()
        print("✅ GitHub Secrets 설정용 정보:")
        print(f"   KAKAO_ACCESS_TOKEN: {access_token}")
        print(f"   KAKAO_OPENCHAT_ID: {chat_id}")
    else:
        print("\n❌ 카카오톡 전송 실패!")
        print("🔍 설정을 다시 확인해주세요.")

if __name__ == "__main__":
    main() 