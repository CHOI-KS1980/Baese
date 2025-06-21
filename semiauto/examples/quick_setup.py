#!/usr/bin/env python3
"""
🚀 카카오톡 API 빠른 설정 스크립트
토큰 발급부터 테스트까지 한 번에 처리
"""

import requests
import webbrowser
import time
import threading
from urllib.parse import urlparse, parse_qs
from flask import Flask, request
import json

class QuickSetup:
    def __init__(self):
        self.rest_api_key = None
        self.access_token = None
        self.refresh_token = None
        self.redirect_uri = "http://localhost:8080/oauth/kakao/callback"
        
    def step1_get_api_key(self):
        """1단계: REST API 키 입력"""
        print("🎯 카카오톡 API 빠른 설정을 시작합니다!")
        print()
        print("📋 사전 준비사항:")
        print("1. https://developers.kakao.com 접속")
        print("2. 애플리케이션 생성")
        print("3. 플랫폼 > Web 플랫폼 등록 > 사이트 도메인: http://localhost:8080")
        print("4. 카카오 로그인 활성화")
        print("5. Redirect URI 등록: http://localhost:8080/oauth/kakao/callback")
        print("6. 동의항목 > '카카오톡 메시지 전송' 체크")
        print()
        
        self.rest_api_key = input("🔑 REST API 키를 입력하세요: ").strip()
        
        if not self.rest_api_key:
            print("❌ REST API 키가 필요합니다.")
            return False
            
        print(f"✅ REST API 키 설정 완료: {self.rest_api_key[:20]}...")
        return True
    
    def step2_get_tokens_simple(self):
        """2단계: 간단한 토큰 발급"""
        print("\n🔐 토큰 발급을 시작합니다...")
        
        # 인증 URL 생성
        auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={self.rest_api_key}&redirect_uri={self.redirect_uri}&response_type=code&scope=talk_message"
        
        print("🌐 브라우저에서 카카오 로그인 페이지가 열립니다...")
        webbrowser.open(auth_url)
        
        print("\n📝 로그인 후 리다이렉트된 URL을 확인하세요.")
        print("예: http://localhost:8080/oauth/kakao/callback?code=XXXXXXXX")
        
        callback_url = input("\n✅ 전체 URL을 붙여넣으세요: ").strip()
        
        try:
            # code 추출
            parsed_url = urlparse(callback_url)
            code = parse_qs(parsed_url.query)['code'][0]
            print(f"📝 인증 코드 추출: {code[:20]}...")
            
            # 토큰 발급
            return self._exchange_code_for_tokens(code)
            
        except Exception as e:
            print(f"❌ 코드 추출 실패: {e}")
            return False
    
    def step2_get_tokens_auto(self):
        """2단계: 자동 토큰 발급 (Flask 서버 사용)"""
        print("\n🔐 자동 토큰 발급을 시작합니다...")
        
        app = Flask(__name__)
        tokens_received = threading.Event()
        
        @app.route('/oauth/kakao/callback')
        def kakao_callback():
            code = request.args.get('code')
            
            if code:
                print(f"\n📝 인증 코드 수신: {code[:20]}...")
                success = self._exchange_code_for_tokens(code)
                
                # 서버 종료 신호
                threading.Timer(2.0, lambda: tokens_received.set()).start()
                
                if success:
                    return "✅ 토큰 발급 완료! 창을 닫아주세요."
                else:
                    return "❌ 토큰 발급 실패"
            
            return "❌ 인증 코드가 없습니다"
        
        # 서버 시작
        server_thread = threading.Thread(
            target=lambda: app.run(port=8080, debug=False, use_reloader=False)
        )
        server_thread.daemon = True
        server_thread.start()
        
        time.sleep(1)  # 서버 시작 대기
        
        # 브라우저에서 인증 페이지 열기
        auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={self.rest_api_key}&redirect_uri={self.redirect_uri}&response_type=code&scope=talk_message"
        print("🌐 브라우저에서 카카오 로그인 페이지가 열립니다...")
        webbrowser.open(auth_url)
        
        # 토큰 발급 대기 (최대 60초)
        if tokens_received.wait(timeout=60):
            return self.access_token is not None
        else:
            print("❌ 토큰 발급 시간 초과")
            return False
    
    def _exchange_code_for_tokens(self, code):
        """인증 코드를 토큰으로 교환"""
        token_url = "https://kauth.kakao.com/oauth/token"
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.rest_api_key,
            'redirect_uri': self.redirect_uri,
            'code': code
        }
        
        try:
            response = requests.post(token_url, data=data)
            tokens = response.json()
            
            if 'access_token' in tokens:
                self.access_token = tokens['access_token']
                self.refresh_token = tokens['refresh_token']
                
                print("✅ 토큰 발급 성공!")
                print(f"🔑 Access Token: {self.access_token[:30]}...")
                print(f"🔄 Refresh Token: {self.refresh_token[:30]}...")
                
                return True
            else:
                print(f"❌ 토큰 발급 실패: {tokens}")
                return False
                
        except Exception as e:
            print(f"❌ 토큰 발급 중 오류: {e}")
            return False
    
    def step3_test_message(self):
        """3단계: 메시지 전송 테스트"""
        print("\n📱 메시지 전송 테스트를 시작합니다...")
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
        
        template_object = {
            "object_type": "text",
            "text": f"🧪 카카오톡 API 설정 완료!\n시간: {time.strftime('%Y-%m-%d %H:%M:%S')}\n✅ 모든 설정이 정상적으로 완료되었습니다!",
            "link": {
                "web_url": "https://developers.kakao.com",
                "mobile_web_url": "https://developers.kakao.com"
            },
            "button_title": "개발자 문서"
        }
        
        data = {
            'template_object': json.dumps(template_object, ensure_ascii=False)
        }
        
        try:
            response = requests.post(
                "https://kapi.kakao.com/v2/api/talk/memo/default/send",
                headers=headers,
                data=data
            )
            
            result = response.json()
            
            if result.get('result_code') == 0:
                print("✅ 테스트 메시지 전송 성공!")
                print("📱 카카오톡에서 메시지를 확인해보세요.")
                return True
            else:
                print(f"❌ 메시지 전송 실패: {result}")
                return False
                
        except Exception as e:
            print(f"❌ 메시지 전송 중 오류: {e}")
            return False
    
    def step4_save_config(self):
        """4단계: 설정 파일 저장"""
        print("\n💾 설정 파일을 저장합니다...")
        
        try:
            # config.txt 파일 생성
            with open('config.txt', 'w') as f:
                f.write(f"REST_API_KEY={self.rest_api_key}\n")
                f.write(f"REFRESH_TOKEN={self.refresh_token}\n")
            
            # kakao_tokens.txt 파일 생성
            with open('kakao_tokens.txt', 'w') as f:
                f.write(f"ACCESS_TOKEN={self.access_token}\n")
                f.write(f"REFRESH_TOKEN={self.refresh_token}\n")
            
            print("✅ 설정 파일 저장 완료!")
            print("📁 생성된 파일:")
            print("   - config.txt (메인 설정)")
            print("   - kakao_tokens.txt (토큰 정보)")
            
            return True
            
        except Exception as e:
            print(f"❌ 설정 파일 저장 실패: {e}")
            return False
    
    def run_setup(self):
        """전체 설정 프로세스 실행"""
        print("=" * 60)
        print("🚀 카카오톡 API 빠른 설정")
        print("=" * 60)
        
        # 1단계: API 키 입력
        if not self.step1_get_api_key():
            return False
        
        # 2단계: 토큰 발급 방법 선택
        print("\n🔧 토큰 발급 방법을 선택하세요:")
        print("1. 자동 발급 (추천)")
        print("2. 수동 발급")
        
        choice = input("\n선택 (1 또는 2): ").strip()
        
        if choice == "1":
            success = self.step2_get_tokens_auto()
        else:
            success = self.step2_get_tokens_simple()
        
        if not success:
            print("❌ 토큰 발급 실패")
            return False
        
        # 3단계: 메시지 테스트
        if not self.step3_test_message():
            print("❌ 메시지 테스트 실패")
            return False
        
        # 4단계: 설정 저장
        if not self.step4_save_config():
            print("❌ 설정 저장 실패")
            return False
        
        # 완료
        print("\n" + "=" * 60)
        print("🎉 설정 완료!")
        print("=" * 60)
        print("✅ 이제 다음 명령으로 자동화를 시작할 수 있습니다:")
        print("   python core/final_solution.py")
        print()
        print("📱 카카오톡 '나와의 채팅'에서 메시지를 확인하고")
        print("   오픈채팅방에 복사/붙여넣기하세요!")
        print()
        print("🌐 GitHub Actions 24시간 자동화를 원한다면:")
        print("=" * 50)
        print("📋 GitHub Secrets에 다음 정보를 등록하세요:")
        print()
        print(f"🔑 KAKAO_REST_API_KEY:")
        print(f"   {self.rest_api_key}")
        print()
        print(f"🔄 KAKAO_REFRESH_TOKEN:")
        print(f"   {self.refresh_token}")
        print()
        print("📖 자세한 설정 방법:")
        print("   docs/GitHub_Actions_설정가이드.md 파일을 참고하세요!")
        
        return True

def main():
    """메인 실행 함수"""
    setup = QuickSetup()
    setup.run_setup()

if __name__ == "__main__":
    main() 