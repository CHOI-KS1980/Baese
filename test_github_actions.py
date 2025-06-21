#!/usr/bin/env python3
"""
🧪 GitHub Actions 카카오톡 자동화 테스트

설정이 올바르게 되었는지 로컬에서 테스트합니다.
"""

import os
import sys
import requests
import json
from datetime import datetime

def test_kakao_token():
    """카카오 토큰 테스트"""
    print("🔑 카카오 토큰 테스트...")
    
    # 환경변수에서 토큰 로드
    access_token = os.getenv('KAKAO_ACCESS_TOKEN', '')
    
    if not access_token:
        print("❌ KAKAO_ACCESS_TOKEN 환경변수가 설정되지 않았습니다.")
        print("💡 해결 방법:")
        print("   export KAKAO_ACCESS_TOKEN='your_token_here'")
        print("   또는 .env 파일에 설정")
        return False
    
    print(f"✅ 토큰 발견: {access_token[:15]}...")
    
    # 토큰 유효성 확인
    try:
        url = 'https://kapi.kakao.com/v2/user/me'
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            nickname = user_data.get('properties', {}).get('nickname', '사용자')
            print(f"✅ 토큰 유효 확인 - 사용자: {nickname}")
            return True
        elif response.status_code == 401:
            print("❌ 토큰이 만료되었거나 무효합니다.")
            print("💡 새 토큰을 발급받으세요: python3 카카오_토큰_생성기.py")
            return False
        else:
            print(f"⚠️ 토큰 확인 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 토큰 테스트 오류: {e}")
        return False

def test_kakao_message():
    """카카오톡 메시지 전송 테스트"""
    print("\n📱 카카오톡 메시지 전송 테스트...")
    
    access_token = os.getenv('KAKAO_ACCESS_TOKEN', '')
    if not access_token:
        print("❌ 토큰이 설정되지 않아 테스트를 건너뜁니다.")
        return False
    
    try:
        url = 'https://kapi.kakao.com/v2/api/talk/memo/default/send'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        # 테스트 메시지
        test_message = f"""🧪 GitHub Actions 테스트 메시지

📅 {datetime.now().strftime('%Y년 %m월 %d일 %H시 %M분')}

✅ 카카오톡 "나에게 보내기" 연결 성공!
🤖 GitHub Actions 자동화 준비 완료

━━━━━━━━━━━━━━━━━━━━━━━━
🚀 이제 컴퓨터가 꺼져있어도 
   24시간 자동으로 메시지가 전송됩니다!

🔧 설정 완료 시간: {datetime.now().strftime('%H:%M:%S')}
💻 테스트 환경: Local"""
        
        template = {
            "object_type": "text",
            "text": test_message,
            "link": {
                "web_url": "https://jangboo.grider.ai/",
                "mobile_web_url": "https://jangboo.grider.ai/"
            }
        }
        
        data = {'template_object': json.dumps(template)}
        
        response = requests.post(url, headers=headers, data=data, timeout=30)
        
        if response.status_code == 200:
            print("✅ 테스트 메시지 전송 성공!")
            print("📱 카카오톡에서 메시지를 확인하세요.")
            return True
        else:
            print(f"❌ 메시지 전송 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 메시지 전송 오류: {e}")
        return False

def test_weather_api():
    """날씨 API 테스트 (선택사항)"""
    print("\n🌤️ 날씨 API 테스트...")
    
    weather_key = os.getenv('OPENWEATHER_API_KEY', '')
    if not weather_key:
        print("⚠️ OPENWEATHER_API_KEY가 설정되지 않았습니다. (선택사항)")
        return True
    
    try:
        url = 'http://api.openweathermap.org/data/2.5/weather'
        params = {
            'lat': 37.3236,  # 안산시
            'lon': 126.8219,
            'appid': weather_key,
            'units': 'metric',
            'lang': 'kr'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            temp = round(data['main']['temp'])
            desc = data['weather'][0]['description']
            print(f"✅ 날씨 API 연결 성공 - 안산시: {temp}°C ({desc})")
            return True
        else:
            print(f"❌ 날씨 API 오류: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 날씨 API 테스트 오류: {e}")
        return False

def test_github_actions_simulation():
    """GitHub Actions 환경 시뮬레이션"""
    print("\n🤖 GitHub Actions 환경 시뮬레이션...")
    
    try:
        # GitHub Actions 스크립트 실행 테스트
        from github_actions_memo_automation import GitHubActionsKakaoSender
        
        print("📦 GitHub Actions 스크립트 로드 성공")
        
        # 인스턴스 생성 테스트
        try:
            sender = GitHubActionsKakaoSender()
            print("✅ GitHubActionsKakaoSender 초기화 성공")
            
            # 메시지 생성 테스트
            message = sender.create_report_message("test")
            print("✅ 리포트 메시지 생성 성공")
            print(f"📝 메시지 길이: {len(message)} 글자")
            
            return True
            
        except Exception as e:
            print(f"❌ GitHub Actions 스크립트 오류: {e}")
            return False
            
    except ImportError:
        print("❌ github_actions_memo_automation.py 파일을 찾을 수 없습니다.")
        return False

def check_required_files():
    """필수 파일 존재 확인"""
    print("\n📁 필수 파일 확인...")
    
    required_files = [
        'github_actions_memo_automation.py',
        '.github/workflows/kakao-automation.yml',
        '카카오_토큰_생성기.py'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - 파일이 없습니다!")
            all_exist = False
    
    return all_exist

def load_environment():
    """환경변수 로드"""
    print("🔧 환경변수 로드...")
    
    # .env 파일이 있으면 로드
    if os.path.exists('.env'):
        try:
            with open('.env', 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            print("✅ .env 파일 로드 완료")
        except Exception as e:
            print(f"⚠️ .env 파일 로드 오류: {e}")
    else:
        print("⚠️ .env 파일이 없습니다. 환경변수를 직접 설정하세요.")

def main():
    """메인 테스트 함수"""
    print("🧪 GitHub Actions 카카오톡 자동화 테스트")
    print("=" * 50)
    
    # 환경변수 로드
    load_environment()
    
    # 테스트 결과 저장
    test_results = {}
    
    # 1. 필수 파일 확인
    test_results['files'] = check_required_files()
    
    # 2. 카카오 토큰 테스트
    test_results['token'] = test_kakao_token()
    
    # 3. 메시지 전송 테스트
    if test_results['token']:
        test_results['message'] = test_kakao_message()
    else:
        test_results['message'] = False
        print("⚠️ 토큰 오류로 메시지 테스트를 건너뜁니다.")
    
    # 4. 날씨 API 테스트
    test_results['weather'] = test_weather_api()
    
    # 5. GitHub Actions 시뮬레이션
    test_results['github_actions'] = test_github_actions_simulation()
    
    # 결과 요약
    print("\n" + "="*50)
    print("📊 테스트 결과 요약")
    print("="*50)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{test_name.ljust(15)}: {status}")
    
    print(f"\n🎯 결과: {passed}/{total} 테스트 통과")
    
    if passed == total:
        print("\n🎉 모든 테스트 통과! GitHub Actions 설정이 완료되었습니다.")
        print("\n📋 다음 단계:")
        print("1. GitHub에 코드 푸시")
        print("2. GitHub Secrets 설정")
        print("3. Actions 탭에서 워크플로우 활성화")
        print("4. 수동 테스트 실행")
        
        return True
    else:
        print("\n⚠️ 일부 테스트가 실패했습니다.")
        print("실패한 항목들을 확인하고 수정한 후 다시 테스트하세요.")
        
        if not test_results['token']:
            print("\n🔑 토큰 문제 해결:")
            print("   python3 카카오_토큰_생성기.py")
        
        if not test_results['files']:
            print("\n📁 파일 문제 해결:")
            print("   누락된 파일들을 생성하거나 복사하세요.")
        
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 테스트가 중단되었습니다.")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        sys.exit(1) 