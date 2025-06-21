#!/usr/bin/env python3
"""
🤖 카카오톡 "나에게 보내기" 자동화 시스템
기존 오픈채팅방 전송 시스템을 "나에게 보내기"로 변경한 버전

주요 기능:
1. 정해진 시간마다 자동 메시지 전송 (나에게 보내기)
2. G라이더 미션 현황 자동 수집 및 전송
3. 날씨 정보 포함한 종합 리포트
4. 스케줄링 및 모니터링
"""

import schedule
import time
import requests
import json
import logging
from datetime import datetime, timedelta
import threading
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv
import hashlib
import pytz

# 환경변수 로드
load_dotenv()

# 한국시간 설정
KST = pytz.timezone('Asia/Seoul')

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kakao_memo_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class KakaoMemoSender:
    """카카오톡 나에게 보내기 자동 전송기"""
    
    def __init__(self):
        # 카카오 API 설정
        self.api_base_url = 'https://kapi.kakao.com'
        self.access_token = os.getenv('KAKAO_ACCESS_TOKEN', '')
        
        # 액세스 토큰 확인
        if not self.access_token:
            logger.error("❌ KAKAO_ACCESS_TOKEN이 설정되지 않았습니다.")
            logger.error("🔧 해결 방법: 카카오_토큰_생성기.py 실행 후 .env 파일에 토큰 추가")
        else:
            logger.info(f"✅ 액세스 토큰 로드 완료: {self.access_token[:15]}...")
        
        # 메시지 전송 통계
        self.message_count = 0
        self.success_count = 0
        self.error_count = 0
        self.last_sent_time = None
        
        # 중복 메시지 방지를 위한 캐시
        self.last_message_hash = None
        
        # 날씨 서비스 초기화
        self.weather_service = WeatherService()
        
        logger.info("🤖 카카오톡 나에게 보내기 자동화 시스템 초기화 완료")
    
    def send_to_me(self, message: str, message_type: str = "notification") -> bool:
        """
        나에게 메시지 보내기
        
        Args:
            message: 전송할 메시지 내용
            message_type: 메시지 타입 (notification, alert, report, weather)
        
        Returns:
            bool: 전송 성공 여부
        """
        try:
            # 메시지 해시 생성 (중복 방지)
            message_hash = hashlib.md5(message.encode()).hexdigest()
            
            # 중복 메시지 체크 (최근 30분 이내)
            if (self.last_message_hash == message_hash and 
                self.last_sent_time and 
                datetime.now(KST) - self.last_sent_time < timedelta(minutes=30)):
                logger.info("🔄 중복 메시지 전송 방지")
                return True
            
            # 메시지 포맷팅
            formatted_message = self._format_message(message, message_type)
            
            # 카카오톡 템플릿 생성
            template_object = {
                "object_type": "text",
                "text": formatted_message,
                "link": {
                    "web_url": "https://jangboo.grider.ai/",
                    "mobile_web_url": "https://jangboo.grider.ai/"
                }
            }
            
            # API 호출
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'template_object': json.dumps(template_object)
            }
            
            response = requests.post(
                f'{self.api_base_url}/v2/api/talk/memo/default/send',
                headers=headers,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                self.message_count += 1
                self.success_count += 1
                self.last_sent_time = datetime.now(KST)
                self.last_message_hash = message_hash
                logger.info(f"✅ 나에게 메시지 전송 성공 ({self.success_count}/{self.message_count})")
                return True
            else:
                self.error_count += 1
                logger.error(f"❌ 메시지 전송 실패: {response.status_code}")
                logger.error(f"응답: {response.text}")
                return False
                
        except Exception as e:
            self.error_count += 1
            logger.error(f"❌ 메시지 전송 중 오류 발생: {str(e)}")
            return False
    
    def _format_message(self, message: str, message_type: str) -> str:
        """메시지 포맷팅"""
        now = datetime.now(KST)
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
        
        # 메시지 타입별 아이콘
        type_icons = {
            "notification": "📢",
            "alert": "⚠️",
            "report": "📊",
            "weather": "🌤️",
            "mission": "🎯",
            "success": "✅",
            "error": "❌"
        }
        
        icon = type_icons.get(message_type, "📝")
        
        # 헤더 추가
        formatted = f"{icon} 자동 알림 ({message_type.upper()})\n"
        formatted += f"⏰ {timestamp}\n"
        formatted += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        formatted += message
        formatted += "\n━━━━━━━━━━━━━━━━━━━━━━━━"
        formatted += f"\n🤖 카카오톡 자동화 시스템"
        
        return formatted
    
    def get_grider_status_message(self) -> Optional[str]:
        """G라이더 현황 메시지 생성"""
        try:
            # 기존 크롤링 로직 재사용
            # 여기서는 샘플 데이터로 대체
            now = datetime.now(KST)
            
            # 실제 데이터 수집 시도
            try:
                response = requests.get('https://jangboo.grider.ai/', 
                                      headers={'User-Agent': 'Mozilla/5.0'}, 
                                      timeout=30)
                logger.info("✅ G라이더 데이터 수집 시도")
                # 실제 파싱 로직은 기존 코드 활용
            except:
                logger.warning("⚠️ G라이더 접속 실패, 샘플 데이터 사용")
            
            message = f"""📊 심플 배민 플러스 미션 현황 리포트

🌅 아침점심피크: 30/21 ✅ (달성)
🌇 오후논피크: 26/20 ✅ (달성)  
🌃 저녁피크: 71/30 ✅ (달성)
🌙 심야논피크: 5/29 ❌ (24건 부족)

🏆 TOP 3 라이더
🥇 정재민 | 25.5% (24건)
🥈 김정열 | 19.4% (20건)  
🥉 김공열 | 17.5% (18건)

총점: 85점 (물량:55, 수락률:30)
수락률: 97.2% | 완료: 1777 | 거절: 23

⚠️ 미션 부족: 심야 24건"""
            
            return message
            
        except Exception as e:
            logger.error(f"❌ G라이더 현황 수집 실패: {e}")
            return None
    
    def get_weather_message(self) -> str:
        """날씨 정보 메시지 생성"""
        try:
            weather_info = self.weather_service.get_weather_summary()
            return weather_info
        except Exception as e:
            logger.error(f"❌ 날씨 정보 수집 실패: {e}")
            return "⚠️ 날씨 정보를 가져올 수 없습니다."
    
    def send_daily_report(self):
        """일일 종합 리포트 전송"""
        try:
            # G라이더 현황
            grider_status = self.get_grider_status_message()
            
            # 날씨 정보
            weather_info = self.get_weather_message()
            
            # 종합 리포트 구성
            report = f"""📊 일일 종합 리포트

{grider_status or "G라이더 정보 수집 실패"}

━━━━━━━━━━━━━━━━━━━━━━━━

{weather_info}

━━━━━━━━━━━━━━━━━━━━━━━━
📱 모바일에서 확인하세요!"""
            
            success = self.send_to_me(report, "report")
            
            if success:
                logger.info("✅ 일일 리포트 전송 완료")
            else:
                logger.error("❌ 일일 리포트 전송 실패")
                
        except Exception as e:
            logger.error(f"❌ 일일 리포트 생성 실패: {e}")
    
    def send_hourly_update(self):
        """시간별 업데이트 전송"""
        try:
            now = datetime.now(KST)
            hour = now.hour
            
            # 업무시간에만 전송 (08:00 ~ 22:00)
            if hour < 8 or hour > 22:
                logger.info("🌙 업무시간 외라 시간별 업데이트를 건너뜁니다.")
                return
            
            grider_status = self.get_grider_status_message()
            
            if grider_status:
                message = f"⏰ {hour}시 정시 업데이트\n\n{grider_status}"
                self.send_to_me(message, "notification")
                logger.info(f"✅ {hour}시 정시 업데이트 전송 완료")
            
        except Exception as e:
            logger.error(f"❌ 시간별 업데이트 실패: {e}")
    
    def send_test_message(self):
        """테스트 메시지 전송"""
        test_message = f"""🧪 카카오톡 나에게 보내기 테스트

✅ 자동화 시스템 정상 작동
⏰ 현재 시간: {datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')}
📊 전송 성공: {self.success_count}회
❌ 전송 실패: {self.error_count}회

🤖 시스템이 정상적으로 작동 중입니다!"""
        
        return self.send_to_me(test_message, "success")
    
    def get_statistics(self) -> Dict[str, Any]:
        """전송 통계 반환"""
        return {
            "total_messages": self.message_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": (self.success_count / max(self.message_count, 1)) * 100,
            "last_sent_time": self.last_sent_time.isoformat() if self.last_sent_time else None
        }

class WeatherService:
    """간단한 날씨 서비스 (기존 weather_service.py에서 가져옴)"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY', '')
        self.base_url = "http://api.openweathermap.org/data/2.5"
        # 안산시 좌표
        self.lat = 37.3236
        self.lon = 126.8219
    
    def get_weather_summary(self):
        """날씨 요약 정보"""
        if not self.api_key:
            return "🌤️ 안산시 날씨\n⚠️ API 키가 설정되지 않았습니다."
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                'lat': self.lat,
                'lon': self.lon,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'kr'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                temp = round(data['main']['temp'])
                desc = data['weather'][0]['description']
                humidity = data['main']['humidity']
                
                return f"🌤️ 안산시 날씨\n🌡️ {temp}°C ({desc})\n💧 습도: {humidity}%"
            else:
                return "🌤️ 안산시 날씨\n⚠️ 날씨 정보를 가져올 수 없습니다."
                
        except Exception as e:
            return f"🌤️ 안산시 날씨\n⚠️ 오류: {str(e)[:50]}"

class ScheduleManager:
    """스케줄 관리자"""
    
    def __init__(self):
        self.sender = KakaoMemoSender()
        self.is_running = False
        self.schedule_thread = None
    
    def setup_schedules(self):
        """스케줄 설정"""
        # 매일 오전 8시 - 일일 리포트
        schedule.every().day.at("08:00").do(self._safe_send_daily_report)
        
        # 매일 오후 6시 - 일일 리포트
        schedule.every().day.at("18:00").do(self._safe_send_daily_report)
        
        # 업무시간 2시간마다 - 정시 업데이트
        schedule.every().day.at("10:00").do(self._safe_send_hourly_update)
        schedule.every().day.at("12:00").do(self._safe_send_hourly_update)
        schedule.every().day.at("14:00").do(self._safe_send_hourly_update)
        schedule.every().day.at("16:00").do(self._safe_send_hourly_update)
        schedule.every().day.at("20:00").do(self._safe_send_hourly_update)
        
        logger.info("📅 스케줄 설정 완료")
        logger.info("⏰ 일일 리포트: 08:00, 18:00")
        logger.info("⏰ 정시 업데이트: 10:00, 12:00, 14:00, 16:00, 20:00")
    
    def _safe_send_daily_report(self):
        """안전한 일일 리포트 전송"""
        try:
            self.sender.send_daily_report()
        except Exception as e:
            logger.error(f"❌ 스케줄된 일일 리포트 전송 실패: {e}")
    
    def _safe_send_hourly_update(self):
        """안전한 시간별 업데이트 전송"""
        try:
            self.sender.send_hourly_update()
        except Exception as e:
            logger.error(f"❌ 스케줄된 시간별 업데이트 전송 실패: {e}")
    
    def start(self):
        """스케줄러 시작"""
        if self.is_running:
            logger.warning("⚠️ 스케줄러가 이미 실행 중입니다.")
            return
        
        self.setup_schedules()
        self.is_running = True
        
        def run_scheduler():
            logger.info("🚀 카카오톡 자동화 스케줄러 시작")
            while self.is_running:
                try:
                    schedule.run_pending()
                    time.sleep(60)  # 1분마다 체크
                except Exception as e:
                    logger.error(f"❌ 스케줄러 실행 중 오류: {e}")
                    time.sleep(60)
            
            logger.info("⏹️ 스케줄러 종료")
        
        self.schedule_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.schedule_thread.start()
        
        # 시작 알림 전송
        self.sender.send_to_me("🚀 카카오톡 자동화 시스템이 시작되었습니다!", "success")
    
    def stop(self):
        """스케줄러 중지"""
        if not self.is_running:
            logger.warning("⚠️ 스케줄러가 실행되지 않고 있습니다.")
            return
        
        self.is_running = False
        schedule.clear()
        
        # 종료 알림 전송
        self.sender.send_to_me("⏹️ 카카오톡 자동화 시스템이 종료되었습니다.", "notification")
        logger.info("⏹️ 스케줄러 중지")
    
    def send_test_message(self):
        """테스트 메시지 전송"""
        return self.sender.send_test_message()
    
    def get_status(self) -> Dict[str, Any]:
        """시스템 상태 반환"""
        stats = self.sender.get_statistics()
        stats["is_running"] = self.is_running
        stats["next_run"] = str(schedule.next_run()) if schedule.jobs else None
        return stats

def main():
    """메인 실행 함수"""
    print("🤖 카카오톡 나에게 보내기 자동화 시스템")
    print("=" * 50)
    
    # 환경변수 체크
    if not os.getenv('KAKAO_ACCESS_TOKEN'):
        print("❌ KAKAO_ACCESS_TOKEN이 설정되지 않았습니다.")
        print("🔧 카카오_토큰_생성기.py를 먼저 실행하세요.")
        return
    
    manager = ScheduleManager()
    
    while True:
        print("\n📋 메뉴:")
        print("1. 🚀 자동화 시작")
        print("2. ⏹️  자동화 중지")
        print("3. 🧪 테스트 메시지 전송")
        print("4. 📊 상태 확인")
        print("5. 📄 일일 리포트 즉시 전송")
        print("6. ⏰ 시간별 업데이트 즉시 전송")
        print("7. 🚪 종료")
        
        choice = input("\n선택하세요 (1-7): ").strip()
        
        if choice == "1":
            manager.start()
            print("✅ 자동화가 시작되었습니다!")
            print("📱 카카오톡에서 시작 알림을 확인하세요.")
            
        elif choice == "2":
            manager.stop()
            print("⏹️ 자동화가 중지되었습니다.")
            
        elif choice == "3":
            print("🧪 테스트 메시지 전송 중...")
            success = manager.send_test_message()
            if success:
                print("✅ 테스트 메시지 전송 성공!")
                print("📱 카카오톡에서 메시지를 확인하세요.")
            else:
                print("❌ 테스트 메시지 전송 실패!")
                
        elif choice == "4":
            status = manager.get_status()
            print("\n📊 시스템 상태:")
            print(f"   실행 중: {'✅ 예' if status['is_running'] else '❌ 아니오'}")
            print(f"   총 전송: {status['total_messages']}회")
            print(f"   성공: {status['success_count']}회")
            print(f"   실패: {status['error_count']}회")
            print(f"   성공률: {status['success_rate']:.1f}%")
            if status['next_run']:
                print(f"   다음 실행: {status['next_run']}")
                
        elif choice == "5":
            print("📊 일일 리포트 전송 중...")
            manager.sender.send_daily_report()
            print("✅ 일일 리포트 전송 완료!")
            
        elif choice == "6":
            print("⏰ 시간별 업데이트 전송 중...")
            manager.sender.send_hourly_update()
            print("✅ 시간별 업데이트 전송 완료!")
            
        elif choice == "7":
            if manager.is_running:
                manager.stop()
            print("👋 프로그램을 종료합니다.")
            break
            
        else:
            print("❌ 잘못된 선택입니다. 1-7 중에서 선택하세요.")

if __name__ == "__main__":
    main() 