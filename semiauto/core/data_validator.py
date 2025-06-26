#!/usr/bin/env python3
"""
🔍 데이터 검증 및 정확성 보장 시스템
- 실시간 데이터 검증
- 날짜 정확성 체크
- 교차 검증 시스템
- 이상치 탐지
"""

import json
import os
import hashlib
from datetime import datetime, timedelta
import pytz
import logging
from typing import Dict, List, Optional, Tuple, Any
import re

# 한국시간 설정
KST = pytz.timezone('Asia/Seoul')

logger = logging.getLogger(__name__)

class DataFreshnessChecker:
    """데이터 신선도 검증"""
    
    def __init__(self):
        self.cache_file = 'data_cache.json'
        self.max_age_minutes = 30  # 데이터 최대 허용 시간 (30분)
    
    def get_data_hash(self, data: Dict) -> str:
        """데이터 해시 생성"""
        # 시간 관련 정보는 제외하고 해시 생성
        filtered_data = {k: v for k, v in data.items() 
                        if k not in ['timestamp', 'crawl_time', 'sent_at']}
        data_str = json.dumps(filtered_data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(data_str.encode('utf-8')).hexdigest()
    
    def is_data_fresh(self, data: Dict) -> Tuple[bool, str]:
        """데이터 신선도 확인"""
        now = datetime.now(KST)
        
        # 1. 타임스탬프 확인
        if 'timestamp' in data:
            try:
                data_time = datetime.fromisoformat(data['timestamp'])
                if data_time.tzinfo is None:
                    data_time = data_time.replace(tzinfo=KST)
                
                age_minutes = (now - data_time).total_seconds() / 60
                
                if age_minutes > self.max_age_minutes:
                    return False, f"데이터가 너무 오래됨 ({age_minutes:.1f}분 전)"
                
            except Exception as e:
                return False, f"타임스탬프 파싱 오류: {e}"
        
        # 2. 날짜 정보 확인 (미션 데이터)
        if 'mission_date' in data:
            try:
                mission_date = datetime.strptime(data['mission_date'], '%Y-%m-%d').date()
                today = now.date()
                
                if mission_date != today:
                    return False, f"미션 날짜 불일치 (데이터: {mission_date}, 오늘: {today})"
                    
            except Exception as e:
                return False, f"미션 날짜 파싱 오류: {e}"
        
        return True, "데이터 신선도 양호"
    
    def save_data_cache(self, data: Dict):
        """데이터 캐시 저장"""
        try:
            cache_data = {
                'data': data,
                'hash': self.get_data_hash(data),
                'cached_at': datetime.now(KST).isoformat(),
                'mission_date': data.get('mission_date', datetime.now(KST).strftime('%Y-%m-%d'))
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"💾 데이터 캐시 저장 완료: {cache_data['hash'][:8]}")
            
        except Exception as e:
            logger.error(f"❌ 데이터 캐시 저장 실패: {e}")
    
    def load_data_cache(self) -> Optional[Dict]:
        """데이터 캐시 로드"""
        if not os.path.exists(self.cache_file):
            return None
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 캐시 데이터 유효성 확인
            cached_at = datetime.fromisoformat(cache_data['cached_at'])
            age_minutes = (datetime.now(KST) - cached_at).total_seconds() / 60
            
            if age_minutes > self.max_age_minutes:
                logger.warning(f"⚠️ 캐시 데이터 만료 ({age_minutes:.1f}분 전)")
                return None
            
            return cache_data
            
        except Exception as e:
            logger.error(f"❌ 데이터 캐시 로드 실패: {e}")
            return None

class DataConsistencyChecker:
    """데이터 일관성 검증"""
    
    def __init__(self):
        self.validation_rules = self._load_validation_rules()
    
    def _load_validation_rules(self) -> Dict:
        """검증 규칙 로드"""
        return {
            'score_ranges': {
                '총점': (0, 200),
                '물량점수': (0, 100),
                '수락률점수': (0, 100),
                '수락률': (0.0, 100.0)
            },
            'mission_ranges': {
                'current': (0, 500),
                'target': (0, 200)
            },
            'rider_ranges': {
                'contribution': (0.0, 100.0),
                'complete': (0, 100),
                'reject': (0, 50),
                'cancel': (0, 30)
            }
        }
    
    def validate_score_data(self, data: Dict) -> Tuple[bool, List[str]]:
        """점수 데이터 검증"""
        errors = []
        
        for field, (min_val, max_val) in self.validation_rules['score_ranges'].items():
            if field in data:
                value = data[field]
                
                if not isinstance(value, (int, float)):
                    errors.append(f"{field}: 숫자가 아님 ({type(value)})")
                    continue
                
                if not (min_val <= value <= max_val):
                    errors.append(f"{field}: 범위 초과 ({value}, 허용: {min_val}-{max_val})")
        
        return len(errors) == 0, errors
    
    def validate_mission_data(self, data: Dict) -> Tuple[bool, List[str]]:
        """미션 데이터 검증"""
        errors = []
        
        mission_types = ['아침점심피크', '오후논피크', '저녁피크', '심야논피크']
        
        for mission_type in mission_types:
            if mission_type in data:
                mission_data = data[mission_type]
                
                if not isinstance(mission_data, dict):
                    errors.append(f"{mission_type}: dict 타입이 아님")
                    continue
                
                for field, (min_val, max_val) in self.validation_rules['mission_ranges'].items():
                    if field in mission_data:
                        value = mission_data[field]
                        
                        if not isinstance(value, (int, float)):
                            errors.append(f"{mission_type}.{field}: 숫자가 아님")
                            continue
                        
                        if not (min_val <= value <= max_val):
                            errors.append(f"{mission_type}.{field}: 범위 초과 ({value})")
                
                # current가 target보다 너무 크면 이상
                if 'current' in mission_data and 'target' in mission_data:
                    current = mission_data['current']
                    target = mission_data['target']
                    
                    if current > target * 2:  # target의 2배 초과시 경고
                        errors.append(f"{mission_type}: current({current})가 target({target})의 2배 초과")
        
        return len(errors) == 0, errors
    
    def validate_rider_data(self, data: Dict) -> Tuple[bool, List[str]]:
        """라이더 데이터 검증"""
        errors = []
        
        if 'riders' not in data:
            return True, []
        
        riders = data['riders']
        if not isinstance(riders, list):
            return False, ["riders가 list 타입이 아님"]
        
        for i, rider in enumerate(riders):
            if not isinstance(rider, dict):
                errors.append(f"rider[{i}]: dict 타입이 아님")
                continue
            
            # 필수 필드 확인
            if 'name' not in rider or not rider['name']:
                errors.append(f"rider[{i}]: 이름 없음")
            
            # 숫자 필드 검증
            for field, (min_val, max_val) in self.validation_rules['rider_ranges'].items():
                if field in rider:
                    value = rider[field]
                    
                    if not isinstance(value, (int, float)):
                        errors.append(f"rider[{i}].{field}: 숫자가 아님")
                        continue
                    
                    if not (min_val <= value <= max_val):
                        errors.append(f"rider[{i}].{field}: 범위 초과 ({value})")
        
        return len(errors) == 0, errors

class DataCrossValidator:
    """교차 검증 시스템"""
    
    def __init__(self):
        self.comparison_tolerance = 5  # 오차 허용 범위 (건수)
    
    def compare_daily_totals(self, data: Dict) -> Tuple[bool, List[str]]:
        """일일 데이터 교차 검증: 미션 합계 vs 라이더 합계"""
        errors = []
        
        # 1. 개별 미션의 'current' 합계 계산
        mission_types = ['아침점심피크', '오후논피크', '저녁피크', '심야논피크']
        mission_total_current = 0
        for mission_type in mission_types:
            if mission_type in data and isinstance(data[mission_type], dict):
                mission_total_current += data[mission_type].get('current', 0)
        
        # 2. 개별 라이더의 'complete' 합계 계산
        rider_total_complete = 0
        if 'riders' in data and isinstance(data['riders'], list):
            for rider in data['riders']:
                if isinstance(rider, dict):
                    rider_total_complete += rider.get('complete', 0)

        # 3. 두 합계 비교
        if mission_total_current != rider_total_complete:
            # 허용 오차 범위 내에 있는지 확인
            if abs(mission_total_current - rider_total_complete) > self.comparison_tolerance:
                error_msg = f"미션 합계와 라이더 합계 불일치: 미션({mission_total_current}) vs 라이더({rider_total_complete})"
                errors.append(error_msg)
            else:
                logger.info(f"🤔 미션-라이더 합계에 약간의 차이가 있지만 허용 범위 내입니다: 미션({mission_total_current}) vs 라이더({rider_total_complete})")

        # '총완료' 필드는 주간 누적 데이터이므로 일일 검증에서 제외합니다.
        # 대신, 이 값이 비정상적으로 0인 경우만 경고합니다.
        if '총완료' in data and data['총완료'] == 0 and rider_total_complete > 0:
            warn_msg = f"주간 총완료가 0이지만, 라이더 일일 완료는 {rider_total_complete}건입니다."
            # 이것은 에러가 아닌 경고이므로 errors 리스트에는 추가하지 않습니다.
            logger.warning(f"⚠️ 교차검증 경고: {warn_msg}")
            
        return len(errors) == 0, errors

    def compare_mission_totals(self, data: Dict) -> Tuple[bool, List[str]]:
        """[사용되지 않음] 미션 총합과 개별 미션 합계 비교"""
        # 이 함수는 더 이상 사용되지 않으며, compare_daily_totals로 대체되었습니다.
        return True, []

    def compare_rider_contributions(self, data: Dict) -> Tuple[bool, List[str]]:
        """라이더 기여도와 완료 건수 비교"""
        errors = []
        
        if 'riders' not in data:
            return True, []
        
        riders = data['riders']
        total_contribution = sum(rider.get('contribution', 0) for rider in riders)
        
        # 기여도 합계가 100%를 크게 초과하면 이상
        if total_contribution > 120:  # 120% 초과시 경고
            errors.append(f"라이더 기여도 합계 이상: {total_contribution:.1f}%")
        
        # 개별 라이더 기여도가 음수이거나 너무 크면 이상
        for i, rider in enumerate(riders):
            contribution = rider.get('contribution', 0)
            if contribution < 0 or contribution > 100:
                errors.append(f"라이더[{i}] 기여도 이상: {contribution:.1f}%")
        
        return len(errors) == 0, errors

class EnhancedDataValidator:
    """향상된 데이터 검증기 (상태 저장 및 자동 수정)"""
    
    def __init__(self):
        self.freshness_checker = DataFreshnessChecker()
        self.consistency_checker = DataConsistencyChecker()
        self.cross_validator = DataCrossValidator()
        self.validation_history = []
    
    def validate_data(self, data: Dict, source: str = "unknown") -> Tuple[bool, Dict]:
        """데이터 유효성 검사 (신선도, 일관성, 교차검증)"""
        
        errors = []
        warnings = []
        
        # 1. 데이터 신선도 검증
        is_fresh, reason = self.freshness_checker.is_data_fresh(data)
        if not is_fresh:
            errors.append(f"신선도: {reason}")
            
        # 2. 데이터 일관성 검증
        is_consistent, score_errors = self.consistency_checker.validate_score_data(data)
        if not is_consistent: errors.extend(score_errors)
        
        is_consistent, mission_errors = self.consistency_checker.validate_mission_data(data)
        if not is_consistent: errors.extend(mission_errors)
        
        is_consistent, rider_errors = self.consistency_checker.validate_rider_data(data)
        if not is_consistent: errors.extend(rider_errors)
        
        # 3. 교차 검증
        # is_valid, cross_errors = self.cross_validator.compare_mission_totals(data)
        # if not is_valid: warnings.extend(cross_errors) # 교차검증은 경고로 처리
        
        # 새로운 교차 검증 로직 사용
        is_valid, daily_total_errors = self.cross_validator.compare_daily_totals(data)
        if not is_valid:
            warnings.extend(daily_total_errors) # 교차검증은 경고로 처리

        is_valid, contribution_errors = self.cross_validator.compare_rider_contributions(data)
        if not is_valid:
            warnings.extend(contribution_errors)

        validation_result = {
            'source': source,
            'validated_at': datetime.now(KST).isoformat(),
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
        
        self.validation_history.append(validation_result)
        self._cleanup_validation_history()
        
        return len(errors) == 0, validation_result
    
    def fix_data_issues(self, data: Dict, validation_result: Dict) -> Dict:
        """데이터 자동 수정 시도"""
        fixed_data = data.copy()
        
        for error in validation_result['errors']:
            # 범위 초과 데이터 자동 수정
            if "범위 초과" in error:
                self._fix_range_errors(fixed_data, error)
            
            # 타입 오류 자동 수정
            elif "숫자가 아님" in error:
                self._fix_type_errors(fixed_data, error)
        
        # 수정된 데이터 재검증
        if fixed_data != data:
            logger.info("🔧 데이터 자동 수정 시도")
            is_valid, new_result = self.validate_data(fixed_data, "auto_fixed")
            
            if is_valid:
                logger.info("✅ 데이터 자동 수정 성공")
                return fixed_data
            else:
                logger.warning("⚠️ 데이터 자동 수정 실패, 원본 데이터 사용")
        
        return data
    
    def _fix_range_errors(self, data: Dict, error: str):
        """범위 초과 오류 수정"""
        # 간단한 범위 수정 로직
        # 실제로는 더 정교한 수정 알고리즘이 필요
        pass
    
    def _fix_type_errors(self, data: Dict, error: str):
        """타입 오류 수정"""
        # 문자열을 숫자로 변환 시도
        pass
    
    def _cleanup_validation_history(self, max_records: int = 100):
        """검증 히스토리 정리"""
        if len(self.validation_history) > max_records:
            self.validation_history = self.validation_history[-max_records:]
    
    def get_validation_stats(self) -> Dict:
        """검증 통계 반환"""
        if not self.validation_history:
            return {'total': 0, 'valid': 0, 'invalid': 0, 'success_rate': 0.0}
        
        total = len(self.validation_history)
        valid = sum(1 for result in self.validation_history if result['is_valid'])
        invalid = total - valid
        success_rate = (valid / total) * 100
        
        return {
            'total': total,
            'valid': valid,
            'invalid': invalid,
            'success_rate': success_rate,
            'recent_errors': [r['errors'] for r in self.validation_history[-5:] if r['errors']]
        }

def test_validator():
    """데이터 검증 시스템 테스트"""
    print("🧪 데이터 검증 시스템 테스트 시작")
    
    validator = EnhancedDataValidator()
    
    # 테스트 데이터
    test_data = {
        '총점': 150,
        '물량점수': 75,
        '수락률점수': 75,
        '수락률': 95.5,
        '총완료': 100,
        '총거절': 5,
        '아침점심피크': {'current': 30, 'target': 25},
        '오후논피크': {'current': 25, 'target': 20},
        '저녁피크': {'current': 25, 'target': 30},
        '심야논피크': {'current': 20, 'target': 15},
        'riders': [
            {'name': '라이더1', 'contribution': 25.5, 'complete': 30, 'reject': 2},
            {'name': '라이더2', 'contribution': 35.2, 'complete': 40, 'reject': 1},
        ],
        'timestamp': datetime.now(KST).isoformat(),
        'mission_date': datetime.now(KST).strftime('%Y-%m-%d')
    }
    
    # 검증 수행
    is_valid, result = validator.validate_data(test_data, "test")
    
    print(f"검증 결과: {'통과' if is_valid else '실패'}")
    if result['errors']:
        print("오류:", result['errors'])
    if result['warnings']:
        print("경고:", result['warnings'])
    
    # 통계 출력
    stats = validator.get_validation_stats()
    print(f"검증 통계: {stats}")

if __name__ == "__main__":
    test_validator() 