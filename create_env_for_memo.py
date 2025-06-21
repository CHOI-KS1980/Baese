#!/usr/bin/env python3
"""
🤖 카카오톡 나에게 보내기 자동화 - 환경설정 파일 생성기
기존 오픈채팅방 설정을 "나에게 보내기" 방식으로 간소화
"""

import os
from pathlib import Path

def create_env_file():
    """나에게 보내기용 .env 파일 생성"""
    env_content = """# 카카오톡 나에게 보내기 자동화 설정
# 아래 값들을 실제 값으로 변경하세요

# 🔑 카카오 API 설정 (필수)
KAKAO_ACCESS_TOKEN=your_kakao_access_token_here

# 🌤️ 날씨 API 설정 (선택사항)
OPENWEATHER_API_KEY=your_openweather_api_key_here

# 📊 로그 설정
LOG_LEVEL=INFO
LOG_FILE_PATH=./logs/kakao_memo_automation.log

# ⚙️ 기타 설정
AUTO_SCHEDULE=true
BACKUP_TO_CLIPBOARD=true
SEND_WEATHER_INFO=true

# ⏰ 스케줄 시간 설정 (24시간 형식)
MORNING_REPORT_TIME=08:00
EVENING_REPORT_TIME=18:00
HOURLY_UPDATE_TIMES=10:00,12:00,14:00,16:00,20:00

# 🔄 메시지 중복 방지 (분 단위)
DUPLICATE_PREVENTION_MINUTES=30

# ═══════════════════════════════════════════════
# 📝 설정 가이드:
# 
# 1. KAKAO_ACCESS_TOKEN:
#    - 카카오_토큰_생성기.py 실행하여 발급
#    - 카카오 개발자 콘솔에서 REST API 키 필요
#    - "나에게 보내기" 권한 필요
# 
# 2. OPENWEATHER_API_KEY:
#    - https://openweathermap.org/api 에서 무료 발급
#    - 날씨 정보를 원하지 않으면 비워두세요
# 
# 3. 스케줄 시간:
#    - HH:MM 형식으로 입력
#    - 여러 시간은 콤마로 구분
# 
# ═══════════════════════════════════════════════
"""
    
    env_file = Path('.env')
    
    # 기존 파일 확인
    if env_file.exists():
        print("⚠️ .env 파일이 이미 존재합니다.")
        
        # 기존 파일 백업
        backup_file = Path('.env.backup')
        if backup_file.exists():
            response = input("기존 백업을 덮어쓰시겠습니까? (y/N): ").strip().lower()
            if response != 'y':
                print("❌ 설정을 중단합니다.")
                return False
        
        # 백업 생성
        with open(env_file, 'r', encoding='utf-8') as f:
            backup_content = f.read()
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(backup_content)
        
        print(f"💾 기존 .env 파일을 {backup_file}로 백업했습니다.")
        
        response = input(".env 파일을 새로 생성하시겠습니까? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ 설정을 중단합니다.")
            return False
    
    # 새 파일 생성
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ .env 파일이 생성되었습니다!")
        print()
        print("🔧 다음 단계:")
        print("1. .env 파일을 열어서 KAKAO_ACCESS_TOKEN 설정")
        print("2. 카카오_토큰_생성기.py 실행하여 토큰 발급")
        print("3. 필요시 OPENWEATHER_API_KEY 설정")
        print("4. kakao_memo_automation.py 실행하여 테스트")
        
        return True
        
    except Exception as e:
        print(f"❌ .env 파일 생성 실패: {e}")
        return False

def create_directories():
    """필요한 디렉토리 생성"""
    dirs = ['logs', 'backup']
    
    for dir_name in dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 {dir_name} 디렉토리 생성")
        else:
            print(f"📁 {dir_name} 디렉토리 이미 존재")

def create_requirements():
    """requirements.txt 생성"""
    requirements_content = """# 카카오톡 나에게 보내기 자동화 필수 패키지

# 스케줄링
schedule==1.2.0

# HTTP 요청
requests==2.31.0

# 환경변수 관리
python-dotenv==1.0.0

# 클립보드 조작
pyperclip==1.8.2

# 시간대 처리
pytz==2023.3

# 로깅
colorama==0.4.6

# 선택사항 (기존 크롤링 기능 사용시)
beautifulsoup4==4.12.2
selenium==4.15.0
matplotlib==3.8.0
pandas==2.1.0
"""
    
    req_file = Path('requirements_memo.txt')
    
    try:
        with open(req_file, 'w', encoding='utf-8') as f:
            f.write(requirements_content)
        
        print(f"✅ {req_file} 파일 생성 완료")
        print(f"📦 패키지 설치: pip install -r {req_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ requirements.txt 생성 실패: {e}")
        return False

def create_startup_script():
    """시작 스크립트 생성"""
    startup_content = """#!/bin/bash
# 카카오톡 나에게 보내기 자동화 시스템 시작 스크립트

echo "🤖 카카오톡 나에게 보내기 자동화 시스템"
echo "================================================"

# 가상환경 확인 및 활성화 (선택사항)
if [ -d "venv" ]; then
    echo "📁 가상환경 활성화..."
    source venv/bin/activate
fi

# 필요한 패키지 설치 확인
echo "📦 패키지 확인 중..."
python3 -c "import schedule, requests, dotenv, pyperclip, pytz" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 필요한 패키지가 설치되지 않았습니다."
    echo "📦 다음 명령어로 설치하세요:"
    echo "   pip install -r requirements_memo.txt"
    exit 1
fi

# 환경변수 파일 확인
if [ ! -f ".env" ]; then
    echo "❌ .env 파일이 없습니다."
    echo "🔧 create_env_for_memo.py를 먼저 실행하세요."
    exit 1
fi

# 카카오톡 자동화 시스템 실행
echo "🚀 카카오톡 자동화 시스템 시작..."
python3 kakao_memo_automation.py

echo "👋 시스템이 종료되었습니다."
"""
    
    script_file = Path('start_memo_automation.sh')
    
    try:
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(startup_content)
        
        # 실행 권한 부여 (Unix 계열)
        if os.name != 'nt':  # Windows가 아닌 경우
            script_file.chmod(0o755)
        
        print(f"✅ 시작 스크립트 생성: {script_file}")
        print(f"🚀 실행: ./{script_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ 시작 스크립트 생성 실패: {e}")
        return False

def show_setup_guide():
    """설정 가이드 출력"""
    print("\n" + "="*60)
    print("📋 카카오톡 나에게 보내기 자동화 설정 가이드")
    print("="*60)
    
    print("\n1️⃣ 카카오 개발자 설정:")
    print("   🔗 https://developers.kakao.com/ 접속")
    print("   📝 애플리케이션 등록")
    print("   🔑 REST API 키 발급")
    print("   ✅ 카카오톡 메시지 API 권한 활성화")
    
    print("\n2️⃣ 토큰 발급:")
    print("   🔧 카카오_토큰_생성기.py 실행")
    print("   🔐 브라우저에서 인증 진행")
    print("   📋 발급받은 토큰을 .env 파일에 입력")
    
    print("\n3️⃣ 테스트:")
    print("   🧪 kakao_memo_automation.py 실행")
    print("   📱 '3. 테스트 메시지 전송' 선택")
    print("   ✅ 카카오톡에서 메시지 확인")
    
    print("\n4️⃣ 자동화 시작:")
    print("   🚀 '1. 자동화 시작' 선택")
    print("   ⏰ 설정된 시간에 자동 리포트 전송")
    print("   📊 일일 2회, 정시 업데이트 5회")
    
    print("\n🎯 주요 장점:")
    print("   ✅ 오픈채팅방 설정 불필요")
    print("   ✅ 복잡한 권한 설정 없음")
    print("   ✅ 나에게만 전송되어 프라이버시 보호")
    print("   ✅ 클립보드 백업으로 수동 전송 가능")
    
    print("\n🔗 도움말:")
    print("   📖 카카오 API 문서: https://developers.kakao.com/docs/latest/ko/message/")
    print("   🆘 문제 발생시: GitHub Issues 또는 문서 참조")

def main():
    """메인 설정 함수"""
    print("🚀 카카오톡 나에게 보내기 자동화 - 초기 설정")
    print("="*50)
    
    print("\n📋 설정 항목:")
    print("1. 📁 필요한 디렉토리 생성")
    print("2. 📄 .env 환경설정 파일 생성")
    print("3. 📦 requirements.txt 생성")
    print("4. 🚀 시작 스크립트 생성")
    print("5. 📋 설정 가이드 표시")
    
    print("\n🔧 자동으로 모든 설정을 진행합니다...")
    
    # 1. 디렉토리 생성
    print("\n1️⃣ 디렉토리 생성 중...")
    create_directories()
    
    # 2. .env 파일 생성
    print("\n2️⃣ .env 파일 생성 중...")
    create_env_file()
    
    # 3. requirements.txt 생성
    print("\n3️⃣ requirements.txt 생성 중...")
    create_requirements()
    
    # 4. 시작 스크립트 생성
    print("\n4️⃣ 시작 스크립트 생성 중...")
    create_startup_script()
    
    # 5. 설정 가이드 표시
    print("\n5️⃣ 설정 가이드")
    show_setup_guide()
    
    print("\n" + "="*50)
    print("✅ 초기 설정이 완료되었습니다!")
    print("🔧 다음 단계: .env 파일에서 KAKAO_ACCESS_TOKEN 설정")
    print("🚀 테스트: python3 kakao_memo_automation.py")

if __name__ == "__main__":
    main() 