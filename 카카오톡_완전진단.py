#!/usr/bin/env python3
"""
🔍 카카오톡 전송 문제 완전 진단 시스템
모든 가능한 원인을 체크하고 즉시 해결
"""

import os
import json
import requests
import webbrowser
from datetime import datetime

print("🔍 카카오톡 전송 문제 완전 진단 시스템")
print("=" * 70)

def check_token_file():
    """토큰 파일 확인"""
    print("\n1️⃣ 토큰 파일 상태 확인:")
    print("-" * 40)
    
    try:
        with open('kakao_access_token.txt', 'r') as f:
            token = f.read().strip()
        
        if token:
            print(f"✅ 토큰 파일 존재: {token[:15]}...")
            return token
        else:
            print("❌ 토큰 파일이 비어있음")
            return None
            
    except FileNotFoundError:
        print("❌ 토큰 파일 없음")
        return None
    except Exception as e:
        print(f"❌ 토큰 파일 읽기 오류: {e}")
        return None

def check_token_validity(token):
    """토큰 유효성 확인"""
    print("\n2️⃣ 토큰 유효성 확인:")
    print("-" * 40)
    
    try:
        url = "https://kapi.kakao.com/v1/user/access_token_info"
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            token_info = response.json()
            print("✅ 토큰 유효함")
            print(f"   📱 앱 ID: {token_info.get('app_id')}")
            print(f"   ⏰ 만료: {token_info.get('expires_in')} 초 후")
            return True, token_info
        else:
            print(f"❌ 토큰 만료됨: {response.status_code}")
            print(f"   응답: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ 토큰 확인 오류: {e}")
        return False, None

def check_app_permissions(token):
    """앱 권한 확인"""
    print("\n3️⃣ 앱 권한 확인:")
    print("-" * 40)
    
    try:
        # 메시지 전송 테스트로 권한 확인
        url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        test_template = {
            "object_type": "text",
            "text": "권한 테스트 메시지"
        }
        
        data = {"template_object": json.dumps(test_template)}
        
        response = requests.post(url, headers=headers, data=data, timeout=10)
        
        if response.status_code == 200:
            print("✅ 메시지 전송 권한 정상")
            return True, "권한 정상"
            
        elif response.status_code == 403:
            error_data = response.json()
            
            if "insufficient scopes" in error_data.get("msg", ""):
                print("❌ 권한 부족 (insufficient scopes)")
                print(f"   필요 권한: {error_data.get('required_scopes', [])}")
                print(f"   현재 권한: {error_data.get('allowed_scopes', [])}")
                return False, "권한 미설정"
                
            elif "disabled" in error_data.get("msg", ""):
                print("❌ 앱에서 기능 비활성화")
                print("   개발자센터에서 권한을 활성화해야 함")
                return False, "앱 설정 필요"
            else:
                print(f"❌ 기타 권한 오류: {error_data}")
                return False, "기타 오류"
        else:
            print(f"❌ 알 수 없는 오류: {response.status_code}")
            print(f"   응답: {response.text}")
            return False, "알 수 없는 오류"
            
    except Exception as e:
        print(f"❌ 권한 확인 오류: {e}")
        return False, "확인 오류"

def check_developer_console_guide():
    """개발자센터 설정 안내"""
    print("\n4️⃣ 카카오 개발자센터 설정 필요:")
    print("-" * 40)
    
    print("🌐 자동으로 개발자센터를 열겠습니다...")
    
    try:
        webbrowser.open("https://developers.kakao.com")
        print("✅ 브라우저가 열렸습니다!")
    except:
        print("❌ 브라우저 자동 열기 실패")
        print("   수동으로 https://developers.kakao.com 접속하세요")
    
    print("\n📋 단계별 설정 방법:")
    print("   1. 로그인 → '내 애플리케이션' 클릭")
    print("   2. '배민 미션정보 발송 자동화' 앱 선택")
    print("   3. 좌측 메뉴: '제품 설정' → '카카오 로그인'")
    print("   4. '동의항목' 탭 클릭")
    print("   5. '카카오톡 메시지 전송' 체크박스 활성화 ✅")
    print("   6. '저장' 버튼 클릭")
    
    print("\n⚠️  중요: 저장 후 2-3분 대기 필요")

def generate_new_token():
    """새 토큰 생성"""
    print("\n5️⃣ 새 액세스 토큰 생성:")
    print("-" * 40)
    
    rest_api_key = "3f2716744254c8c199bd05c59b84142b"
    redirect_uri = "https://localhost"
    
    auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={redirect_uri}&response_type=code&scope=talk_message"
    
    print(f"🔗 인증 URL:")
    print(f"   {auth_url}")
    
    try:
        webbrowser.open(auth_url)
        print("✅ 브라우저가 자동으로 열렸습니다!")
    except:
        print("❌ 브라우저 자동 열기 실패")
        print(f"   수동으로 위 URL에 접속하세요")
    
    print("\n📝 인증 과정:")
    print("   1. 카카오 로그인")
    print("   2. '카카오톡 메시지 전송' 권한 동의")
    print("   3. localhost 페이지로 이동 (오류 페이지 정상)")
    print("   4. 주소창에서 'code=' 뒤의 값을 복사")
    
    auth_code = input("\n📋 인증 코드를 입력하세요: ").strip()
    
    if auth_code:
        print("\n📤 액세스 토큰 요청 중...")
        return get_access_token(auth_code, rest_api_key, redirect_uri)
    else:
        print("❌ 인증 코드가 입력되지 않았습니다.")
        return None

def get_access_token(auth_code, client_id, redirect_uri):
    """인증 코드로 액세스 토큰 받기"""
    try:
        url = "https://kauth.kakao.com/oauth/token"
        data = {
            'grant_type': 'authorization_code',
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'code': auth_code
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            
            if access_token:
                print("🎉 액세스 토큰 생성 성공!")
                print(f"🔑 토큰: {access_token}")
                
                # 파일로 저장
                with open('kakao_access_token.txt', 'w') as f:
                    f.write(access_token)
                print("💾 토큰이 파일로 저장되었습니다!")
                
                return access_token
            else:
                print("❌ 토큰 생성 실패: 토큰 없음")
                return None
        else:
            print(f"❌ 토큰 요청 실패: {response.status_code}")
            print(f"   응답: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 토큰 생성 오류: {e}")
        return None

def final_test(token):
    """최종 실제 전송 테스트"""
    print("\n6️⃣ 최종 실제 전송 테스트:")
    print("-" * 40)
    
    try:
        url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        message = f"""🎉 심플 배민 플러스 카카오톡 연동 성공!

✅ 개발자센터 설정 완료
✅ 실제 카카오톡 전송 가능
✅ 자동화 시스템 준비 완료

⏰ 테스트 시간: {now}
💪 이제 24시간 자동 전송이 시작됩니다!

🎊 축하합니다! 모든 설정이 완료되었습니다!"""

        template = {
            "object_type": "text",
            "text": message,
            "link": {
                "web_url": "https://github.com/CHOI-KS1980/baemin",
                "mobile_web_url": "https://github.com/CHOI-KS1980/baemin"
            }
        }
        
        data = {"template_object": json.dumps(template)}
        
        print("📤 실제 카카오톡 전송 중...")
        response = requests.post(url, headers=headers, data=data, timeout=10)
        
        if response.status_code == 200:
            print("🎉 실제 카카오톡 전송 성공!")
            print("📱 휴대폰에서 카카오톡 메시지를 확인하세요!")
            return True
        else:
            print(f"❌ 전송 실패: {response.status_code}")
            print(f"   응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 전송 오류: {e}")
        return False

def main():
    """메인 진단 프로세스"""
    print("\n🚀 카카오톡 전송 문제 완전 진단을 시작합니다!")
    print("=" * 70)
    
    # 1. 토큰 파일 확인
    token = check_token_file()
    
    if not token:
        print("\n❌ 토큰이 없습니다. 새로 생성하겠습니다.")
        token = generate_new_token()
        if not token:
            print("❌ 토큰 생성 실패. 수동 설정 필요.")
            return False
    
    # 2. 토큰 유효성 확인
    is_valid, token_info = check_token_validity(token)
    
    if not is_valid:
        print("\n❌ 토큰이 만료되었습니다. 새로 생성하겠습니다.")
        token = generate_new_token()
        if not token:
            print("❌ 토큰 생성 실패. 수동 설정 필요.")
            return False
    
    # 3. 앱 권한 확인
    has_permission, error_type = check_app_permissions(token)
    
    if not has_permission:
        if error_type == "권한 미설정" or error_type == "앱 설정 필요":
            print("\n❌ 개발자센터에서 권한 설정이 필요합니다.")
            check_developer_console_guide()
            
            print("\n⏳ 설정 완료 후 이 스크립트를 다시 실행하세요!")
            print("   python3 카카오톡_완전진단.py")
            return False
        else:
            print(f"\n❌ 해결할 수 없는 오류: {error_type}")
            return False
    
    # 4. 최종 테스트
    success = final_test(token)
    
    if success:
        print("\n🎊 축하합니다! 모든 문제가 해결되었습니다!")
        print("🚀 이제 GitHub Actions에서 자동 전송이 시작됩니다!")
        return True
    else:
        print("\n❌ 최종 테스트 실패. 추가 확인 필요.")
        return False

if __name__ == "__main__":
    success = main()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ 진단 완료: 모든 문제 해결됨")
        print("🎉 심플 배민 플러스 자동화 시스템 가동 준비 완료!")
    else:
        print("⚠️  진단 완료: 추가 설정 필요")
        print("💡 위의 안내에 따라 설정을 완료해주세요.")
    print("=" * 70) 