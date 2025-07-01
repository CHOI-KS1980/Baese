import os
import sys
import logging
from dotenv import load_dotenv

# --- 모듈 경로 문제 해결 ---
# 현재 파일의 절대 경로를 기준으로 프로젝트 루트 경로를 계산하여 sys.path에 추가
# 이렇게 하면 'semiauto'나 'weather_service' 같은 최상위 모듈을 어디서든 임포트할 수 있습니다.
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
# -------------------------

from semiauto.core.main_executor import GriderAutoSender, KSTFormatter, get_korea_time
from weather_service import WeatherService

def setup_logging():
    """로그 설정"""
    log_formatter = KSTFormatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)

def main():
    """메인 실행 함수"""
    load_dotenv()
    setup_logging()
    
    logging.info("="*50)
    logging.info("G-Rider 자동화 스크립트 시작 (run_sender.py)")
    logging.info(f"실행 시간: {get_korea_time().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("="*50)
    
    try:
        # 1. 날씨 서비스 객체 생성
        weather_service_instance = WeatherService()

        # 2. GriderAutoSender에 날씨 서비스 객체 주입
        executor = GriderAutoSender(
            weather_service=weather_service_instance,
            rest_api_key=os.getenv("KAKAO_REST_API_KEY"),
            refresh_token=os.getenv("KAKAO_REFRESH_TOKEN")
        )
        success = executor.send_report()
        
        logging.info("="*50)
        logging.info("G-Rider 자동화 스크립트 종료")
        logging.info("="*50)

        if not success:
            logging.error("스크립트 실행 중 오류가 발생하여 실패로 종료합니다.")
            sys.exit(1)
            
    except Exception as e:
        logging.critical(f"스크립트 실행 중 치명적인 오류 발생: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 