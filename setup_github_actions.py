#!/usr/bin/env python3
"""
🤖 GitHub Actions 카카오톡 자동화 설정 도우미

컴퓨터 없이도 24시간 자동 실행되는 카카오톡 시스템을 설정합니다.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def check_git_repository():
    """Git 저장소 확인"""
    if not Path('.git').exists():
        print("❌ Git 저장소가 아닙니다.")
        
        response = input("🔧 Git 저장소를 초기화할까요? (y/N): ").strip().lower()
        if response == 'y':
            try:
                subprocess.run(['git', 'init'], check=True)
                print("✅ Git 저장소 초기화 완료")
                return True
            except subprocess.CalledProcessError:
                print("❌ Git 초기화 실패")
                return False
        else:
            print("⚠️ GitHub Actions를 사용하려면 Git 저장소가 필요합니다.")
            return False
    
    print("✅ Git 저장소 확인 완료")
    return True

def check_required_files():
    """필수 파일 확인"""
    required_files = [
        'github_actions_memo_automation.py',
        '.github/workflows/kakao-automation.yml',
        '카카오_토큰_생성기.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print("\n❌ 누락된 파일들:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("\n🔧 먼저 필요한 파일들을 생성하세요.")
        return False
    
    print("✅ 모든 필수 파일 확인 완료")
    return True

def get_kakao_token():
    """카카오 토큰 발급 도움"""
    print("\n🔑 카카오 액세스 토큰 설정")
    print("=" * 40)
    
    # 기존 토큰 확인
    existing_token = os.getenv('KAKAO_ACCESS_TOKEN', '')
    if existing_token:
        print(f"💡 기존 토큰 발견: {existing_token[:15]}...")
        use_existing = input("기존 토큰을 사용하시겠습니까? (y/N): ").strip().lower()
        if use_existing == 'y':
            return existing_token
    
    print("\n📝 새 토큰 발급 방법:")
    print("1. python3 카카오_토큰_생성기.py 실행")
    print("2. 브라우저에서 카카오 인증 진행")
    print("3. 발급받은 토큰 복사")
    
    generate_now = input("\n🚀 지금 토큰을 발급하시겠습니까? (y/N): ").strip().lower()
    if generate_now == 'y':
        try:
            result = subprocess.run([sys.executable, '카카오_토큰_생성기.py'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ 토큰 발급 스크립트 실행 완료")
                print("📋 발급받은 토큰을 아래에 입력하세요:")
            else:
                print("⚠️ 토큰 발급 스크립트 실행 중 문제가 발생했습니다.")
                print("수동으로 실행해주세요: python3 카카오_토큰_생성기.py")
        
        except Exception as e:
            print(f"❌ 토큰 발급 스크립트 실행 실패: {e}")
    
    # 토큰 입력
    while True:
        token = input("\n🔑 카카오 액세스 토큰을 입력하세요: ").strip()
        if len(token) > 20:  # 최소 길이 체크
            return token
        else:
            print("❌ 토큰이 너무 짧습니다. 올바른 토큰을 입력하세요.")

def get_optional_settings():
    """선택적 설정"""
    settings = {}
    
    print("\n⚙️ 선택적 설정 (Enter로 건너뛰기)")
    print("=" * 40)
    
    # 날씨 API
    weather_key = input("🌤️ OpenWeather API 키 (날씨 정보용): ").strip()
    if weather_key:
        settings['OPENWEATHER_API_KEY'] = weather_key
    
    # 텔레그램 백업 알림
    print("\n📱 텔레그램 백업 알림 설정 (선택사항)")
    telegram_token = input("🤖 텔레그램 봇 토큰: ").strip()
    if telegram_token:
        settings['TELEGRAM_BOT_TOKEN'] = telegram_token
        
        telegram_chat_id = input("💬 텔레그램 채팅 ID: ").strip()
        if telegram_chat_id:
            settings['TELEGRAM_CHAT_ID'] = telegram_chat_id
    
    return settings

def create_secrets_guide(kakao_token, optional_settings):
    """GitHub Secrets 설정 가이드 생성"""
    guide_content = f"""# 🔐 GitHub Secrets 설정 가이드

## 필수 Secrets

### KAKAO_ACCESS_TOKEN
```
{kakao_token}
```

## 선택적 Secrets
"""
    
    if optional_settings:
        for key, value in optional_settings.items():
            guide_content += f"""
### {key}
```
{value}
```"""
    else:
        guide_content += """
(선택적 설정이 없습니다)
"""
    
    guide_content += f"""

## 🔧 설정 방법

1. GitHub 저장소로 이동
2. Settings → Secrets and variables → Actions
3. "New repository secret" 클릭
4. 위의 Secret 이름과 값을 각각 추가

## 🚀 다음 단계

1. GitHub에 코드 푸시
2. Actions 탭에서 워크플로우 확인
3. "Run workflow"로 수동 테스트
4. 카카오톡에서 메시지 수신 확인

---
생성일: {os.popen('date').read().strip()}
"""
    
    try:
        with open('GITHUB_SECRETS_설정.md', 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        print("✅ GitHub Secrets 설정 가이드 생성: GITHUB_SECRETS_설정.md")
        return True
    except Exception as e:
        print(f"❌ 가이드 파일 생성 실패: {e}")
        return False

def check_github_remote():
    """GitHub 원격 저장소 확인"""
    try:
        result = subprocess.run(['git', 'remote', '-v'], 
                              capture_output=True, text=True)
        
        if 'github.com' in result.stdout:
            print("✅ GitHub 원격 저장소 확인됨")
            print(f"🔗 저장소: {result.stdout.split()[1]}")
            return True
        else:
            print("⚠️ GitHub 원격 저장소가 설정되지 않았습니다.")
            
            repo_url = input("🔗 GitHub 저장소 URL을 입력하세요: ").strip()
            if repo_url:
                try:
                    subprocess.run(['git', 'remote', 'add', 'origin', repo_url], 
                                 check=True)
                    print("✅ GitHub 원격 저장소 추가 완료")
                    return True
                except subprocess.CalledProcessError:
                    print("❌ 원격 저장소 추가 실패")
                    return False
            
            return False
    
    except subprocess.CalledProcessError:
        print("⚠️ Git이 설치되지 않았거나 저장소가 아닙니다.")
        return False

def create_commit_and_push():
    """변경사항 커밋 및 푸시"""
    try:
        # 변경사항 확인
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if not result.stdout.strip():
            print("✅ 커밋할 변경사항이 없습니다.")
            return True
        
        print("\n📝 Git 커밋 및 푸시")
        commit_msg = input("커밋 메시지 (Enter: 기본 메시지): ").strip()
        if not commit_msg:
            commit_msg = "GitHub Actions 카카오톡 자동화 설정"
        
        # 스테이징
        subprocess.run(['git', 'add', '.'], check=True)
        
        # 커밋
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
        
        # 푸시 확인
        push_now = input("🚀 GitHub에 바로 푸시하시겠습니까? (y/N): ").strip().lower()
        if push_now == 'y':
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            print("✅ GitHub 푸시 완료")
        else:
            print("⚠️ 나중에 수동으로 푸시하세요: git push origin main")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git 작업 실패: {e}")
        return False

def show_final_instructions():
    """최종 안내사항"""
    print("\n" + "="*60)
    print("🎉 GitHub Actions 카카오톡 자동화 설정 완료!")
    print("="*60)
    
    print("\n📋 다음 단계:")
    print("1. 📁 GITHUB_SECRETS_설정.md 파일을 확인하세요")
    print("2. 🔐 GitHub 저장소에서 Secrets를 설정하세요")
    print("3. 🚀 Actions 탭에서 워크플로우를 테스트하세요")
    print("4. 📱 카카오톡에서 메시지 수신을 확인하세요")
    
    print("\n⏰ 자동 실행 스케줄:")
    print("   • 운영시간: 오전 10시 ~ 자정 (14시간)")
    print("   • 기본 알림: 30분 간격 (논피크)")
    print("   • 피크 알림: 15분 간격 (점심/저녁피크)")
    print("   • 특별 메시지: 10시 시작, 자정 마무리")
    
    print("\n🔗 유용한 링크:")
    print("   • GitHub Actions: https://github.com/YOUR_REPO/actions")
    print("   • 설정 가이드: GITHUB_ACTIONS_설정가이드.md")
    print("   • 문제 해결: README_나에게보내기.md")
    
    print("\n💡 팁:")
    print("   • 토큰은 3개월마다 갱신하세요")
    print("   • 실패시 자동으로 GitHub Issue가 생성됩니다")
    print("   • Private 저장소는 유료 기능입니다")
    
    print("\n✨ 이제 컴퓨터가 꺼져있어도 24시간 자동으로 메시지가 전송됩니다!")

def main():
    """메인 설정 함수"""
    print("🤖 GitHub Actions 카카오톡 자동화 설정 도우미")
    print("=" * 50)
    print("컴퓨터 없이도 24시간 자동으로 카카오톡 메시지를 전송합니다!\n")
    
    # 1. Git 저장소 확인
    print("1️⃣ Git 저장소 확인...")
    if not check_git_repository():
        return
    
    # 2. 필수 파일 확인
    print("\n2️⃣ 필수 파일 확인...")
    if not check_required_files():
        return
    
    # 3. GitHub 원격 저장소 확인
    print("\n3️⃣ GitHub 원격 저장소 확인...")
    if not check_github_remote():
        print("⚠️ 나중에 GitHub 저장소를 설정하고 다시 실행하세요.")
    
    # 4. 카카오 토큰 설정
    print("\n4️⃣ 카카오 토큰 설정...")
    kakao_token = get_kakao_token()
    
    # 5. 선택적 설정
    print("\n5️⃣ 선택적 설정...")
    optional_settings = get_optional_settings()
    
    # 6. 설정 가이드 생성
    print("\n6️⃣ 설정 가이드 생성...")
    create_secrets_guide(kakao_token, optional_settings)
    
    # 7. Git 커밋 및 푸시
    print("\n7️⃣ Git 커밋 및 푸시...")
    create_commit_and_push()
    
    # 8. 최종 안내
    show_final_instructions()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 설정이 중단되었습니다.")
        print("다시 실행하려면: python3 setup_github_actions.py")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        print("문제가 지속되면 수동으로 설정하세요.")
        sys.exit(1) 