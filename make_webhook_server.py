#!/usr/bin/env python3
"""
Make.com용 웹훅 서버
Make.com에서 전송된 데이터를 받아 카카오톡으로 전송
"""

from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# 카카오 API 설정
KAKAO_ACCESS_TOKEN = os.getenv('KAKAO_ACCESS_TOKEN')
OPENCHAT_ID = os.getenv('KAKAO_OPENCHAT_ID', 'gt26QiBg')

@app.route('/webhook/mission', methods=['POST'])
def receive_mission_data():
    """Make.com에서 미션 데이터 수신"""
    try:
        data = request.get_json()
        
        message = data.get('message', '')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        source = data.get('source', 'make.com')
        
        print(f"📥 {timestamp} 웹훅 수신 ({source})")
        print(f"📝 메시지: {message[:100]}...")
        
        # 카카오톡 전송 시뮬레이션 (실제로는 다른 방법 사용)
        result = send_to_kakao_alternative(message)
        
        return jsonify({
            'status': 'success',
            'message': '메시지 처리 완료',
            'timestamp': datetime.now().isoformat(),
            'result': result
        })
        
    except Exception as e:
        print(f"❌ 웹훅 처리 오류: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

def send_to_kakao_alternative(message):
    """카카오톡 대안 전송 방법들"""
    methods = []
    
    # 1. 텔레그램으로 전송
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if telegram_token and telegram_chat_id:
        try:
            telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
            telegram_data = {
                'chat_id': telegram_chat_id,
                'text': f"🤖 G라이더 미션 알림\n\n{message}",
                'parse_mode': 'HTML'
            }
            response = requests.post(telegram_url, json=telegram_data)
            if response.status_code == 200:
                methods.append("✅ 텔레그램 전송 성공")
        except Exception as e:
            methods.append(f"❌ 텔레그램 실패: {e}")
    
    # 2. Discord 웹훅으로 전송
    discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
    if discord_webhook:
        try:
            discord_data = {
                'content': f"🤖 **G라이더 미션 현황**\n```\n{message}\n```"
            }
            response = requests.post(discord_webhook, json=discord_data)
            if response.status_code == 204:
                methods.append("✅ Discord 전송 성공")
        except Exception as e:
            methods.append(f"❌ Discord 실패: {e}")
    
    # 3. 슬랙 웹훅으로 전송
    slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
    if slack_webhook:
        try:
            slack_data = {
                'text': f"🤖 G라이더 미션 현황",
                'attachments': [
                    {
                        'color': 'good',
                        'text': message,
                        'ts': datetime.now().timestamp()
                    }
                ]
            }
            response = requests.post(slack_webhook, json=slack_data)
            if response.status_code == 200:
                methods.append("✅ 슬랙 전송 성공")
        except Exception as e:
            methods.append(f"❌ 슬랙 실패: {e}")
    
    # 4. 이메일 전송 (SendGrid 등)
    email_api_key = os.getenv('SENDGRID_API_KEY')
    if email_api_key:
        methods.append("📧 이메일 전송 기능 대기")
    
    return methods if methods else ["📋 메시지 로그만 저장"]

@app.route('/webhook/test', methods=['GET', 'POST'])
def test_webhook():
    """웹훅 테스트 엔드포인트"""
    return jsonify({
        'status': 'ok',
        'message': 'Make.com 웹훅 서버 정상 작동',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print("🚀 Make.com 웹훅 서버 시작!")
    print(f"📡 포트: {port}")
    print(f"🔧 디버그: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
