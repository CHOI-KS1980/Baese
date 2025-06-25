"""
⚙️ 카카오톡 스케줄러 설정
정확한 스케줄링과 전송 확인을 위한 설정값들
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ScheduleConfig:
    """스케줄 설정"""
    # 정기 전송 간격 (분)
    regular_intervals: Optional[List[int]] = None
    
    # 피크 시간 전송 간격 (분)
    peak_intervals: Optional[List[int]] = None
    
    # 피크 시간대 (시간)
    peak_hours: Optional[List[int]] = None
    
    # 전송 확인 대기 시간 (초)
    confirmation_delay: int = 10
    
    # 재시도 간격 (초)
    retry_delays: Optional[List[int]] = None
    
    # 전송 확인 타임아웃 (초)
    confirmation_timeout: int = 30
    
    # 최대 재시도 횟수
    max_retries: int = 3
    
    # 최대 전송 확인 시도 횟수
    max_confirmation_attempts: int = 5
    
    def __post_init__(self):
        if self.regular_intervals is None:
            self.regular_intervals = [0, 30]  # 매시간 0분, 30분
        
        if self.peak_intervals is None:
            self.peak_intervals = [0, 15, 30, 45]  # 피크시간 15분 간격
        
        if self.peak_hours is None:
            self.peak_hours = [7, 8, 9, 11, 12, 13, 17, 18, 19, 20]  # 피크 시간대
        
        if self.retry_delays is None:
            self.retry_delays = [30, 60, 120, 300]  # 재시도 간격

@dataclass
class KakaoConfig:
    """카카오 API 설정"""
    # 카카오 API URL
    api_url: str = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    
    # API 타임아웃 (초)
    timeout: int = 10
    
    # 액세스 토큰 (환경변수에서 가져옴)
    access_token: Optional[str] = None
    
    # 웹 URL
    web_url: str = "https://github.com/CHOI-KS1980/Baese"
    
    # 모바일 웹 URL
    mobile_web_url: str = "https://github.com/CHOI-KS1980/Baese"

@dataclass
class MonitoringConfig:
    """모니터링 설정"""
    # 통계 업데이트 간격 (초)
    stats_update_interval: int = 60
    
    # 로그 레벨
    log_level: str = "INFO"
    
    # 성능 지표 수집 여부
    enable_metrics: bool = True
    
    # 알림 임계값
    alert_thresholds: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.alert_thresholds is None:
            self.alert_thresholds = {
                'max_failure_rate': 0.1,  # 최대 실패율 10%
                'max_retry_count': 5,     # 최대 재시도 횟수
                'min_success_rate': 0.9,  # 최소 성공률 90%
                'max_delay_minutes': 5    # 최대 지연 시간 5분
            }

@dataclass
class MessageTemplateConfig:
    """메시지 템플릿 설정"""
    # 기본 메시지 템플릿
    default_template: str = """📊 자동 모니터링 알림

⏰ 시간: {time}
📈 상태: {status}
🎯 성공률: {success_rate}%
✅ 완료: {completed_count}건

🤖 자동 모니터링 시스템"""
    
    # 정기 알림 템플릿
    regular_template: str = """🕐 정기 모니터링 알림

⏰ 현재 시간: {time}
📊 시스템 상태: 정상
📈 성능 지표: {metrics}
✅ 안정성: {stability}%

🤖 자동 모니터링 시스템"""
    
    # 피크 시간 알림 템플릿
    peak_template: str = """🚨 피크 시간 알림

⏰ 현재 시간: {time}
🔥 피크 시간대 활성화
⚡ 실시간 모니터링 중
📊 현재 부하: {load}%

🤖 자동 모니터링 시스템"""
    
    # 오류 알림 템플릿
    error_template: str = """⚠️ 시스템 오류 알림

⏰ 발생 시간: {time}
❌ 오류 유형: {error_type}
🔧 자동 복구 시도 중
📱 관리자 확인 필요

🤖 자동 모니터링 시스템"""
    
    # 전송 실패 알림 템플릿
    failure_template: str = """❌ 메시지 전송 실패

⏰ 시도 시간: {time}
🔄 재시도 횟수: {retry_count}
📊 실패 원인: {failure_reason}
🔧 자동 재시도 중

🤖 자동 모니터링 시스템"""

# 기본 설정 인스턴스들
DEFAULT_SCHEDULE_CONFIG = ScheduleConfig()
DEFAULT_KAKAO_CONFIG = KakaoConfig()
DEFAULT_MONITORING_CONFIG = MonitoringConfig()
DEFAULT_MESSAGE_TEMPLATE_CONFIG = MessageTemplateConfig()

# 환경별 설정
CONFIG_PROFILES = {
    'development': {
        'schedule': ScheduleConfig(
            confirmation_delay=5,
            retry_delays=[10, 20, 30],
            max_retries=2
        ),
        'monitoring': MonitoringConfig(
            stats_update_interval=30,
            log_level="DEBUG"
        )
    },
    
    'production': {
        'schedule': ScheduleConfig(
            confirmation_delay=15,
            retry_delays=[30, 60, 120, 300],
            max_retries=5
        ),
        'monitoring': MonitoringConfig(
            stats_update_interval=300,
            log_level="INFO",
            enable_metrics=True
        )
    },
    
    'testing': {
        'schedule': ScheduleConfig(
            confirmation_delay=1,
            retry_delays=[5, 10],
            max_retries=1
        ),
        'monitoring': MonitoringConfig(
            stats_update_interval=10,
            log_level="DEBUG",
            enable_metrics=False
        )
    }
}

def get_config(profile: str = 'production') -> Dict[str, Any]:
    """환경별 설정 반환"""
    if profile not in CONFIG_PROFILES:
        profile = 'production'
    
    return CONFIG_PROFILES[profile]

def validate_config(config: Dict[str, Any]) -> bool:
    """설정 유효성 검사"""
    try:
        # 필수 설정 확인
        required_fields = [
            'schedule.regular_intervals',
            'schedule.peak_intervals', 
            'schedule.peak_hours',
            'kakao.api_url',
            'kakao.timeout'
        ]
        
        for field in required_fields:
            section, key = field.split('.')
            if section not in config or key not in config[section]:
                return False
        
        # 값 범위 확인
        schedule = config['schedule']
        if not (0 <= schedule['confirmation_delay'] <= 300):
            return False
        
        if not (1 <= schedule['max_retries'] <= 10):
            return False
        
        return True
        
    except Exception:
        return False 