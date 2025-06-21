from flask import Flask, request, jsonify
import requests
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return "🚀 간단한 테스트 서버 작동중!"

@app.route('/send-kakao', methods=['POST'])
def send_kakao():
    try:
        data = request.json
        
        # 현재 시간으로 간단한 메시지 생성
        now = datetime.now()
        message = f"""🚀 G라이더 미션 현황 📊

📅 {now.strftime('%Y-%m-%d %H:%M')} 업데이트

📊 **미션 현황**
총 미션: 집계중

🏆 **TOP 라이더**
집계중

💰 **오늘의 포인트**
포인트 집계중...

🎯 화이팅! 더 많은 미션을 완주하세요!
⚡ 자동 업데이트 by G라이더봇"""

        return jsonify({
            "status": "success",
            "message": "테스트 메시지 생성 완료",
            "generated_message": message,
            "timestamp": now.isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 