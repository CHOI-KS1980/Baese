REST API 키 복사 (KAKAO_ACCESS_TOKEN)#!/usr/bin/env python3
"""
🍕 배민 G라이더 완전 자동화 시스템 빠른 설정 도우미

GitHub Secrets 설정, API 키 발급, 테스트까지 단계별 안내
"""

import os
import sys
import json
import webbrowser
from datetime import datetime
import requests

class AutomationSetupHelper:
    def __init__(self):
        self.secrets = {}
        self.setup_progress = {
            'github_secrets': False,
            'kakao_openbuilder': False,
            'holiday_api': False,
            'weather_api': False,
            'test_completed': False
        }
        
    def print_header(self):
        print("━" * 60)
        print("🍕 배민 G라이더 완전 자동화 시스템 설정 도우미")
        print("━" * 60)
        print("📝 이 도우미는 자동화 설정을 단계별로 안내합니다.")
        print("🔧 각 단계를 차례대로 완료하면 완전 자동화가 구현됩니다!")
        print("━" * 60)
        print()
        
    def show_progress(self):
        print("\n📊 현재 설정 진행상황:")
        print("━" * 40)
        
        for step, completed in self.setup_progress.items():
            status = "✅" if completed else "❌"
            step_name = {
                'github_secrets': '1. GitHub Secrets 설정',
                'kakao_openbuilder': '2. 카카오 오픈빌더 설정',
                'holiday_api': '3. 한국천문연구원 API',
                'weather_api': '4. 날씨 API (선택)',
                'test_completed': '5. 테스트 완료'
            }[step]
            
            print(f"{status} {step_name}")
        
        completed_count = sum(self.setup_progress.values())
        print(f"\n진행률: {completed_count}/5 단계 완료 ({completed_count*20}%)")
        print("━" * 40)
        
    def step1_github_secrets(self):
        print("\n🚀 1단계: GitHub Secrets 설정")
        print("━" * 50)
        print("GitHub 저장소에 API 키들을 안전하게 저장해야 합니다.")
        print()
        
        print("📍 설정 방법:")
        print("1. GitHub.com → baemin 저장소 접속")
        print("2. Settings → Secrets and variables → Actions")
        print("3. 'New repository secret' 클릭")
        print()
        
        secrets_needed = [
            ("KAKAO_ACCESS_TOKEN", "카카오 오픈빌더 액세스 토큰", "필수"),
            ("KAKAO_OPENCHAT_ID", "카카오톡 오픈채팅방 ID", "필수"), 
            ("KAKAO_OPENBUILDER_WEBHOOK", "오픈빌더 웹훅 URL", "필수"),
            ("KOREA_HOLIDAY_API_KEY", "한국천문연구원 공휴일 API 키", "필수"),
            ("WEBHOOK_URL", "메인 웹훅 URL", "필수"),
            ("FALLBACK_WEBHOOK_URL", "백업 웹훅 URL", "권장"),
            ("WEATHER_API_KEY", "날씨 API 키", "선택")
        ]
        
        print("🔑 설정해야 할 Secrets:")
        for name, desc, importance in secrets_needed:
            importance_icon = "🔴" if importance == "필수" else "🟡" if importance == "권장" else "🔵"
            print(f"   {importance_icon} {name}")
            print(f"      └─ {desc} ({importance})")
        
        print("\n🌐 GitHub Secrets 설정 페이지를 열까요?")
        if self.ask_yes_no("GitHub 페이지 열기"):
            github_url = "https://github.com/CHOI-KS1980/baemin/settings/secrets/actions"
            webbrowser.open(github_url)
            print(f"🔗 브라우저에서 열었습니다: {github_url}")
        
        print("\n✅ 모든 필수 Secrets를 설정하셨나요?")
        if self.ask_yes_no("설정 완료"):
            self.setup_progress['github_secrets'] = True
            print("🎉 1단계 완료!")
        else:
            print("⚠️  필수 Secrets를 모두 설정한 후 다시 시도하세요.")
            
    def step2_kakao_openbuilder(self):
        print("\n🤖 2단계: 카카오 i 오픈빌더 설정")
        print("━" * 50)
        print("카카오톡 챗봇을 만들어 메시지를 자동 전송합니다.")
        print()
        
        print("📍 설정 순서:")
        print("1. 카카오 i 오픈빌더 계정 생성")
        print("2. 새 챗봇 만들기")
        print("3. 스킬 서버 설정")
        print("4. 토큰 및 웹훅 URL 복사")
        print("5. 카카오톡 채널 연결")
        print()
        
        print("💡 챗봇 설정 정보:")
        print("   📛 챗봇 이름: 배민 G라이더 미션봇")
        print("   📝 설명: 배달의민족 G라이더 미션 현황 자동 알림 시스템")
        print("   📂 카테고리: 비즈니스/업무")
        print()
        
        print("🌐 카카오 i 오픈빌더 페이지를 열까요?")
        if self.ask_yes_no("카카오 i 오픈빌더 열기"):
            kakao_url = "https://i.kakao.com/"
            webbrowser.open(kakao_url)
            print(f"🔗 브라우저에서 열었습니다: {kakao_url}")
        
        print("\n📋 설정 완료 체크리스트:")
        checklist = [
            "챗봇 생성 완료",
            "스킬 서버 설정 완료", 
            "액세스 토큰 복사 완료",
            "웹훅 URL 복사 완료",
            "오픈채팅방 ID 확인 완료"
        ]
        
        for item in checklist:
            completed = self.ask_yes_no(f"✅ {item}")
            if not completed:
                print("⚠️  모든 설정을 완료한 후 다시 시도하세요.")
                return
        
        self.setup_progress['kakao_openbuilder'] = True
        print("🎉 2단계 완료!")
        
    def step3_holiday_api(self):
        print("\n🏛️ 3단계: 한국천문연구원 공휴일 API 설정")
        print("━" * 50)
        print("한국 공휴일을 정확하게 인식하기 위한 API 설정입니다.")
        print()
        
        print("📍 설정 순서:")
        print("1. 공공데이터포털 가입")
        print("2. '한국천문연구원 특일 정보' API 신청")
        print("3. API 키 발급 (승인 후)")
        print()
        
        print("🌐 공공데이터포털을 열까요?")
        if self.ask_yes_no("공공데이터포털 열기"):
            data_url = "https://data.go.kr/"
            webbrowser.open(data_url)
            print(f"🔗 브라우저에서 열었습니다: {data_url}")
            
        print("\n🔍 API 검색을 도와드릴까요?")
        if self.ask_yes_no("API 검색 페이지 열기"):
            search_url = "https://data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15012690"
            webbrowser.open(search_url)
            print(f"🔗 특일 정보 API 페이지를 열었습니다: {search_url}")
        
        print("\n📝 신청 사유 예시:")
        print("━" * 30)
        print("배달의민족 G라이더 미션 자동화 시스템에서")
        print("한국 공휴일 정보를 실시간으로 확인하여")
        print("평일/휴일별 차별화된 알림 서비스 제공")
        print("━" * 30)
        
        print("\n✅ API 신청 및 승인을 받으셨나요?")
        if self.ask_yes_no("API 키 발급 완료"):
            self.setup_progress['holiday_api'] = True
            print("🎉 3단계 완료!")
        else:
            print("⚠️  API 승인은 1-2일 소요될 수 있습니다.")
            print("💡 승인 후 다시 실행하여 진행하세요.")
            
    def step4_weather_api(self):
        print("\n🌤️ 4단계: 날씨 API 설정 (선택사항)")
        print("━" * 50)
        print("날씨 정보를 포함한 더 풍부한 메시지 제공을 위한 설정입니다.")
        print()
        
        skip = self.ask_yes_no("이 단계를 건너뛰시겠습니까?")
        if skip:
            print("🔵 4단계를 건너뛰었습니다.")
            return
            
        print("📍 설정 순서:")
        print("1. OpenWeatherMap 무료 계정 생성")
        print("2. API 키 발급")
        print("3. GitHub Secrets에 추가")
        print()
        
        print("🌐 OpenWeatherMap을 열까요?")
        if self.ask_yes_no("OpenWeatherMap 열기"):
            weather_url = "https://openweathermap.org/api"
            webbrowser.open(weather_url)
            print(f"🔗 브라우저에서 열었습니다: {weather_url}")
            
        print("\n✅ 날씨 API 키를 발급받으셨나요?")
        if self.ask_yes_no("API 키 발급 완료"):
            self.setup_progress['weather_api'] = True
            print("🎉 4단계 완료!")
        else:
            print("🔵 날씨 API는 선택사항이므로 나중에 설정 가능합니다.")
            
    def step5_test(self):
        print("\n✅ 5단계: 시스템 테스트")
        print("━" * 50)
        print("설정이 올바른지 테스트해봅시다!")
        print()
        
        print("📍 테스트 방법:")
        print("1. GitHub → baemin 저장소 → Actions 탭")
        print("2. '🍕 배민 G라이더 미션 자동화' 워크플로우 선택")
        print("3. 'Run workflow' → message_type: 'test' → 'Run workflow'")
        print("4. 실행 로그 확인")
        print("5. 카카오톡 메시지 수신 확인")
        print()
        
        print("🌐 GitHub Actions 페이지를 열까요?")
        if self.ask_yes_no("GitHub Actions 열기"):
            actions_url = "https://github.com/CHOI-KS1980/baemin/actions"
            webbrowser.open(actions_url)
            print(f"🔗 브라우저에서 열었습니다: {actions_url}")
            
        print("\n📱 테스트 결과:")
        success = self.ask_yes_no("테스트가 성공적으로 완료되었나요?")
        
        if success:
            message_received = self.ask_yes_no("카카오톡에 메시지가 정상 수신되었나요?")
            if message_received:
                self.setup_progress['test_completed'] = True
                print("🎉 모든 설정이 완료되었습니다!")
                self.show_final_success()
            else:
                print("⚠️  메시지 수신에 문제가 있습니다.")
                print("🔍 카카오 오픈빌더 설정을 다시 확인해주세요.")
        else:
            print("❌ 테스트 실패")
            print("🔍 GitHub Actions 로그를 확인하여 문제를 해결해주세요.")
            
    def show_final_success(self):
        print("\n" + "🎉" * 20)
        print("🍕 배민 G라이더 완전 자동화 시스템 구축 완료!")
        print("🎉" * 20)
        print()
        print("✅ 설정된 기능들:")
        print("   🤖 24시간 무인 자동화")
        print("   📅 한국 공휴일 자동 인식")
        print("   ⏰ 스마트 스케줄링 (피크/논피크)")
        print("   📱 카카오톡 실시간 알림")
        print("   🛡️ 이중화 안전 시스템")
        print()
        print("📊 실행 스케줄:")
        print("   🌅 09:00 - 하루 시작 인사")
        print("   🔄 09:30~23:30 - 30분 간격 정기 알림")
        print("   🔥 피크시간 - 15분 간격 강화 알림")
        print("   🌙 00:00 - 하루 마무리 인사")
        print()
        print("🚀 이제 완전 자동화된 G라이더 미션 관리를 즐기세요!")
        print("📞 문제 발생 시 GitHub Issues에 문의하세요.")
        print()
        
    def ask_yes_no(self, question):
        while True:
            answer = input(f"❓ {question} (y/n): ").lower().strip()
            if answer in ['y', 'yes', '예', 'ㅇ']:
                return True
            elif answer in ['n', 'no', '아니오', 'ㄴ']:
                return False
            else:
                print("❌ 'y' 또는 'n'으로 답해주세요.")
                
    def run_setup(self):
        self.print_header()
        
        while True:
            self.show_progress()
            
            print("\n🛠️ 다음 설정 단계를 선택하세요:")
            print("1. GitHub Secrets 설정")
            print("2. 카카오 i 오픈빌더 설정") 
            print("3. 한국천문연구원 API 설정")
            print("4. 날씨 API 설정 (선택)")
            print("5. 시스템 테스트")
            print("0. 종료")
            
            choice = input("\n📝 선택 (0-5): ").strip()
            
            if choice == '1':
                self.step1_github_secrets()
            elif choice == '2':
                self.step2_kakao_openbuilder()
            elif choice == '3':
                self.step3_holiday_api()
            elif choice == '4':
                self.step4_weather_api()
            elif choice == '5':
                self.step5_test()
            elif choice == '0':
                print("\n👋 설정 도우미를 종료합니다.")
                break
            else:
                print("❌ 올바른 번호를 선택해주세요.")
            
            print("\n" + "─" * 60)

if __name__ == "__main__":
    helper = AutomationSetupHelper()
    helper.run_setup() 