# 🚀 카카오톡 정확한 스케줄링 시스템 구현 가이드

## 📋 목차
1. [개요](#개요)
2. [핵심 기능](#핵심-기능)
3. [문제 해결 방안](#문제-해결-방안)
4. [구현 구조](#구현-구조)
5. [사용법](#사용법)
6. [설정](#설정)
7. [모니터링](#모니터링)
8. [배포 가이드](#배포-가이드)

## 🎯 개요

### 문제점 분석
- **스케줄 불일치**: 매시간 30분/정각, 피크시간 15분 간격 미준수
- **전송 누락**: 메시지가 전송되지 않고 몇 시간 후 재전송
- **중복 전송**: 여러 번 겹쳐서 전송되는 문제
- **전송 확인 부족**: 실제 전송 여부 확인 메커니즘 없음

### 해결 목표
- ✅ **정확한 스케줄링**: 한국시간 기준 정확한 시간 전송
- ✅ **전송 확인**: 실제 전송 여부 확인 및 재시도
- ✅ **중복 방지**: 동일 메시지 중복 전송 방지
- ✅ **실시간 모니터링**: 전송 상태 실시간 추적

## 🔧 핵심 기능

### 1. 정확한 스케줄링
```python
# 매시간 30분, 정각 전송
scheduler.schedule_regular_message("정기 알림")

# 피크시간 15분 간격 전송
scheduler.schedule_peak_message("피크 알림")
```

### 2. 전송 확인 및 재시도
```python
# 전송 후 자동 확인
await scheduler._confirm_transmission(message)

# 실패 시 자동 재시도
await scheduler._retry_message(message, delay)
```

### 3. 중복 전송 방지
```python
# 메시지 해시 기반 중복 체크
message_hash = self._generate_message_hash(content, schedule_time)
if message_hash in self.recent_message_hashes:
    return None  # 중복 메시지 감지
```

## 🛠️ 문제 해결 방안

### 1. 스케줄 불일치 해결
```python
def _get_next_regular_time(self) -> datetime:
    """다음 정기 전송 시간 계산"""
    now = datetime.now(KST)
    
    # 현재 시간이 30분 이전이면 30분, 아니면 다음 시간 정각
    if now.minute < 30:
        next_time = now.replace(minute=30, second=0, microsecond=0)
    else:
        next_time = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    
    return next_time
```

### 2. 전송 누락 해결
```python
async def _confirm_transmission(self, message: ScheduledMessage):
    """전송 확인"""
    await asyncio.sleep(self.schedule_config['confirmation_delay'])
    
    # 전송 확인 시도
    confirmation_success = await self._check_transmission_confirmation(message)
    
    if not confirmation_success:
        # 전송 확인 실패 시 재시도
        await self._handle_confirmation_failure(message)
```

### 3. 중복 전송 해결
```python
def schedule_message(self, content: str, schedule_time: datetime) -> Optional[str]:
    # 중복 메시지 체크
    message_hash = self._generate_message_hash(content, schedule_time)
    if message_hash in self.recent_message_hashes:
        logger.warning(f"⚠️ 중복 메시지 감지: {content[:50]}...")
        return None
```

## 🏗️ 구현 구조

### 파일 구조
```
auto_finance/
├── core/
│   └── kakao_scheduler.py          # 메인 스케줄러
├── config/
│   └── kakao_scheduler_config.py   # 설정 파일
├── examples/
│   └── kakao_scheduler_usage.py    # 사용 예시
└── utils/
    ├── logger.py                   # 로깅 유틸리티
    └── error_handler.py           # 오류 처리
```

### 클래스 구조
```python
class KakaoScheduler:
    """카카오톡 정확한 스케줄링 시스템"""
    
    def __init__(self):
        # 스케줄 관리
        self.scheduled_messages: Dict[str, ScheduledMessage] = {}
        self.sent_messages: Dict[str, TransmissionResult] = {}
        self.failed_messages: Dict[str, List[TransmissionResult]] = {}
        
        # 중복 전송 방지
        self.recent_message_hashes: List[str] = []
        
        # 스케줄러 상태
        self.is_running = False
```

## 📖 사용법

### 1. 기본 사용법
```python
import asyncio
from auto_finance.core.kakao_scheduler import KakaoScheduler

async def main():
    # 스케줄러 초기화
    scheduler = KakaoScheduler()
    
    # 카카오 토큰 설정
    scheduler.set_kakao_token("your_kakao_access_token")
    
    # 스케줄러 시작
    await scheduler.start_scheduler()
    
    # 정기 메시지 스케줄링
    message_id = scheduler.schedule_regular_message("정기 알림 메시지")
    
    # 스케줄러 중지
    await scheduler.stop_scheduler()

asyncio.run(main())
```

### 2. 고급 사용법
```python
# 특정 시간에 메시지 스케줄링
from datetime import datetime, timedelta

target_time = datetime.now() + timedelta(minutes=5)
message_id = scheduler.schedule_message(
    content="특정 시간 알림",
    schedule_time=target_time,
    schedule_type=ScheduleType.CUSTOM,
    metadata={'priority': 'high'}
)

# 메시지 상태 확인
status = scheduler.get_message_status(message_id)
print(f"메시지 상태: {status['status']}")

# 스케줄 상태 확인
schedule_status = scheduler.get_schedule_status()
print(f"스케줄된 메시지: {schedule_status['scheduled_count']}")
```

### 3. 실제 사용 시나리오
```python
# 장부 모니터링 알림
regular_alert = """📊 장부 모니터링 정기 알림

⏰ 현재 시간: {time}
📈 총점: 95점
🎯 수락률: 93.8%
✅ 총완료: 75건

🤖 자동 모니터링 시스템"""

message_id = scheduler.schedule_regular_message(regular_alert)
```

## ⚙️ 설정

### 1. 환경변수 설정
```bash
# 카카오 액세스 토큰
export KAKAO_ACCESS_TOKEN="your_kakao_access_token"

# 환경 설정
export ENVIRONMENT="production"  # development, production, testing
```

### 2. 설정 파일 사용
```python
from auto_finance.config.kakao_scheduler_config import get_config

# 환경별 설정 가져오기
config = get_config('production')

# 스케줄러에 설정 적용
scheduler = KakaoScheduler()
scheduler.schedule_config = config['schedule']
```

### 3. 커스텀 설정
```python
# 피크 시간대 커스터마이징
scheduler.schedule_config['peak_hours'] = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

# 재시도 간격 조정
scheduler.schedule_config['retry_delays'] = [60, 120, 300, 600]  # 1분, 2분, 5분, 10분

# 전송 확인 대기 시간 조정
scheduler.schedule_config['confirmation_delay'] = 15  # 15초
```

## 📊 모니터링

### 1. 실시간 상태 확인
```python
# 스케줄 상태 확인
status = scheduler.get_schedule_status()
print(f"실행 상태: {status['is_running']}")
print(f"스케줄된 메시지: {status['scheduled_count']}")
```

### 2. 성능 지표
```python
stats = status['stats']
print(f"총 스케줄된: {stats['total_scheduled']}")
print(f"총 전송된: {stats['total_sent']}")
print(f"총 실패한: {stats['total_failed']}")
print(f"총 확인된: {stats['total_confirmed']}")

# 성공률 계산
if stats['total_scheduled'] > 0:
    success_rate = (stats['total_sent'] / stats['total_scheduled']) * 100
    print(f"전송 성공률: {success_rate:.1f}%")
```

### 3. 로그 모니터링
```python
# 로그 레벨 설정
import logging
logging.basicConfig(level=logging.INFO)

# 주요 로그 메시지
# 📅 메시지 스케줄링: message_id - 2024-01-01 12:30:00
# 📤 메시지 전송 시작: message_id
# ✅ 메시지 전송 성공: message_id
# ✅ 전송 확인 완료: message_id
# 🔄 메시지 재시도: message_id
# ❌ 메시지 최종 실패: message_id
```

## 🚀 배포 가이드

### 1. 의존성 설치
```bash
pip install pytz requests asyncio
```

### 2. 환경 설정
```bash
# .env 파일 생성
KAKAO_ACCESS_TOKEN=your_kakao_access_token
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### 3. 시스템 서비스 등록 (Linux)
```bash
# /etc/systemd/system/kakao-scheduler.service
[Unit]
Description=Kakao Scheduler Service
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/your/app
Environment=KAKAO_ACCESS_TOKEN=your_token
ExecStart=/usr/bin/python3 -m auto_finance.examples.kakao_scheduler_usage
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 4. Docker 배포
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
ENV KAKAO_ACCESS_TOKEN=your_token
ENV ENVIRONMENT=production

CMD ["python", "-m", "auto_finance.examples.kakao_scheduler_usage"]
```

### 5. 모니터링 설정
```python
# 헬스체크 엔드포인트
@app.route('/health')
def health_check():
    status = scheduler.get_schedule_status()
    return {
        'status': 'healthy' if status['is_running'] else 'unhealthy',
        'scheduled_count': status['scheduled_count'],
        'success_rate': calculate_success_rate(status['stats'])
    }
```

## 🔍 문제 해결

### 1. 전송 실패 시
```python
# 재시도 횟수 확인
message_status = scheduler.get_message_status(message_id)
print(f"재시도 횟수: {message_status['retry_count']}")

# 수동 재시도
if message_status['status'] == 'failed':
    # 메시지 재스케줄링
    new_message_id = scheduler.schedule_message(
        content=original_content,
        schedule_time=datetime.now(),
        schedule_type=ScheduleType.CUSTOM
    )
```

### 2. 중복 전송 문제
```python
# 중복 메시지 해시 확인
recent_hashes = scheduler.recent_message_hashes
print(f"최근 메시지 해시 수: {len(recent_hashes)}")

# 해시 목록 초기화 (필요시)
scheduler.recent_message_hashes.clear()
```

### 3. 스케줄 지연 문제
```python
# 현재 시간과 스케줄 시간 비교
now = datetime.now(KST)
next_regular = scheduler._get_next_regular_time()
delay = (next_regular - now).total_seconds()

print(f"다음 정기 전송까지: {delay:.0f}초")
```

## 📈 성능 최적화

### 1. 메모리 사용량 최적화
```python
# 최근 메시지 해시 수 제한
scheduler.max_recent_hashes = 50  # 기본값: 100

# 오래된 메시지 정리
def cleanup_old_messages(scheduler, days=7):
    cutoff_time = datetime.now(KST) - timedelta(days=days)
    # 7일 이상 된 메시지 정리
```

### 2. 네트워크 최적화
```python
# API 타임아웃 조정
scheduler.kakao_config['timeout'] = 5  # 5초

# 연결 풀 사용
import requests
session = requests.Session()
scheduler.session = session
```

### 3. 로깅 최적화
```python
# 로그 레벨 조정
logging.getLogger('auto_finance.core.kakao_scheduler').setLevel(logging.WARNING)

# 로그 로테이션 설정
from logging.handlers import RotatingFileHandler
handler = RotatingFileHandler('kakao_scheduler.log', maxBytes=1024*1024, backupCount=5)
```

## 🎯 결론

이 카카오톡 스케줄러는 다음과 같은 문제들을 해결합니다:

1. **정확한 스케줄링**: 한국시간 기준 정확한 시간 전송
2. **전송 확인**: 실제 전송 여부 확인 및 자동 재시도
3. **중복 방지**: 메시지 해시 기반 중복 전송 방지
4. **실시간 모니터링**: 전송 상태 실시간 추적 및 통계

이 시스템을 통해 안정적이고 정확한 카카오톡 메시지 전송이 가능합니다. 