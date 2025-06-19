#!/usr/bin/env python3
"""
카카오톡 자동 전송 메시지 예시 생성기
실제 데이터를 기반으로 한 다양한 상황의 메시지 예시를 제공합니다.
"""

from datetime import datetime
import json

def create_sample_data():
    """샘플 데이터 생성 (실제 장부 데이터 구조 기반)"""
    
    # 상황 1: 평상시 미션 진행 중
    normal_data = {
        "총점": 847,
        "물량점수": 520,
        "수락률점수": 327,
        "총완료": 210,
        "총거절": 26,
        "수락률": 89.2,
        
        # 피크별 미션 현황
        "아침점심피크": {"current": 18, "target": 20, "progress": 90.0},
        "오후논피크": {"current": 156, "target": 200, "progress": 78.0},
        "저녁피크": {"current": 23, "target": 25, "progress": 92.0},
        "심야논피크": {"current": 13, "target": 20, "progress": 65.0},
        
        # 라이더 데이터
        "riders": [
            {
                "name": "김라이더",
                "complete": 45,
                "아침점심피크": 12,
                "오후논피크": 18,
                "저녁피크": 10,
                "심야논피크": 5,
                "acceptance_rate": 94.2,
                "reject": 3,
                "cancel": 1,
                "contribution": 82.5
            },
            {
                "name": "박기사",
                "complete": 38,
                "아침점심피크": 8,
                "오후논피크": 15,
                "저녁피크": 12,
                "심야논피크": 3,
                "acceptance_rate": 90.5,
                "reject": 4,
                "cancel": 0,
                "contribution": 68.7
            },
            {
                "name": "이드라이버",
                "complete": 32,
                "아침점심피크": 6,
                "오후논피크": 12,
                "저녁피크": 8,
                "심야논피크": 6,
                "acceptance_rate": 86.5,
                "reject": 5,
                "cancel": 2,
                "contribution": 62.3
            },
            {
                "name": "최운전",
                "complete": 24,
                "아침점심피크": 4,
                "오후논피크": 8,
                "저녁피크": 7,
                "심야논피크": 5,
                "acceptance_rate": 82.8,
                "reject": 5,
                "cancel": 1,
                "contribution": 45.2
            },
            {
                "name": "정배송",
                "complete": 19,
                "아침점심피크": 3,
                "오후논피크": 6,
                "저녁피크": 5,
                "심야논피크": 5,
                "acceptance_rate": 79.2,
                "reject": 5,
                "cancel": 3,
                "contribution": 38.1
            }
        ]
    }
    
    # 상황 2: 미션 부족 상황
    shortage_data = {
        "총점": 623,
        "물량점수": 380,
        "수락률점수": 243,
        "총완료": 152,
        "총거절": 34,
        "수락률": 81.7,
        
        "아침점심피크": {"current": 15, "target": 20, "progress": 75.0},
        "오후논피크": {"current": 89, "target": 200, "progress": 44.5},
        "저녁피크": {"current": 18, "target": 25, "progress": 72.0},
        "심야논피크": {"current": 8, "target": 20, "progress": 40.0},
        
        "riders": [
            {
                "name": "김라이더",
                "complete": 32,
                "아침점심피크": 8,
                "오후논피크": 12,
                "저녁피크": 8,
                "심야논피크": 4,
                "acceptance_rate": 88.9,
                "reject": 4,
                "cancel": 2,
                "contribution": 65.2
            },
            {
                "name": "박기사",
                "complete": 28,
                "아침점심피크": 5,
                "오후논피크": 10,
                "저녁피크": 8,
                "심야논피크": 5,
                "acceptance_rate": 84.8,
                "reject": 5,
                "cancel": 1,
                "contribution": 58.7
            }
        ]
    }
    
    # 상황 3: 우수한 성과 (모든 미션 달성)
    excellent_data = {
        "총점": 1024,
        "물량점수": 650,
        "수락률점수": 374,
        "총완료": 265,
        "총거절": 18,
        "수락률": 93.6,
        
        "아침점심피크": {"current": 22, "target": 20, "progress": 110.0},
        "오후논피크": {"current": 205, "target": 200, "progress": 102.5},
        "저녁피크": {"current": 26, "target": 25, "progress": 104.0},
        "심야논피크": {"current": 22, "target": 20, "progress": 110.0},
        
        "riders": [
            {
                "name": "김라이더",
                "complete": 52,
                "아침점심피크": 14,
                "오후논피크": 20,
                "저녁피크": 12,
                "심야논피크": 6,
                "acceptance_rate": 96.3,
                "reject": 2,
                "cancel": 0,
                "contribution": 95.8
            },
            {
                "name": "박기사",
                "complete": 48,
                "아침점심피크": 12,
                "오후논피크": 18,
                "저녁피크": 14,
                "심야논피크": 4,
                "acceptance_rate": 94.1,
                "reject": 3,
                "cancel": 1,
                "contribution": 89.2
            }
        ]
    }
    
    return {
        "normal": normal_data,
        "shortage": shortage_data,
        "excellent": excellent_data
    }

def format_kakao_message(data, weather_info="🌤️ 안산 날씨\n현재: 맑음 🌞 18°C\n오늘: 최고 22°C, 최저 12°C\n습도: 65% | 바람: 북서 2.1m/s"):
    """실제 make_message 함수와 동일한 형태로 메시지 생성"""
    
    # 1. 미션 현황 섹션
    mission_status_parts = []
    lacking_missions = []
    
    peak_order = ['아침점심피크', '오후논피크', '저녁피크', '심야논피크']
    peak_emojis = {
        '아침점심피크': '🌅', 
        '오후논피크': '🌇', 
        '저녁피크': '🌃', 
        '심야논피크': '🌙'
    }
    
    for key in peak_order:
        peak_info = data.get(key, {'current': 0, 'target': 0})
        cur = peak_info.get('current', 0)
        tgt = peak_info.get('target', 0)
        
        if tgt == 0:
            continue
            
        if cur >= tgt:
            status = '✅ (달성)'
        else:
            status = f'❌ ({tgt-cur}건 부족)'
            lacking_missions.append(f'{key.replace("피크","").replace("논","")} {tgt-cur}건')
        
        mission_status_parts.append(f"{peak_emojis.get(key, '')} {key}: {cur}/{tgt} {status}")

    mission_status_str = "\n".join(mission_status_parts)

    # 2. 종합 정보 섹션
    summary_str = (
        f'총점: {data.get("총점", 0)}점 (물량:{data.get("물량점수", 0)}, 수락률:{data.get("수락률점수", 0)})\n'
        f'수락률: {data.get("수락률", 0.0)}% | 완료: {data.get("총완료", 0)} | 거절: {data.get("총거절", 0)}'
    )
    
    # 3. 라이더별 기여도 섹션
    rider_parts = []
    sorted_riders = sorted(
        [r for r in data.get('riders', []) if r.get('complete', 0) > 0], 
        key=lambda x: x.get('contribution', 0), 
        reverse=True
    )
    
    top_riders = sorted_riders[:3]
    other_riders = sorted_riders[3:]

    # TOP 3 라이더
    if top_riders:
        rider_parts.append("🏆 TOP 3 라이더")
        medals = ['🥇', '🥈', '🥉']
        for i, rider in enumerate(top_riders):
            bar_len = 12
            filled = int(round(rider.get('contribution', 0) / 100 * bar_len))
            bar = '■' * filled + '─' * (bar_len - filled)
            
            details = (
                f"총 {rider.get('complete', 0)}건 (아침:{rider.get('아침점심피크',0)}/오후:{rider.get('오후논피크',0)}/저녁:{rider.get('저녁피크',0)}/심야:{rider.get('심야논피크',0)})\n"
                f"    └ 수락률: {rider.get('acceptance_rate', 0.0)}% (거절:{rider.get('reject', 0)}, 취소:{rider.get('cancel', 0)})"
            )
            rider_parts.append(f"{medals[i]} {rider.get('name', '이름없음')} | [{bar}] {rider.get('contribution', 0.0)}%\n    └ {details}")

    # 기타 라이더
    if other_riders:
        if top_riders:
             rider_parts.append("─" * 15)
        rider_parts.append("🏃 그 외 라이더")
        for i, rider in enumerate(other_riders, 4):
            details = (
                f"총 {rider.get('complete', 0)}건 (아침:{rider.get('아침점심피크',0)}/오후:{rider.get('오후논피크',0)}/저녁:{rider.get('저녁피크',0)}/심야:{rider.get('심야논피크',0)})\n"
                f"   └ 수락률: {rider.get('acceptance_rate', 0.0)}% (거절:{rider.get('reject', 0)}, 취소:{rider.get('cancel', 0)})"
            )
            rider_parts.append(f"{i}. {rider.get('name', '이름없음')} ({rider.get('contribution', 0.0)}%)\n   └ {details}")

    rider_str = "\n".join(rider_parts)

    # 최종 메시지 조합
    separator = "\n" + "─" * 22 + "\n"
    
    msg = (
        f"{mission_status_str}"
        f"{separator}"
        f"{weather_info}"
        f"{separator}"
        f"{summary_str}"
        f"{separator}"
        f"{rider_str}"
    )
    
    if lacking_missions:
        msg += f"{separator}⚠️ 미션 부족: {', '.join(lacking_missions)}"

    return msg

def generate_example_messages():
    """다양한 상황의 예시 메시지 생성"""
    sample_data = create_sample_data()
    examples = {}
    
    # 상황별 메시지 생성
    situations = {
        "평상시": "normal",
        "미션부족": "shortage", 
        "우수성과": "excellent"
    }
    
    for situation_name, data_key in situations.items():
        message = format_kakao_message(sample_data[data_key])
        examples[situation_name] = message
    
    return examples

def show_example_messages():
    """예시 메시지들을 출력"""
    examples = generate_example_messages()
    
    print("=" * 60)
    print("📱 카카오톡 자동 전송 메시지 예시")
    print("=" * 60)
    
    for situation, message in examples.items():
        print(f"\n🔹 {situation} 상황:\n")
        print("📊 미션 현황 리포트")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print()
        print(message)
        print()
        print("🔄 자동 업데이트 | 🤖 G라이더 미션봇")
        print("\n" + "="*60)

def save_examples_to_file():
    """예시 메시지들을 파일로 저장"""
    examples = generate_example_messages()
    
    with open('kakao_message_examples.json', 'w', encoding='utf-8') as f:
        json.dump(examples, f, ensure_ascii=False, indent=2)
    
    print("✅ 예시 메시지가 'kakao_message_examples.json'에 저장되었습니다.")

if __name__ == "__main__":
    print("🤖 카카오톡 메시지 예시 생성기")
    print("1. 화면에 예시 출력")
    print("2. 파일로 저장")
    print("3. 둘 다")
    
    choice = input("\n선택 (1-3): ").strip()
    
    if choice in ["1", "3"]:
        show_example_messages()
    
    if choice in ["2", "3"]:
        save_examples_to_file()
    
    if choice not in ["1", "2", "3"]:
        print("잘못된 선택입니다. 기본적으로 화면에 출력합니다.")
        show_example_messages() 