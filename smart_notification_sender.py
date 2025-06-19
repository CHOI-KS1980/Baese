#!/usr/bin/env python3
"""
스마트 알림 + 클립보드 시스템
가장 실용적인 오픈채팅방 메시지 전송 솔루션
"""

import schedule
import time
import subprocess
import webbrowser
import os
import platform
from datetime import datetime
from kakao_scheduled_sender import KakaoOpenChatSender

class SmartNotificationSender:
    def __init__(self):
        self.sender = KakaoOpenChatSender()
        self.openchat_url = "https://open.kakao.com/o/gt26QiBg"
        
    def send_notification(self, title, message):
        """시스템 알림 표시"""
        system = platform.system()
        
        if system == "Darwin":  # macOS
            script = f'''
            display notification "{message}" with title "{title}" sound name "Glass"
            '''
            subprocess.run(['osascript', '-e', script])
            
        elif system == "Windows":
            # Windows 토스트 알림
            subprocess.run([
                'powershell', '-Command',
                f'[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null; '
                f'$template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02); '
                f'$template.SelectSingleNode("//text[@id=\\"1\\"]").InnerText = "{title}"; '
                f'$template.SelectSingleNode("//text[@id=\\"2\\"]").InnerText = "{message}"; '
                f'$toast = [Windows.UI.Notifications.ToastNotification]::new($template); '
                f'[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("G라이더 미션봇").Show($toast)'
            ])
            
        elif system == "Linux":
            # Linux notify-send
            subprocess.run(['notify-send', title, message])
    
    def copy_to_clipboard(self, text):
        """클립보드에 텍스트 복사"""
        system = platform.system()
        
        if system == "Darwin":  # macOS
            process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            process.communicate(text.encode('utf-8'))
            
        elif system == "Windows":
            process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, shell=True)
            process.communicate(text.encode('utf-8'))
            
        elif system == "Linux":
            process = subprocess.Popen(['xclip', '-selection', 'clipboard'], stdin=subprocess.PIPE)
            process.communicate(text.encode('utf-8'))
    
    def smart_send_message(self):
        """스마트 메시지 전송"""
        try:
            print(f"\n🚀 {datetime.now().strftime('%H:%M')} 스마트 알림 시작!")
            
            # 1. 미션 메시지 생성
            message = self.sender.get_mission_status_message()
            if not message:
                print("❌ 메시지 생성 실패")
                return
            
            # 2. 클립보드에 복사
            self.copy_to_clipboard(message)
            print("📋 메시지가 클립보드에 복사되었습니다!")
            
            # 3. 시스템 알림 표시
            self.send_notification(
                "🤖 G라이더 미션봇",
                "메시지가 준비되었습니다! 오픈채팅방에서 Cmd+V로 붙여넣기하세요."
            )
            
            # 4. 오픈채팅방 자동 열기
            time.sleep(2)  # 알림 표시 대기
            webbrowser.open(self.openchat_url)
            print(f"🌐 오픈채팅방이 열렸습니다: {self.openchat_url}")
            
            # 5. 추가 알림음
            if platform.system() == "Darwin":
                subprocess.run(['afplay', '/System/Library/Sounds/Glass.aiff'])
            
            print("✅ 스마트 알림 완료! 이제 Cmd+V (또는 Ctrl+V)로 붙여넣기하세요!")
            
        except Exception as e:
            print(f"❌ 스마트 알림 실패: {e}")
    
    def setup_schedule(self):
        """스케줄 설정"""
        # 주요 알림 시간
        schedule.every().day.at("08:00").do(self.smart_send_message)
        schedule.every().day.at("12:00").do(self.smart_send_message)
        schedule.every().day.at("18:00").do(self.smart_send_message)
        schedule.every().day.at("22:00").do(self.smart_send_message)
        
        # 피크타임 알림
        schedule.every().day.at("10:30").do(self.smart_send_message)
        schedule.every().day.at("14:30").do(self.smart_send_message)
        schedule.every().day.at("20:30").do(self.smart_send_message)
        
        print("📅 스케줄 설정 완료:")
        print("   - 주요 알림: 08:00, 12:00, 18:00, 22:00")
        print("   - 피크 알림: 10:30, 14:30, 20:30")
    
    def start(self):
        """스마트 알림 시스템 시작"""
        print("🤖 스마트 알림 시스템 시작!")
        print("="*50)
        
        self.setup_schedule()
        
        print("\n⏰ 대기 중... (Ctrl+C로 종료)")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 체크
        except KeyboardInterrupt:
            print("\n⏹️ 스마트 알림 시스템 종료")

def main():
    sender = SmartNotificationSender()
    
    print("🤖 스마트 알림 시스템")
    print("="*30)
    print("1. 스케줄 시작")
    print("2. 즉시 테스트")
    
    choice = input("\n선택 (1-2): ").strip()
    
    if choice == "1":
        sender.start()
    elif choice == "2":
        sender.smart_send_message()
    else:
        print("❌ 잘못된 선택입니다.")

if __name__ == "__main__":
    main() 