#!/usr/bin/env python3
"""
카카오톡 오픈채팅방 ID 및 사용자 ID 확인 도구
"""

import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

class KakaoIDFinder:
    """카카오 ID 확인 도구"""
    
    def __init__(self):
        self.access_token = os.getenv('KAKAO_ACCESS_TOKEN')
        self.admin_key = os.getenv('KAKAO_ADMIN_KEY')  # 백업용
        self.api_base = os.getenv('KAKAO_API_BASE_URL', 'https://kapi.kakao.com')
        
        # 액세스 토큰 우선 사용, 없으면 admin key 사용
        if self.access_token and self.access_token != 'your_access_token_here':
            self.auth_token = self.access_token
            self.auth_type = "Bearer"
            print(f"✅ 액세스 토큰 로드 완료: {self.auth_token[:15]}...")
        elif self.admin_key and self.admin_key != 'your_kakao_admin_key_here':
            self.auth_token = self.admin_key
            self.auth_type = "Bearer"
            print(f"⚠️ REST API 키 사용 (제한적): {self.auth_token[:10]}...")
            print("💡 더 나은 기능을 위해 액세스 토큰 생성을 권장합니다.")
            print("   실행: python kakao_token_generator.py")
        else:
            print("❌ 카카오 API 키가 설정되지 않았습니다.")
            print("📝 다음 중 하나를 설정해주세요:")
            print("   1. KAKAO_ACCESS_TOKEN (권장)")
            print("   2. KAKAO_ADMIN_KEY (제한적)")
            print("\n🔧 토큰 생성: python kakao_token_generator.py")
            self.auth_token = None
            return
        
    def get_user_info(self):
        """현재 사용자 정보 조회"""
        print("\n1️⃣ 사용자 정보 조회")
        print("-" * 30)
        
        if not self.auth_token:
            print("❌ 인증 토큰이 없습니다.")
            return None
        
        url = f"{self.api_base}/v2/user/me"
        headers = {
            'Authorization': f'{self.auth_type} {self.auth_token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                print("✅ 사용자 정보 조회 성공:")
                print(f"   사용자 ID: {user_data.get('id')}")
                print(f"   닉네임: {user_data.get('properties', {}).get('nickname', 'N/A')}")
                print(f"   이메일: {user_data.get('kakao_account', {}).get('email', 'N/A')}")
                
                # 이 ID가 봇 사용자 ID로 사용될 수 있음
                bot_user_id = user_data.get('id')
                if bot_user_id:
                    print(f"\n💡 봇 사용자 ID로 사용 가능: {bot_user_id}")
                    return bot_user_id
                    
            elif response.status_code == 401:
                print(f"❌ 인증 실패: {response.status_code}")
                print(f"   응답: {response.text}")
                print("\n💡 해결 방법:")
                print("   1. 액세스 토큰을 생성하세요: python kakao_token_generator.py")
                print("   2. 토큰이 만료되었을 수 있습니다")
                print("   3. 권한 설정을 확인하세요")
            else:
                print(f"❌ 사용자 정보 조회 실패: {response.status_code}")
                print(f"   응답: {response.text}")
                
        except Exception as e:
            print(f"❌ 요청 중 오류 발생: {e}")
        
        return None
    
    def get_friends_list(self):
        """친구 목록 조회"""
        print("\n2️⃣ 친구 목록 조회")
        print("-" * 30)
        
        if not self.auth_token:
            print("❌ 인증 토큰이 없습니다.")
            return None
            
        url = f"{self.api_base}/v1/api/talk/friends"
        headers = {
            'Authorization': f'{self.auth_type} {self.auth_token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                friends_data = response.json()
                total_count = friends_data.get('total_count', 0)
                friends = friends_data.get('elements', [])
                
                print(f"✅ 친구 목록 조회 성공: 총 {total_count}명")
                
                if friends:
                    print("\n📋 친구 목록:")
                    for i, friend in enumerate(friends[:10], 1):  # 최대 10명만 표시
                        uuid = friend.get('uuid')
                        profile_nickname = friend.get('profile_nickname', 'N/A')
                        print(f"   {i}. {profile_nickname} (UUID: {uuid})")
                    
                    if len(friends) > 10:
                        print(f"   ... 외 {len(friends) - 10}명 더")
                        
                    return friends
                else:
                    print("📝 등록된 친구가 없습니다.")
                    
            else:
                print(f"❌ 친구 목록 조회 실패: {response.status_code}")
                print(f"   응답: {response.text}")
                
                if response.status_code == 403:
                    print("\n💡 권한 부족 해결 방법:")
                    print("   1. 카카오 개발자 콘솔에서 'friends' 권한 활성화")
                    print("   2. 카카오톡 메시지 API 활성화")
                    print("   3. 사용자 동의 과정 완료")
                
        except Exception as e:
            print(f"❌ 요청 중 오류 발생: {e}")
        
        return None
    
    def test_message_send(self, target_uuid=None):
        """테스트 메시지 전송 (나에게 보내기)"""
        print("\n3️⃣ 테스트 메시지 전송")
        print("-" * 30)
        
        if not self.auth_token:
            print("❌ 인증 토큰이 없습니다.")
            return False
            
        # 나에게 메시지 보내기 API 사용
        url = f"{self.api_base}/v2/api/talk/memo/default/send"
        headers = {
            'Authorization': f'{self.auth_type} {self.auth_token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        # 템플릿 객체 생성
        template_object = {
            "object_type": "text",
            "text": f"🧪 카카오톡 API 테스트\n\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n✅ API 연결이 정상적으로 작동합니다!",
            "link": {
                "web_url": "https://developers.kakao.com"
            }
        }
        
        data = {
            'template_object': json.dumps(template_object)
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            
            if response.status_code == 200:
                print("✅ 테스트 메시지 전송 성공!")
                print("📱 카카오톡에서 메시지를 확인해보세요.")
                return True
            else:
                print(f"❌ 메시지 전송 실패: {response.status_code}")
                print(f"   응답: {response.text}")
                
                if response.status_code == 403:
                    print("\n💡 권한 부족 해결 방법:")
                    print("   1. 카카오 개발자 콘솔에서 'talk_message' 권한 활성화")
                    print("   2. 앱 설정에서 카카오톡 메시지 API 활성화")
                
        except Exception as e:
            print(f"❌ 요청 중 오류 발생: {e}")
        
        return False
    
    def get_app_info(self):
        """앱 정보 조회"""
        print("\n4️⃣ 앱 정보 조회")
        print("-" * 30)
        
        if not self.auth_token:
            print("❌ 인증 토큰이 없습니다.")
            return None
            
        url = f"{self.api_base}/v1/api/talk/profile"
        headers = {
            'Authorization': f'{self.auth_type} {self.auth_token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                profile_data = response.json()
                print("✅ 프로필 정보 조회 성공:")
                print(f"   닉네임: {profile_data.get('nickName', 'N/A')}")
                print(f"   프로필 이미지: {profile_data.get('profileImageURL', 'N/A')}")
                return profile_data
            else:
                print(f"❌ 프로필 조회 실패: {response.status_code}")
                print(f"   응답: {response.text}")
                
        except Exception as e:
            print(f"❌ 요청 중 오류 발생: {e}")
        
        return None
    
    def show_setup_guide(self):
        """설정 가이드 표시"""
        print("\n" + "="*60)
        print("📋 오픈채팅방 ID 확인 가이드")
        print("="*60)
        
        print("\n🔍 **방법 1: 카카오톡 앱에서 확인**")
        print("   1. 오픈채팅방 생성 또는 참여")
        print("   2. 채팅방 설정 → 관리 → 채팅방 정보")
        print("   3. URL에서 ID 확인 (예: openchat.kakao.com/o/gABCDEF123)")
        print("   4. 'gABCDEF123' 부분이 채팅방 ID")
        
        print("\n🔍 **방법 2: 개발자 도구 사용**")
        print("   1. 브라우저에서 카카오톡 웹 버전 접속")
        print("   2. 오픈채팅방 입장")
        print("   3. 개발자 도구(F12) → Network 탭")
        print("   4. 메시지 전송 시 요청에서 room_id 확인")
        
        print("\n🔍 **방법 3: API 테스트 (추천)**")
        print("   1. 위의 테스트 메시지 전송이 성공하면")
        print("   2. 친구 목록에서 UUID 확인")
        print("   3. UUID를 KAKAO_OPENCHAT_ID로 사용 가능")
        
        print("\n💡 **권한 설정 확인사항**")
        print("   - 카카오 개발자 콘솔에서 다음 권한 활성화:")
        print("     ✓ talk_message (메시지 전송)")
        print("     ✓ friends (친구 목록 조회)")
        print("     ✓ profile_image (프로필 조회)")
        
        print("\n🔗 **유용한 링크**")
        print("   - 카카오 개발자 콘솔: https://developers.kakao.com/")
        print("   - API 문서: https://developers.kakao.com/docs/latest/ko/message/")

def main():
    """메인 함수"""
    print("🔍 카카오톡 오픈채팅방 ID 및 사용자 ID 확인 도구")
    print("="*60)
    
    finder = KakaoIDFinder()
    
    if not finder.auth_token:
        return
    
    print("\n📋 실행할 작업을 선택하세요:")
    print("1. 사용자 정보 조회 (봇 사용자 ID 확인)")
    print("2. 친구 목록 조회")
    print("3. 테스트 메시지 전송 (나에게 보내기)")
    print("4. 앱 정보 조회")
    print("5. 모든 정보 조회")
    print("6. 설정 가이드 보기")
    
    choice = input("\n선택 (1-6): ").strip()
    
    if choice == "1":
        user_id = finder.get_user_info()
        if user_id:
            print(f"\n💾 .env 파일에 추가할 내용:")
            print(f"KAKAO_BOT_USER_ID={user_id}")
            
    elif choice == "2":
        friends = finder.get_friends_list()
        if friends:
            print(f"\n💾 친구 UUID 중 하나를 KAKAO_OPENCHAT_ID로 사용할 수 있습니다.")
            
    elif choice == "3":
        success = finder.test_message_send()
        if success:
            print("\n✅ API 연결이 정상적으로 작동합니다!")
            
    elif choice == "4":
        finder.get_app_info()
        
    elif choice == "5":
        user_id = finder.get_user_info()
        friends = finder.get_friends_list()
        finder.test_message_send()
        finder.get_app_info()
        
        print("\n" + "="*60)
        print("📋 종합 결과")
        print("="*60)
        
        if user_id:
            print(f"🤖 봇 사용자 ID: {user_id}")
            
        if friends:
            print(f"👥 친구 수: {len(friends)}명")
            print("💡 친구 UUID 중 하나를 오픈채팅방 ID로 사용 가능")
            
        print(f"\n💾 .env 파일 업데이트:")
        if user_id:
            print(f"KAKAO_BOT_USER_ID={user_id}")
        print("KAKAO_OPENCHAT_ID=선택한_친구의_UUID")
        
    elif choice == "6":
        finder.show_setup_guide()
        
    else:
        print("❌ 잘못된 선택입니다.")

if __name__ == "__main__":
    main() 