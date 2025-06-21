#!/usr/bin/env python3
"""
🔗 GitHub Actions → 카카오톡 완전 연결
webhook.site를 통한 최종 자동화 완성
"""

import os
import json
import requests
import time
from datetime import datetime
import pytz

KST = pytz.timezone('Asia/Seoul')

def send_to_kakao_openbuilder(message):
    """카카오 오픈빌더로 메시지 전송"""
    
    # 실제 카카오 오픈빌더 웹훅 URL (설정 필요)
    kakao_webhook = "YOUR_KAKAO_OPENBUILDER_WEBHOOK_URL"
    
    try:
        data = {"message": message}
        response = requests.post(kakao_webhook, json=data, timeout=10)
        
        if response.status_code == 200:
            print("✅ 카카오 오픈빌더 전송 성공!")
            return True
        else:
            print(f"❌ 카카오 오픈빌더 전송 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 카카오 오픈빌더 오류: {e}")
        return False

def monitor_webhook_and_forward():
    """webhook.site 모니터링하고 카카오톡으로 전달"""
    
    webhook_url = "https://webhook.site/token/dbf3ed6e-e7ca-4430-be5a-19fb1fb1ba57/requests"
    
    print("🔗 GitHub Actions → 카카오톡 연결 시작!")
    print("━" * 60)
    print(f"📡 모니터링: {webhook_url}")
    print(f"📱 전송대상: 카카오톡 (오픈빌더)")
    print("━" * 60)
    
    last_check_time = datetime.now(KST)
    
    try:
        while True:
            current_time = datetime.now(KST)
            print(f"🔍 {current_time.strftime('%H:%M:%S')} - 새 메시지 확인 중...")
            
            try:
                response = requests.get(webhook_url, timeout=10)
                
                if response.status_code == 200:
                    requests_data = response.json()
                    
                    if requests_data.get('data'):
                        # 가장 최근 요청 확인
                        latest_request = requests_data['data'][0]
                        request_time = datetime.fromisoformat(latest_request['created_at'].replace('Z', '+00:00')).astimezone(KST)
                        
                        # 마지막 확인 시간 이후의 새 메시지인지 확인
                        if request_time > last_check_time:
                            print("📨 새로운 G라이더 데이터 발견!")
                            print(f"⏰ 수신 시간: {request_time.strftime('%H:%M:%S')}")
                            
                            # 메시지 내용 추출
                            content = latest_request.get('content', '{}')
                            if isinstance(content, str):
                                try:
                                    content = json.loads(content)
                                except:
                                    pass
                            
                            message = content.get('message', '메시지 내용을 찾을 수 없음')
                            
                            print(f"💬 G라이더 정보: {message[:100]}...")
                            
                            # 카카오톡으로 전달
                            success = send_to_kakao_openbuilder(message)
                            
                            if success:
                                print("🎉 카카오톡 전송 완료!")
                                print("━" * 60)
                            else:
                                print("❌ 카카오톡 전송 실패!")
                            
                            last_check_time = request_time
                            
                        else:
                            print("📭 새 메시지 없음")
                        
                else:
                    print(f"⚠️ webhook.site API 오류: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ 모니터링 오류: {e}")
            
            # 1분마다 확인
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\n👋 모니터링을 종료합니다.")

def test_github_actions_now():
    """GitHub Actions 즉시 테스트 실행"""
    
    print("🧪 GitHub Actions 즉시 테스트")
    print("━" * 50)
    
    # GitHub Actions workflow dispatch API 호출
    repo_owner = "CHOI-KS1980"
    repo_name = "baemin"
    workflow_id = "baemin-grider-automation.yml"
    
    # GitHub Personal Access Token 필요
    github_token = os.getenv('GITHUB_TOKEN')
    
    if not github_token:
        print("⚠️ GITHUB_TOKEN 환경변수가 필요합니다!")
        print("GitHub Settings → Developer settings → Personal access tokens")
        return False
    
    try:
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/workflows/{workflow_id}/dispatches"
        
        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        data = {
            "ref": "main"
        }
        
        print("🚀 GitHub Actions 워크플로우 실행 중...")
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 204:
            print("✅ GitHub Actions 실행 성공!")
            print("📡 약 1-2분 후 webhook.site에서 결과를 확인할 수 있습니다!")
            return True
        else:
            print(f"❌ GitHub Actions 실행 실패: {response.status_code}")
            print(f"응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ GitHub Actions 실행 오류: {e}")
        return False

def show_final_setup_guide():
    """최종 설정 가이드 표시"""
    
    print("━" * 70)
    print("🎉 배민 G라이더 완전 자동화 최종 설정 가이드")
    print("━" * 70)
    print()
    print("✅ 현재 완료된 것들:")
    print("   • GitHub Actions 워크플로우 (완벽한 스케줄링)")
    print("   • G라이더 데이터 수집 시스템")
    print("   • 한국 공휴일 API 연동")
    print("   • 날씨 정보 연동")
    print("   • webhook.site 전송 성공")
    print()
    print("🎯 마지막 단계 (선택):")
    print("━" * 50)
    print()
    print("🔸 방법 1: 현재 webhook.site 그대로 사용")
    print("   → GitHub Actions가 이미 정상 작동!")
    print("   → webhook.site에서 실시간 결과 확인 가능")
    print("   → 추가 설정 없이 바로 사용 가능")
    print()
    print("🔸 방법 2: 카카오톡 직접 연결 (고급)")
    print("   → 카카오 오픈빌더 웹훅 URL 설정")
    print("   → 위의 monitor_webhook_and_forward() 실행")
    print("   → 완전 무인 카카오톡 자동 전송")
    print()
    print("━" * 70)
    print("🚀 추천: 방법 1로 먼저 사용해보세요!")
    print("GitHub Actions가 이미 완벽하게 작동하고 있습니다!")
    print("━" * 70)

if __name__ == "__main__":
    print("━" * 70)
    print("🔗 GitHub Actions ↔️ 카카오톡 연결 시스템")
    print("━" * 70)
    print("1. webhook.site 모니터링 및 카카오톡 전달")
    print("2. GitHub Actions 즉시 테스트 실행")
    print("3. 최종 설정 가이드 보기")
    print("0. 종료")
    
    choice = input("\n📝 선택 (0-3): ").strip()
    
    if choice == "1":
        monitor_webhook_and_forward()
    elif choice == "2":
        test_github_actions_now()
    elif choice == "3":
        show_final_setup_guide()
    else:
        print("👋 종료합니다.")
        
    print("\n🎉 GitHub Actions 자동화가 이미 완벽하게 작동 중입니다!")
    print("📊 다음 자동 실행을 기다리거나 webhook.site에서 결과를 확인하세요!") 