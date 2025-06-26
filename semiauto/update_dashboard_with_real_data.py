#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 대시보드 실시간 데이터 업데이트 스크립트

실제 G라이더 크롤링 데이터로 대시보드를 즉시 업데이트합니다.
"""

import sys
import os
import logging

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.final_solution import GriderDataCollector, load_config
from core.dashboard_data_generator import RealGriderDashboard

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def update_dashboard_with_real_data():
    """실제 G라이더 데이터로 대시보드 업데이트"""
    try:
        logger.info("🚀 대시보드 실시간 데이터 업데이트 시작")
        
        # 1. 환경변수 로드
        config = load_config()
        logger.info("✅ 환경변수 로드 완료")
        
        # 2. G라이더 데이터 수집기 초기화
        data_collector = GriderDataCollector()
        logger.info("✅ G라이더 데이터 수집기 초기화 완료")
        
        # 3. 실제 G라이더 데이터 수집
        logger.info("🔍 실제 G라이더 데이터 수집 중...")
        grider_data = data_collector.get_grider_data()
        
        if not grider_data or grider_data.get('error'):
            logger.error(f"❌ G라이더 데이터 수집 실패: {grider_data.get('error', '알 수 없는 오류')}")
            return False
        
        logger.info(f"✅ G라이더 데이터 수집 성공: 총점 {grider_data.get('총점', 0)}점, 라이더 {len(grider_data.get('riders', []))}명")
        
        # 4. 대시보드 데이터 생성기 초기화
        dashboard_generator = RealGriderDashboard()
        logger.info("✅ 대시보드 생성기 초기화 완료")
        
        # 5. 실제 데이터로 대시보드 생성
        logger.info("🌐 실제 데이터로 대시보드 생성 중...")
        dashboard_data = dashboard_generator.generate_dashboard_data(grider_data)
        
        # 6. 대시보드 데이터 저장
        success = dashboard_generator.save_dashboard_data(dashboard_data)
        
        if success:
            logger.info("✅ 대시보드 데이터 업데이트 완료!")
            logger.info(f"📊 업데이트된 데이터:")
            logger.info(f"   • 총점: {dashboard_data.get('총점', 0)}점")
            logger.info(f"   • 총완료: {dashboard_data.get('총완료', 0)}건")
            logger.info(f"   • 수락률: {dashboard_data.get('수락률', 0):.1f}%")
            logger.info(f"   • 활성 라이더: {dashboard_data.get('active_rider_count', 0)}명")
            logger.info(f"   • TOP 라이더: {dashboard_data.get('top_rider', {}).get('name', '없음')}")
            
            # 미션 현황
            peaks = ['아침점심피크', '오후논피크', '저녁피크', '심야논피크']
            logger.info(f"📈 미션 현황:")
            for peak in peaks:
                peak_data = dashboard_data.get(peak, {})
                current = peak_data.get('current', 0)
                target = peak_data.get('target', 0)
                progress = (current / target * 100) if target > 0 else 0
                logger.info(f"   • {peak}: {current}/{target}건 ({progress:.1f}%)")
            
            return True
        else:
            logger.error("❌ 대시보드 데이터 저장 실패")
            return False
            
    except Exception as e:
        logger.error(f"❌ 대시보드 업데이트 중 오류: {e}")
        return False

def main():
    """메인 함수"""
    logger.info("🔄 대시보드 실시간 데이터 업데이트 스크립트")
    logger.info("=" * 50)
    
    success = update_dashboard_with_real_data()
    
    logger.info("=" * 50)
    if success:
        logger.info("🎉 대시보드 업데이트 성공!")
        logger.info("🌐 https://choi-ks1980.github.io/Baese/semiauto/dashboard/ 에서 확인 가능")
    else:
        logger.error("💥 대시보드 업데이트 실패!")
        sys.exit(1)

if __name__ == "__main__":
    main() 