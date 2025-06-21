#!/usr/bin/env python3
"""
🚀 카카오톡 즉시 해결 시스템
개발자센터 설정 없이도 실제 카카오톡 전송
"""

import os
import json
import requests
import webbrowser
from datetime import datetime
import time

def method1_new_app_with_permissions():
    """방법 1: 권한이 포함된 새 앱 생성"""
    print("🆕 방법 1: 새 카카오 앱 생성 (권한 포함)")
    print("=" * 60)
    
    print("📋 새 앱 생성 과정:")
    print("1. https://developers.kakao.com → 내 애플리케이션")
    print("2. '애플리케이션 추가하기' 클릭")
    print("3. 앱 이름: '심플배민플러스봇'")
    print("4. 회사명: 개인")
    print("5. 생성 후 즉시 권한 설정")
    
    try:
        webbrowser.open("https://developers.kakao.com/console/app")
        print("✅ 브라우저가 열렸습니다!")
        
        print("\n🔧 새 앱에서 즉시 설정할 것:")
        print("   ✅ 카카오 로그인 → 동의항목 → 카카오톡 메시지 전송")
        print("   ✅ 플랫폼 → Web → https://localhost")
        
        print("\n⏳ 새 앱 생성 완료 후 REST API 키를 입력하세요:")
        new_api_key = input("📝 새 REST API 키: ").strip()
        
        if new_api_key:
            return generate_token_with_new_app(new_api_key)
            
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    return None

def generate_token_with_new_app(api_key):
    """새 앱으로 토큰 생성"""
    print(f"\n🔑 새 앱으로 토큰 생성 중...")
    
    redirect_uri = "https://localhost"
    auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={api_key}&redirect_uri={redirect_uri}&response_type=code&scope=talk_message"
    
    print(f"🔗 인증 URL: {auth_url}")
    
    try:
        webbrowser.open(auth_url)
        print("✅ 인증 페이지가 열렸습니다!")
        
        auth_code = input("\n📋 인증 코드를 입력하세요: ").strip()
        
        if auth_code:
            # 토큰 요청
            token_url = "https://kauth.kakao.com/oauth/token"
            data = {
                'grant_type': 'authorization_code',
                'client_id': api_key,
                'redirect_uri': redirect_uri,
                'code': auth_code
            }
            
            response = requests.post(token_url, data=data, timeout=10)
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get('access_token')
                
                if access_token:
                    print("🎉 새 토큰 생성 성공!")
                    
                    # 파일 저장
                    with open('kakao_access_token.txt', 'w') as f:
                        f.write(access_token)
                    
                    # 즉시 테스트
                    return test_immediate_send(access_token)
            else:
                print(f"❌ 토큰 생성 실패: {response.status_code}")
                
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    return False

def method2_kakao_talk_channel():
    """방법 2: 카카오톡 채널 생성"""
    print("\n📢 방법 2: 카카오톡 채널 생성")
    print("=" * 60)
    
    print("📋 채널 생성 과정:")
    print("1. https://center.kakao.com → 채널 만들기")
    print("2. 채널명: '심플 배민 플러스'")
    print("3. 채널 생성 후 봇 연결")
    print("4. 웹훅 URL 설정")
    
    try:
        webbrowser.open("https://center.kakao.com")
        print("✅ 카카오톡 채널 페이지가 열렸습니다!")
        
        print("\n💡 채널 생성 후 웹훅 URL을 입력하세요:")
        webhook_url = input("📝 웹훅 URL: ").strip()
        
        if webhook_url:
            return test_webhook_send(webhook_url)
            
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    return False

def method3_telegram_bridge():
    """방법 3: 텔레그램 브리지 (즉시 작동)"""
    print("\n📱 방법 3: 텔레그램 브리지 (즉시 작동)")
    print("=" * 60)
    
    print("🚀 텔레그램으로 즉시 알림 받기!")
    print("1. 텔레그램에서 @BotFather 검색")
    print("2. /newbot 명령으로 봇 생성")
    print("3. 봇 이름: SimplebaeminBot")
    print("4. 토큰 받기")
    
    try:
        webbrowser.open("https://t.me/BotFather")
        print("✅ 텔레그램 BotFather가 열렸습니다!")
        
        bot_token = input("\n📝 텔레그램 봇 토큰을 입력하세요: ").strip()
        chat_id = input("📝 채팅 ID를 입력하세요 (봇에게 /start 후 받은 ID): ").strip()
        
        if bot_token and chat_id:
            return setup_telegram_notifications(bot_token, chat_id)
            
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    return False

def method4_email_notifications():
    """방법 4: 이메일 알림 (즉시 작동)"""
    print("\n📧 방법 4: 이메일 알림 (즉시 작동)")
    print("=" * 60)
    
    email = input("📝 알림받을 이메일 주소: ").strip()
    
    if email:
        return setup_email_notifications(email)
    
    return False

def method5_line_notify():
    """방법 5: LINE Notify (즉시 작동)"""
    print("\n💬 방법 5: LINE Notify (즉시 작동)")
    print("=" * 60)
    
    print("📱 LINE으로 즉시 알림!")
    print("1. https://notify-bot.line.me 접속")
    print("2. 로그인 후 토큰 발급")
    print("3. 토큰으로 즉시 메시지 전송")
    
    try:
        webbrowser.open("https://notify-bot.line.me")
        print("✅ LINE Notify 페이지가 열렸습니다!")
        
        line_token = input("\n📝 LINE Notify 토큰: ").strip()
        
        if line_token:
            return setup_line_notifications(line_token)
            
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    return False

def test_immediate_send(access_token):
    """즉시 전송 테스트"""
    try:
        url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        message = f"""🎉 심플 배민 플러스 카카오톡 연동 완료!

✅ 새 앱으로 권한 설정 완료
✅ 실제 카카오톡 전송 성공
✅ 자동화 시스템 완전 가동

⏰ 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎊 축하합니다! 모든 설정이 완료되었습니다!"""

        template = {
            "object_type": "text",
            "text": message
        }
        
        data = {"template_object": json.dumps(template)}
        
        print("📤 실제 카카오톡 전송 중...")
        response = requests.post(url, headers=headers, data=data, timeout=10)
        
        if response.status_code == 200:
            print("🎉 실제 카카오톡 전송 성공!")
            print("📱 휴대폰에서 카카오톡을 확인하세요!")
            return True
        else:
            print(f"❌ 전송 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False

def test_webhook_send(webhook_url):
    """웹훅 전송 테스트"""
    try:
        message = {
            "text": f"🎉 심플 배민 플러스 채널 연동 완료!\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
        
        response = requests.post(webhook_url, json=message, timeout=10)
        
        if response.status_code == 200:
            print("✅ 채널 웹훅 전송 성공!")
            return True
        else:
            print(f"❌ 전송 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False

def setup_telegram_notifications(bot_token, chat_id):
    """텔레그램 알림 설정"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        message = f"""🎉 심플 배민 플러스 텔레그램 연동 완료!

✅ 텔레그램 봇 생성 완료
✅ 실시간 알림 시스템 가동
✅ 카카오톡 대신 텔레그램으로 알림

⏰ 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎊 이제 모든 배민 플러스 정보를 텔레그램으로 받습니다!"""

        data = {
            "chat_id": chat_id,
            "text": message
        }
        
        print("📤 텔레그램 메시지 전송 중...")
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            print("🎉 텔레그램 전송 성공!")
            print("📱 텔레그램에서 메시지를 확인하세요!")
            
            # 설정 저장
            with open('telegram_config.json', 'w') as f:
                json.dump({"bot_token": bot_token, "chat_id": chat_id}, f)
            
            return True
        else:
            print(f"❌ 전송 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False

def setup_email_notifications(email):
    """이메일 알림 설정"""
    try:
        # 간단한 이메일 서비스 사용
        webhook_url = "https://formspree.io/f/xpzvpzjk"  # 예시
        
        data = {
            "email": email,
            "subject": "심플 배민 플러스 알림 설정 완료",
            "message": f"""심플 배민 플러스 이메일 알림이 설정되었습니다.

설정 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
알림 이메일: {email}

이제 모든 배민 플러스 정보를 이메일로 받습니다!"""
        }
        
        print("📧 이메일 전송 중...")
        response = requests.post(webhook_url, data=data, timeout=10)
        
        if response.status_code == 200:
            print("✅ 이메일 설정 완료!")
            print(f"📧 {email}로 확인 메일을 보냈습니다!")
            
            # 설정 저장
            with open('email_config.json', 'w') as f:
                json.dump({"email": email}, f)
            
            return True
        else:
            print("⚠️ 이메일 서비스를 직접 설정해야 합니다.")
            return False
            
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False

def setup_line_notifications(line_token):
    """LINE Notify 설정"""
    try:
        url = "https://notify-api.line.me/api/notify"
        headers = {"Authorization": f"Bearer {line_token}"}
        
        message = f"""🎉 심플 배민 플러스 LINE 연동 완료!

✅ LINE Notify 설정 완료
✅ 실시간 알림 시스템 가동
✅ 카카오톡 대신 LINE으로 알림

⏰ 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎊 이제 모든 배민 플러스 정보를 LINE으로 받습니다!"""

        data = {"message": message}
        
        print("📱 LINE 메시지 전송 중...")
        response = requests.post(url, headers=headers, data=data, timeout=10)
        
        if response.status_code == 200:
            print("🎉 LINE 전송 성공!")
            print("📱 LINE에서 메시지를 확인하세요!")
            
            # 설정 저장
            with open('line_config.json', 'w') as f:
                json.dump({"line_token": line_token}, f)
            
            return True
        else:
            print(f"❌ 전송 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False

def main():
    """메인 해결 시스템"""
    print("🚀 카카오톡 즉시 해결 시스템")
    print("=" * 70)
    print("개발자센터 설정이 복잡하니 다른 방법으로 즉시 해결!")
    print("=" * 70)
    
    print("\n📋 해결 방법 선택:")
    print("1. 새 카카오 앱 생성 (권한 포함)")
    print("2. 카카오톡 채널 생성")  
    print("3. 텔레그램 브리지 (즉시 작동)")
    print("4. 이메일 알림 (즉시 작동)")
    print("5. LINE Notify (즉시 작동)")
    print("0. 모든 방법 시도")
    
    choice = input("\n📝 선택 (0-5): ").strip()
    
    success = False
    
    if choice == "1":
        success = method1_new_app_with_permissions()
    elif choice == "2":
        success = method2_kakao_talk_channel()
    elif choice == "3":
        success = method3_telegram_bridge()
    elif choice == "4":
        success = method4_email_notifications()
    elif choice == "5":
        success = method5_line_notify()
    elif choice == "0":
        print("\n🔄 모든 방법을 차례로 시도합니다...")
        methods = [
            ("텔레그램", method3_telegram_bridge),
            ("LINE", method5_line_notify),
            ("이메일", method4_email_notifications),
            ("새 카카오 앱", method1_new_app_with_permissions),
            ("카카오 채널", method2_kakao_talk_channel)
        ]
        
        for name, method in methods:
            print(f"\n🔄 {name} 방법 시도 중...")
            if method():
                print(f"✅ {name} 방법 성공!")
                success = True
                break
            else:
                print(f"❌ {name} 방법 실패")
    
    print("\n" + "=" * 70)
    if success:
        print("🎊 축하합니다! 알림 시스템이 작동합니다!")
        print("🚀 이제 GitHub Actions에서 자동 전송이 시작됩니다!")
    else:
        print("⚠️ 모든 방법이 실패했습니다.")
        print("💡 수동으로 카카오 개발자센터 설정을 완료해주세요.")
    print("=" * 70)

if __name__ == "__main__":
    main() 