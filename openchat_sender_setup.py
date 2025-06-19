#!/usr/bin/env python3
"""
오픈채팅방 메시지 전송 방식 설정 도구
카카오 API 제한으로 인한 대안적 전송 방법들을 제공합니다.
"""

import os
import webbrowser
from dotenv import load_dotenv

load_dotenv()

class OpenChatSenderSetup:
    """오픈채팅방 전송 설정"""
    
    def __init__(self):
        self.chat_id = os.getenv('KAKAO_OPENCHAT_ID', '')
        print("🔧 오픈채팅방 메시지 전송 방식 설정")
        print("="*50)
    
    def show_methods(self):
        """사용 가능한 전송 방법들 안내"""
        print("\n📋 **오픈채팅방 메시지 전송 방법들**")
        print("="*50)
        
        print("\n1️⃣ **클립보드 복사 + 수동 붙여넣기** (권장)")
        print("   ✅ 장점: 확실하고 빠름")
        print("   ⚠️ 단점: 수동 작업 필요")
        print("   📋 동작: 메시지를 클립보드에 복사 → 오픈채팅방에서 붙여넣기")
        
        print("\n2️⃣ **나에게 보내기 + 전달**")
        print("   ✅ 장점: API로 자동 전송")
        print("   ⚠️ 단점: 수동 전달 필요")
        print("   📱 동작: 내 카카오톡에 메시지 전송 → 오픈채팅방으로 전달")
        
        print("\n3️⃣ **텔레그램 연동**")
        print("   ✅ 장점: 완전 자동화")
        print("   ⚠️ 단점: 텔레그램 설정 필요")
        print("   🤖 동작: 텔레그램 봇으로 알림 → 확인 후 수동 복사")
        
        print("\n4️⃣ **Discord/Slack 웹훅**")
        print("   ✅ 장점: 팀 공유 가능")
        print("   ⚠️ 단점: 별도 플랫폼 필요")
        print("   🔗 동작: 웹훅으로 알림 → 확인 후 수동 복사")
        
        print("\n5️⃣ **자동 브라우저 열기**")
        print("   ✅ 장점: 편의성")
        print("   ⚠️ 단점: 여전히 수동")
        print("   🌐 동작: 오픈채팅방 자동 열기 → 클립보드에서 붙여넣기")
    
    def setup_clipboard_method(self):
        """클립보드 방식 설정"""
        print("\n🔧 **클립보드 방식 설정**")
        print("-" * 30)
        
        # .env 파일 업데이트
        self._update_env_file('KAKAO_SEND_METHOD', 'clipboard')
        
        print("✅ 클립보드 방식으로 설정되었습니다!")
        print("\n📋 **사용 방법:**")
        print("1. 자동 전송 시스템 시작")
        print("2. 메시지가 클립보드에 자동 복사됨")
        print("3. 오픈채팅방에서 Cmd+V (또는 Ctrl+V) 붙여넣기")
        print("4. 완료!")
        
        return True
    
    def setup_telegram_method(self):
        """텔레그램 방식 설정"""
        print("\n🤖 **텔레그램 방식 설정**")
        print("-" * 30)
        
        print("📋 **텔레그램 봇 설정 단계:**")
        print("1. @BotFather에게 /newbot 명령어로 봇 생성")
        print("2. 봇 토큰 받기")
        print("3. 봇과 대화 시작")
        print("4. @userinfobot에게 메시지 보내서 Chat ID 확인")
        
        # 사용자 입력
        bot_token = input("\n🔑 텔레그램 봇 토큰을 입력하세요: ").strip()
        chat_id = input("🆔 텔레그램 Chat ID를 입력하세요: ").strip()
        
        if bot_token and chat_id:
            self._update_env_file('TELEGRAM_BOT_TOKEN', bot_token)
            self._update_env_file('TELEGRAM_CHAT_ID', chat_id)
            self._update_env_file('KAKAO_SEND_METHOD', 'telegram')
            
            print("✅ 텔레그램 방식으로 설정되었습니다!")
            print("\n📱 **사용 방법:**")
            print("1. 자동 전송 시스템 시작")
            print("2. 텔레그램으로 메시지 수신")
            print("3. 메시지 복사 후 오픈채팅방에 붙여넣기")
            
            # 테스트 메시지 전송
            test_choice = input("\n🧪 테스트 메시지를 보내시겠습니까? (y/n): ").strip().lower()
            if test_choice in ['y', 'yes', '예']:
                self._test_telegram(bot_token, chat_id)
            
            return True
        else:
            print("❌ 토큰 또는 Chat ID가 입력되지 않았습니다.")
            return False
    
    def setup_webhook_method(self):
        """웹훅 방식 설정"""
        print("\n🔗 **웹훅 방식 설정**")
        print("-" * 30)
        
        print("📋 **지원하는 웹훅:**")
        print("1. Discord 웹훅")
        print("2. Slack 웹훅")
        
        webhook_type = input("\n선택 (1-2): ").strip()
        
        if webhook_type == "1":
            print("\n📋 **Discord 웹훅 생성:**")
            print("1. Discord 서버 → 채널 설정 → 연동")
            print("2. 웹훅 만들기 → 웹훅 URL 복사")
            
            webhook_url = input("\n🔗 Discord 웹훅 URL을 입력하세요: ").strip()
            env_key = 'DISCORD_WEBHOOK_URL'
            
        elif webhook_type == "2":
            print("\n📋 **Slack 웹훅 생성:**")
            print("1. Slack 앱 → Incoming Webhooks")
            print("2. 채널 선택 → 웹훅 URL 생성")
            
            webhook_url = input("\n🔗 Slack 웹훅 URL을 입력하세요: ").strip()
            env_key = 'SLACK_WEBHOOK_URL'
        else:
            print("❌ 잘못된 선택입니다.")
            return False
        
        if webhook_url:
            self._update_env_file(env_key, webhook_url)
            self._update_env_file('KAKAO_SEND_METHOD', 'webhook')
            
            print("✅ 웹훅 방식으로 설정되었습니다!")
            print("\n🔗 **사용 방법:**")
            print("1. 자동 전송 시스템 시작")
            print("2. 웹훅으로 메시지 수신")
            print("3. 메시지 복사 후 오픈채팅방에 붙여넣기")
            
            return True
        else:
            print("❌ 웹훅 URL이 입력되지 않았습니다.")
            return False
    
    def setup_auto_browser_method(self):
        """자동 브라우저 열기 방식 설정"""
        print("\n🌐 **자동 브라우저 열기 방식 설정**")
        print("-" * 30)
        
        if not self.chat_id:
            print("❌ 오픈채팅방 ID가 설정되지 않았습니다.")
            print("🔧 먼저 python3 openchat_id_extractor.py를 실행하세요.")
            return False
        
        self._update_env_file('KAKAO_SEND_METHOD', 'browser')
        
        print("✅ 자동 브라우저 열기 방식으로 설정되었습니다!")
        print("\n🌐 **사용 방법:**")
        print("1. 자동 전송 시스템 시작")
        print("2. 오픈채팅방이 자동으로 브라우저에서 열림")
        print("3. 클립보드에서 메시지 붙여넣기 (Cmd+V 또는 Ctrl+V)")
        
        # 테스트로 오픈채팅방 열기
        test_choice = input("\n🧪 지금 오픈채팅방을 열어보시겠습니까? (y/n): ").strip().lower()
        if test_choice in ['y', 'yes', '예']:
            openchat_url = f"https://open.kakao.com/o/{self.chat_id}"
            webbrowser.open(openchat_url)
            print(f"🌐 오픈채팅방이 열렸습니다: {openchat_url}")
        
        return True
    
    def _test_telegram(self, bot_token: str, chat_id: str):
        """텔레그램 테스트 메시지 전송"""
        try:
            import requests
            from datetime import datetime
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            test_message = f"""
🧪 **G라이더 미션봇 테스트**

📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ 텔레그램 연동이 성공적으로 설정되었습니다!

이제 G라이더 미션 현황이 이 채널로 전송됩니다.
메시지를 복사해서 오픈채팅방에 붙여넣기하세요!

🤖 G라이더 미션봇
            """.strip()
            
            data = {
                'chat_id': chat_id,
                'text': test_message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                print("✅ 텔레그램 테스트 메시지 전송 성공!")
                print("📱 텔레그램에서 메시지를 확인해보세요.")
            else:
                print(f"❌ 텔레그램 테스트 실패: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 텔레그램 테스트 오류: {e}")
    
    def _update_env_file(self, key: str, value: str):
        """환경변수 파일 업데이트"""
        try:
            # .env 파일 읽기
            env_file = '.env'
            lines = []
            
            if os.path.exists(env_file):
                with open(env_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            
            # 기존 키 찾기 및 업데이트
            key_found = False
            for i, line in enumerate(lines):
                if line.strip().startswith(f'{key}='):
                    lines[i] = f'{key}={value}\n'
                    key_found = True
                    break
            
            # 새로운 키 추가
            if not key_found:
                lines.append(f'{key}={value}\n')
            
            # 파일 저장
            with open(env_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print(f"✅ {key} 설정 완료")
            
        except Exception as e:
            print(f"❌ 환경변수 설정 실패: {e}")
    
    def show_current_settings(self):
        """현재 설정 상태 표시"""
        print("\n📊 **현재 설정 상태**")
        print("-" * 30)
        
        send_method = os.getenv('KAKAO_SEND_METHOD', 'self')
        chat_id = os.getenv('KAKAO_OPENCHAT_ID', '')
        telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        discord_webhook = os.getenv('DISCORD_WEBHOOK_URL', '')
        slack_webhook = os.getenv('SLACK_WEBHOOK_URL', '')
        
        print(f"📤 전송 방식: {send_method}")
        print(f"🆔 오픈채팅방 ID: {chat_id[:8]}..." if chat_id else "❌ 오픈채팅방 ID 미설정")
        print(f"🤖 텔레그램: {'✅ 설정됨' if telegram_token else '❌ 미설정'}")
        print(f"🔗 Discord 웹훅: {'✅ 설정됨' if discord_webhook else '❌ 미설정'}")
        print(f"🔗 Slack 웹훅: {'✅ 설정됨' if slack_webhook else '❌ 미설정'}")

def main():
    """메인 함수"""
    setup = OpenChatSenderSetup()
    
    setup.show_methods()
    setup.show_current_settings()
    
    print("\n📋 **전송 방식을 선택하세요:**")
    print("1. 클립보드 복사 + 수동 붙여넣기 (권장)")
    print("2. 나에게 보내기 + 전달")
    print("3. 텔레그램 연동")
    print("4. Discord/Slack 웹훅")
    print("5. 자동 브라우저 열기")
    print("6. 현재 설정 보기")
    
    choice = input("\n선택 (1-6): ").strip()
    
    if choice == "1":
        setup.setup_clipboard_method()
    elif choice == "2":
        # 나에게 보내기는 기본 설정
        setup._update_env_file('KAKAO_SEND_METHOD', 'self')
        print("✅ 나에게 보내기 방식으로 설정되었습니다!")
        print("📱 카카오톡에서 메시지를 받은 후 오픈채팅방으로 전달하세요.")
    elif choice == "3":
        setup.setup_telegram_method()
    elif choice == "4":
        setup.setup_webhook_method()
    elif choice == "5":
        setup.setup_auto_browser_method()
    elif choice == "6":
        setup.show_current_settings()
    else:
        print("❌ 잘못된 선택입니다.")
        return
    
    print("\n🎉 설정 완료!")
    print("📝 이제 다음 명령어로 자동 전송을 시작하세요:")
    print("   python3 kakao_scheduled_sender.py")

if __name__ == "__main__":
    main() 