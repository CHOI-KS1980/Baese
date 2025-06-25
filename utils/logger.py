"""
📝 로깅 유틸리티
구조화된 로깅, 로그 레벨 관리, 로그 파일 관리 등
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from loguru import logger
from auto_finance.config.settings import LOG_LEVEL, LOG_FORMAT, LOG_FILE

def setup_logger(name: str = __name__, level: str = LOG_LEVEL) -> logger:
    """로거 설정"""
    # 기존 핸들러 제거
    logger.remove()
    
    # 콘솔 출력 설정
    logger.add(
        sys.stdout,
        format=LOG_FORMAT,
        level=level,
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # 파일 출력 설정
    if LOG_FILE:
        log_dir = Path(LOG_FILE).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            LOG_FILE,
            format=LOG_FORMAT,
            level=level,
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )
    
    return logger

def get_logger(name: str = __name__) -> logger:
    """로거 인스턴스 반환"""
    return logger.bind(name=name)

def log_performance(func):
    """성능 측정 데코레이터"""
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"⏱️ {func.__name__} 실행 시간: {duration:.2f}초")
        return result
    return wrapper

def log_error_with_context(error: Exception, context: dict = None):
    """에러 로깅 with 컨텍스트"""
    error_info = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "timestamp": datetime.now().isoformat(),
        "context": context or {}
    }
    
    logger.error(f"❌ 에러 발생: {json.dumps(error_info, ensure_ascii=False, indent=2)}")

def log_system_status(status: dict):
    """시스템 상태 로깅"""
    status_info = {
        "timestamp": datetime.now().isoformat(),
        "status": status
    }
    
    logger.info(f"📊 시스템 상태: {json.dumps(status_info, ensure_ascii=False, indent=2)}")

# 전역 로거 설정
setup_logger() 