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
    
    def generate_message_data(self, dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
        """대시보드 데이터를 기반으로 맞춤형 메시지 생성"""
        try:
            # MessageConfigManager 사용 (사용 가능한 경우) - 현재 주석 처리
            # if MESSAGE_CONFIG_AVAILABLE:
            #     try:
            #         config_manager = MessageConfigManager()
            #         message_data = config_manager.generate_custom_message(dashboard_data)
            #         logger.info("✅ MessageConfigManager로 맞춤형 메시지 생성 완료")
            #         return message_data
            #     except Exception as e:
            #         logger.warning(f"MessageConfigManager 사용 실패: {e}, 기본 메시지 사용")
            
            # 기본 메시지 생성
            return self._generate_default_message(dashboard_data)
            
        except Exception as e:
            logger.error(f"❌ 메시지 데이터 생성 실패: {e}")
            return self._generate_fallback_message(dashboard_data)
    
    def _generate_default_message(self, dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
        """기존 final_solution.py와 동일한 메시지 포맷으로 생성"""
        now = datetime.now(KST)
        current_hour = now.hour
        current_minute = now.minute
        
        # 시간대별 인사말
        greeting = self._get_time_based_greeting(current_hour, current_minute)
        
        # 휴일/평일 정보 확인
        is_weekend_or_holiday = self._is_weekend_or_holiday(now)
        day_type = "휴일" if is_weekend_or_holiday else "평일"
        
        # 날씨 정보
        weather_info = self._get_weather_info()
        
        # 1. 미션 현황
        peak_order = ['아침점심피크', '오후논피크', '저녁피크', '심야논피크']
        peak_emojis = {
            '아침점심피크': '🌅', 
            '오후논피크': '🌇', 
            '저녁피크': '🌃', 
            '심야논피크': '🌙'
        }
        
        mission_parts = []
        lacking_missions = []
        
        # 03:00~06:00는 미션 준비 시간
        if 3 <= current_hour < 6:
            holiday_info = " (주말/휴일)" if is_weekend_or_holiday else " (평일)"
            mission_parts.append(f"🛌 미션 준비 시간입니다{holiday_info} - 06:00부터 미션 정보가 표시됩니다")
            preparation_time = True
        else:
            preparation_time = False
        
        if not preparation_time:
            # 시작된 미션만 표시
            started_missions = []
            
            for key in peak_order:
                peak_info = dashboard_data.get(key, {'current': 0, 'target': 0})
                cur = peak_info.get('current', 0)
                tgt = peak_info.get('target', 0)
                
                if tgt == 0:
                    continue
                
                # 미션 시간대 확인
                mission_started = False
                mission_active = False
                
                if key == '아침점심피크':
                    if is_weekend_or_holiday:
                        mission_started = current_hour >= 6
                        mission_active = 6 <= current_hour < 14
                        peak_time_info = "06:00-14:00 (휴일)"
                    else:
                        mission_started = current_hour >= 6
                        mission_active = 6 <= current_hour < 13
                        peak_time_info = "06:00-13:00 (평일)"
                elif key == '오후논피크':
                    if is_weekend_or_holiday:
                        mission_started = current_hour >= 14
                        mission_active = 14 <= current_hour < 17
                        peak_time_info = "14:00-17:00 (휴일)"
                    else:
                        mission_started = current_hour >= 13
                        mission_active = 13 <= current_hour < 17
                        peak_time_info = "13:00-17:00 (평일)"
                elif key == '저녁피크':
                    mission_started = current_hour >= 17
                    mission_active = 17 <= current_hour < 20
                    peak_time_info = "17:00-20:00"
                elif key == '심야논피크':
                    mission_started = current_hour >= 20 or current_hour < 3
                    mission_active = current_hour >= 20 or current_hour < 3
                    peak_time_info = "20:00-03:00 (익일)"
                
                # 아직 시작되지 않은 미션은 표시하지 않음
                if not mission_started:
                    continue
                
                # 상태 결정
                if cur >= tgt:
                    status = '✅'
                else:
                    if mission_active:
                        status = f'⏳ ({tgt-cur}건 남음)'
                        lacking_missions.append(f'{key.replace("피크","").replace("논","")} {tgt-cur}건')
                    else:
                        status = f'❌ ({tgt-cur}건 부족)'
                
                mission_line = f"{peak_emojis.get(key, '')} {key}: {cur}/{tgt} {status}"
                started_missions.append(mission_line)
            
            # 금일 미션 현황 표시
            if started_missions:
                mission_parts.append("🎯 금일 미션 현황")
                mission_parts.extend(started_missions)
            else:
                mission_parts.append("🎯 금일 미션 현황")
                mission_parts.append("⏰ 미션 시작 전입니다")
                mission_parts.append("첫 번째 미션은 06:00부터 시작됩니다")
        
        # 2. 기본 정보
        total_score = dashboard_data.get("총점", 0)
        quantity_score = dashboard_data.get("물량점수", 0)
        acceptance_score = dashboard_data.get("수락률점수", 0)
        acceptance_rate = dashboard_data.get("수락률", 0.0)
        total_completed = dashboard_data.get("총완료", 0)
        total_rejected = dashboard_data.get("총거절", 0)
        
        summary_parts = [
            "📊 금주 미션 수행 예상점수",
            f"총점: {total_score}점 (물량:{quantity_score}, 수락률:{acceptance_score})",
            f"수락률: {acceptance_rate:.1f}% | 완료: {total_completed} | 거절: {total_rejected}"
        ]
        
        # 3. 라이더 순위
        sorted_riders = sorted(
            [r for r in dashboard_data.get('riders', []) if r.get('complete', 0) > 0], 
            key=lambda x: x.get('contribution', 0), 
            reverse=True
        )
        
        rider_parts = []
        
        if sorted_riders:
            active_rider_count = len(sorted_riders)
            rider_parts.append(f"🏆 라이더 순위 (운행 : {active_rider_count}명)")
            medals = ['🥇', '🥈', '🥉']
            
            # 3위까지만 표시
            for i, rider in enumerate(sorted_riders[:3]):
                name = rider.get('name', '이름없음')
                contribution = rider.get('contribution', 0)
                
                # 피크별 기여도
                morning = rider.get('아침점심피크', 0)
                afternoon = rider.get('오후논피크', 0)
                evening = rider.get('저녁피크', 0)
                midnight = rider.get('심야논피크', 0)
                
                acceptance_rate_rider = rider.get('acceptance_rate', 0.0)
                reject = rider.get('reject', 0)
                cancel = rider.get('cancel', 0)
                complete = rider.get('complete', 0)
                
                # 진행률 바 생성
                bar_len = 10
                filled = int(round(contribution / 10))
                if filled > 10:
                    filled = 10
                
                percent_text = f"{contribution:.1f}%"
                remaining_dashes = bar_len - filled - len(percent_text)
                
                if remaining_dashes > 0:
                    bar = '■' * filled + '─' * remaining_dashes + percent_text
                else:
                    bar = '■' * max(0, bar_len - len(percent_text)) + percent_text
                
                rider_parts.append(f"**{medals[i]} {name}** | [{bar}]")
                rider_parts.append(f"    총 {complete}건 (🌅{morning} 🌇{afternoon} 🌃{evening} 🌙{midnight})")
                rider_parts.append(f"    수락률: {acceptance_rate_rider:.1f}% (거절:{reject}, 취소:{cancel})")
        
        # 전체 라이더 통계
        total_complete_today = sum(rider.get('complete', 0) for rider in dashboard_data.get('riders', []))
        total_reject_today = sum(rider.get('reject', 0) for rider in dashboard_data.get('riders', []))
        total_cancel_today = sum(rider.get('cancel', 0) for rider in dashboard_data.get('riders', []))
        total_delivery_cancel_today = sum(rider.get('delivery_cancel', 0) for rider in dashboard_data.get('riders', []))
        
        total_cancel_all = total_cancel_today + total_delivery_cancel_today
        total_attempts = total_complete_today + total_reject_today + total_cancel_all
        overall_acceptance_rate = (total_complete_today / total_attempts * 100) if total_attempts > 0 else 0.0
        total_reject_combined = total_reject_today + total_cancel_all
        
        mission_summary_parts = [
            "📈 금일 수행 내역",
            f"수락률: {overall_acceptance_rate:.1f}% | 완료: {total_complete_today} | 거절: {total_reject_combined}"
        ]
        mission_summary = "\n".join(mission_summary_parts)
        
        # 최종 메시지 조합
        message_parts = [
            greeting,
            "",
            f"📊 심플 배민 플러스 미션 알리미 ({day_type})",
            "",
            "\n".join(mission_parts),
            "",
            weather_info,
            "",
            mission_summary,
            "",
            "\n".join(summary_parts),
            "",
            "\n".join(rider_parts)
        ]
        
        if lacking_missions:
            message_parts.append("")
            message_parts.append(f"⚠️ 미션 부족: {', '.join(lacking_missions)}")
        
        message_parts.append("")
        message_parts.append("🤖 자동화 시스템에 의해 전송됨")
        
        full_message = "\n".join(message_parts)
        
        return {
            'full_message': full_message,
            'settings': {
                'template': 'original',
                'format': 'detailed'
            },
            'timestamp': now.isoformat()
        }
    
    def _get_time_based_greeting(self, hour, minute):
        """시간대별 인사말 생성"""
        
        # 10:00 하루 시작 - 특별 인사말
        if hour == 10 and minute == 0:
            return """🌅 좋은 아침입니다!
오늘도 심플 배민 플러스와 함께 힘찬 하루를 시작해보세요!
안전운행하시고 좋은 하루 되세요! 💪"""
        
        # 00:00 하루 마무리 - 특별 인사말
        elif hour == 0 and minute == 0:
            return """🌙 오늘 하루도 정말 수고하셨습니다!
안전하게 귀가하시고 푹 쉬세요.
내일도 좋은 하루 되시길 바랍니다! 🙏"""
        
        # 일반 30분 간격 메시지
        else:
            time_greetings = {
                (10, 30): "☀️ 오전 업무 시작! 오늘도 화이팅하세요!",
                (11, 0): "🌅 오전 11시! 점심 피크 준비 시간입니다!",
                (11, 30): "🌅 점심 피크 시간이 다가오고 있어요!",
                (12, 0): "🍽️ 정오 12시! 점심 피크 시작!",
                (12, 30): "🍽️ 점심 피크 시간! 안전운행 부탁드려요!",
                (13, 0): "⏰ 오후 1시! 점심 피크 마무리 시간!",
                (13, 30): "⏰ 오후 시간대 접어들었습니다!",
                (14, 0): "🌇 오후 2시! 논피크 시간대!",
                (14, 30): "🌇 오후 논피크 시간이에요!",
                (15, 0): "☕ 오후 3시! 잠시 휴식 시간!",
                (15, 30): "☕ 오후 3시 30분, 잠시 휴식하세요!",
                (16, 0): "🌆 오후 4시! 저녁 피크 준비!",
                (16, 30): "🌆 저녁 피크 준비 시간입니다!",
                (17, 0): "🌃 오후 5시! 저녁 피크 시작!",
                (17, 30): "🌃 저녁 피크 시간! 주문이 많을 예정이에요!",
                (18, 0): "🍽️ 저녁 6시! 저녁 식사 시간!",
                (18, 30): "🍽️ 저녁 식사 시간! 바쁜 시간대입니다!",
                (19, 0): "🌉 저녁 7시! 피크 마무리 시간!",
                (19, 30): "🌉 저녁 피크 마무리 시간이에요!",
                (20, 0): "🌙 저녁 8시! 심야 논피크 시작!",
                (20, 30): "🌙 심야 논피크 시간대 시작!",
                (21, 0): "🌃 밤 9시! 오늘도 수고하고 계세요!",
                (21, 30): "🌃 밤 9시 30분, 오늘도 수고하고 계세요!",
                (22, 0): "🌙 밤 10시! 심야 시간대 안전운행!",
                (22, 30): "🌙 심야 시간대, 안전운행 최우선!",
                (23, 0): "🌌 밤 11시! 하루 마무리가 다가와요!",
                (23, 30): "🌌 하루 마무리 시간이 다가오고 있어요!",
                # 익일 새벽 시간대 추가
                (0, 30): "🌙 새벽 12시 30분, 오늘도 정말 수고하셨습니다!",
                (1, 0): "🌅 새벽 1시, 심야 미션 진행중입니다!",
                (1, 30): "🌅 새벽 1시 30분, 안전운행 최우선입니다!",
                (2, 0): "🌅 새벽 2시, 곧 하루가 마무리됩니다!",
                (2, 30): "🌅 새벽 2시 30분, 마지막 미션 시간입니다!",
                (3, 0): "🌅 새벽 3시, 오늘 하루도 정말 고생하셨습니다!"
            }
            
            greeting = time_greetings.get((hour, minute), f"⏰ {hour:02d}:{minute:02d} 현재 상황을 알려드립니다!")
            return greeting
    
    def _is_weekend_or_holiday(self, dt):
        """주말 또는 휴일 판정"""
        # 주말 체크 (토요일=5, 일요일=6)
        if dt.weekday() >= 5:
            return True
        
        # 기본 공휴일 체크 (2025년)
        holidays_2025 = [
            (1, 1), (1, 27), (1, 28), (1, 29), (1, 30),  # 신정, 설날 연휴
            (3, 1), (3, 3),  # 삼일절, 대체공휴일
            (5, 5), (5, 6),  # 어린이날, 부처님오신날, 대체공휴일
            (6, 3), (6, 6),  # 임시공휴일, 현충일
            (8, 15),  # 광복절
            (10, 3), (10, 5), (10, 6), (10, 7), (10, 8), (10, 9),  # 개천절, 추석 연휴, 한글날
            (12, 25)  # 크리스마스
        ]
        
        for month, day in holidays_2025:
            if dt.month == month and dt.day == day:
                return True
                
        return False
    
    def _get_weather_info(self):
        """날씨 정보 가져오기"""
        try:
            # 간단한 날씨 정보
            return f"""🌍 오늘의 날씨 (기상청)
🌅 오전: ☀️ 18~22°C
🌇 오후: ☀️ 20~24°C"""
        except Exception as e:
            return "⚠️ 날씨 정보를 가져올 수 없습니다."
    
    def _generate_fallback_message(self, dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
        """에러 발생시 대체 메시지"""
        now = datetime.now(KST)
        
        fallback_message = f"""🚚 G라이더 미션 현황
📅 {now.strftime('%Y-%m-%d %H:%M')}

⚠️ 데이터 처리 중 문제가 발생했습니다.
📞 시스템 점검이 필요할 수 있습니다.

💪 오늘도 화이팅!"""
        
        return {
            'full_message': fallback_message,
            'settings': {
                'template': 'fallback',
                'format': 'error'
            },
            'timestamp': now.isoformat()
        }
    
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

# 호환성을 위한 클래스 alias
DashboardDataGenerator = RealGriderDashboard

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