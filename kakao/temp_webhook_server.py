#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
카카오 i 오픈빌더 테스트용 임시 웹훅 서버
실제 웹훅 URL을 생성하고 테스트하기 위한 서버입니다.
"""

from flask import Flask, request, jsonify
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    """카카오 i 오픈빌더 웹훅 엔드포인트"""
    try:
        # 요청 데이터 받기
        data = request.get_json()
        print(f"🎯 웹훅 요청 받음: {datetime.now()}")
        print(f"📩 데이터: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        # 사용자 메시지 추출
        user_message = ""
        if data and 'userRequest' in data:
            user_message = data['userRequest'].get('utterance', '')
        
        # 응답 생성
        response = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": f"✅ 웹훅 테스트 성공!\n받은 메시지: {user_message}\n시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        }
                    }
                ]
            }
        }
        
        print(f"📤 응답 전송: {json.dumps(response, ensure_ascii=False, indent=2)}")
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        error_response = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": f"❌ 오류가 발생했습니다: {str(e)}"
                        }
                    }
                ]
            }
        }
        return jsonify(error_response)

@app.route('/health', methods=['GET'])
def health():
    """서버 상태 확인"""
    return jsonify({
        "status": "healthy",
        "time": datetime.now().isoformat(),
        "message": "카카오 웹훅 서버가 정상 작동 중입니다."
    })

if __name__ == '__main__':
    print("🚀 카카오 i 오픈빌더 테스트 웹훅 서버 시작")
    print("📍 웹훅 URL: http://localhost:5000/webhook")
    print("🔍 상태 확인: http://localhost:5000/health")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True) 