#!/usr/bin/env python3
"""
카카오 인증 코드 → 액세스 토큰 변환기
"""

import requests
import json

def convert_code_to_token(auth_code):
    """인증 코드를 액세스 토큰으로 변환"""
    
    token_url = "https://kauth.kakao.com/oauth/token"
    
    data = {
        'grant_type': 'authorization_code',
        'client_id': 'de4104bc707439376061bf497ce87b8e',
        'redirect_uri': 'http://localhost:8080/callback',
        'code': auth_code
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        print(f"🔄 인증 코드 변환 중: {auth_code[:10]}...")
        
        response = requests.post(token_url, data=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            refresh_token = token_data.get('refresh_token')
            expires_in = token_data.get('expires_in')
            
            print("✅ 액세스 토큰 발급 성공!")
            print(f"🔑 액세스 토큰: {access_token}")
            print(f"🔄 리프레시 토큰: {refresh_token}")
            print(f"⏰ 만료 시간: {expires_in}초 ({expires_in//3600}시간)")
            
            # 토큰 테스트
            test_token(access_token)
            
            return access_token
            
        else:
            print(f"❌ 토큰 발급 실패: {response.status_code}")
            print(f"📄 응답: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 토큰 변환 오류: {e}")
        return None

def test_token(access_token):
    """토큰 유효성 테스트"""
    try:
        print("\n🧪 토큰 테스트 중...")
        
        # 사용자 정보 조회
        user_url = "https://kapi.kakao.com/v2/user/me"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = requests.get(user_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            user_data = response.json()
            user_id = user_data.get('id')
            nickname = user_data.get('properties', {}).get('nickname', 'N/A')
            
            print("✅ 토큰 테스트 성공!")
            print(f"👤 사용자 ID: {user_id}")
            print(f"📝 닉네임: {nickname}")
            
            # 친구 목록 조회
            get_friends_list(access_token)
            
        else:
            print(f"❌ 토큰 테스트 실패: {response.status_code}")
            print(f"📄 응답: {response.text}")
            
    except Exception as e:
        print(f"❌ 토큰 테스트 오류: {e}")

def get_friends_list(access_token):
    """친구 목록 조회"""
    try:
        print("\n👥 친구 목록 조회 중...")
        
        friends_url = "https://kapi.kakao.com/v1/api/talk/friends"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        response = requests.get(friends_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            friends_data = response.json()
            friends = friends_data.get('elements', [])
            
            print(f"✅ 친구 목록 조회 성공! ({len(friends)}명)")
            
            if friends:
                print("\n📋 친구 목록 (UUID):")
                for i, friend in enumerate(friends[:5]):  # 처음 5명만 표시
                    uuid = friend.get('uuid')
                    nickname = friend.get('profile_nickname', 'N/A')
                    print(f"  {i+1}. {nickname}: {uuid}")
                
                if len(friends) > 5:
                    print(f"  ... 외 {len(friends)-5}명 더")
                
                print(f"\n💾 오픈채팅방 참여자의 UUID를 KAKAO_OPENCHAT_ID로 사용하세요!")
                
        else:
            print(f"❌ 친구 목록 조회 실패: {response.status_code}")
            print(f"📄 응답: {response.text}")
            
    except Exception as e:
        print(f"❌ 친구 목록 조회 오류: {e}")

if __name__ == "__main__":
    print("🔑 카카오 인증 코드 → 액세스 토큰 변환기")
    print("="*50)
    
    auth_code = input("🔑 브라우저에서 받은 인증 코드를 입력하세요: ").strip()
    
    if auth_code:
        access_token = convert_code_to_token(auth_code)
        
        if access_token:
            print(f"\n💾 GitHub Secrets에 설정할 값:")
            print(f"KAKAO_ACCESS_TOKEN={access_token}")
    else:
        print("❌ 인증 코드가 입력되지 않았습니다.") 