#!/usr/bin/env python3
"""
🔑 카카오 액세스 토큰 자동 생성기
REST API 키 → 액세스 토큰 변환
"""

import requests
import urllib.parse
import webbrowser
from datetime import datetime
import pytz

KST = pytz.timezone('Asia/Seoul')

def get_access_token_from_rest_api():
    """REST API 키로 액세스 토큰 생성"""
    
    print("🔑 카카오 액세스 토큰 생성기")
    print("━" * 50)
    
    # REST API 키
    rest_api_key = "3f2716744254c8c199bd05c59b84142b"
    redirect_uri = "https://localhost"
    
    print(f"✅ REST API 키: {rest_api_key}")
    print(f"🔗 리다이렉트 URI: {redirect_uri}")
    print("━" * 50)
    
    # 1단계: 인증 코드 받기
    auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={redirect_uri}&response_type=code"
    
    print("📋 1단계: 인증 코드 받기")
    print(f"🌐 다음 URL로 이동합니다:")
    print(f"   {auth_url}")
    print()
    
    # 자동으로 브라우저 열기
    try:
        webbrowser.open(auth_url)
        print("✅ 브라우저가 자동으로 열렸습니다!")
    except:
        print("⚠️  브라우저를 수동으로 열어서 위 URL로 이동하세요!")
    
    print()
    print("📝 브라우저에서:")
    print("   1. 카카오 로그인")
    print("   2. 권한 동의")
    print("   3. 'localhost' 페이지로 이동 (오류 페이지 정상)")
    print("   4. 주소창에서 'code=' 뒤의 값을 복사")
    print()
    
    # 인증 코드 입력받기
    auth_code = input("📋 인증 코드를 입력하세요: ").strip()
    
    if not auth_code:
        print("❌ 인증 코드가 필요합니다!")
        return None
    
    print(f"✅ 인증 코드 확인: {auth_code[:20]}...")
    print()
    
    # 2단계: 액세스 토큰 받기
    print("📋 2단계: 액세스 토큰 받기")
    
    try:
        token_url = "https://kauth.kakao.com/oauth/token"
        
        token_data = {
            'grant_type': 'authorization_code',
            'client_id': rest_api_key,
            'redirect_uri': redirect_uri,
            'code': auth_code
        }
        
        print("📤 토큰 요청 중...")
        response = requests.post(token_url, data=token_data, timeout=10)
        
        if response.status_code == 200:
            token_info = response.json()
            access_token = token_info.get('access_token')
            
            if access_token:
                print("🎉 액세스 토큰 생성 성공!")
                print("━" * 50)
                print(f"🔑 액세스 토큰: {access_token}")
                print("━" * 50)
                
                # 토큰 파일로 저장
                with open('kakao_access_token.txt', 'w') as f:
                    f.write(access_token)
                
                print("💾 토큰이 'kakao_access_token.txt' 파일로 저장되었습니다!")
                print()
                
                return access_token
            else:
                print("❌ 액세스 토큰을 찾을 수 없습니다!")
                print(f"응답: {token_info}")
                return None
        else:
            print(f"❌ 토큰 요청 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return None

def test_access_token(access_token):
    """액세스 토큰으로 바로 테스트"""
    
    print("🧪 액세스 토큰 테스트")
    print("━" * 50)
    
    # 간단한 테스트 메시지
    test_message = f"""🎉 카카오 액세스 토큰 테스트 성공!

⏰ 시간: {datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')}
🔑 토큰: 정상 작동
✅ 상태: 카카오톡 연결 완료

━━━━━━━━━━━━━━━━━━━━━━━━
🍕 배민 G라이더 자동화 준비 완료!
━━━━━━━━━━━━━━━━━━━━━━━━

이제 GitHub Actions와 연결하면
완전 자동화가 완성됩니다! 🚀"""

    try:
        url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        import json
        template = {
            "object_type": "text",
            "text": test_message,
            "link": {
                "web_url": "https://github.com/CHOI-KS1980/baemin",
                "mobile_web_url": "https://github.com/CHOI-KS1980/baemin"
            }
        }
        
        data = {
            "template_object": json.dumps(template)
        }
        
        print("📤 테스트 메시지 전송 중...")
        response = requests.post(url, headers=headers, data=data, timeout=10)
        
        if response.status_code == 200:
            print("🎉 성공! 카카오톡을 확인하세요!")
            print("✅ 액세스 토큰이 정상 작동합니다!")
            return True
        else:
            print(f"❌ 전송 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 테스트 오류: {e}")
        return False

if __name__ == "__main__":
    print("━" * 60)
    print("🔑 카카오 액세스 토큰 생성 및 테스트")
    print("━" * 60)
    
    # 액세스 토큰 생성
    access_token = get_access_token_from_rest_api()
    
    if access_token:
        print("\n🎯 생성된 액세스 토큰으로 바로 테스트!")
        print("━" * 50)
        
        # 바로 테스트
        success = test_access_token(access_token)
        
        if success:
            print("\n🎊 완전 성공!")
            print("이제 GitHub Actions 자동화를 시작할 수 있습니다!")
            print(f"📋 액세스 토큰: {access_token}")
        else:
            print("\n❌ 테스트 실패. 토큰을 다시 생성해주세요.")
    else:
        print("\n❌ 액세스 토큰 생성 실패!")
        print("REST API 키나 인증 과정을 다시 확인해주세요.") 