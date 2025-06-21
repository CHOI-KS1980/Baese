# 🤖 GitHub Actions 카카오톡 자동화 설정 가이드

**컴퓨터를 켜놓지 않아도 24시간 자동으로 카카오톡 메시지가 전송됩니다!**

## 🎯 개요

GitHub Actions를 사용하여 클라우드에서 자동으로 카카오톡 "나에게 보내기" 메시지를 전송하는 시스템입니다.

### ✅ 주요 장점
- **24시간 자동 실행**: 컴퓨터가 꺼져있어도 동작
- **무료**: GitHub Actions 월 2,000분 무료 제공
- **안정성**: 클라우드 기반으로 안정적
- **모니터링**: 실패시 자동 알림 및 이슈 생성

### ⏰ 자동 스케줄
- **운영시간**: 오전 10시 ~ 자정 (14시간)
- **기본 알림**: 30분 간격 (논피크 시간)
- **피크 알림**: 15분 간격 (점심피크 11:30-14:00, 저녁피크 17:00-21:00)
- **특별 메시지**: 10시 시작, 자정 마무리
- **토큰 체크**: 주기적으로 토큰 유효성 검사

## 📋 1단계: GitHub 저장소 설정

### 1.1 저장소 생성 또는 준비
```bash
# 기존 프로젝트가 GitHub에 있다면 건너뛰기
# 없다면 새 저장소 생성
git init
git add .
git commit -m "카카오톡 자동화 초기 설정"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 1.2 필수 파일 확인
다음 파일들이 저장소에 있는지 확인:
- `github_actions_memo_automation.py`
- `.github/workflows/kakao-automation.yml`
- `카카오_토큰_생성기.py`

## 🔐 2단계: GitHub Secrets 설정

### 2.1 카카오 토큰 발급
```bash
# 로컬에서 토큰 발급
python3 카카오_토큰_생성기.py
```

발급받은 토큰을 복사해둡니다.

### 2.2 GitHub Secrets 등록
1. **GitHub 저장소 → Settings → Secrets and variables → Actions**
2. **"New repository secret" 클릭**
3. **필수 설정**:

| Secret 이름 | 값 | 설명 |
|-------------|----|----|
| `KAKAO_ACCESS_TOKEN` | `발급받은_토큰` | **필수** - 카카오톡 API 토큰 |
| `OPENWEATHER_API_KEY` | `날씨_API_키` | 선택 - 날씨 정보용 |
| `TELEGRAM_BOT_TOKEN` | `텔레그램_봇_토큰` | 선택 - 백업 알림용 |
| `TELEGRAM_CHAT_ID` | `텔레그램_채팅_ID` | 선택 - 백업 알림용 |

### 2.3 설정 예시
```
KAKAO_ACCESS_TOKEN: eyJ0eXAiOiJKV1QiLCJhbGc...
OPENWEATHER_API_KEY: abc123def456ghi789...
TELEGRAM_BOT_TOKEN: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID: 123456789
```

## 🚀 3단계: 자동화 활성화

### 3.1 워크플로우 활성화
1. **GitHub 저장소 → Actions 탭**
2. **"카카오톡 나에게 보내기 자동화" 워크플로우 확인**
3. **활성화되어 있는지 확인**

### 3.2 수동 테스트 실행
1. **Actions → 워크플로우 선택**
2. **"Run workflow" 클릭**
3. **"test" 선택 후 실행**

### 3.3 성공 확인
- 실행 로그에서 "✅ 전송 성공" 확인
- 카카오톡에서 테스트 메시지 수신 확인

## ⏰ 4단계: 스케줄 확인

### 4.1 자동 실행 시간 (한국시간)
```yaml
# 🌅 하루 시작: 10:00
- cron: '0 1 * * *'   # UTC 01:00 = KST 10:00

# ⏰ 기본 알림: 30분 간격 (논피크)
- cron: '30 1 * * *'  # 10:30
- cron: '0 2 * * *'   # 11:00
- cron: '0 3 * * *'   # 12:00
- cron: '30 3 * * *'  # 12:30
... (총 28회 30분 간격)
- cron: '30 14 * * *' # 23:30

# 🔥 피크 알림: 15분 간격 추가
# 점심피크 (11:30-14:00)
- cron: '45 2 * * *'  # 11:45
- cron: '15 3 * * *'  # 12:15
... (총 10회 추가)

# 저녁피크 (17:00-21:00)  
- cron: '15 8 * * *'  # 17:15
- cron: '45 8 * * *'  # 17:45
... (총 8회 추가)

# 🌙 자정 마무리: 00:00
- cron: '0 15 * * *'  # UTC 15:00 = KST 00:00
```

**총 47회/일 자동 전송** (컴퓨터 꺼져있어도 실행)

### 4.2 스케줄 수정 방법
`.github/workflows/kakao-automation.yml` 파일의 `cron` 값 수정:

```yaml
# 예: 매일 오전 9시로 변경
- cron: '0 0 * * *'  # UTC 00:00 = KST 09:00
```

**참고**: [Cron 표현식 도구](https://crontab.guru/)에서 시간 계산 가능

## 📊 5단계: 모니터링 설정

### 5.1 실행 상태 확인
- **GitHub Actions → 워크플로우 실행 기록**
- **성공/실패 상태 확인**
- **로그 상세 확인**

### 5.2 자동 알림 설정
실패시 자동으로 GitHub Issue가 생성됩니다:
- 토큰 만료 알림
- 전송 실패 알림
- 오류 원인 분석

### 5.3 백업 알림 (텔레그램)
선택사항이지만 권장:
1. **텔레그램 봇 생성**: @BotFather에서 봇 생성
2. **토큰 및 채팅 ID 획득**
3. **GitHub Secrets에 등록**

## 🔧 6단계: 고급 설정

### 6.1 커스텀 메시지 설정
`github_actions_memo_automation.py` 파일 수정:

```python
# 메시지 내용 커스터마이징
def create_report_message(self, report_type="scheduled"):
    # 여기서 메시지 내용 수정 가능
    pass
```

### 6.2 추가 API 연동
날씨 정보 외에 다른 API 연동 가능:
- 주식 정보
- 뉴스 헤드라인
- 암호화폐 시세

### 6.3 리포트 주기 변경
필요에 따라 실행 주기 조정:
```yaml
# 매 시간마다 실행
- cron: '0 * * * *'

# 주말 제외
- cron: '0 9 * * 1-5'  # 월-금만
```

## ❓ 문제 해결

### 7.1 일반적인 문제

#### 🔴 토큰 오류
```
Error: KAKAO_ACCESS_TOKEN이 GitHub Secrets에 설정되지 않았습니다.
```
**해결**: GitHub Secrets에서 `KAKAO_ACCESS_TOKEN` 확인

#### 🔴 토큰 만료
```
❌ 카카오톡 전송 실패: 401
```
**해결**: 
1. `카카오_토큰_생성기.py` 재실행
2. 새 토큰으로 GitHub Secrets 업데이트

#### 🔴 스케줄 미실행
**확인사항**:
- 저장소가 Public인지 확인 (Private는 유료)
- 90일간 미활동시 자동 비활성화됨
- Actions 탭에서 워크플로우 활성화 상태 확인

### 7.2 로그 확인 방법
1. **GitHub → Actions → 실행 기록 선택**
2. **"카카오톡 자동화 실행" 단계 클릭**
3. **상세 로그 확인**

### 7.3 디버깅 모드
워크플로우 파일에 디버깅 추가:
```yaml
- name: 🐛 디버그 정보
  run: |
    echo "현재 시간: $(date)"
    echo "환경 변수: $REPORT_TYPE"
    echo "토큰 길이: ${#KAKAO_ACCESS_TOKEN}"
```

## 💡 최적화 팁

### 8.1 API 사용량 관리
- **카카오 API**: 월 1,000건 무료
- **GitHub Actions**: 월 2,000분 무료
- **계산**: 하루 7회 × 30일 = 210회 (여유있음)

### 8.2 비용 절약
```yaml
# 필요한 경우에만 실행
if: github.event_name == 'schedule' && github.ref == 'refs/heads/main'
```

### 8.3 성능 최적화
```yaml
# 패키지 캐시 사용
- uses: actions/setup-python@v4
  with:
    cache: 'pip'
```

## 🎉 완료!

이제 설정이 완료되었습니다!

### ✅ 최종 확인사항
- [ ] GitHub Secrets에 `KAKAO_ACCESS_TOKEN` 설정
- [ ] 수동 테스트 실행 성공
- [ ] 카카오톡에서 메시지 수신 확인
- [ ] Actions 탭에서 스케줄 확인

### 🔄 유지관리
- **월 1회**: 토큰 유효성 확인
- **필요시**: 스케줄 조정
- **문제 발생시**: GitHub Issues 확인

---

## 📚 추가 리소스

### 공식 문서
- [GitHub Actions 문서](https://docs.github.com/en/actions)
- [카카오 API 문서](https://developers.kakao.com/docs/latest/ko/message/)

### 도움말
- **Cron 표현식**: https://crontab.guru/
- **시간대 변환**: https://www.worldtimebuddy.com/
- **YAML 검증**: https://yamllint.com/

### 예제 저장소
완전히 설정된 예제를 보려면:
```bash
git clone https://github.com/YOUR_USERNAME/kakao-automation-example.git
```

---

**🎯 이제 컴퓨터가 꺼져있어도 24시간 자동으로 카카오톡 메시지가 전송됩니다!** 