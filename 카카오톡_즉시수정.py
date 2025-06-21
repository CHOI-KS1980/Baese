#!/usr/bin/env python3
"""
🔧 카카오톡 개발자센터 설정 문제 해결 가이드
즉시 수정하여 실제 전송 가능하게 만들기
"""

print("🔧 카카오톡 개발자센터 설정 문제 해결 가이드")
print("=" * 60)

print("\n🚨 현재 오류:")
print("   [배민 미션정보 발송 자동화] App disabled [talk_message] scopes")
print("   ❌ 'talk_message' 권한이 비활성화됨")

print("\n✅ 즉시 해결 방법:")
print("=" * 60)

print("\n1️⃣ 카카오 개발자센터 접속:")
print("   🌐 https://developers.kakao.com")
print("   🔑 로그인 → 내 애플리케이션")

print("\n2️⃣ '배민 미션정보 발송 자동화' 앱 선택:")
print("   📱 앱 목록에서 선택")

print("\n3️⃣ 카카오톡 메시지 권한 활성화:")
print("   📋 좌측 메뉴: '제품 설정' > '카카오 로그인'")
print("   ⚙️ '동의항목' 탭 클릭")
print("   ✅ '카카오톡 메시지 전송' 권한 체크")
print("   💾 저장 버튼 클릭")

print("\n4️⃣ 플랫폼 설정 확인:")
print("   🌐 좌측 메뉴: '앱 설정' > '플랫폼'")
print("   🔗 Web 플랫폼: https://localhost 등록 확인")

print("\n5️⃣ 카카오톡 채널 권한 추가:")
print("   📋 좌측 메뉴: '제품 설정' > '카카오톡 채널'")
print("   ✅ '카카오톡 채널 프로필 조회' 활성화")
print("   ✅ '카카오톡 채널 대화' 활성화")

print("\n📱 완료 후 즉시 테스트:")
print("=" * 40)

import os
import requests
import json

def test_kakao_access():
    """설정 완료 후 즉시 테스트"""
    try:
        # 토큰 파일에서 읽기
        with open('kakao_access_token.txt', 'r') as f:
            access_token = f.read().strip()
        
        if not access_token:
            print("❌ 토큰 파일이 비어있습니다.")
            return False
        
        print(f"\n🔑 토큰 확인: {access_token[:10]}...")
        
        # 카카오 API 테스트
        url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        template = {
            "object_type": "text",
            "text": """🎉 심플 배민 플러스 카카오톡 연동 성공!
            
✅ 개발자센터 설정 완료
✅ 실제 카카오톡 전송 가능
✅ 자동화 시스템 준비 완료

💪 이제 24시간 자동 전송이 시작됩니다!""",
            "link": {
                "web_url": "https://github.com/CHOI-KS1980/baemin",
                "mobile_web_url": "https://github.com/CHOI-KS1980/baemin"
            }
        }
        
        data = {
            "template_object": json.dumps(template)
        }
        
        print("\n📤 카카오톡 전송 테스트 중...")
        response = requests.post(url, headers=headers, data=data, timeout=10)
        
        if response.status_code == 200:
            print("🎉 카카오톡 전송 성공!")
            print("📱 휴대폰에서 카카오톡 메시지를 확인하세요!")
            return True
        else:
            print(f"❌ 전송 실패: {response.status_code}")
            print(f"📝 응답: {response.text}")
            
            if "disabled" in response.text:
                print("\n🔧 아직 권한 설정이 완료되지 않았습니다.")
                print("💡 위의 1-5단계를 다시 확인해주세요.")
            return False
            
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🔄 설정 완료 후 이 스크립트를 다시 실행하세요!")
    print("   python3 카카오톡_즉시수정.py")
    print("=" * 60)
    
    # 자동 테스트 실행
    print("\n⏳ 3초 후 자동 테스트 시작...")
    import time
    time.sleep(3)
    
    success = test_kakao_access()
    
    if success:
        print("\n🎊 축하합니다! 모든 설정이 완료되었습니다!")
        print("🚀 이제 GitHub Actions에서 자동 전송이 시작됩니다!")
    else:
        print("\n💡 설정을 완료한 후 다시 실행해주세요.") 