"""
🚨 에러 처리 및 재시도 유틸리티
에러 로깅, 재시도 로직, 예외 처리 등
"""

import time
import functools
import traceback
from typing import Callable, Any, Optional, Type, Union
from datetime import datetime
from auto_finance.utils.logger import setup_logger

logger = setup_logger(__name__)

class ErrorHandler:
    """에러 처리 및 재시도 관리 클래스"""
    
    def __init__(self, max_retries: int = 3, delay: float = 1.0):
        self.max_retries = max_retries
        self.delay = delay
        self.error_count = 0
        self.success_count = 0
    
    def handle_error(self, error: Exception, context: str = "") -> dict:
        """에러 처리 및 로깅"""
        self.error_count += 1
        
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'traceback': traceback.format_exc()
        }
        
        logger.error(f"❌ 에러 발생 ({context}): {error}")
        logger.debug(f"상세 에러 정보: {error_info}")
        
        return error_info
    
    def log_success(self, context: str = ""):
        """성공 로깅"""
        self.success_count += 1
        logger.info(f"✅ 성공 ({context})")
    
    def get_statistics(self) -> dict:
        """에러 통계 반환"""
        total = self.error_count + self.success_count
        success_rate = (self.success_count / total * 100) if total > 0 else 0
        
        return {
            'total_operations': total,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'success_rate': success_rate,
            'timestamp': datetime.now().isoformat()
        }

def retry_on_error(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Union[Type[Exception], tuple] = Exception,
    on_error: Optional[Callable] = None
):
    """재시도 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 0:
                        logger.info(f"✅ 재시도 성공 (시도 {attempt + 1}/{max_retries + 1})")
                    return result
                    
                except exceptions as e:
                    last_exception = e
                    current_delay = delay * (backoff_factor ** attempt)
                    
                    if attempt < max_retries:
                        logger.warning(
                            f"⚠️ 재시도 중 (시도 {attempt + 1}/{max_retries + 1}): "
                            f"{type(e).__name__}: {e} - {current_delay:.1f}초 후 재시도"
                        )
                        
                        if on_error:
                            try:
                                on_error(e, attempt, current_delay)
                            except Exception as callback_error:
                                logger.error(f"콜백 에러: {callback_error}")
                        
                        time.sleep(current_delay)
                    else:
                        logger.error(f"❌ 최대 재시도 횟수 초과: {type(e).__name__}: {e}")
                        raise last_exception
            
            return None
        
        return wrapper
    return decorator

def safe_execute(func: Callable, *args, default_return: Any = None, **kwargs) -> Any:
    """안전한 함수 실행"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"❌ 함수 실행 실패 ({func.__name__}): {e}")
        return default_return

def validate_input(data: Any, expected_type: Type, field_name: str = "data") -> bool:
    """입력 데이터 검증"""
    if not isinstance(data, expected_type):
        logger.error(f"❌ 입력 검증 실패: {field_name}은 {expected_type.__name__} 타입이어야 합니다")
        return False
    return True

def handle_api_error(response, context: str = "") -> bool:
    """API 응답 에러 처리"""
    if response.status_code >= 400:
        logger.error(f"❌ API 에러 ({context}): {response.status_code} - {response.text}")
        return False
    return True 