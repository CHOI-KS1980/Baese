#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 대시보드 실시간 데이터 업데이트 스크립트

실제 G라이더 크롤링 데이터로 대시보드를 즉시 업데이트합니다.
"""

import sys
import os
import logging
import json
from datetime import datetime, time, timedelta

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.final_solution import GriderDataCollector, load_config, KoreaHolidayChecker
from core.dashboard_data_generator import RealGriderDashboard

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dashboard_generator.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RealtimeGriderDashboardGenerator:
    """실시간 G-Rider 데이터를 기반으로 대시보드 JSON을 생성하는 클래스"""

    def __init__(self, output_path='dashboard/api/latest-data.json'):
        self.output_path = output_path
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        logger.info(f"🚚 실제 G라이더 대시보드 생성기 초기화 완료. 결과는 '{self.output_path}'에 저장됩니다.")

    def generate_and_save(self, data):
        """실시간 데이터를 받아 대시보드 JSON을 생성하고 저장합니다."""
        if not data:
            logger.error("❌ 입력된 데이터가 없어 대시보드를 생성할 수 없습니다.")
            return

        logger.info(f"✅ 실제 G라이더 대시보드 데이터 생성 완료: 총점 {data.get('총점', 0)}점, 라이더 {len(data.get('riders', []))}명")
        
        # 데이터를 JSON 형식으로 저장
        try:
            with open(self.output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 대시보드 데이터 저장 완료: {self.output_path}")
        except Exception as e:
            logger.error(f"❌ 대시보드 JSON 저장 실패: {e}")

def main():
    """메인 실행 함수"""
    collector = GriderDataCollector()
    
    # 실제 G라이더 데이터를 가져옵니다.
    logger.info("🔍 실제 G라이더 데이터 수집 중...")
    grider_data = collector.get_grider_data()

    if not grider_data:
        logger.error("❌ G라이더 데이터 수집에 실패하여 대시보드 업데이트를 중단합니다.")
        return

    logger.info(f"✅ G라이더 데이터 수집 성공: 총점 {grider_data.get('총점', 0)}점, 라이더 {len(grider_data.get('riders', []))}명")
    
    # 대시보드 생성기를 초기화합니다.
    try:
        dashboard_generator = RealtimeGriderDashboardGenerator()
    except Exception as e:
        logger.error(f"❌ 대시보드 생성기 초기화 실패: {e}")
        return

    # 실제 데이터로 대시보드를 생성하고 저장합니다.
    try:
        logger.info("🌐 실제 데이터로 대시보드 생성 중...")
        dashboard_generator.generate_and_save(grider_data)

        # 업데이트된 데이터 요약 로그 (안정성 강화)
        logger.info("📊 업데이트된 데이터:")
        logger.info(f"   • 총점: {grider_data.get('총점', 'N/A')}점")
        logger.info(f"   • 총완료: {grider_data.get('총완료', 'N/A')}건")
        logger.info(f"   • 수락률: {grider_data.get('수락률', 'N/A')}%")
        logger.info(f"   • 활성 라이더: {len(grider_data.get('riders', []))}명")

    except Exception as e:
        logger.error(f"❌ 대시보드 업데이트 중 오류: {e}")
        # 실패하더라도 계속 진행하도록 return 대신 pass 처리
        pass

if __name__ == '__main__':
    logger.info("🔄 대시보드 실시간 데이터 업데이트 스크립트")
    logger.info("==================================================")
    try:
        main()
        logger.info("✅ 대시보드 데이터 업데이트 완료!")
    except Exception as e:
        logger.error(f"💥 대시보드 업데이트 실패!: {e}")
    logger.info("==================================================") 