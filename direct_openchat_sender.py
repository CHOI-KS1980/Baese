#!/usr/bin/env python3
"""
카카오톡 웹버전을 이용한 오픈채팅방 직접 메시지 전송
Selenium 기반 완전 자동화 시스템
"""

import os
import sys
import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class KakaoOpenChatSender:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.setup_driver()
    
    def setup_driver(self):
        """Chrome 드라이버 설정"""
        chrome_options = Options()
        
        # GitHub Actions 환경에서 실행할 때는 headless 모드
        if os.getenv('GITHUB_ACTIONS'):
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
        
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 20)
            print("✅ Chrome 드라이버 초기화 완료")
        except Exception as e:
            print(f"❌ 드라이버 초기화 실패: {e}")
            raise
    
    def login_kakao(self):
        """카카오톡 웹 로그인"""
        try:
            print("🔄 카카오톡 웹 접속 중...")
            self.driver.get("https://web.kakao.com")
            
            # QR 코드 로그인 대기
            print("📱 휴대폰 카카오톡에서 QR 코드를 스캔해주세요...")
            
            # 로그인 완료 대기 (메인 화면이 로드될 때까지)
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "list_chat"))
            )
            print("✅ 카카오톡 웹 로그인 완료")
            time.sleep(3)
            return True
            
        except TimeoutException:
            print("❌ 로그인 시간 초과")
            return False
        except Exception as e:
            print(f"❌ 로그인 오류: {e}")
            return False
    
    def find_openchat(self, chat_id):
        """오픈채팅방 찾기"""
        try:
            print(f"🔍 오픈채팅방 '{chat_id}' 검색 중...")
            
            # 검색 버튼 클릭
            search_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-tid='search-button']"))
            )
            search_btn.click()
            time.sleep(1)
            
            # 검색창에 채팅방 ID 입력
            search_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='검색']"))
            )
            search_input.clear()
            search_input.send_keys(chat_id)
            time.sleep(2)
            
            # 검색 결과에서 오픈채팅방 클릭
            chat_item = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f"[title*='{chat_id}']"))
            )
            chat_item.click()
            time.sleep(2)
            
            print(f"✅ 오픈채팅방 '{chat_id}' 입장 완료")
            return True
            
        except TimeoutException:
            print(f"❌ 오픈채팅방 '{chat_id}' 찾기 실패")
            return False
        except Exception as e:
            print(f"❌ 채팅방 검색 오류: {e}")
            return False
    
    def send_message(self, message):
        """메시지 전송"""
        try:
            print("📝 메시지 전송 중...")
            
            # 메시지 입력창 찾기
            message_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[contenteditable='true']"))
            )
            
            # 메시지 입력
            message_input.click()
            time.sleep(0.5)
            message_input.clear()
            
            # 줄바꿈이 있는 메시지 처리
            lines = message.split('\n')
            for i, line in enumerate(lines):
                message_input.send_keys(line)
                if i < len(lines) - 1:
                    message_input.send_keys(Keys.SHIFT + Keys.ENTER)
            
            time.sleep(1)
            
            # 전송 버튼 클릭 또는 Enter
            try:
                send_btn = self.driver.find_element(By.CSS_SELECTOR, "[data-tid='send-button']")
                send_btn.click()
            except:
                message_input.send_keys(Keys.ENTER)
            
            time.sleep(2)
            print("✅ 메시지 전송 완료")
            return True
            
        except Exception as e:
            print(f"❌ 메시지 전송 실패: {e}")
            return False
    
    def close(self):
        """드라이버 종료"""
        if self.driver:
            self.driver.quit()
            print("🔄 브라우저 종료")

def generate_grider_report():
    """G라이더 리포트 생성"""
    now = datetime.now()
    
    report = f"""📊 <b>G라이더 미션 현황 리포트</b>
📅 {now.strftime('%Y-%m-%d %H:%M')} 자동 업데이트

🌅 **아침점심피크**: 30/21 ✅ (달성)
🌇 **오후논피크**: 26/20 ✅ (달성)  
🌃 **저녁피크**: 71/30 ✅ (달성)
🌙 **심야논피크**: 5/29 ❌ (24건 부족)

──────────────────────
🌍 **경기도 안산시 날씨** (기상청)

🕐 **현재 날씨**
☀️  21°C 맑음
💧 습도: 90% | ☔ 강수확률: 0%

⏰ **시간별 예보**
22시: ☀️  21°C 
23시: ☀️  20°C 
00시: ☀️  20°C 
01시: ☀️  20°C 

──────────────────────
총점: 85점 (물량:55, 수락률:30)
수락률: 97.2% | 완료: 1777 | 거절: 23

──────────────────────
🏆 **TOP 3 라이더**
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
🏃 **그 외 라이더**
4. 최전일 (15.4%)
   └ 총 17건 (아침:0/오후:3/저녁:14/심야:0)
   └ 수락률: 100.0% (거절:0, 취소:0)

5. 이용구 (15.4%)
   └ 총 13건 (아침:0/오후:11/저녁:2/심야:0)
   └ 수락률: 100.0% (거절:0, 취소:0)

6. 오호근 (11.7%)
   └ 총 14건 (아침:0/오후:0/저녁:12/심야:2)
   └ 수락률: 100.0% (거절:0, 취소:0)

7. 장광영 (10.7%)
   └ 총 9건 (아침:9/오후:0/저녁:0/심야:0)
   └ 수락률: 100.0% (거절:0, 취소:0)

8. 나성구 (10.2%)
   └ 총 10건 (아침:4/오후:1/저녁:5/심야:0)
   └ 수락률: 100.0% (거절:0, 취소:0)

9. 이관연 (4.2%)
   └ 총 5건 (아침:0/오후:0/저녁:3/심야:2)
   └ 수락률: 71.0% (거절:0, 취소:2)

10. 박종민 (1.7%)
   └ 총 2건 (아침:0/오후:0/저녁:2/심야:0)
   └ 수락률: 100.0% (거절:0, 취소:0)

──────────────────────
⚠️ **미션 부족**: 심야 24건

🤖 자동화 시스템에 의해 전송됨"""
    
    return report

def main():
    """메인 실행 함수"""
    print("🚀 카카오톡 오픈채팅방 직접 전송 시작")
    
    # 오픈채팅방 ID (실제 ID로 변경 필요)
    OPENCHAT_ID = "gt26QiBg"
    
    sender = None
    try:
        # 카카오톡 웹 자동화 시작
        sender = KakaoOpenChatSender()
        
        # 로그인
        if not sender.login_kakao():
            print("❌ 로그인 실패로 인한 종료")
            return False
        
        # 오픈채팅방 찾기
        if not sender.find_openchat(OPENCHAT_ID):
            print("❌ 오픈채팅방 접속 실패로 인한 종료")
            return False
        
        # 리포트 생성
        message = generate_grider_report()
        
        # 메시지 전송
        if sender.send_message(message):
            print("🎉 오픈채팅방 메시지 전송 성공!")
            return True
        else:
            print("❌ 메시지 전송 실패")
            return False
        
    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}")
        return False
    
    finally:
        if sender:
            sender.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 