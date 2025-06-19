#!/usr/bin/env python3
"""
카카오 API 액세스 토큰 생성 도구
REST API 키로부터 실제 사용 가능한 액세스 토큰을 생성합니다.
"""

import requests
import urllib.parse
import webbrowser
import os
from dotenv import load_dotenv
import json

# 환경변수 로드
load_dotenv()

class KakaoTokenGenerator:
    """카카오 액세스 토큰 생성기"""
    
    def __init__(self):
        self.rest_api_key = os.getenv('KAKAO_ADMIN_KEY', '')
        self.redirect_uri = "http://localhost:8080/callback"  # 기본 리다이렉트 URI
        
        print("🔑 카카오 액세스 토큰 생성 도구")
        print("="*50)
        
        if not self.rest_api_key or self.rest_api_key == 'your_kakao_admin_key_here':
            print("❌ KAKAO_ADMIN_KEY가 설정되지 않았습니다.")
            print("📝 .env 파일에서 REST API 키를 확인해주세요.")
            return
            
        print(f"✅ REST API 키 로드: {self.rest_api_key[:10]}...")
    
    def step1_get_auth_code(self):
        """1단계: 인증 코드 받기"""
        print("\n1️⃣ 인증 코드 받기")
        print("-" * 30)
        
        # 카카오 로그인 URL 생성
        auth_url = "https://kauth.kakao.com/oauth/authorize"
        params = {
            'client_id': self.rest_api_key,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'profile_nickname,talk_message,friends'
        }
        
        full_auth_url = f"{auth_url}?{urllib.parse.urlencode(params)}"
        
        print("🌐 다음 URL을 브라우저에서 열어주세요:")
        print(f"{full_auth_url}")
        print()
        
        # 자동으로 브라우저 열기 시도
        try:
            webbrowser.open(full_auth_url)
            print("✅ 브라우저에서 자동으로 열렸습니다.")
        except:
            print("⚠️ 브라우저를 수동으로 열어주세요.")
        
        print("\n📋 진행 방법:")
        print("1. 위 URL을 브라우저에서 열기")
        print("2. 카카오 계정으로 로그인")
        print("3. 권한 동의하기")
        print("4. 리다이렉트된 URL에서 'code=' 부분 복사")
        
        print("\n💡 예시:")
        print("http://localhost:8080/callback?code=ABC123XYZ...")
        print("→ 'ABC123XYZ...' 부분을 복사하세요")
        
        auth_code = input("\n🔑 인증 코드를 입력하세요: ").strip()
        
        if auth_code:
            print(f"✅ 인증 코드 입력됨: {auth_code[:10]}...")
            return auth_code
        else:
            print("❌ 인증 코드가 입력되지 않았습니다.")
            return None
    
    def step2_get_access_token(self, auth_code):
        """2단계: 액세스 토큰 받기"""
        print("\n2️⃣ 액세스 토큰 받기")
        print("-" * 30)
        
        token_url = "https://kauth.kakao.com/oauth/token"
        
        data = {
            'grant_type': 'authorization_code',
            'client_id': self.rest_api_key,
            'redirect_uri': self.redirect_uri,
            'code': auth_code
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.post(token_url, data=data, headers=headers)
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get('access_token')
                refresh_token = token_data.get('refresh_token')
                expires_in = token_data.get('expires_in')
                
                print("✅ 액세스 토큰 발급 성공!")
                print(f"🔑 액세스 토큰: {access_token[:20]}...")
                print(f"🔄 리프레시 토큰: {refresh_token[:20] if refresh_token else 'N/A'}...")
                print(f"⏰ 만료 시간: {expires_in}초 ({expires_in//3600}시간)")
                
                return {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'expires_in': expires_in
                }
            else:
                print(f"❌ 토큰 발급 실패: {response.status_code}")
                print(f"📄 응답: {response.text}")
                
                # 일반적인 오류 해결 방법 안내
                if response.status_code == 400:
                    error_data = response.json()
                    error_code = error_data.get('error')
                    
                    if error_code == 'invalid_grant':
                        print("\n💡 해결 방법:")
                        print("1. 인증 코드가 만료되었을 수 있습니다 (10분 제한)")
                        print("2. 1단계부터 다시 진행해주세요")
                        print("3. 인증 코드를 정확히 복사했는지 확인하세요")
                
        except Exception as e:
            print(f"❌ 요청 중 오류 발생: {e}")
        
        return None
    
    def step3_test_token(self, access_token):
        """3단계: 토큰 테스트"""
        print("\n3️⃣ 액세스 토큰 테스트")
        print("-" * 30)
        
        # 사용자 정보 조회로 토큰 테스트
        test_url = "https://kapi.kakao.com/v2/user/me"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.get(test_url, headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                user_id = user_data.get('id')
                nickname = user_data.get('properties', {}).get('nickname', 'N/A')
                
                print("✅ 토큰 테스트 성공!")
                print(f"👤 사용자 ID: {user_id}")
                print(f"📝 닉네임: {nickname}")
                
                return user_id
            else:
                print(f"❌ 토큰 테스트 실패: {response.status_code}")
                print(f"📄 응답: {response.text}")
                
        except Exception as e:
            print(f"❌ 테스트 중 오류 발생: {e}")
        
        return None
    
    def step4_update_env(self, tokens, user_id):
        """4단계: 환경변수 파일 업데이트"""
        print("\n4️⃣ 환경변수 파일 업데이트")
        print("-" * 30)
        
        access_token = tokens['access_token']
        refresh_token = tokens.get('refresh_token', '')
        
        # .env 파일 읽기
        env_file = '.env'
        env_lines = []
        
        if os.path.exists(env_file):
            with open(env_file, 'r', encoding='utf-8') as f:
                env_lines = f.readlines()
        
        # 업데이트할 변수들
        updates = {
            'KAKAO_ACCESS_TOKEN': access_token,
            'KAKAO_REFRESH_TOKEN': refresh_token,
            'KAKAO_BOT_USER_ID': str(user_id)
        }
        
        # 기존 라인 업데이트 또는 새로 추가
        updated_keys = set()
        
        for i, line in enumerate(env_lines):
            if '=' in line:
                key = line.split('=')[0].strip()
                if key in updates:
                    env_lines[i] = f"{key}={updates[key]}\n"
                    updated_keys.add(key)
        
        # 새로운 키 추가
        for key, value in updates.items():
            if key not in updated_keys:
                env_lines.append(f"{key}={value}\n")
        
        # 파일 저장
        try:
            with open(env_file, 'w', encoding='utf-8') as f:
                f.writelines(env_lines)
            
            print(f"✅ {env_file} 파일이 업데이트되었습니다!")
            print("\n📋 추가된 내용:")
            for key, value in updates.items():
                display_value = f"{value[:20]}..." if len(value) > 20 else value
                print(f"   {key}={display_value}")
                
        except Exception as e:
            print(f"❌ 파일 저장 실패: {e}")
            print("\n💾 수동으로 추가해야 할 내용:")
            for key, value in updates.items():
                print(f"{key}={value}")
    
    def show_setup_guide(self):
        """설정 가이드 표시"""
        print("\n" + "="*60)
        print("📋 카카오 개발자 콘솔 사전 설정 가이드")
        print("="*60)
        
        print("\n1️⃣ 카카오 개발자 콘솔 설정")
        print("   🔗 https://developers.kakao.com/")
        print("   1. 내 애플리케이션 → 앱 선택")
        print("   2. 앱 설정 → 플랫폼 → Web 플랫폼 등록")
        print(f"   3. 사이트 도메인: {self.redirect_uri}")
        
        print("\n2️⃣ 카카오 로그인 설정")
        print("   1. 제품 설정 → 카카오 로그인 → 활성화 설정 ON")
        print(f"   2. Redirect URI 등록: {self.redirect_uri}")
        
        print("\n3️⃣ 동의항목 설정")
        print("   1. 제품 설정 → 카카오 로그인 → 동의항목")
        print("   2. 다음 권한들을 필수 동의로 설정:")
        print("      ✅ 닉네임 (profile_nickname)")
        print("      ✅ 카카오톡 메시지 전송 (talk_message)")
        print("      ✅ 친구 목록 기본정보 (friends)")
        
        print("\n4️⃣ 비즈니스 채널 설정 (선택사항)")
        print("   1. 제품 설정 → 카카오톡 채널")
        print("   2. 채널 추가 후 검수 요청")
        
        print("\n⚠️ 중요 사항:")
        print("   - 개발자 콘솔 설정이 완료된 후에 이 도구를 사용하세요")
        print("   - 리다이렉트 URI가 정확히 등록되어야 합니다")
        print("   - 권한 설정이 완료되어야 토큰 발급이 가능합니다")

def main():
    """메인 함수"""
    generator = KakaoTokenGenerator()
    
    if not generator.rest_api_key:
        return
    
    print("\n📋 실행할 작업을 선택하세요:")
    print("1. 액세스 토큰 생성 (전체 과정)")
    print("2. 카카오 개발자 콘솔 설정 가이드")
    
    choice = input("\n선택 (1-2): ").strip()
    
    if choice == "1":
        print("\n🚀 액세스 토큰 생성을 시작합니다...")
        
        # 1단계: 인증 코드 받기
        auth_code = generator.step1_get_auth_code()
        if not auth_code:
            return
        
        # 2단계: 액세스 토큰 받기
        tokens = generator.step2_get_access_token(auth_code)
        if not tokens:
            return
        
        # 3단계: 토큰 테스트
        user_id = generator.step3_test_token(tokens['access_token'])
        if not user_id:
            return
        
        # 4단계: 환경변수 업데이트
        generator.step4_update_env(tokens, user_id)
        
        print("\n🎉 완료!")
        print("이제 kakao_id_finder.py를 다시 실행해보세요.")
        
    elif choice == "2":
        generator.show_setup_guide()
        
    else:
        print("❌ 잘못된 선택입니다.")

if __name__ == "__main__":
    main() 