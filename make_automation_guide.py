#!/usr/bin/env python3
"""
Make.com을 이용한 G라이더 미션 완전 자동화 가이드
노코드로 시각적 워크플로우를 만들어 24/7 자동 전송
"""

import json
import requests
from datetime import datetime

class MakeAutomationGuide:
    """Make.com 자동화 설정 가이드"""
    
    def __init__(self):
        print("🎯 Make.com으로 G라이더 미션 완전 자동화")
        print("="*60)
        print("💡 드래그 앤 드롭으로 시각적 워크플로우 생성!")
        
    def show_make_overview(self):
        """Make.com 개요"""
        print("\n🌟 **Make.com이란?**")
        print("="*40)
        print("• 구 Integromat으로 유명한 자동화 플랫폼")
        print("• 시각적 워크플로우 생성")
        print("• 1,000+ 앱 연동 지원")
        print("• 복잡한 조건부 로직 구현")
        print("• 실시간 모니터링 및 로그")
        
        print("\n✅ **장점:**")
        print("   - 🎨 직관적인 시각적 인터페이스")
        print("   - 🔄 복잡한 자동화 시나리오 구현")
        print("   - 📊 실시간 실행 모니터링")
        print("   - 🛠️ 강력한 데이터 변환 기능")
        print("   - 🔗 웹훅, API 호출 지원")
        
        print("\n💰 **요금:**")
        print("   - 🆓 무료: 월 1,000 작업")
        print("   - 💎 Core: 월 $9 (10,000 작업)")
        print("   - ⭐ Pro: 월 $16 (40,000 작업)")
    
    def create_make_scenario_guide(self):
        """Make.com 시나리오 생성 가이드"""
        print("\n🎯 **Make.com 시나리오 구축 단계별 가이드**")
        print("="*55)
        
        print("\n📋 **1단계: 계정 생성 및 준비**")
        print("-" * 35)
        print("1. https://make.com 접속")
        print("2. 회원가입 (구글/이메일)")
        print("3. 무료 요금제로 시작")
        print("4. 대시보드 확인")
        
        print("\n🔧 **2단계: 새 시나리오 생성**")
        print("-" * 35)
        print("1. 'Create a new scenario' 클릭")
        print("2. 시나리오 이름: 'G라이더 미션 자동 전송'")
        print("3. 빈 시나리오에서 시작")
        
        print("\n⏰ **3단계: 시간 트리거 설정**")
        print("-" * 35)
        print("1. 첫 번째 모듈로 'Schedule' 선택")
        print("2. 'Every N hours/minutes' 설정")
        print("3. 실행 시간 설정:")
        print("   - 08:00 (아침 미션)")
        print("   - 12:00 (점심 미션)")
        print("   - 18:00 (저녁 미션)")
        print("   - 22:00 (밤 미션)")
        print("   - 10:30, 14:30, 20:30 (피크타임)")
        
        print("\n🌐 **4단계: 데이터 수집 (HTTP 모듈)**")
        print("-" * 35)
        print("1. 'HTTP' 모듈 추가")
        print("2. 'Make a request' 선택")
        print("3. URL: G라이더 미션 페이지")
        print("4. Method: GET")
        print("5. Headers 설정 (필요시)")
        
        print("\n🔧 **5단계: 데이터 변환 (Tools 모듈)**")
        print("-" * 35)
        print("1. 'Tools' > 'Set variable' 모듈 추가")
        print("2. HTML 파싱 로직 구현")
        print("3. 미션 데이터 추출")
        print("4. 메시지 포맷 생성")
        
        print("\n📤 **6단계: 메시지 전송 (Webhook)**")
        print("-" * 35)
        print("1. 'HTTP' 모듈 추가 (전송용)")
        print("2. 'Make a request' 선택")
        print("3. URL: 웹훅 엔드포인트")
        print("4. Method: POST")
        print("5. Body에 메시지 데이터 설정")
        
        print("\n✅ **7단계: 테스트 및 활성화**")
        print("-" * 35)
        print("1. 'Run once' 클릭하여 테스트")
        print("2. 각 모듈별 실행 결과 확인")
        print("3. 오류 수정")
        print("4. 'Scheduling' ON으로 활성화")
        
        # Make.com 시나리오 JSON 템플릿 생성
        self._create_make_scenario_template()
        
    def create_webhook_integration(self):
        """웹훅 연동 방법"""
        print("\n🔗 **웹훅 연동으로 오픈채팅방 전송**")
        print("="*45)
        
        print("\n💡 **개념:**")
        print("Make.com → 웹훅 → 카카오톡 전송 서비스")
        
        print("\n🔧 **웹훅 엔드포인트 옵션:**")
        print("1. 🆓 **Zapier Webhooks** (무료)")
        print("2. 🔥 **IFTTT Webhooks** (무료)")
        print("3. ☁️ **AWS API Gateway** (거의 무료)")
        print("4. 🚀 **Netlify Functions** (무료)")
        print("5. 📱 **Discord/Slack 웹훅** (무료)")
        
        # 웹훅 서버 생성
        self._create_webhook_server()
        
    def create_advanced_scenarios(self):
        """고급 시나리오들"""
        print("\n🚀 **고급 Make.com 시나리오들**")
        print("="*40)
        
        print("\n🎯 **시나리오 1: 조건부 전송**")
        print("• 미션 달성률이 50% 이하일 때만 알림")
        print("• 주말과 평일 다른 메시지")
        print("• 날씨에 따른 메시지 변경")
        
        print("\n📊 **시나리오 2: 다중 플랫폼 전송**")
        print("• 오픈채팅방 + 텔레그램 + 디스코드")
        print("• 슬랙 + 이메일 + SMS")
        print("• 구글 시트에 로그 저장")
        
        print("\n🔄 **시나리오 3: 실패 시 자동 재시도**")
        print("• API 호출 실패 시 5분 후 재시도")
        print("• 3회 실패 시 관리자 알림")
        print("• 에러 로그 수집 및 분석")
        
        print("\n🎨 **시나리오 4: 동적 콘텐츠**")
        print("• 시간대별 다른 이모지")
        print("• 개인별 맞춤 메시지")
        print("• 기념일 특별 메시지")
        
    def _create_make_scenario_template(self):
        """Make.com 시나리오 JSON 템플릿 생성"""
        scenario_template = {
            "name": "G라이더 미션 자동 전송",
            "flow": [
                {
                    "id": 1,
                    "module": "util:Schedule",
                    "version": 1,
                    "parameters": {
                        "interval": 1,
                        "intervalType": "day",
                        "times": [
                            "08:00",
                            "12:00", 
                            "18:00",
                            "22:00",
                            "10:30",
                            "14:30",
                            "20:30"
                        ],
                        "timezone": "Asia/Seoul"
                    },
                    "mapper": {},
                    "metadata": {
                        "designer": {
                            "x": 0,
                            "y": 0
                        }
                    }
                },
                {
                    "id": 2,
                    "module": "http:ActionSendData",
                    "version": 3,
                    "parameters": {
                        "url": "https://www.fanhowmission.ai.cloudbuild.app/rider/",
                        "method": "GET",
                        "headers": [
                            {
                                "name": "User-Agent",
                                "value": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
                            }
                        ]
                    },
                    "mapper": {},
                    "metadata": {
                        "designer": {
                            "x": 300,
                            "y": 0
                        }
                    }
                },
                {
                    "id": 3,
                    "module": "util:SetVariable2",
                    "version": 1,
                    "parameters": {},
                    "mapper": {
                        "name": "mission_data",
                        "value": "{{parseHTML(2.data)}}"
                    },
                    "metadata": {
                        "designer": {
                            "x": 600,
                            "y": 0
                        }
                    }
                },
                {
                    "id": 4,
                    "module": "http:ActionSendData",
                    "version": 3,
                    "parameters": {
                        "url": "YOUR_WEBHOOK_URL",
                        "method": "POST",
                        "headers": [
                            {
                                "name": "Content-Type",
                                "value": "application/json"
                            }
                        ]
                    },
                    "mapper": {
                        "data": {
                            "message": "🤖 G라이더 미션 현황\\n{{formatMissionData(3.mission_data)}}",
                            "timestamp": "{{now}}",
                            "source": "make.com"
                        }
                    },
                    "metadata": {
                        "designer": {
                            "x": 900,
                            "y": 0
                        }
                    }
                }
            ],
            "metadata": {
                "version": 1,
                "scenario": {
                    "roundtrips": 1,
                    "maxErrors": 3,
                    "autoCommit": True,
                    "sequential": False,
                    "confidential": False,
                    "dataloss": False,
                    "dlq": False
                },
                "designer": {
                    "orphans": []
                }
            }
        }
        
        with open('make_scenario_template.json', 'w', encoding='utf-8') as f:
            json.dump(scenario_template, f, indent=2, ensure_ascii=False)
        
        print("✅ Make.com 시나리오 템플릿 생성 완료!")
        print("📁 파일: make_scenario_template.json")
        
    def _create_webhook_server(self):
        """간단한 웹훅 서버 생성"""
        webhook_server = '''#!/usr/bin/env python3
"""
Make.com용 웹훅 서버
Make.com에서 전송된 데이터를 받아 카카오톡으로 전송
"""

from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# 카카오 API 설정
KAKAO_ACCESS_TOKEN = os.getenv('KAKAO_ACCESS_TOKEN')
OPENCHAT_ID = os.getenv('KAKAO_OPENCHAT_ID', 'gt26QiBg')

@app.route('/webhook/mission', methods=['POST'])
def receive_mission_data():
    """Make.com에서 미션 데이터 수신"""
    try:
        data = request.get_json()
        
        message = data.get('message', '')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        source = data.get('source', 'make.com')
        
        print(f"📥 {timestamp} 웹훅 수신 ({source})")
        print(f"📝 메시지: {message[:100]}...")
        
        # 카카오톡 전송 시뮬레이션 (실제로는 다른 방법 사용)
        result = send_to_kakao_alternative(message)
        
        return jsonify({
            'status': 'success',
            'message': '메시지 처리 완료',
            'timestamp': datetime.now().isoformat(),
            'result': result
        })
        
    except Exception as e:
        print(f"❌ 웹훅 처리 오류: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

def send_to_kakao_alternative(message):
    """카카오톡 대안 전송 방법들"""
    methods = []
    
    # 1. 텔레그램으로 전송
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if telegram_token and telegram_chat_id:
        try:
            telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
            telegram_data = {
                'chat_id': telegram_chat_id,
                'text': f"🤖 G라이더 미션 알림\\n\\n{message}",
                'parse_mode': 'HTML'
            }
            response = requests.post(telegram_url, json=telegram_data)
            if response.status_code == 200:
                methods.append("✅ 텔레그램 전송 성공")
        except Exception as e:
            methods.append(f"❌ 텔레그램 실패: {e}")
    
    # 2. Discord 웹훅으로 전송
    discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
    if discord_webhook:
        try:
            discord_data = {
                'content': f"🤖 **G라이더 미션 현황**\\n```\\n{message}\\n```"
            }
            response = requests.post(discord_webhook, json=discord_data)
            if response.status_code == 204:
                methods.append("✅ Discord 전송 성공")
        except Exception as e:
            methods.append(f"❌ Discord 실패: {e}")
    
    # 3. 슬랙 웹훅으로 전송
    slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
    if slack_webhook:
        try:
            slack_data = {
                'text': f"🤖 G라이더 미션 현황",
                'attachments': [
                    {
                        'color': 'good',
                        'text': message,
                        'ts': datetime.now().timestamp()
                    }
                ]
            }
            response = requests.post(slack_webhook, json=slack_data)
            if response.status_code == 200:
                methods.append("✅ 슬랙 전송 성공")
        except Exception as e:
            methods.append(f"❌ 슬랙 실패: {e}")
    
    # 4. 이메일 전송 (SendGrid 등)
    email_api_key = os.getenv('SENDGRID_API_KEY')
    if email_api_key:
        methods.append("📧 이메일 전송 기능 대기")
    
    return methods if methods else ["📋 메시지 로그만 저장"]

@app.route('/webhook/test', methods=['GET', 'POST'])
def test_webhook():
    """웹훅 테스트 엔드포인트"""
    return jsonify({
        'status': 'ok',
        'message': 'Make.com 웹훅 서버 정상 작동',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print("🚀 Make.com 웹훅 서버 시작!")
    print(f"📡 포트: {port}")
    print(f"🔧 디버그: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
'''
        
        with open('make_webhook_server.py', 'w', encoding='utf-8') as f:
            f.write(webhook_server)
        
        print("✅ Make.com 웹훅 서버 생성 완료!")
        print("📁 파일: make_webhook_server.py")
        
        # requirements.txt 업데이트
        requirements = '''flask==2.3.3
requests==2.31.0
python-dotenv==1.0.0
'''
        with open('make_requirements.txt', 'w', encoding='utf-8') as f:
            f.write(requirements)
        
        print("📁 파일: make_requirements.txt")
        
    def create_deployment_options(self):
        """웹훅 서버 배포 옵션들"""
        print("\n☁️ **웹훅 서버 배포 옵션**")
        print("="*35)
        
        print("\n🆓 **무료 옵션들:**")
        print("1. **Render** (추천)")
        print("   - 무료 요금제 제공")
        print("   - 자동 SSL")
        print("   - Git 연동")
        print("   - 설정: render.com")
        
        print("\n2. **Railway**")
        print("   - $5 크레딧 제공")
        print("   - 간단한 배포")
        print("   - 설정: railway.app")
        
        print("\n3. **Heroku**")
        print("   - 무료 요금제 (제한적)")
        print("   - 설정: heroku.com")
        
        print("\n4. **Vercel**")
        print("   - 서버리스 함수")
        print("   - 무료 요금제")
        print("   - 설정: vercel.com")
        
        print("\n💰 **저가 옵션들:**")
        print("1. **AWS Lambda** - 거의 무료")
        print("2. **Google Cloud Run** - 무료 할당량")
        print("3. **Azure Functions** - 무료 할당량")
        
    def create_step_by_step_tutorial(self):
        """단계별 튜토리얼"""
        tutorial_content = '''# 🎯 Make.com으로 G라이더 미션 완전 자동화

## 📋 1단계: Make.com 계정 생성

1. https://make.com 접속
2. "Get started free" 클릭
3. 이메일 또는 구글 계정으로 가입
4. 이메일 인증 완료
5. 대시보드 접속

---

## 🔧 2단계: 새 시나리오 생성

1. 대시보드에서 "Create a new scenario" 클릭
2. 시나리오 이름: "G라이더 미션 자동 전송" 입력
3. "Blank scenario" 선택
4. 시각적 편집기 열림

---

## ⏰ 3단계: 스케줄 트리거 설정

1. 첫 번째 모듈에서 "Schedule" 검색 후 선택
2. "Every N hours" 선택
3. 설정:
   - Interval: 1
   - Unit: hour
   - Start time: 08:00
   - Timezone: Asia/Seoul
4. Advanced settings에서 특정 시간 설정:
   - 08:00, 12:00, 18:00, 22:00
   - 10:30, 14:30, 20:30

---

## 🌐 4단계: HTTP 요청 모듈 추가

1. "+" 버튼 클릭하여 새 모듈 추가
2. "HTTP" 검색 후 선택
3. "Make a request" 선택
4. 설정:
   - URL: `https://www.fanhowmission.ai.cloudbuild.app/rider/`
   - Method: GET
   - Headers: 
     - User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)

---

## 🔧 5단계: 데이터 파싱 모듈

1. "Tools" 모듈 추가
2. "Set variable" 선택
3. Variable name: `mission_data`
4. Variable value: HTML 파싱 함수 적용
5. JavaScript 함수로 데이터 추출

---

## 📤 6단계: 웹훅 전송 모듈

1. "HTTP" 모듈 추가 (전송용)
2. "Make a request" 선택
3. 설정:
   - URL: 웹훅 엔드포인트 URL
   - Method: POST
   - Headers: Content-Type: application/json
   - Body: JSON 형태로 메시지 데이터

---

## 🚀 7단계: 웹훅 서버 배포

### Render.com 배포 (추천):

1. https://render.com 가입
2. "New Web Service" 클릭
3. GitHub 저장소 연결
4. 설정:
   - Build Command: `pip install -r make_requirements.txt`
   - Start Command: `python make_webhook_server.py`
5. 환경변수 설정:
   - TELEGRAM_BOT_TOKEN (옵션)
   - DISCORD_WEBHOOK_URL (옵션)
6. 배포 완료 후 URL 확인

---

## ✅ 8단계: 테스트 및 활성화

1. Make.com에서 "Run once" 클릭
2. 각 모듈 실행 결과 확인
3. 오류 수정
4. "Scheduling" 토글을 ON으로 설정
5. 자동화 시작!

---

## 📊 모니터링

- **Make.com 대시보드**: 실행 로그 및 통계
- **웹훅 서버 로그**: 실시간 메시지 처리 현황
- **텔레그램/Discord**: 실제 전송 결과 확인

---

## 🔧 고급 설정

### 조건부 실행:
- Router 모듈로 분기 처리
- Filter로 조건 설정
- 시간대별 다른 메시지

### 오류 처리:
- Error handler 설정
- 재시도 로직
- 실패 시 알림

### 다중 플랫폼:
- 여러 웹훅 동시 전송
- 플랫폼별 메시지 포맷
- 우선순위 설정

---

## 💰 비용

- **Make.com**: 무료 (월 1,000 operations)
- **웹훅 서버**: 무료 (Render.com)
- **총 비용**: 완전 무료! 🎉

---

**🎉 축하합니다! 이제 Make.com으로 완전 자동화된 시스템이 구축되었습니다!**
'''
        
        with open('make_tutorial.md', 'w', encoding='utf-8') as f:
            f.write(tutorial_content)
        
        print("✅ Make.com 단계별 튜토리얼 생성 완료!")
        print("📁 파일: make_tutorial.md")

def main():
    """메인 함수"""
    guide = MakeAutomationGuide()
    
    guide.show_make_overview()
    
    print("\n🎯 **Make.com 자동화 옵션 선택:**")
    print("1. 📋 기본 시나리오 구축 가이드")
    print("2. 🔗 웹훅 연동 설정")
    print("3. 🚀 고급 시나리오들")
    print("4. ☁️ 웹훅 서버 배포 옵션")
    print("5. 📖 완전한 단계별 튜토리얼")
    print("6. 🎨 모든 기능 생성")
    
    choice = input("\n선택 (1-6): ").strip()
    
    if choice == "1":
        guide.create_make_scenario_guide()
    elif choice == "2":
        guide.create_webhook_integration()
    elif choice == "3":
        guide.create_advanced_scenarios()
    elif choice == "4":
        guide.create_deployment_options()
    elif choice == "5":
        guide.create_step_by_step_tutorial()
    elif choice == "6":
        print("\n🚀 모든 Make.com 자동화 구성요소 생성 중...")
        guide.create_make_scenario_guide()
        guide.create_webhook_integration()
        guide.create_advanced_scenarios()
        guide.create_deployment_options()
        guide.create_step_by_step_tutorial()
        print("\n🎉 Make.com 완전 자동화 시스템 구축 완료!")
    else:
        print("❌ 잘못된 선택입니다.")
    
    print("\n🎯 **Make.com의 장점:**")
    print("• 🎨 직관적인 드래그 앤 드롭 인터페이스")
    print("• 🔄 복잡한 조건부 로직 구현 가능")
    print("• 📊 실시간 모니터링 및 디버깅")
    print("• 🆓 무료 요금제로도 충분함")
    print("• 🌐 1,000+ 앱과 연동 가능")

if __name__ == "__main__":
    main() 