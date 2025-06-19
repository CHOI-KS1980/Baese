#!/usr/bin/env python3
"""
카카오톡 오픈채팅방 ID 추출 도구
다양한 방법으로 오픈채팅방 ID를 확인할 수 있습니다.
"""

import re
import requests
import json
import webbrowser
from urllib.parse import urlparse, parse_qs

class OpenChatIDExtractor:
    """오픈채팅방 ID 추출기"""
    
    def __init__(self):
        print("🔍 카카오톡 오픈채팅방 ID 추출 도구")
        print("="*50)
    
    def method1_url_analysis(self):
        """방법 1: URL에서 직접 추출"""
        print("\n1️⃣ URL에서 오픈채팅방 ID 추출")
        print("-" * 30)
        
        print("📋 진행 방법:")
        print("1. 카카오톡에서 오픈채팅방 입장")
        print("2. 채팅방 설정(⚙️) → 채팅방 관리 → 채팅방 정보")
        print("3. '채팅방 링크 복사' 또는 URL 확인")
        
        url = input("\n🔗 오픈채팅방 URL을 입력하세요: ").strip()
        
        if not url:
            print("❌ URL이 입력되지 않았습니다.")
            return None
        
        # 다양한 카카오톡 오픈채팅 URL 패턴 분석
        patterns = [
            r'open\.kakao\.com/o/([a-zA-Z0-9]+)',
            r'openchat\.kakao\.com/o/([a-zA-Z0-9]+)',
            r'open-talk\.kakao\.com/o/([a-zA-Z0-9]+)',
            r'/o/([a-zA-Z0-9]+)',
            r'chatId=([a-zA-Z0-9]+)',
            r'roomId=([a-zA-Z0-9]+)'
        ]
        
        openchat_id = None
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                openchat_id = match.group(1)
                break
        
        if openchat_id:
            print(f"✅ 오픈채팅방 ID 추출 성공: {openchat_id}")
            print(f"💾 .env 파일에 추가할 내용:")
            print(f"KAKAO_OPENCHAT_ID={openchat_id}")
            return openchat_id
        else:
            print("❌ URL에서 오픈채팅방 ID를 찾을 수 없습니다.")
            print("\n💡 지원하는 URL 형식:")
            print("   - https://open.kakao.com/o/gABCDEF123")
            print("   - https://openchat.kakao.com/o/gABCDEF123")
            print("   - https://open-talk.kakao.com/o/gABCDEF123")
            return None
    
    def method2_manual_guide(self):
        """방법 2: 수동 확인 가이드"""
        print("\n2️⃣ 카카오톡 앱에서 수동 확인")
        print("-" * 30)
        
        print("📱 **모바일 카카오톡:**")
        print("1. 오픈채팅방 입장")
        print("2. 채팅방 이름 옆 '≡' 메뉴 터치")
        print("3. '채팅방 설정' 선택")
        print("4. '채팅방 관리' → '채팅방 정보'")
        print("5. URL에서 /o/ 뒤의 문자열이 채팅방 ID")
        
        print("\n💻 **PC 카카오톡:**")
        print("1. 오픈채팅방 입장")
        print("2. 우측 상단 설정(⚙️) 버튼")
        print("3. '채팅방 정보' 또는 '채팅방 관리'")
        print("4. '링크 복사' 버튼으로 URL 복사")
        print("5. URL 분석하여 ID 추출")
        
        print("\n🌐 **웹 카카오톡:**")
        print("1. web.kakao.com 접속")
        print("2. 오픈채팅방 입장")
        print("3. 브라우저 주소창 URL 확인")
        print("4. URL의 파라미터에서 roomId 또는 chatId 확인")
        
        manual_id = input("\n🔑 확인한 오픈채팅방 ID를 입력하세요: ").strip()
        
        if manual_id:
            print(f"✅ 입력된 오픈채팅방 ID: {manual_id}")
            print(f"💾 .env 파일에 추가할 내용:")
            print(f"KAKAO_OPENCHAT_ID={manual_id}")
            return manual_id
        else:
            print("❌ ID가 입력되지 않았습니다.")
            return None
    
    def method3_developer_tools(self):
        """방법 3: 브라우저 개발자 도구 사용"""
        print("\n3️⃣ 브라우저 개발자 도구로 ID 추출")
        print("-" * 30)
        
        print("🔧 **진행 단계:**")
        print("1. 브라우저에서 https://web.kakao.com 접속")
        print("2. 카카오계정 로그인")
        print("3. 원하는 오픈채팅방 입장")
        print("4. F12 키로 개발자 도구 열기")
        print("5. Network 탭으로 이동")
        print("6. 메시지 하나 전송")
        print("7. 요청 목록에서 'send' 또는 'message' 관련 요청 찾기")
        print("8. 요청 헤더/바디에서 roomId, chatId 등 확인")
        
        print("\n🔍 **찾아야 할 파라미터:**")
        print("   - roomId: 채팅방 고유 ID")
        print("   - chatId: 채팅방 식별자")
        print("   - channelId: 채널 식별자")
        print("   - uuid: 고유 식별자")
        
        print("\n💡 **팁:**")
        print("   - JSON 형태의 요청에서 주로 발견됩니다")
        print("   - 숫자+문자 조합의 긴 문자열입니다")
        print("   - 보통 20-30자 길이입니다")
        
        dev_id = input("\n🔑 개발자 도구에서 찾은 ID를 입력하세요: ").strip()
        
        if dev_id:
            print(f"✅ 입력된 ID: {dev_id}")
            print(f"💾 .env 파일에 추가할 내용:")
            print(f"KAKAO_OPENCHAT_ID={dev_id}")
            return dev_id
        else:
            print("❌ ID가 입력되지 않았습니다.")
            return None
    
    def method4_qr_code(self):
        """방법 4: QR 코드에서 추출"""
        print("\n4️⃣ QR 코드에서 ID 추출")
        print("-" * 30)
        
        print("📱 **QR 코드 생성:**")
        print("1. 카카오톡 오픈채팅방에서 'QR 코드' 생성")
        print("2. QR 코드를 다른 기기로 스캔하거나 이미지로 저장")
        print("3. QR 코드 스캐너로 URL 추출")
        print("4. URL에서 오픈채팅방 ID 확인")
        
        qr_url = input("\n🔗 QR 코드에서 추출한 URL을 입력하세요: ").strip()
        
        if qr_url:
            # URL 패턴 분석 (method1과 동일)
            patterns = [
                r'open\.kakao\.com/o/([a-zA-Z0-9]+)',
                r'openchat\.kakao\.com/o/([a-zA-Z0-9]+)',
                r'/o/([a-zA-Z0-9]+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, qr_url)
                if match:
                    qr_id = match.group(1)
                    print(f"✅ QR 코드에서 ID 추출 성공: {qr_id}")
                    print(f"💾 .env 파일에 추가할 내용:")
                    print(f"KAKAO_OPENCHAT_ID={qr_id}")
                    return qr_id
            
            print("❌ QR 코드 URL에서 ID를 찾을 수 없습니다.")
        else:
            print("❌ URL이 입력되지 않았습니다.")
        
        return None
    
    def method5_invitation_link(self):
        """방법 5: 초대 링크에서 추출"""
        print("\n5️⃣ 초대 링크에서 ID 추출")
        print("-" * 30)
        
        print("📨 **초대 링크 받기:**")
        print("1. 오픈채팅방에서 '초대하기' 선택")
        print("2. '링크 공유'로 초대 링크 생성")
        print("3. 생성된 링크에서 ID 추출")
        
        invite_url = input("\n🔗 초대 링크를 입력하세요: ").strip()
        
        if invite_url:
            # 초대 링크 패턴 분석
            patterns = [
                r'kakaotalk://join/([a-zA-Z0-9]+)',
                r'invite\.kakao\.com/([a-zA-Z0-9]+)',
                r'join\.kakao\.com/([a-zA-Z0-9]+)',
                r'/join/([a-zA-Z0-9]+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, invite_url)
                if match:
                    invite_id = match.group(1)
                    print(f"✅ 초대 링크에서 ID 추출 성공: {invite_id}")
                    print(f"💾 .env 파일에 추가할 내용:")
                    print(f"KAKAO_OPENCHAT_ID={invite_id}")
                    return invite_id
            
            print("❌ 초대 링크에서 ID를 찾을 수 없습니다.")
        else:
            print("❌ 링크가 입력되지 않았습니다.")
        
        return None
    
    def update_env_file(self, openchat_id):
        """환경변수 파일 업데이트"""
        if not openchat_id:
            return False
        
        try:
            # .env 파일 읽기
            with open('.env', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # KAKAO_OPENCHAT_ID 업데이트
            if 'KAKAO_OPENCHAT_ID=' in content:
                content = re.sub(
                    r'KAKAO_OPENCHAT_ID=.*',
                    f'KAKAO_OPENCHAT_ID={openchat_id}',
                    content
                )
            else:
                content += f'\nKAKAO_OPENCHAT_ID={openchat_id}\n'
            
            # 파일 저장
            with open('.env', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"\n✅ .env 파일이 업데이트되었습니다!")
            print(f"🔑 오픈채팅방 ID: {openchat_id}")
            return True
            
        except Exception as e:
            print(f"❌ .env 파일 업데이트 실패: {e}")
            print(f"💾 수동으로 추가하세요: KAKAO_OPENCHAT_ID={openchat_id}")
            return False
    
    def show_common_formats(self):
        """일반적인 ID 형식 안내"""
        print("\n💡 **일반적인 오픈채팅방 ID 형식:**")
        print("   - 길이: 보통 8-15자")
        print("   - 구성: 영문자(대소문자) + 숫자")
        print("   - 예시: gABCDEF123, xYz789AbC, m1N2o3P4q5")
        
        print("\n🔍 **ID를 찾을 수 있는 곳:**")
        print("   ✅ 채팅방 공유 링크")
        print("   ✅ QR 코드 URL")
        print("   ✅ 초대 링크")
        print("   ✅ 브라우저 개발자 도구")
        print("   ✅ 카카오톡 앱 설정")

def main():
    """메인 함수"""
    extractor = OpenChatIDExtractor()
    
    print("\n📋 오픈채팅방 ID 추출 방법을 선택하세요:")
    print("1. URL에서 직접 추출 (가장 쉬움)")
    print("2. 카카오톡 앱에서 수동 확인")
    print("3. 브라우저 개발자 도구 사용")
    print("4. QR 코드에서 추출")
    print("5. 초대 링크에서 추출")
    print("6. 일반적인 ID 형식 안내")
    
    choice = input("\n선택 (1-6): ").strip()
    
    openchat_id = None
    
    if choice == "1":
        openchat_id = extractor.method1_url_analysis()
    elif choice == "2":
        openchat_id = extractor.method2_manual_guide()
    elif choice == "3":
        openchat_id = extractor.method3_developer_tools()
    elif choice == "4":
        openchat_id = extractor.method4_qr_code()
    elif choice == "5":
        openchat_id = extractor.method5_invitation_link()
    elif choice == "6":
        extractor.show_common_formats()
        return
    else:
        print("❌ 잘못된 선택입니다.")
        return
    
    # .env 파일 업데이트 제안
    if openchat_id:
        update_choice = input("\n🔧 .env 파일을 자동으로 업데이트하시겠습니까? (y/n): ").strip().lower()
        if update_choice in ['y', 'yes', '예', 'ㅇ']:
            extractor.update_env_file(openchat_id)
        else:
            print(f"\n💾 수동으로 .env 파일에 추가하세요:")
            print(f"KAKAO_OPENCHAT_ID={openchat_id}")
    
    print("\n🎉 완료! 이제 카카오톡 자동 전송을 시작할 수 있습니다.")
    print("📝 다음 명령어로 테스트해보세요:")
    print("   python3 kakao_scheduled_sender.py")

if __name__ == "__main__":
    main() 