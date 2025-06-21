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
import subprocess
import webbrowser

# 기존 미션 모니터링 시스템 임포트
import importlib.util

def load_main_module():
    """메인 모듈을 동적으로 로드"""
    try:
        # 먼저 main_ 모듈 시도
        from main_ import job, parse_data, crawl_jangboo, make_message, MessageSender
        return job, parse_data, crawl_jangboo, make_message, MessageSender
    except ImportError:
        try:
            # main_(2) 파일에서 동적 로드
            spec = importlib.util.spec_from_file_location("main_module", "main_(2).py")
            main_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(main_module)
            
            return (main_module.job, main_module.parse_data, main_module.crawl_jangboo, 
                   main_module.make_message, main_module.MessageSender)
        except Exception as e:
            logger.error(f"메인 모듈 로드 실패: {e}")
            return None, None, None, None, None

# 모듈 로드
job, parse_data, crawl_jangboo, make_message, MessageSender = load_main_module()

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kakao_scheduler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class KakaoOpenChatSender:
    """카카오톡 오픈채팅방 자동 메시지 전송기"""
    
    def __init__(self):
        # 카카오 API 설정
        self.api_base_url = os.getenv('KAKAO_API_BASE_URL', 'https://kapi.kakao.com')
        self.access_token = os.getenv('KAKAO_ACCESS_TOKEN', '')  # 액세스 토큰 사용
        self.admin_key = os.getenv('KAKAO_ADMIN_KEY', '')  # 백업용
        self.chat_id = os.getenv('KAKAO_OPENCHAT_ID', '')  # 오픈채팅방 ID
        self.bot_user_id = os.getenv('KAKAO_BOT_USER_ID', '')  # 봇 사용자 ID
        
        # 메시지 전송 방식 설정
        self.send_method = os.getenv('KAKAO_SEND_METHOD', 'self')  # self, clipboard, telegram
        
        # 액세스 토큰 확인
        if not self.access_token:
            logger.error("❌ KAKAO_ACCESS_TOKEN이 설정되지 않았습니다.")
            logger.error("🔧 해결 방법: python3 kakao_token_generator.py 실행")
        else:
            logger.info(f"✅ 액세스 토큰 로드 완료: {self.access_token[:15]}...")
        
        # 메시지 전송 통계
        self.message_count = 0
        self.success_count = 0
        self.error_count = 0
        self.last_sent_time = None
        
        # 중복 메시지 방지를 위한 캐시
        self.last_message_hash = None
        
        logger.info("🤖 카카오톡 오픈채팅 자동 전송기 초기화 완료")
        logger.info(f"📤 전송 방식: {self.send_method}")
    
    def send_to_openchat(self, message: str, message_type: str = "mission_status") -> bool:
        """
        오픈채팅방에 메시지 전송 (다양한 방법 지원)
        
        Args:
            message: 전송할 메시지 내용
            message_type: 메시지 타입 (mission_status, alert, notification)
        
        Returns:
            bool: 전송 성공 여부
        """
        try:
            # 메시지 해시 생성 (중복 방지)
            import hashlib
            message_hash = hashlib.md5(message.encode()).hexdigest()
            
            # 중복 메시지 체크 (최근 10분 이내)
            if (self.last_message_hash == message_hash and 
                self.last_sent_time and 
                datetime.now() - self.last_sent_time < timedelta(minutes=10)):
                logger.info("🔄 중복 메시지 전송 방지")
                return True
            
            # 메시지 포맷팅
            formatted_message = self._format_message(message, message_type)
            
            # 전송 방식에 따라 분기
            success = False
            
            if self.send_method == 'self':
                success = self._send_to_self(formatted_message)
            elif self.send_method == 'clipboard':
                success = self._send_to_clipboard(formatted_message)
            elif self.send_method == 'telegram':
                success = self._send_to_telegram(formatted_message)
            elif self.send_method == 'webhook':
                success = self._send_to_webhook(formatted_message)
            else:
                # 기본값: 나에게 보내기 + 클립보드 복사
                success = self._send_to_self(formatted_message)
                self._send_to_clipboard(formatted_message)
            
            if success:
                self.message_count += 1
                self.success_count += 1
                self.last_sent_time = datetime.now()
                self.last_message_hash = message_hash
                logger.info(f"✅ 메시지 처리 성공 ({self.success_count}/{self.message_count})")
            else:
                self.error_count += 1
                logger.error("❌ 메시지 처리 실패")
            
            return success
                
        except Exception as e:
            self.error_count += 1
            logger.error(f"❌ 메시지 전송 중 오류 발생: {str(e)}")
            return False
    
    def _send_to_self(self, message: str) -> bool:
        """나에게 메시지 보내기 (확인/백업용)"""
        try:
            if not self.access_token:
                logger.error("❌ 액세스 토큰이 없습니다.")
                return False
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            template_object = {
                "object_type": "text",
                "text": message,
                "link": {
                    "web_url": "https://jangboo.grider.ai/",
                    "mobile_web_url": "https://jangboo.grider.ai/"
                }
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
                logger.info("✅ 나에게 메시지 전송 성공 (백업)")
                return True
            else:
                logger.error(f"❌ 나에게 메시지 전송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 나에게 메시지 전송 오류: {str(e)}")
            return False
    
    def _send_to_clipboard(self, message: str) -> bool:
        """클립보드에 메시지 복사 (수동 붙여넣기용)"""
        try:
            # macOS
            if os.system('which pbcopy > /dev/null 2>&1') == 0:
                process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
                process.communicate(message.encode('utf-8'))
                logger.info("✅ 메시지가 클립보드에 복사되었습니다 (macOS)")
                logger.info("📋 오픈채팅방에서 Cmd+V로 붙여넣기하세요!")
                return True
            
            # Windows
            elif os.system('where clip > nul 2>&1') == 0:
                process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, shell=True)
                process.communicate(message.encode('utf-8'))
                logger.info("✅ 메시지가 클립보드에 복사되었습니다 (Windows)")
                logger.info("📋 오픈채팅방에서 Ctrl+V로 붙여넣기하세요!")
                return True
            
            # Linux
            elif os.system('which xclip > /dev/null 2>&1') == 0:
                process = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
                process.communicate(message.encode('utf-8'))
                logger.info("✅ 메시지가 클립보드에 복사되었습니다 (Linux)")
                logger.info("📋 오픈채팅방에서 Ctrl+V로 붙여넣기하세요!")
                return True
            
            else:
                logger.warning("⚠️ 클립보드 복사를 지원하지 않는 시스템입니다")
                return False
                
        except Exception as e:
            logger.error(f"❌ 클립보드 복사 오류: {str(e)}")
            return False
    
    def _send_to_telegram(self, message: str) -> bool:
        """텔레그램으로 메시지 전송 (대체 수단)"""
        try:
            telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
            telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
            
            if not telegram_token or not telegram_chat_id:
                logger.warning("⚠️ 텔레그램 설정이 없습니다")
                return False
            
            url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
            data = {
                'chat_id': telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=30)
            
            if response.status_code == 200:
                logger.info("✅ 텔레그램 메시지 전송 성공")
                return True
            else:
                logger.error(f"❌ 텔레그램 전송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 텔레그램 전송 오류: {str(e)}")
            return False
    
    def _send_to_webhook(self, message: str) -> bool:
        """웹훅으로 메시지 전송 (Slack, Discord 등)"""
        try:
            webhook_url = os.getenv('DISCORD_WEBHOOK_URL', '') or os.getenv('SLACK_WEBHOOK_URL', '')
            
            if not webhook_url:
                logger.warning("⚠️ 웹훅 URL이 설정되지 않았습니다")
                return False
            
            # Discord 웹훅 형식
            if 'discord.com' in webhook_url:
                data = {
                    'content': message,
                    'username': 'G라이더 미션봇'
                }
            # Slack 웹훅 형식
            else:
                data = {
                    'text': message,
                    'username': 'G라이더 미션봇'
                }
            
            response = requests.post(webhook_url, json=data, timeout=30)
            
            if response.status_code in [200, 204]:
                logger.info("✅ 웹훅 메시지 전송 성공")
                return True
            else:
                logger.error(f"❌ 웹훅 전송 실패: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 웹훅 전송 오류: {str(e)}")
            return False
    
    def open_openchat_url(self):
        """오픈채팅방 URL 자동으로 열기"""
        try:
            if self.chat_id:
                openchat_url = f"https://open.kakao.com/o/{self.chat_id}"
                webbrowser.open(openchat_url)
                logger.info(f"🌐 오픈채팅방 자동 열기: {openchat_url}")
                return True
            else:
                logger.warning("⚠️ 오픈채팅방 ID가 설정되지 않았습니다")
                return False
        except Exception as e:
            logger.error(f"❌ 오픈채팅방 열기 실패: {str(e)}")
            return False
    
    def _format_message(self, message: str, message_type: str) -> str:
        """카카오톡에 최적화된 메시지 포맷팅"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # 메시지 타입별 이모지 및 제목 설정
        type_config = {
            "mission_status": {"emoji": "📊", "title": "미션 현황 리포트"},
            "alert": {"emoji": "⚠️", "title": "긴급 알림"},
            "notification": {"emoji": "📢", "title": "공지사항"},
            "summary": {"emoji": "📈", "title": "일일 요약"}
        }
        
        config = type_config.get(message_type, type_config["mission_status"])
        
        # 메시지 타입에 따라 다른 포맷 적용
        if message_type == "mission_status":
            # 미션 현황은 기존 메시지를 그대로 사용 (이미 make_message에서 포맷됨)
            formatted = f"""
{config['emoji']} {config['title']}
📅 {timestamp}

{message}

🔄 자동 업데이트 | 🤖 G라이더 미션봇
            """.strip()
        else:
            # 다른 메시지 타입은 간단한 포맷 사용
            formatted = f"""
{config['emoji']} {config['title']}
📅 {timestamp}

{message}

━━━━━━━━━━━━━━━━━
🔄 자동 업데이트 | 🤖 G라이더 미션봇
            """.strip()
        
        return formatted
    
    def get_mission_status_message(self) -> Optional[str]:
        """현재 미션 상황 메시지 생성"""
        try:
            logger.info("🔍 미션 데이터 수집 중...")
            
            # 미션 데이터 크롤링 및 파싱
            html = crawl_jangboo()
            if not html:
                return "❌ 미션 데이터를 가져올 수 없습니다."
            
            mission_data = parse_data(html)
            if not mission_data:
                return "❌ 미션 데이터 파싱에 실패했습니다."
            
            # 메시지 생성
            message = make_message(mission_data)
            return message
            
        except Exception as e:
            logger.error(f"미션 상황 메시지 생성 실패: {str(e)}")
            return f"❌ 오류 발생: {str(e)}"
    
    def send_scheduled_message(self):
        """정기 메시지 전송"""
        try:
            logger.info("📨 정기 미션 현황 메시지 전송 시작")
            
            # 미션 현황 메시지 생성
            message = self.get_mission_status_message()
            if not message:
                logger.warning("메시지 생성 실패")
                return
            
            # 오픈채팅방에 전송
            success = self.send_to_openchat(message, "mission_status")
            
            if success:
                logger.info("✅ 정기 메시지 전송 완료")
            else:
                logger.error("❌ 정기 메시지 전송 실패")
                
        except Exception as e:
            logger.error(f"정기 메시지 전송 중 오류: {str(e)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """전송 통계 반환"""
        return {
            "total_messages": self.message_count,
            "successful_messages": self.success_count,
            "failed_messages": self.error_count,
            "success_rate": f"{(self.success_count/max(self.message_count, 1)*100):.1f}%",
            "last_sent": self.last_sent_time.isoformat() if self.last_sent_time else None
        }

class ScheduleManager:
    """스케줄 관리자"""
    
    def __init__(self):
        self.sender = KakaoOpenChatSender()
        self.is_running = False
        self.schedule_thread = None
        
    def setup_schedules(self):
        """메시지 전송 스케줄 설정"""
        
        # 주요 시간대 알림 (일 4회)
        schedule.every().day.at("08:00").do(self._safe_send_message).tag('main')
        schedule.every().day.at("12:00").do(self._safe_send_message).tag('main')
        schedule.every().day.at("18:00").do(self._safe_send_message).tag('main')
        schedule.every().day.at("22:00").do(self._safe_send_message).tag('main')
        
        # 피크 시간대 추가 알림
        schedule.every().day.at("10:30").do(self._safe_send_message).tag('peak')
        schedule.every().day.at("14:30").do(self._safe_send_message).tag('peak')
        schedule.every().day.at("20:30").do(self._safe_send_message).tag('peak')
        
        # 30분마다 업무시간 알림 (선택적)
        # for hour in range(9, 22):
        #     schedule.every().day.at(f"{hour:02d}:30").do(self._safe_send_message).tag('frequent')
        
        logger.info("📅 메시지 전송 스케줄 설정 완료")
        logger.info("주요 알림: 08:00, 12:00, 18:00, 22:00")
        logger.info("피크 알림: 10:30, 14:30, 20:30")
    
    def _safe_send_message(self):
        """안전한 메시지 전송 (예외 처리 포함)"""
        try:
            self.sender.send_scheduled_message()
        except Exception as e:
            logger.error(f"스케줄 메시지 전송 중 오류: {str(e)}")
    
    def start(self):
        """스케줄러 시작"""
        if self.is_running:
            logger.warning("스케줄러가 이미 실행 중입니다.")
            return
        
        self.setup_schedules()
        self.is_running = True
        
        def run_scheduler():
            logger.info("🚀 카카오톡 자동 메시지 스케줄러 시작!")
            while self.is_running:
                try:
                    schedule.run_pending()
                    time.sleep(30)  # 30초마다 스케줄 체크
                except Exception as e:
                    logger.error(f"스케줄러 실행 중 오류: {str(e)}")
                    time.sleep(60)  # 오류 시 1분 대기
        
        self.schedule_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.schedule_thread.start()
        
        logger.info("✅ 스케줄러 시작 완료")
    
    def stop(self):
        """스케줄러 중지"""
        self.is_running = False
        schedule.clear()
        
        if self.schedule_thread and self.schedule_thread.is_alive():
            self.schedule_thread.join(timeout=5)
        
        logger.info("⏹️ 스케줄러 중지 완료")
    
    def send_test_message(self):
        """테스트 메시지 전송"""
        logger.info("🧪 테스트 메시지 전송 중...")
        test_message = f"""
🧪 테스트 메시지

📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

카카오톡 오픈채팅 자동 전송 시스템이 정상적으로 작동하고 있습니다.

통계:
{json.dumps(self.sender.get_statistics(), indent=2, ensure_ascii=False)}
        """.strip()
        
        return self.sender.send_to_openchat(test_message, "notification")
    
    def get_status(self) -> Dict[str, Any]:
        """현재 상태 반환"""
        return {
            "is_running": self.is_running,
            "next_run": str(schedule.next_run()) if schedule.jobs else None,
            "total_jobs": len(schedule.jobs),
            "sender_stats": self.sender.get_statistics()
        }

def main():
    """메인 실행 함수"""
    print("🤖 카카오톡 오픈채팅 자동 메시지 전송 시스템")
    print("=" * 50)
    
    manager = ScheduleManager()
    
    try:
        while True:
            print("\n📋 메뉴:")
            print("1. 스케줄러 시작")
            print("2. 스케줄러 중지")
            print("3. 테스트 메시지 전송")
            print("4. 현재 상태 확인")
            print("5. 즉시 미션 현황 전송")
            print("6. 통계 확인")
            print("0. 종료")
            
            choice = input("\n선택: ").strip()
            
            if choice == "1":
                manager.start()
            elif choice == "2":
                manager.stop()
            elif choice == "3":
                success = manager.send_test_message()
                print(f"테스트 메시지 전송: {'성공' if success else '실패'}")
            elif choice == "4":
                status = manager.get_status()
                print(f"상태: {json.dumps(status, indent=2, ensure_ascii=False)}")
            elif choice == "5":
                manager.sender.send_scheduled_message()
            elif choice == "6":
                stats = manager.sender.get_statistics()
                print(f"통계: {json.dumps(stats, indent=2, ensure_ascii=False)}")
            elif choice == "0":
                print("👋 시스템을 종료합니다.")
                manager.stop()
                break
            else:
                print("❌ 잘못된 선택입니다.")
    
    except KeyboardInterrupt:
        print("\n\n⏹️ 사용자에 의해 중단되었습니다.")
        manager.stop()
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        manager.stop()

if __name__ == "__main__":
    main() 