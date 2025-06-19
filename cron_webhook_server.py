from flask import Flask, request, jsonify
import requests
import json
import re
import schedule
import time
import threading
from datetime import datetime
from apscheduler import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

app = Flask(__name__)

# 글로벌 설정
KAKAO_ACCESS_TOKEN = "a42a7d49082706c3e7241271f9fe3d00"
OPENCHAT_ID = "gt26QiBg"

@app.route('/')
def home():
    return "🚀 G라이더 자동화 서버 v3.0 - 크론 스케줄러 포함!"

@app.route('/send-kakao', methods=['POST'])
def send_kakao():
    """Make.com이나 외부에서 호출하는 API"""
    try:
        data = request.json
        
        # 데이터 추출
        status = data.get('status', '')
        raw_data = data.get('raw_data', '')
        chat_id = data.get('chat_id', OPENCHAT_ID)
        access_token = data.get('access_token', KAKAO_ACCESS_TOKEN)
        
        # 기존 방식도 지원 (하위 호환성)
        if not status and data.get('message'):
            message = data.get('message')
        else:
            # 새로운 방식: 서버에서 메시지 생성
            message = generate_mission_message(raw_data)
        
        # 필수 파라미터 확인
        if not all([message, chat_id, access_token]):
            return jsonify({
                "error": "필수 파라미터가 누락되었습니다",
                "received": {
                    "message_length": len(message) if message else 0,
                    "chat_id": chat_id,
                    "access_token": f"{access_token[:10]}..." if access_token else ""
                }
            }), 400
        
        # 카카오톡 API 호출
        kakao_result = send_to_kakao(message, chat_id, access_token)
        
        return jsonify(kakao_result)
            
    except Exception as e:
        return jsonify({
            "error": "서버 내부 오류",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/auto-send', methods=['POST'])
def auto_send():
    """자동 스케줄링으로 호출되는 엔드포인트"""
    try:
        print(f"🔄 {datetime.now()} 자동 전송 시작")
        
        # G라이더 데이터 수집
        try:
            response = requests.get('https://jangboo.grider.ai/', 
                                  headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                                  timeout=30)
            raw_data = response.text
        except Exception as e:
            print(f"⚠️ 데이터 수집 실패: {e}")
            raw_data = "<script>location.href='/login';</script>"
        
        # 메시지 생성
        message = generate_mission_message(raw_data)
        
        # 카카오톡 전송
        result = send_to_kakao(message, OPENCHAT_ID, KAKAO_ACCESS_TOKEN)
        
        print(f"✅ 자동 전송 완료: {result}")
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ 자동 전송 오류: {e}")
        return jsonify({"error": str(e)}), 500

def generate_mission_message(raw_data):
    """HTML 데이터에서 메시지 자동 생성"""
    
    # 현재 시간
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H:%M')
    
    # 기본 메시지
    message = f"""🚀 G라이더 미션 현황 📊

📅 {date_str} {time_str} 업데이트

"""
    
    # HTML에서 데이터 추출 시도
    try:
        if raw_data and isinstance(raw_data, str):
            # 숫자 찾기 (미션 개수)
            numbers = re.findall(r'\d{1,3}(?:,\d{3})*', raw_data)
            mission_count = numbers[0] if numbers else "집계중"
            
            # 라이더 이름 찾기
            rider_pattern = r'라이더[^0-9]*([가-힣]{2,4})'
            rider_match = re.search(rider_pattern, raw_data)
            top_rider = rider_match.group(1) if rider_match else "집계중"
            
            # 로그인 리다이렉트 체크
            if '<script>' in raw_data and 'location.href' in raw_data:
                message += """❌ **사이트 접근 제한**
로그인이 필요한 상태입니다.

🔄 **다음 업데이트에서 재시도**
시스템이 자동으로 재연결을 시도합니다.

💡 **임시 현황**
수동 확인이 필요한 시점입니다."""
            else:
                message += f"""📊 **미션 현황**
총 미션: {mission_count}건

🏆 **TOP 라이더**
{top_rider}님

💰 **오늘의 포인트**
포인트 집계중...

🎯 화이팅! 더 많은 미션을 완주하세요!"""
        else:
            message += """📊 **미션 현황**
총 미션: 집계중

🏆 **TOP 라이더**
집계중

💰 **오늘의 포인트**
포인트 집계중...

🎯 화이팅! 더 많은 미션을 완주하세요!"""
            
    except Exception as e:
        message += f"""❌ **데이터 처리 오류**
{str(e)[:50]}...

🔄 **자동 재시도**
다음 업데이트를 기다려주세요."""
    
    # 공통 푸터
    message += "\n\n⚡ 자동 업데이트 by G라이더봇 (Render.com)"
    
    return message

def send_to_kakao(message, chat_id, access_token):
    """카카오톡 API 전송"""
    try:
        url = "https://kapi.kakao.com/v1/api/talk/friends/message/default/send"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        template_object = {
            "object_type": "text", 
            "text": message,
            "link": {
                "web_url": "https://jangboo.grider.ai/",
                "mobile_web_url": "https://jangboo.grider.ai/"
            }
        }
        
        payload = {
            "template_object": json.dumps(template_object),
            "receiver_uuids": f'["{chat_id}"]'
        }
        
        response = requests.post(url, headers=headers, data=payload, timeout=30)
        
        if response.status_code == 200:
            return {
                "status": "success",
                "message": "카카오톡 전송 성공!",
                "response": response.json(),
                "sent_message": message[:100] + "..." if len(message) > 100 else message
            }
        else:
            return {
                "status": "error", 
                "message": "카카오톡 전송 실패",
                "error": response.text,
                "status_code": response.status_code
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": "카카오톡 API 호출 실패", 
            "error": str(e)
        }

# 스케줄링 함수들
def scheduled_send():
    """스케줄된 자동 전송"""
    try:
        # 내부적으로 auto_send 호출
        response = requests.post('http://localhost:5000/auto-send', timeout=60)
        print(f"스케줄 실행 결과: {response.status_code}")
    except Exception as e:
        print(f"스케줄 실행 오류: {e}")

# 스케줄 설정
def setup_schedule():
    """자동 전송 스케줄 설정"""
    # 주요 시간대 (08:00, 12:00, 18:00, 22:00)
    schedule.every().day.at("08:00").do(scheduled_send)
    schedule.every().day.at("12:00").do(scheduled_send)
    schedule.every().day.at("18:00").do(scheduled_send)
    schedule.every().day.at("22:00").do(scheduled_send)
    
    # 피크 시간대 (10:30, 14:30, 20:30)
    schedule.every().day.at("10:30").do(scheduled_send)
    schedule.every().day.at("14:30").do(scheduled_send)
    schedule.every().day.at("20:30").do(scheduled_send)

def run_scheduler():
    """백그라운드 스케줄러 실행"""
    setup_schedule()
    print("⏰ 자동 스케줄러 시작!")
    print("📅 전송 시간: 08:00, 10:30, 12:00, 14:30, 18:00, 20:30, 22:00")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 체크

# 헬스체크 엔드포인트
@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0",
        "features": ["webhook", "auto-schedule", "kakao-api"],
        "next_scheduled": str(schedule.next_run()) if schedule.jobs else None
    })

@app.route('/schedule-status')
def schedule_status():
    """스케줄 상태 확인"""
    return jsonify({
        "total_jobs": len(schedule.jobs),
        "next_run": str(schedule.next_run()) if schedule.jobs else None,
        "jobs": [str(job) for job in schedule.jobs]
    })

if __name__ == '__main__':
    # 백그라운드에서 스케줄러 시작
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    print("🚀 G라이더 완전 자동화 서버 시작!")
    print("🔗 웹훅: /send-kakao")
    print("⏰ 자동 실행: 하루 7회")
    print("❤️ 헬스체크: /health")
    
    app.run(debug=False, host='0.0.0.0', port=5000) 