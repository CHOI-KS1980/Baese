#!/usr/bin/env python3
"""
🎯 최종 현실적 솔루션: 카카오톡 나에게 보내기 + 수동 복사
- 웹 크롤링 → 데이터 가공 (자동)
- 카카오톡 나에게 보내기 (자동)
- 오픈채팅방 복사/붙여넣기 (수동 5초)
"""

import requests
import json
import schedule
import time
from datetime import datetime
import pyperclip  # 클립보드 기능

# 카카오톡 나에게 보내기 설정
KAKAO_REST_API_KEY = "your_rest_api_key"
KAKAO_ACCESS_TOKEN = "your_access_token"

def get_grider_data():
    """G라이더 데이터 크롤링 및 가공 (기존 로직)"""
    try:
        # 여기에 기존 크롤링 로직 삽입
        data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "missions": ["미션 1", "미션 2", "미션 3"],
            "rewards": "1,500원",
            "status": "활성"
        }
        return data
    except Exception as e:
        print(f"❌ 데이터 수집 실패: {e}")
        return None

def format_message(data):
    """메시지 포맷팅"""
    if not data:
        return None
    
    message = f"""🚀 G라이더 미션 알림 [{data['timestamp']}]

📋 오늘의 미션:
{chr(10).join(f"• {mission}" for mission in data['missions'])}

💰 예상 리워드: {data['rewards']}
📊 상태: {data['status']}

#G라이더 #미션알림 #자동화"""
    
    return message

def send_to_kakao_me(message):
    """카카오톡 나에게 보내기"""
    try:
        url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
        
        headers = {
            "Authorization": f"Bearer {KAKAO_ACCESS_TOKEN}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        template_object = {
            "object_type": "text",
            "text": message,
            "link": {
                "web_url": "https://your-website.com",
                "mobile_web_url": "https://your-website.com"
            }
        }
        
        data = {
            "template_object": json.dumps(template_object)
        }
        
        response = requests.post(url, headers=headers, data=data)
        
        if response.status_code == 200:
            print("✅ 카카오톡 나에게 보내기 성공!")
            return True
        else:
            print(f"❌ 카카오톡 전송 실패: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ 카카오톡 전송 오류: {e}")
        return False

def copy_to_clipboard(message):
    """클립보드에 복사 (백업용)"""
    try:
        pyperclip.copy(message)
        print("📋 클립보드에 복사 완료!")
        print("💡 오픈채팅방에서 Ctrl+V로 붙여넣기 하세요!")
        return True
    except Exception as e:
        print(f"❌ 클립보드 복사 실패: {e}")
        return False

def send_notification():
    """메인 실행 함수"""
    print(f"\n🚀 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 자동 알림 시작")
    
    # 1. 데이터 수집
    data = get_grider_data()
    if not data:
        print("❌ 데이터 수집 실패로 중단")
        return
    
    # 2. 메시지 포맷팅
    message = format_message(data)
    if not message:
        print("❌ 메시지 생성 실패로 중단")
        return
    
    print("📝 생성된 메시지:")
    print("-" * 50)
    print(message)
    print("-" * 50)
    
    # 3. 카카오톡 나에게 보내기
    kakao_success = send_to_kakao_me(message)
    
    # 4. 클립보드에도 복사 (백업)
    clipboard_success = copy_to_clipboard(message)
    
    # 5. 결과 안내
    if kakao_success:
        print("\n🎉 완료! 다음 단계:")
        print("1. 📱 카카오톡에서 나에게 온 메시지 확인")
        print("2. 📋 메시지 복사 (길게 터치)")
        print("3. 📤 오픈채팅방에 붙여넣기")
        print("⏱️  소요시간: 약 5초")
    else:
        print("\n⚠️  카카오톡 전송 실패!")
        print("📋 클립보드에 복사된 내용을 직접 붙여넣기 하세요!")

def setup_scheduler():
    """스케줄러 설정"""
    # 매일 특정 시간에 실행
    schedule.every().day.at("09:00").do(send_notification)
    schedule.every().day.at("12:00").do(send_notification)
    schedule.every().day.at("18:00").do(send_notification)
    
    print("⏰ 스케줄러 설정 완료:")
    print("- 매일 09:00, 12:00, 18:00에 자동 실행")
    print("- 카카오톡 나에게 보내기 + 클립보드 복사")
    print("- 수동 복사/붙여넣기만 하면 됩니다!")

def main():
    """메인 실행"""
    print("🎯 G라이더 현실적 자동화 시스템 시작")
    print("=" * 60)
    
    # 즉시 한 번 실행 (테스트)
    print("🧪 테스트 실행:")
    send_notification()
    
    # 스케줄러 설정
    setup_scheduler()
    
    print("\n🔄 스케줄러 실행 중... (Ctrl+C로 종료)")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크
    except KeyboardInterrupt:
        print("\n⏹️  시스템 종료")

if __name__ == "__main__":
    main() 