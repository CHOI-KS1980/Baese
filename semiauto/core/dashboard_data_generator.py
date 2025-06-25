#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌐 G라이더 대시보드 데이터 생성기

실시간 대시보드를 위한 데이터 생성 및 업데이트 시스템
"""

import json
import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pytz

try:
    from core.message_config_manager import MessageConfigManager
    MESSAGE_CONFIG_AVAILABLE = True
except ImportError:
    MESSAGE_CONFIG_AVAILABLE = False

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

# 한국 시간대
KST = pytz.timezone('Asia/Seoul')

class RealGriderDashboard:
    """실제 G라이더 데이터 기반 대시보드 생성기"""
    
    def __init__(self):
        self.dashboard_dir = "dashboard"
        self.api_dir = os.path.join(self.dashboard_dir, "api")
        self.ensure_directories()
        logger.info("🚚 실제 G라이더 대시보드 생성기 초기화 완료")
    
    def ensure_directories(self):
        """필요한 디렉토리 생성"""
        os.makedirs(self.api_dir, exist_ok=True)
    
    def generate_dashboard_data(self, grider_data: Dict[str, Any]) -> Dict[str, Any]:
        """실제 G라이더 데이터를 대시보드 JSON으로 변환"""
        try:
            now = datetime.now(KST)
            
            # 실제 크롤링 데이터 필드명 사용
            dashboard_data = {
                # 기본 통계 (실제 필드명)
                "총점": grider_data.get('총점', 0),
                "물량점수": grider_data.get('물량점수', 0),
                "수락률점수": grider_data.get('수락률점수', 0),
                "총완료": grider_data.get('총완료', 0),
                "총거절": grider_data.get('총거절', 0),
                "수락률": grider_data.get('수락률', 0.0),
                
                # 피크별 미션 현황 (실제 필드명)
                "아침점심피크": grider_data.get('아침점심피크', {'current': 0, 'target': 0}),
                "오후논피크": grider_data.get('오후논피크', {'current': 0, 'target': 0}),
                "저녁피크": grider_data.get('저녁피크', {'current': 0, 'target': 0}),
                "심야논피크": grider_data.get('심야논피크', {'current': 0, 'target': 0}),
                
                # 호환성을 위한 기존 필드명도 포함
                "오전피크": grider_data.get('오전피크', grider_data.get('아침점심피크', {'current': 0, 'target': 0})),
                "오후피크": grider_data.get('오후피크', grider_data.get('오후논피크', {'current': 0, 'target': 0})),
                "심야피크": grider_data.get('심야피크', grider_data.get('심야논피크', {'current': 0, 'target': 0})),
                
                # 라이더 정보
                "riders": grider_data.get('riders', []),
                
                # 메타데이터
                "timestamp": now.isoformat(),
                "last_update": now.strftime('%Y-%m-%d %H:%M:%S'),
                "system_status": "operational",
                "data_source": "real_grider_crawling",
                
                # 원본 데이터 보존
                "raw_data": grider_data
            }
            
            # 추가 계산된 필드
            dashboard_data.update(self._calculate_additional_metrics(dashboard_data))
            
            logger.info(f"✅ 실제 G라이더 대시보드 데이터 생성 완료: 총점 {dashboard_data['총점']}점, 라이더 {len(dashboard_data['riders'])}명")
            return dashboard_data
            
        except Exception as e:
            logger.error(f"❌ 대시보드 데이터 생성 실패: {e}")
            return self._generate_error_data(str(e))
    
    def _calculate_additional_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """추가 메트릭 계산"""
        metrics = {}
        
        try:
            # 총 미션 목표 대비 달성률
            total_current = 0
            total_target = 0
            
            for peak_name in ['아침점심피크', '오후논피크', '저녁피크', '심야논피크']:
                peak_data = data.get(peak_name, {})
                total_current += peak_data.get('current', 0)
                total_target += peak_data.get('target', 0)
            
            metrics['total_mission_progress'] = (total_current / total_target * 100) if total_target > 0 else 0
            metrics['total_mission_current'] = total_current
            metrics['total_mission_target'] = total_target
            
            # 라이더 통계
            riders = data.get('riders', [])
            if riders:
                active_riders = [r for r in riders if r.get('complete', 0) > 0]
                metrics['active_rider_count'] = len(active_riders)
                metrics['total_rider_count'] = len(riders)
                
                if active_riders:
                    # 평균 완료 건수
                    avg_complete = sum(r.get('complete', 0) for r in active_riders) / len(active_riders)
                    metrics['avg_completion'] = round(avg_complete, 1)
                    
                    # 평균 수락률
                    avg_acceptance = sum(r.get('acceptance_rate', 0) for r in active_riders) / len(active_riders)
                    metrics['avg_acceptance_rate'] = round(avg_acceptance, 1)
                    
                    # TOP 라이더
                    top_rider = max(active_riders, key=lambda x: x.get('complete', 0))
                    metrics['top_rider'] = {
                        'name': top_rider.get('name', '이름없음'),
                        'complete': top_rider.get('complete', 0),
                        'acceptance_rate': top_rider.get('acceptance_rate', 0)
                    }
            else:
                metrics['active_rider_count'] = 0
                metrics['total_rider_count'] = 0
                metrics['avg_completion'] = 0
                metrics['avg_acceptance_rate'] = 0
                metrics['top_rider'] = None
            
            # 시간대별 성과 분석
            current_hour = datetime.now(KST).hour
            if 6 <= current_hour < 12:
                metrics['current_peak'] = '아침점심피크'
            elif 12 <= current_hour < 17:
                metrics['current_peak'] = '오후논피크'
            elif 17 <= current_hour < 22:
                metrics['current_peak'] = '저녁피크'
            else:
                metrics['current_peak'] = '심야논피크'
            
        except Exception as e:
            logger.warning(f"추가 메트릭 계산 실패: {e}")
        
        return metrics
    
    def _generate_error_data(self, error_message: str) -> Dict[str, Any]:
        """오류 발생시 기본 데이터 생성"""
        now = datetime.now(KST)
        
        return {
            "총점": 0,
            "물량점수": 0,
            "수락률점수": 0,
            "총완료": 0,
            "총거절": 0,
            "수락률": 0.0,
            "아침점심피크": {"current": 0, "target": 0},
            "오후논피크": {"current": 0, "target": 0},
            "저녁피크": {"current": 0, "target": 0},
            "심야논피크": {"current": 0, "target": 0},
            "riders": [],
            "timestamp": now.isoformat(),
            "last_update": now.strftime('%Y-%m-%d %H:%M:%S'),
            "system_status": "error",
            "error_message": error_message,
            "data_source": "error_fallback"
        }
    
    def save_dashboard_data(self, dashboard_data: Dict[str, Any]) -> bool:
        """대시보드 데이터를 JSON 파일로 저장"""
        try:
            # latest-data.json 파일에 저장
            output_file = os.path.join(self.api_dir, "latest-data.json")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 대시보드 데이터 저장 완료: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 대시보드 데이터 저장 실패: {e}")
            return False
    
    def generate_sample_data(self) -> Dict[str, Any]:
        """테스트용 샘플 데이터 생성"""
        sample_grider_data = {
            '총점': 87,
            '물량점수': 45,
            '수락률점수': 42,
            '총완료': 134,
            '총거절': 9,
            '수락률': 93.7,
            '아침점심피크': {'current': 35, 'target': 30},
            '오후논피크': {'current': 27, 'target': 25},
            '저녁피크': {'current': 48, 'target': 45},
            '심야논피크': {'current': 24, 'target': 20},
            'riders': [
                {
                    'name': '김철수',
                    'complete': 42,
                    'acceptance_rate': 96.8,
                    'contribution': 31.3,
                    'reject': 1,
                    'cancel': 0,
                    '아침점심피크': 12,
                    '오후논피크': 8,
                    '저녁피크': 15,
                    '심야논피크': 7
                },
                {
                    'name': '이영희',
                    'complete': 38,
                    'acceptance_rate': 94.2,
                    'contribution': 28.4,
                    'reject': 2,
                    'cancel': 1,
                    '아침점심피크': 10,
                    '오후논피크': 9,
                    '저녁피크': 13,
                    '심야논피크': 6
                },
                {
                    'name': '박민수',
                    'complete': 33,
                    'acceptance_rate': 91.7,
                    'contribution': 24.6,
                    'reject': 3,
                    'cancel': 0,
                    '아침점심피크': 8,
                    '오후논피크': 7,
                    '저녁피크': 12,
                    '심야논피크': 6
                },
                {
                    'name': '정수진',
                    'complete': 21,
                    'acceptance_rate': 87.5,
                    'contribution': 15.7,
                    'reject': 3,
                    'cancel': 2,
                    '아침점심피크': 5,
                    '오후논피크': 3,
                    '저녁피크': 8,
                    '심야논피크': 5
                }
            ],
            'timestamp': datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return self.generate_dashboard_data(sample_grider_data)

def main():
    """테스트 실행"""
    dashboard = RealGriderDashboard()
    
    # 샘플 데이터로 테스트
    print("🧪 샘플 데이터 생성 테스트...")
    sample_data = dashboard.generate_sample_data()
    
    # 저장
    success = dashboard.save_dashboard_data(sample_data)
    
    if success:
        print("✅ 실제 G라이더 대시보드 데이터 생성 및 저장 완료!")
        print(f"📊 총점: {sample_data['총점']}점")
        print(f"🏆 TOP 라이더: {sample_data.get('top_rider', {}).get('name', '없음')}")
        print(f"🚀 활성 라이더: {sample_data.get('active_rider_count', 0)}명")
    else:
        print("❌ 데이터 저장 실패")

if __name__ == "__main__":
    main() 