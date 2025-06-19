#!/usr/bin/env python3
"""
카카오톡 오픈채팅 자동 전송 시스템 설정 스크립트
"""

import os
import sys
import json
from pathlib import Path

def create_env_file():
    """환경변수 설정 파일 생성"""
    env_content = """# 카카오톡 오픈채팅 자동 전송 설정
# 아래 값들을 실제 값으로 변경하세요

# 카카오 API 설정
KAKAO_API_BASE_URL=https://kapi.kakao.com
KAKAO_ADMIN_KEY=your_kakao_admin_key_here
KAKAO_OPENCHAT_ID=your_openchat_room_id_here
KAKAO_BOT_USER_ID=your_bot_user_id_here

# 기타 메시징 서비스 (기존)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
SLACK_WEBHOOK_URL=your_slack_webhook_url_here
DISCORD_WEBHOOK_URL=your_discord_webhook_url_here

# 미션 모니터링 설정
MISSION_CHECK_INTERVAL=30
AUTO_SCREENSHOT=true
SCREENSHOT_PATH=./screenshots/

# 로그 설정
LOG_LEVEL=INFO
LOG_FILE_PATH=./logs/kakao_scheduler.log
"""
    
    env_file = Path('.env')
    if env_file.exists():
        print("⚠️  .env 파일이 이미 존재합니다.")
        response = input("덮어쓰시겠습니까? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ 설정을 건너뜁니다.")
            return
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ .env 파일이 생성되었습니다.")
    print("📝 .env 파일을 열어서 실제 API 키와 설정값을 입력하세요.")

def create_directories():
    """필요한 디렉토리 생성"""
    dirs = ['logs', 'screenshots', 'cache']
    
    for dir_name in dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 {dir_name} 디렉토리 생성")
        else:
            print(f"📁 {dir_name} 디렉토리 이미 존재")

def install_requirements():
    """필요한 패키지 설치 확인"""
    required_packages = [
        'schedule',
        'requests',
        'python-dotenv',
        'selenium',
        'beautifulsoup4',
        'matplotlib',
        'pandas',
        'flask'
    ]
    
    print("📦 필요한 패키지 확인 중...")
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 설치 필요")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n🔧 누락된 패키지를 설치하려면 다음 명령어를 실행하세요:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    else:
        print("✅ 모든 필요한 패키지가 설치되어 있습니다.")
        return True

def create_systemd_service():
    """systemd 서비스 파일 생성 (Linux용)"""
    if sys.platform != 'linux':
        print("ℹ️  Linux 환경이 아니므로 systemd 서비스 설정을 건너뜁니다.")
        return
    
    current_dir = Path.cwd()
    python_path = sys.executable
    
    service_content = f"""[Unit]
Description=Kakao OpenChat Auto Message Sender
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'ubuntu')}
WorkingDirectory={current_dir}
Environment=PATH={os.environ.get('PATH')}
ExecStart={python_path} kakao_scheduled_sender.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
"""
    
    service_file = Path('kakao-auto-sender.service')
    with open(service_file, 'w', encoding='utf-8') as f:
        f.write(service_content)
    
    print("✅ systemd 서비스 파일이 생성되었습니다: kakao-auto-sender.service")
    print("📝 다음 명령어로 서비스를 등록할 수 있습니다:")
    print(f"sudo cp {service_file} /etc/systemd/system/")
    print("sudo systemctl daemon-reload")
    print("sudo systemctl enable kakao-auto-sender.service")
    print("sudo systemctl start kakao-auto-sender.service")

def create_startup_script():
    """시작 스크립트 생성"""
    startup_content = """#!/bin/bash
# 카카오톡 오픈채팅 자동 전송 시스템 시작 스크립트

echo "🤖 카카오톡 오픈채팅 자동 전송 시스템 시작"
echo "=" * 50

# 가상환경 활성화 (필요한 경우)
# source venv/bin/activate

# Python 스크립트 실행
python3 kakao_scheduled_sender.py

echo "👋 시스템이 종료되었습니다."
"""
    
    script_file = Path('start_kakao_sender.sh')
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(startup_content)
    
    # 실행 권한 부여
    script_file.chmod(0o755)
    
    print("✅ 시작 스크립트가 생성되었습니다: start_kakao_sender.sh")
    print("📝 다음 명령어로 실행할 수 있습니다: ./start_kakao_sender.sh")

def show_setup_guide():
    """설정 가이드 출력"""
    print("\n" + "="*60)
    print("📋 카카오톡 오픈채팅 자동 전송 시스템 설정 가이드")
    print("="*60)
    
    print("\n1️⃣ 카카오 개발자 콘솔 설정:")
    print("   - https://developers.kakao.com/ 접속")
    print("   - 애플리케이션 등록")
    print("   - REST API 키 발급")
    print("   - 카카오톡 메시지 API 권한 요청")
    
    print("\n2️⃣ 오픈채팅방 설정:")
    print("   - 오픈채팅방 생성 또는 기존 방 사용")
    print("   - 관리자 권한으로 봇 추가")
    print("   - 채팅방 ID 확인")
    
    print("\n3️⃣ 환경변수 설정:")
    print("   - .env 파일 열기")
    print("   - 실제 API 키와 채팅방 ID 입력")
    print("   - 기타 설정값 조정")
    
    print("\n4️⃣ 테스트:")
    print("   - python kakao_scheduled_sender.py 실행")
    print("   - 메뉴에서 '3. 테스트 메시지 전송' 선택")
    print("   - 오픈채팅방에서 메시지 확인")
    
    print("\n5️⃣ 자동 실행 설정:")
    print("   - Linux: systemd 서비스 등록")
    print("   - Windows: 작업 스케줄러 설정")
    print("   - macOS: launchd 설정")
    
    print("\n🔗 도움말:")
    print("   - 카카오 API 문서: https://developers.kakao.com/docs/latest/ko/message/")
    print("   - 프로젝트 README: 상세 설정 방법 참조")

def main():
    """메인 설정 함수"""
    print("🚀 카카오톡 오픈채팅 자동 전송 시스템 설정")
    print("="*50)
    
    # 1. 필요한 패키지 확인
    print("\n1️⃣ 패키지 확인")
    if not install_requirements():
        print("❌ 필요한 패키지를 먼저 설치해주세요.")
        return
    
    # 2. 디렉토리 생성
    print("\n2️⃣ 디렉토리 생성")
    create_directories()
    
    # 3. 환경변수 파일 생성
    print("\n3️⃣ 환경변수 설정")
    create_env_file()
    
    # 4. 시작 스크립트 생성
    print("\n4️⃣ 시작 스크립트 생성")
    create_startup_script()
    
    # 5. systemd 서비스 생성 (Linux만)
    print("\n5️⃣ 시스템 서비스 설정")
    create_systemd_service()
    
    # 6. 설정 가이드 출력
    show_setup_guide()
    
    print("\n✅ 설정이 완료되었습니다!")
    print("📝 .env 파일을 편집한 후 시스템을 시작하세요.")

if __name__ == "__main__":
    main() 