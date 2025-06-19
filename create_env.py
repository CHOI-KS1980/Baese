#!/usr/bin/env python3
"""
.env 파일 생성 스크립트
"""

def create_env_file():
    """카카오 API 키를 포함한 .env 파일 생성"""
    
    env_content = """# 카카오톡 오픈채팅 자동 전송 설정

# 카카오 API 설정
KAKAO_API_BASE_URL=https://kapi.kakao.com
KAKAO_ADMIN_KEY=de4104bc707439376061bf497ce87b8e
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
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ .env 파일이 성공적으로 생성되었습니다!")
        print("📝 카카오 API 키가 설정되었습니다: de4104bc707439376061bf497ce87b8e")
        print("")
        print("🔧 추가로 설정해야 할 항목들:")
        print("   - KAKAO_OPENCHAT_ID: 오픈채팅방 ID")
        print("   - KAKAO_BOT_USER_ID: 봇 사용자 ID")
        print("")
        print("📋 .env 파일 내용:")
        print("-" * 50)
        with open('.env', 'r', encoding='utf-8') as f:
            print(f.read())
        
    except Exception as e:
        print(f"❌ .env 파일 생성 실패: {e}")

if __name__ == "__main__":
    create_env_file() 