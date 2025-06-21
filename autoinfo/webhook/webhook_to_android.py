#!/usr/bin/env python3
"""
웹훅 서버 → 안드로이드 MacroDroid 연동
기존 웹훅 서버를 안드로이드 자동화에 맞게 수정
"""

import os
import json
import requests
from datetime import datetime
from flask import Flask, request, jsonify
import logging

# 환경 변수 설정
MACRODROID_WEBHOOK_KEY = os.getenv('MACRODROID_WEBHOOK_KEY', 'your_macrodroid_key_here')
MACRODROID_IDENTIFIER = os.getenv('MACRODROID_IDENTIFIER', 'grider_report')
OPENCHAT_ROOM_NAME = os.getenv('OPENCHAT_ROOM_NAME', 'G라이더 미션방')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webhook_android.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def generate_grider_report():
    """기존 리포트 생성 함수 (예시)"""
    # 여기에 기존 크롤링 및 데이터 처리 로직 구현
    report = f"""📊 배민 G라이더 미션 현황 📊

🌅 아침점심피크: 18/20 ✅ (달성)
🌇 오후논피크: 156/200 ❌ (44건 부족)  
🌃 저녁피크: 23/25 ❌ (2건 부족)
🌙 심야논피크: 13/20 ❌ (7건 부족)

──────────────────────

🌤️ 안산 날씨
현재: 맑음 🌞 18°C
오늘: 최고 22°C, 최저 12°C
습도: 65% | 바람: 북서 2.1m/s

──────────────────────

총점: 847점 (물량:520, 수락률:327)
수락률: 89.2% | 완료: 210 | 거절: 26

──────────────────────

⏰ 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🤖 자동화 시스템 v2.0"""
    
    return report

def send_to_android_macrodroid(message, chat_room_name=None):
    """안드로이드 MacroDroid로 메시지 전송"""
    try:
        # MacroDroid 웹훅 URL 구성
        macrodroid_url = f"https://trigger.macrodroid.com/{MACRODROID_WEBHOOK_KEY}/{MACRODROID_IDENTIFIER}"
        
        # 전송할 데이터 구성
        payload = {
            "message": message,
            "chat_room_name": chat_room_name or OPENCHAT_ROOM_NAME,
            "timestamp": datetime.now().isoformat(),
            "source": "grider_automation"
        }
        
        # URL 파라미터로 전송 (MacroDroid 웹훅 방식)
        params = {
            "message": message,
            "chat_room": chat_room_name or OPENCHAT_ROOM_NAME
        }
        
        logger.info(f"📤 안드로이드로 전송 시작: {macrodroid_url}")
        logger.info(f"📝 메시지 길이: {len(message)} 문자")
        
        # MacroDroid 웹훅 호출
        response = requests.get(macrodroid_url, params=params, timeout=30)
        
        if response.status_code == 200:
            logger.info("✅ 안드로이드 MacroDroid 전송 성공")
            return True
        else:
            logger.error(f"❌ MacroDroid 전송 실패: {response.status_code}")
            logger.error(f"응답: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error("⏰ MacroDroid 전송 타임아웃")
        return False
    except Exception as e:
        logger.error(f"❌ MacroDroid 전송 오류: {str(e)}")
        return False

@app.route('/webhook', methods=['POST'])
def webhook():
    """기존 웹훅 엔드포인트 (GitHub Actions 등에서 호출)"""
    try:
        logger.info("🔄 웹훅 요청 수신")
        
        # 요청 데이터 파싱
        data = request.get_json() or {}
        
        # 리포트 생성
        message = generate_grider_report()
        
        # 안드로이드 MacroDroid로 전송
        success = send_to_android_macrodroid(message)
        
        if success:
            response_data = {
                "status": "success",
                "message": "안드로이드로 전송 완료",
                "timestamp": datetime.now().isoformat(),
                "message_length": len(message)
            }
            logger.info("🎉 전체 플로우 완료")
            return jsonify(response_data), 200
        else:
            response_data = {
                "status": "error", 
                "message": "안드로이드 전송 실패",
                "timestamp": datetime.now().isoformat()
            }
            return jsonify(response_data), 500
            
    except Exception as e:
        logger.error(f"💥 웹훅 처리 오류: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/test', methods=['GET', 'POST'])
def test_android():
    """안드로이드 연동 테스트 엔드포인트"""
    try:
        logger.info("🧪 안드로이드 연동 테스트 시작")
        
        test_message = f"""🧪 안드로이드 연동 테스트

📱 MacroDroid 자동화 테스트
⏰ 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ 웹훅 서버 정상 동작
✅ 안드로이드 MacroDroid 연동 
✅ 카카오톡 자동 전송 준비

🎉 완전 자동화 시스템 가동!"""
        
        success = send_to_android_macrodroid(test_message)
        
        if success:
            return jsonify({
                "status": "success",
                "message": "안드로이드 테스트 성공",
                "test_message": test_message
            })
        else:
            return jsonify({
                "status": "error",
                "message": "안드로이드 테스트 실패"
            }), 500
            
    except Exception as e:
        logger.error(f"🔥 테스트 오류: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/status', methods=['GET'])
def status():
    """시스템 상태 확인"""
    return jsonify({
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "macrodroid_key": MACRODROID_WEBHOOK_KEY[:10] + "...",
        "identifier": MACRODROID_IDENTIFIER,
        "chat_room": OPENCHAT_ROOM_NAME
    })

@app.route('/config', methods=['GET'])
def config():
    """설정 정보 확인"""
    return jsonify({
        "macrodroid_webhook_key": "설정됨" if MACRODROID_WEBHOOK_KEY != 'your_macrodroid_key_here' else "미설정",
        "macrodroid_identifier": MACRODROID_IDENTIFIER,
        "openchat_room_name": OPENCHAT_ROOM_NAME,
        "webhook_url": f"https://trigger.macrodroid.com/{MACRODROID_WEBHOOK_KEY}/{MACRODROID_IDENTIFIER}"
    })

if __name__ == '__main__':
    logger.info("🚀 웹훅 → 안드로이드 연동 서버 시작")
    logger.info(f"📱 MacroDroid 식별자: {MACRODROID_IDENTIFIER}")
    logger.info(f"💬 오픈채팅방: {OPENCHAT_ROOM_NAME}")
    
    # 환경 변수 확인
    if MACRODROID_WEBHOOK_KEY == 'your_macrodroid_key_here':
        logger.warning("⚠️ MACRODROID_WEBHOOK_KEY가 설정되지 않았습니다!")
        logger.warning("💡 MacroDroid에서 웹훅 URL을 복사하여 환경변수에 설정하세요")
    
    app.run(host='0.0.0.0', port=5000, debug=True) 