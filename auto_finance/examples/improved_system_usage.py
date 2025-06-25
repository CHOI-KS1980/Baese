"""
📚 개선된 시스템 사용 예시
메시지 전송 고도화 + 데이터 검증을 통합한 시스템 사용법
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# 개선된 시스템 임포트 (실제 구현 후 사용)
# from auto_finance.core.integrated_improvement_system import IntegratedImprovementSystem
# from auto_finance.core.advanced_message_system import MessagePriority
# from auto_finance.core.data_validator import ValidationStatus

async def example_usage():
    """개선된 시스템 사용 예시"""
    print("🚀 개선된 시스템 사용 예시")
    print("=" * 60)
    
    print("📝 이 예시는 시스템 구현 완료 후 사용할 수 있습니다.")
    print("현재는 개념적인 사용법만 보여줍니다.")
    
    # 1. 시스템 초기화
    print("\n1️⃣ 시스템 초기화")
    print("system = IntegratedImprovementSystem()")
    
    # 2. 샘플 데이터 생성
    print("\n2️⃣ 샘플 데이터 생성")
    sample_data = create_sample_data()
    print(f"생성된 데이터: {sample_data['총점']}점, {sample_data['수락률']}%")
    
    # 3. 데이터 처리 및 검증
    print("\n3️⃣ 데이터 검증 및 메시지 전송")
    print("success, message = await system.process_data_with_validation(sample_data, 'example_source')")
    print("예상 결과: 성공")
    print("예상 메시지: 데이터 검증 및 메시지 전송 성공")
    
    # 4. 시스템 상태 확인
    print("\n4️⃣ 시스템 상태 확인")
    print("overview = system.get_system_overview()")
    print("예상 결과: 시스템 건강도 정상, 메시지 전송 성공률 95%+")
    
    print("\n✅ 예시 완료!")

def create_sample_data() -> Dict[str, Any]:
    """샘플 데이터 생성"""
    return {
        '총점': 95,
        '물량점수': 40,
        '수락률점수': 55,
        '총완료': 75,
        '총거절': 5,
        '수락률': 93.8,
        '아침점심피크': {"current": 12, "target": 15},
        '오후논피크': {"current": 8, "target": 10},
        '저녁피크': {"current": 18, "target": 20},
        '심야논피크': {"current": 6, "target": 8},
        'riders': [
            {'name': '라이더1', 'score': 85},
            {'name': '라이더2', 'score': 92},
            {'name': '라이더3', 'score': 78}
        ],
        'timestamp': datetime.now().isoformat()
    }

async def advanced_usage_example():
    """고급 사용 예시"""
    print("\n🔧 고급 사용 예시")
    print("=" * 60)
    
    # 다양한 데이터 품질로 테스트
    test_cases = [
        ("정상 데이터", create_sample_data()),
        ("의심스러운 데이터", create_suspicious_data()),
        ("오류 데이터", create_error_data())
    ]
    
    for case_name, test_data in test_cases:
        print(f"\n📋 테스트 케이스: {case_name}")
        print(f"데이터: {test_data['총점']}점, {test_data['수락률']}%")
        print(f"예상 결과: {'성공' if case_name == '정상 데이터' else '실패'}")
        print(f"예상 메시지: {'데이터 검증 및 메시지 전송 성공' if case_name == '정상 데이터' else '데이터 신뢰성 부족'}")
    
    print("\n✅ 고급 예시 완료!")

def create_suspicious_data() -> Dict[str, Any]:
    """의심스러운 데이터 생성"""
    data = create_sample_data()
    data['총점'] = 200  # 비정상적으로 높음
    data['수락률'] = 99.9  # 비정상적으로 높음
    return data

def create_error_data() -> Dict[str, Any]:
    """오류 데이터 생성"""
    return {
        '총점': 'invalid',  # 잘못된 타입
        '수락률': -5,  # 잘못된 범위
        'timestamp': datetime.now().isoformat()
    }

async def monitoring_example():
    """모니터링 예시"""
    print("\n📊 모니터링 예시")
    print("=" * 60)
    
    print("🔄 연속 모니터링 시작")
    print("• 5분마다 시스템 상태 체크")
    print("• 메시지 전송 성공률 모니터링")
    print("• 데이터 검증 성공률 모니터링")
    print("• 오류 발생 시 자동 알림")
    
    print("\n✅ 모니터링 예시 완료!")

if __name__ == "__main__":
    # 기본 사용 예시
    asyncio.run(example_usage())
    
    # 고급 사용 예시
    asyncio.run(advanced_usage_example())
    
    # 모니터링 예시
    asyncio.run(monitoring_example()) 