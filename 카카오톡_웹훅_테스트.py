#!/usr/bin/env python3
"""
🔧 카카오톡 웹훅 테스트 서버
로컬에서 웹훅을 받아서 카카오톡으로 메시지 전송
"""

import os
import json
import requests
from flask import Flask, request, jsonify
from datetime import datetime
import pytz

app = Flask(__name__)
KST = pytz.timezone('Asia/Seoul')

def send_kakao_message(message, chat_id, access_token):
    """카카오톡 메시지 전송"""
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
        
        response = requests.post(url, headers=headers, data=data)
        
        if response.status_code == 200:
            print(f"✅ 카카오톡 메시지 전송 성공!")
            return True
        else:
            print(f"❌ 카카오톡 전송 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 카카오톡 전송 오류: {e}")
        return False

@app.route('/webhook', methods=['POST'])
def webhook():
    """웹훅 엔드포인트"""
    try:
        # 요청 데이터 받기
        data = request.get_json()
        
        print(f"📨 웹훅 수신: {datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        # 환경변수에서 카카오 정보 가져오기
        access_token = os.getenv('KAKAO_ACCESS_TOKEN')
        chat_id = os.getenv('KAKAO_OPENCHAT_ID')
        
        if not access_token or not chat_id:
            print("❌ 카카오 토큰 또는 채팅방 ID가 설정되지 않았습니다!")
            return jsonify({"status": "error", "message": "카카오 설정 필요"}), 400
        
        # 메시지 추출
        message = data.get('message', '테스트 메시지')
        
        # 카카오톡으로 메시지 전송
        success = send_kakao_message(message, chat_id, access_token)
        
        if success:
            return jsonify({
                "status": "success", 
                "message": "메시지 전송 완료",
                "timestamp": datetime.now(KST).isoformat()
            })
        else:
            return jsonify({
                "status": "error", 
                "message": "메시지 전송 실패"
            }), 500
            
    except Exception as e:
        print(f"❌ 웹훅 처리 오류: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    """테스트 엔드포인트"""
    return jsonify({
        "status": "ok",
        "message": "카카오톡 웹훅 서버 정상 작동",
        "timestamp": datetime.now(KST).isoformat()
    })

if __name__ == '__main__':
    print("🚀 카카오톡 웹훅 테스트 서버 시작!")
    print("━" * 50)
    print("📡 엔드포인트:")
    print("  - POST /webhook : 웹훅 수신")
    print("  - GET  /test    : 서버 상태 확인")
    print()
    print("🔧 환경변수 설정 필요:")
    print("  - KAKAO_ACCESS_TOKEN")
    print("  - KAKAO_OPENCHAT_ID")
    print("━" * 50)
    
    # 플라스크 서버 실행
    app.run(host='0.0.0.0', port=5000, debug=True) 