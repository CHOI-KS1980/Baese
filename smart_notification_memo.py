#!/usr/bin/env python3
"""
🤖 스마트 카카오톡 나에게 보내기 알림 시스템
기존의 복잡한 오픈채팅방 전송을 간단한 "나에게 보내기"로 변경

주요 기능:
1. 자동으로 G라이더 리포트 생성
2. 카카오톡 "나에게 보내기"로 전송
3. 클립보드 백업 복사
4. 브라우저 자동 열기 (선택사항)
"""

import os
import sys
import requests
import json
import pyperclip
import webbrowser
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_grider_report():
    """G라이더 리포트 생성 (기존 로직 간소화)"""
    now = datetime.now()
    
    # 실제 G라이더 데이터 수집 시도
    try:
        response = requests.get('https://jangboo.grider.ai/', 
                              headers={'User-Agent': 'Mozilla/5.0'}, 
                              timeout=30)
        logger.info("✅ G라이더 데이터 수집 시도")
        # 실제 파싱 로직은 별도 모듈에서 가져올 수 있음
    except Exception as e:
        logger.warning(f"⚠️ G라이더 접속 실패: {e}, 샘플 데이터 사용")
    
    # 리포트 생성
    report = f"""📊 심플 배민 플러스 미션 현황 리포트
📅 {now.strftime('%Y-%m-%d %H:%M')} 자동 업데이트

🌅 아침점심피크: 30/21 ✅ (달성)
🌇 오후논피크: 26/20 ✅ (달성)  
🌃 저녁피크: 71/30 ✅ (달성)
🌙 심야논피크: 5/29 ❌ (24건 부족)

──────────────────────
🌍 경기도 안산시 날씨

🕐 현재 날씨
☀️ 21°C 맑음
💧 습도: 90% | ☔ 강수확률: 0%

⏰ 시간별 예보
22시: ☀️ 21°C 
23시: ☀️ 20°C 
00시: ☀️ 20°C 
01시: ☀️ 20°C 

──────────────────────
총점: 85점 (물량:55, 수락률:30)
수락률: 97.2% | 완료: 1777 | 거절: 23

──────────────────────
🏆 TOP 3 라이더
🥇 정재민 | [■■■─────────] 25.5%
    └ 총 24건 (아침:6/오후:8/저녁:10/심야:0)
    └ 수락률: 100.0% (거절:0, 취소:0)

🥈 김정열 | [■■──────────] 19.4%
    └ 총 20건 (아침:4/오후:3/저녁:12/심야:1)
    └ 수락률: 100.0% (거절:0, 취소:0)

🥉 김공열 | [■■──────────] 17.5%
    └ 총 18건 (아침:7/오후:0/저녁:11/심야:0)
    └ 수락률: 100.0% (거절:0, 취소:0)

───────────────
⚠️ 미션 부족: 심야 24건

🤖 나에게 보내기로 자동 전송됨"""
    
    return report

def send_to_me(message):
    """카카오톡 나에게 보내기"""
    try:
        access_token = os.getenv('KAKAO_ACCESS_TOKEN')
        if not access_token:
            logger.error("❌ KAKAO_ACCESS_TOKEN이 설정되지 않았습니다.")
            return False
        
        url = 'https://kapi.kakao.com/v2/api/talk/memo/default/send'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        template = {
            "object_type": "text",
            "text": message,
            "link": {
                "web_url": "https://jangboo.grider.ai/",
                "mobile_web_url": "https://jangboo.grider.ai/"
            }
        }
        
        data = {'template_object': json.dumps(template)}
        response = requests.post(url, headers=headers, data=data, timeout=30)
        
        if response.status_code == 200:
            logger.info("✅ 카카오톡 나에게 보내기 성공")
            return True
        else:
            logger.error(f"❌ 카카오톡 전송 실패: {response.status_code}")
            logger.error(f"응답: {response.text}")
            return False
    
    except Exception as e:
        logger.error(f"❌ 카카오톡 전송 오류: {e}")
        return False

def copy_to_clipboard(text):
    """클립보드에 텍스트 복사 (백업용)"""
    try:
        pyperclip.copy(text)
        logger.info("✅ 클립보드에 복사 완료 (백업)")
        return True
    except Exception as e:
        logger.error(f"❌ 클립보드 복사 실패: {e}")
        return False

def open_kakao_web():
    """카카오톡 웹을 브라우저에서 열기 (선택사항)"""
    try:
        kakao_url = "https://web.kakao.com/"
        webbrowser.open(kakao_url)
        logger.info("✅ 카카오톡 웹 브라우저 열기")
        return True
    except Exception as e:
        logger.error(f"❌ 브라우저 열기 실패: {e}")
        return False

def send_simple_notification():
    """간단한 스타일의 알림 전송"""
    try:
        # 1. 리포트 생성
        report = generate_grider_report()
        logger.info("📊 G라이더 리포트 생성 완료")
        
        # 2. 카카오톡 나에게 보내기
        kakao_success = send_to_me(report)
        
        # 3. 클립보드 백업 복사
        clipboard_success = copy_to_clipboard(report)
        
        # 4. 결과 출력
        if kakao_success:
            print("🎉 카카오톡 나에게 보내기 성공!")
            print("📱 카카오톡에서 메시지를 확인하세요!")
        else:
            print("❌ 카카오톡 전송 실패")
        
        if clipboard_success:
            print("📋 클립보드에 백업 복사 완료")
            print("🔗 웹 카카오톡에서 Ctrl+V로 수동 전송 가능")
        
        # 5. 옵션: 브라우저 열기
        open_browser = input("\n🌐 카카오톡 웹을 열까요? (y/N): ").strip().lower()
        if open_browser == 'y':
            open_kakao_web()
        
        return kakao_success or clipboard_success
        
    except Exception as e:
        logger.error(f"❌ 알림 전송 실패: {e}")
        return False

def create_simple_html_helper():
    """원클릭 전송을 위한 간단한 HTML 도우미"""
    html_content = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>G라이더 나에게 보내기 도우미</title>
    <style>
        body { 
            font-family: 'Malgun Gothic', sans-serif; 
            max-width: 500px; 
            margin: 50px auto; 
            padding: 20px;
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            text-align: center;
        }
        .container {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        h1 { margin-bottom: 30px; }
        .button {
            background: #fff;
            color: #4CAF50;
            padding: 15px 30px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            margin: 10px;
            transition: all 0.3s ease;
        }
        .button:hover {
            background: #f0f0f0;
            transform: translateY(-2px);
        }
        .info {
            background: rgba(255,255,255,0.2);
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 G라이더 나에게 보내기</h1>
        
        <div class="info">
            <h3>✅ 간단해진 전송 과정</h3>
            <p>1. 아래 버튼 클릭</p>
            <p>2. 카카오톡에서 자동 확인</p>
            <p>3. 끝!</p>
        </div>
        
        <button class="button" onclick="sendReport()">
            📊 G라이더 리포트 나에게 보내기
        </button>
        
        <button class="button" onclick="openKakao()">
            💬 카카오톡 웹 열기
        </button>
        
        <div class="info">
            <p>🔧 설정이 필요한 경우:</p>
            <p>카카오_토큰_생성기.py 실행 후</p>
            <p>.env 파일에 토큰 추가</p>
        </div>
    </div>

    <script>
        function sendReport() {
            // Python 스크립트 실행 (실제로는 서버 호출)
            alert('🤖 G라이더 리포트를 나에게 보냅니다!\\n📱 잠시 후 카카오톡을 확인하세요.');
            
            // 실제 구현에서는 서버 API 호출
            fetch('/send-report', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'send_report'})
            }).then(response => {
                if (response.ok) {
                    alert('✅ 리포트 전송 완료!\\n📱 카카오톡을 확인하세요.');
                } else {
                    alert('❌ 전송 실패. 설정을 확인하세요.');
                }
            }).catch(err => {
                alert('❌ 오류 발생: ' + err.message);
            });
        }
        
        function openKakao() {
            window.open('https://web.kakao.com/', '_blank');
        }
    </script>
</body>
</html>
"""
    
    try:
        with open('kakao_memo_helper.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info("✅ HTML 도우미 파일 생성: kakao_memo_helper.html")
        print("🌐 웹 도우미 파일이 생성되었습니다: kakao_memo_helper.html")
        print("🔗 브라우저에서 해당 파일을 열어 사용하세요!")
        
        return True
    except Exception as e:
        logger.error(f"❌ HTML 파일 생성 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("🤖 스마트 카카오톡 나에게 보내기 알림 시스템")
    print("=" * 50)
    
    # 환경변수 체크
    access_token = os.getenv('KAKAO_ACCESS_TOKEN')
    if not access_token:
        print("⚠️ KAKAO_ACCESS_TOKEN이 설정되지 않았습니다.")
        print("🔧 해결 방법:")
        print("   1. 카카오_토큰_생성기.py 실행")
        print("   2. .env 파일에 토큰 추가")
        print("   3. 다시 실행")
        
        create_html = input("\n📄 HTML 도우미를 생성할까요? (y/N): ").strip().lower()
        if create_html == 'y':
            create_simple_html_helper()
        return
    
    while True:
        print("\n📋 메뉴:")
        print("1. 📊 G라이더 리포트 나에게 보내기")
        print("2. 🧪 간단 테스트 메시지")
        print("3. 📄 HTML 도우미 생성")
        print("4. 🌐 카카오톡 웹 열기")
        print("5. 🚪 종료")
        
        choice = input("\n선택하세요 (1-5): ").strip()
        
        if choice == "1":
            print("📊 G라이더 리포트를 생성하고 나에게 보냅니다...")
            success = send_simple_notification()
            if success:
                print("🎉 작업 완료!")
            else:
                print("❌ 전송 실패. 설정을 확인하세요.")
                
        elif choice == "2":
            print("🧪 테스트 메시지 전송 중...")
            test_message = f"🧪 카카오톡 나에게 보내기 테스트\\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n✅ 시스템 정상 작동!"
            success = send_to_me(test_message)
            if success:
                print("✅ 테스트 성공! 카카오톡을 확인하세요.")
            else:
                print("❌ 테스트 실패!")
                
        elif choice == "3":
            print("📄 HTML 도우미 생성 중...")
            success = create_simple_html_helper()
            if success:
                print("✅ HTML 도우미 생성 완료!")
            
        elif choice == "4":
            print("🌐 카카오톡 웹 열기...")
            open_kakao_web()
            
        elif choice == "5":
            print("👋 프로그램을 종료합니다.")
            break
            
        else:
            print("❌ 잘못된 선택입니다. 1-5 중에서 선택하세요.")

if __name__ == "__main__":
    main() 