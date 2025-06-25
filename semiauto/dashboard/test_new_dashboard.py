#!/usr/bin/env python3
"""
새로운 G라이더 대시보드 테스트
실제 데이터 구조에 맞춘 대시보드 시스템 테스트
"""

import os
import json
import sys
from datetime import datetime

# 경로 설정
sys.path.append('..')
sys.path.append('../core')

def create_test_data():
    """실제 G라이더 데이터 구조에 맞는 테스트 데이터 생성"""
    return {
        '총점': 92,
        '물량점수': 48,
        '수락률점수': 44,
        '총완료': 156,
        '총거절': 12,
        '수락률': 92.9,
        '아침점심피크': {'current': 38, 'target': 35},
        '오후논피크': {'current': 32, 'target': 30},
        '저녁피크': {'current': 52, 'target': 50},
        '심야논피크': {'current': 34, 'target': 25},
        'riders': [
            {
                'name': '이재현',
                'complete': 48,
                'acceptance_rate': 97.9,
                'contribution': 30.8,
                'reject': 1,
                'cancel': 0,
                '아침점심피크': 14,
                '오후논피크': 10,
                '저녁피크': 16,
                '심야논피크': 8
            },
            {
                'name': '김민수',
                'complete': 41,
                'acceptance_rate': 95.3,
                'contribution': 26.3,
                'reject': 2,
                'cancel': 0,
                '아침점심피크': 12,
                '오후논피크': 9,
                '저녁피크': 14,
                '심야논피크': 6
            },
            {
                'name': '박서연',
                'complete': 35,
                'acceptance_rate': 91.7,
                'contribution': 22.4,
                'reject': 3,
                'cancel': 1,
                '아침점심피크': 8,
                '오후논피크': 8,
                '저녁피크': 12,
                '심야논피크': 7
            },
            {
                'name': '정우진',
                'complete': 32,
                'acceptance_rate': 88.9,
                'contribution': 20.5,
                'reject': 4,
                'cancel': 0,
                '아침점심피크': 4,
                '오후논피크': 5,
                '저녁피크': 10,
                '심야논피크': 13
            }
        ],
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def transform_to_dashboard_format(grider_data):
    """G라이더 데이터를 대시보드 형식으로 변환"""
    now = datetime.now()
    
    # 추가 계산된 필드
    total_current = 0
    total_target = 0
    
    for peak_name in ['아침점심피크', '오후논피크', '저녁피크', '심야논피크']:
        peak_data = grider_data.get(peak_name, {})
        total_current += peak_data.get('current', 0)
        total_target += peak_data.get('target', 0)
    
    # 라이더 통계
    riders = grider_data.get('riders', [])
    active_riders = [r for r in riders if r.get('complete', 0) > 0]
    
    dashboard_data = {
        # 실제 크롤링 데이터 필드명
        "총점": grider_data.get('총점', 0),
        "물량점수": grider_data.get('물량점수', 0),
        "수락률점수": grider_data.get('수락률점수', 0),
        "총완료": grider_data.get('총완료', 0),
        "총거절": grider_data.get('총거절', 0),
        "수락률": grider_data.get('수락률', 0.0),
        
        # 피크별 미션 현황
        "아침점심피크": grider_data.get('아침점심피크', {'current': 0, 'target': 0}),
        "오후논피크": grider_data.get('오후논피크', {'current': 0, 'target': 0}),
        "저녁피크": grider_data.get('저녁피크', {'current': 0, 'target': 0}),
        "심야논피크": grider_data.get('심야논피크', {'current': 0, 'target': 0}),
        
        # 라이더 정보
        "riders": riders,
        
        # 추가 계산된 필드
        "total_mission_progress": (total_current / total_target * 100) if total_target > 0 else 0,
        "total_mission_current": total_current,
        "total_mission_target": total_target,
        "active_rider_count": len(active_riders),
        "total_rider_count": len(riders),
        
        # TOP 라이더
        "top_rider": max(active_riders, key=lambda x: x.get('complete', 0)) if active_riders else None,
        
        # 메타데이터
        "timestamp": now.isoformat(),
        "last_update": now.strftime('%Y-%m-%d %H:%M:%S'),
        "system_status": "operational",
        "data_source": "real_grider_test",
        
        # 원본 데이터 보존
        "raw_data": grider_data
    }
    
    return dashboard_data

def save_dashboard_data(dashboard_data):
    """대시보드 데이터를 JSON 파일로 저장"""
    try:
        # api 디렉토리 생성
        os.makedirs('api', exist_ok=True)
        
        # latest-data.json 파일에 저장
        output_file = 'api/latest-data.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 대시보드 데이터 저장 완료: {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ 대시보드 데이터 저장 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🚚 새로운 G라이더 대시보드 테스트 시작")
    print("=" * 50)
    
    # 1. 테스트 데이터 생성
    print("1️⃣ 실제 G라이더 데이터 구조로 테스트 데이터 생성...")
    test_data = create_test_data()
    print(f"   📊 총점: {test_data['총점']}점")
    print(f"   ✅ 총완료: {test_data['총완료']}건")
    print(f"   🏆 라이더: {len(test_data['riders'])}명")
    
    # 2. 대시보드 형식으로 변환
    print("\n2️⃣ 대시보드 형식으로 데이터 변환...")
    dashboard_data = transform_to_dashboard_format(test_data)
    print(f"   🎯 총 미션 진행률: {dashboard_data['total_mission_progress']:.1f}%")
    print(f"   🚀 활성 라이더: {dashboard_data['active_rider_count']}명")
    
    if dashboard_data['top_rider']:
        top = dashboard_data['top_rider']
        print(f"   🏅 TOP 라이더: {top['name']} ({top['complete']}건)")
    
    # 3. 데이터 저장
    print("\n3️⃣ 대시보드 데이터 저장...")
    success = save_dashboard_data(dashboard_data)
    
    if success:
        print("\n✅ 모든 테스트 완료!")
        print("🌐 이제 대시보드를 브라우저에서 열어보세요:")
        print("   file:///path/to/dashboard/index.html")
    else:
        print("\n❌ 테스트 실패")

if __name__ == "__main__":
    main() 