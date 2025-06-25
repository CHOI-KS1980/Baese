"""
🔍 데이터 검증 시스템
크롤링 데이터의 신뢰성을 보장하는 이중 검증 시스템
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import hashlib

# 유틸리티 임포트
from auto_finance.utils.logger import setup_logger
from auto_finance.utils.error_handler import ErrorHandler
from auto_finance.utils.cache_manager import cache_manager

logger = setup_logger(__name__)

class ValidationStatus(Enum):
    """검증 상태"""
    PENDING = "pending"
    VALIDATING = "validating"
    VALID = "valid"
    INVALID = "invalid"
    SUSPICIOUS = "suspicious"
    ERROR = "error"

class DataSource(Enum):
    """데이터 소스"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    CACHE = "cache"

@dataclass
class ValidationResult:
    """검증 결과"""
    data_id: str
    status: ValidationStatus
    confidence_score: float  # 0.0 ~ 1.0
    validation_time: datetime
    primary_data: Dict[str, Any]
    secondary_data: Optional[Dict[str, Any]] = None
    differences: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class DataValidator:
    """데이터 검증 시스템"""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        
        # 검증 설정
        self.validation_config = {
            'max_retries': 3,
            'retry_delay': 5,
            'similarity_threshold': 0.8,
            'confidence_threshold': 0.7,
            'cache_ttl': 1800,  # 30분
            'validation_timeout': 60  # 60초
        }
        
        # 검증 통계
        self.stats = {
            'total_validations': 0,
            'valid_data': 0,
            'invalid_data': 0,
            'suspicious_data': 0,
            'validation_errors': 0,
            'average_confidence': 0.0,
            'average_validation_time': 0.0
        }
        
        # 검증 히스토리
        self.validation_history: List[ValidationResult] = []
        
        logger.info("🔍 데이터 검증 시스템 초기화 완료")
    
    async def validate_crawled_data(self, primary_data: Dict[str, Any], 
                                   data_source: str = "unknown") -> ValidationResult:
        """크롤링 데이터 검증"""
        start_time = time.time()
        data_id = self._generate_data_id(primary_data, data_source)
        
        logger.info(f"🔍 데이터 검증 시작: {data_id}")
        
        try:
            # 1단계: 기본 데이터 검증
            basic_validation = self._validate_basic_structure(primary_data)
            if not basic_validation['is_valid']:
                return self._create_invalid_result(
                    data_id, primary_data, basic_validation['errors']
                )
            
            # 2단계: 이중 크롤링 검증
            secondary_data = await self._perform_secondary_crawling(data_source)
            
            # 3단계: 데이터 비교 및 일관성 검사
            comparison_result = self._compare_datasets(primary_data, secondary_data)
            
            # 4단계: 이상치 탐지
            anomaly_result = self._detect_anomalies(primary_data)
            
            # 5단계: 최종 검증 결과 생성
            validation_result = self._create_validation_result(
                data_id, primary_data, secondary_data, 
                comparison_result, anomaly_result, start_time
            )
            
            # 통계 업데이트
            self._update_stats(validation_result, time.time() - start_time)
            
            # 히스토리에 추가
            self.validation_history.append(validation_result)
            
            logger.info(f"✅ 데이터 검증 완료: {data_id} (신뢰도: {validation_result.confidence_score:.2f})")
            return validation_result
            
        except Exception as e:
            self.error_handler.handle_error(e, f"데이터 검증 실패: {data_id}")
            logger.error(f"❌ 데이터 검증 실패: {data_id} - {e}")
            
            return self._create_error_result(data_id, primary_data, str(e))
    
    def _validate_basic_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """기본 데이터 구조 검증"""
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # 필수 필드 확인
        required_fields = ['총점', '총완료', '수락률']
        for field in required_fields:
            if field not in data:
                result['errors'].append(f"필수 필드 누락: {field}")
                result['is_valid'] = False
        
        # 데이터 타입 검증
        if '총점' in data and not isinstance(data['총점'], (int, float)):
            result['errors'].append("총점이 숫자가 아닙니다")
            result['is_valid'] = False
        
        if '수락률' in data and not isinstance(data['수락률'], (int, float)):
            result['errors'].append("수락률이 숫자가 아닙니다")
            result['is_valid'] = False
        
        # 데이터 범위 검증
        if '총점' in data and isinstance(data['총점'], (int, float)):
            if data['총점'] < 0 or data['총점'] > 200:
                result['warnings'].append(f"비정상적인 총점: {data['총점']}")
        
        if '수락률' in data and isinstance(data['수락률'], (int, float)):
            if data['수락률'] < 0 or data['수락률'] > 100:
                result['errors'].append(f"비정상적인 수락률: {data['수락률']}")
                result['is_valid'] = False
        
        # 피크 데이터 검증
        peak_fields = ['아침점심피크', '오후논피크', '저녁피크', '심야논피크']
        for peak in peak_fields:
            if peak in data:
                peak_data = data[peak]
                if not isinstance(peak_data, dict):
                    result['errors'].append(f"{peak} 데이터 형식 오류")
                    result['is_valid'] = False
                elif 'current' not in peak_data or 'target' not in peak_data:
                    result['warnings'].append(f"{peak} 필수 하위 필드 누락")
        
        return result
    
    async def _perform_secondary_crawling(self, data_source: str) -> Optional[Dict[str, Any]]:
        """이중 크롤링 수행"""
        try:
            logger.info(f"🔄 이중 크롤링 시작: {data_source}")
            
            # 캐시된 데이터 확인
            cache_key = f"secondary_crawl_{data_source}_{datetime.now().strftime('%Y%m%d_%H')}"
            cached_data = cache_manager.get(cache_key)
            
            if cached_data:
                logger.info("💾 캐시된 이중 크롤링 데이터 사용")
                return cached_data
            
            # 실제 이중 크롤링 수행 (여기서는 시뮬레이션)
            # 실제 구현에서는 다른 크롤링 방법이나 소스를 사용
            await asyncio.sleep(2)  # 크롤링 시뮬레이션
            
            # 시뮬레이션된 이중 크롤링 결과
            secondary_data = self._simulate_secondary_crawl(data_source)
            
            # 캐시에 저장
            if secondary_data:
                cache_manager.set(cache_key, secondary_data, ttl=self.validation_config['cache_ttl'])
            
            return secondary_data
            
        except Exception as e:
            logger.error(f"❌ 이중 크롤링 실패: {e}")
            return None
    
    def _simulate_secondary_crawl(self, data_source: str) -> Dict[str, Any]:
        """이중 크롤링 시뮬레이션"""
        # 실제로는 다른 크롤링 방법을 사용해야 함
        # 여기서는 약간의 변동을 주어 시뮬레이션
        import random
        
        base_data = {
            '총점': random.randint(80, 120),
            '물량점수': random.randint(30, 50),
            '수락률점수': random.randint(40, 60),
            '총완료': random.randint(50, 100),
            '총거절': random.randint(0, 20),
            '수락률': random.uniform(80.0, 95.0),
            '아침점심피크': {"current": random.randint(10, 20), "target": 15},
            '오후논피크': {"current": random.randint(5, 15), "target": 10},
            '저녁피크': {"current": random.randint(15, 25), "target": 20},
            '심야논피크': {"current": random.randint(3, 10), "target": 8},
            'riders': [],
            'timestamp': datetime.now().isoformat()
        }
        
        return base_data
    
    def _compare_datasets(self, primary: Dict[str, Any], 
                         secondary: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """데이터셋 비교"""
        result = {
            'similarity_score': 0.0,
            'differences': [],
            'is_consistent': False
        }
        
        if not secondary:
            result['differences'].append("이중 크롤링 데이터 없음")
            return result
        
        # 주요 필드 비교
        key_fields = ['총점', '총완료', '수락률']
        differences = []
        total_difference = 0
        
        for field in key_fields:
            if field in primary and field in secondary:
                primary_val = primary[field]
                secondary_val = secondary[field]
                
                if isinstance(primary_val, (int, float)) and isinstance(secondary_val, (int, float)):
                    diff = abs(primary_val - secondary_val)
                    if diff > 0:
                        differences.append(f"{field}: {primary_val} vs {secondary_val} (차이: {diff})")
                        total_difference += diff
        
        # 피크 데이터 비교
        peak_fields = ['아침점심피크', '오후논피크', '저녁피크', '심야논피크']
        for peak in peak_fields:
            if peak in primary and peak in secondary:
                p_primary = primary[peak]
                p_secondary = secondary[peak]
                
                if isinstance(p_primary, dict) and isinstance(p_secondary, dict):
                    if 'current' in p_primary and 'current' in p_secondary:
                        diff = abs(p_primary['current'] - p_secondary['current'])
                        if diff > 2:  # 2개 이상 차이나면 차이로 기록
                            differences.append(f"{peak}.current: {p_primary['current']} vs {p_secondary['current']}")
                            total_difference += diff
        
        # 유사도 점수 계산
        if differences:
            result['differences'] = differences
            # 차이가 적을수록 높은 유사도
            result['similarity_score'] = max(0.0, 1.0 - (total_difference / 100.0))
        else:
            result['similarity_score'] = 1.0
        
        result['is_consistent'] = result['similarity_score'] >= self.validation_config['similarity_threshold']
        
        return result
    
    def _detect_anomalies(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """이상치 탐지"""
        result = {
            'anomalies': [],
            'risk_score': 0.0
        }
        
        # 급격한 변화 탐지
        if '총점' in data:
            score = data['총점']
            if score < 50:
                result['anomalies'].append(f"비정상적으로 낮은 총점: {score}")
                result['risk_score'] += 0.3
            elif score > 150:
                result['anomalies'].append(f"비정상적으로 높은 총점: {score}")
                result['risk_score'] += 0.2
        
        if '수락률' in data:
            rate = data['수락률']
            if rate < 50:
                result['anomalies'].append(f"비정상적으로 낮은 수락률: {rate}%")
                result['risk_score'] += 0.4
            elif rate > 99:
                result['anomalies'].append(f"비정상적으로 높은 수락률: {rate}%")
                result['risk_score'] += 0.2
        
        # 피크 데이터 이상치 탐지
        peak_fields = ['아침점심피크', '오후논피크', '저녁피크', '심야논피크']
        for peak in peak_fields:
            if peak in data:
                peak_data = data[peak]
                if isinstance(peak_data, dict) and 'current' in peak_data:
                    current = peak_data['current']
                    target = peak_data.get('target', 0)
                    
                    # 목표 대비 50% 이상 차이나는 경우
                    if target > 0:
                        ratio = abs(current - target) / target
                        if ratio > 0.5:
                            result['anomalies'].append(f"{peak} 목표 대비 큰 차이: {current}/{target}")
                            result['risk_score'] += 0.1
        
        # 라이더 데이터 이상치
        if 'riders' in data and isinstance(data['riders'], list):
            if len(data['riders']) == 0:
                result['anomalies'].append("라이더 데이터가 없습니다")
                result['risk_score'] += 0.2
            elif len(data['riders']) > 100:
                result['anomalies'].append(f"비정상적으로 많은 라이더: {len(data['riders'])}명")
                result['risk_score'] += 0.1
        
        result['risk_score'] = min(1.0, result['risk_score'])
        return result
    
    def _create_validation_result(self, data_id: str, primary_data: Dict[str, Any],
                                 secondary_data: Optional[Dict[str, Any]],
                                 comparison_result: Dict[str, Any],
                                 anomaly_result: Dict[str, Any],
                                 start_time: float) -> ValidationResult:
        """검증 결과 생성"""
        # 신뢰도 점수 계산
        confidence_score = 1.0
        
        # 일관성 점수 반영
        confidence_score *= comparison_result['similarity_score']
        
        # 이상치 점수 반영
        confidence_score *= (1.0 - anomaly_result['risk_score'])
        
        # 최종 신뢰도 점수
        confidence_score = max(0.0, min(1.0, confidence_score))
        
        # 상태 결정
        if confidence_score >= self.validation_config['confidence_threshold']:
            status = ValidationStatus.VALID
        elif confidence_score >= 0.5:
            status = ValidationStatus.SUSPICIOUS
        else:
            status = ValidationStatus.INVALID
        
        # 경고 및 오류 메시지 수집
        warnings = []
        errors = []
        
        if comparison_result['differences']:
            warnings.extend(comparison_result['differences'])
        
        if anomaly_result['anomalies']:
            warnings.extend(anomaly_result['anomalies'])
        
        return ValidationResult(
            data_id=data_id,
            status=status,
            confidence_score=confidence_score,
            validation_time=datetime.now(),
            primary_data=primary_data,
            secondary_data=secondary_data,
            differences=comparison_result['differences'],
            warnings=warnings,
            errors=errors,
            metadata={
                'comparison_score': comparison_result['similarity_score'],
                'anomaly_risk': anomaly_result['risk_score'],
                'validation_duration': time.time() - start_time
            }
        )
    
    def _create_invalid_result(self, data_id: str, data: Dict[str, Any], 
                              errors: List[str]) -> ValidationResult:
        """무효한 결과 생성"""
        return ValidationResult(
            data_id=data_id,
            status=ValidationStatus.INVALID,
            confidence_score=0.0,
            validation_time=datetime.now(),
            primary_data=data,
            errors=errors
        )
    
    def _create_error_result(self, data_id: str, data: Dict[str, Any], 
                            error: str) -> ValidationResult:
        """오류 결과 생성"""
        return ValidationResult(
            data_id=data_id,
            status=ValidationStatus.ERROR,
            confidence_score=0.0,
            validation_time=datetime.now(),
            primary_data=data,
            errors=[error]
        )
    
    def _generate_data_id(self, data: Dict[str, Any], source: str) -> str:
        """데이터 ID 생성"""
        # 주요 필드들을 조합하여 ID 생성
        key_data = {
            '총점': data.get('총점', 0),
            '총완료': data.get('총완료', 0),
            '수락률': data.get('수락률', 0),
            'source': source,
            'timestamp': datetime.now().strftime('%Y%m%d_%H%M')
        }
        
        data_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()[:12]
    
    def _update_stats(self, result: ValidationResult, processing_time: float):
        """통계 업데이트"""
        self.stats['total_validations'] += 1
        
        if result.status == ValidationStatus.VALID:
            self.stats['valid_data'] += 1
        elif result.status == ValidationStatus.INVALID:
            self.stats['invalid_data'] += 1
        elif result.status == ValidationStatus.SUSPICIOUS:
            self.stats['suspicious_data'] += 1
        elif result.status == ValidationStatus.ERROR:
            self.stats['validation_errors'] += 1
        
        # 평균 신뢰도 업데이트
        total_confidence = self.stats['average_confidence'] * (self.stats['total_validations'] - 1)
        self.stats['average_confidence'] = (total_confidence + result.confidence_score) / self.stats['total_validations']
        
        # 평균 처리 시간 업데이트
        total_time = self.stats['average_validation_time'] * (self.stats['total_validations'] - 1)
        self.stats['average_validation_time'] = (total_time + processing_time) / self.stats['total_validations']
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """검증 통계 반환"""
        return {
            'stats': self.stats,
            'success_rate': (self.stats['valid_data'] / self.stats['total_validations'] * 100) 
                           if self.stats['total_validations'] > 0 else 0,
            'recent_validations': len(self.validation_history[-10:])  # 최근 10개
        }
    
    def get_validation_history(self, limit: int = 50) -> List[ValidationResult]:
        """검증 히스토리 반환"""
        return self.validation_history[-limit:]
    
    def is_data_trustworthy(self, result: ValidationResult) -> bool:
        """데이터 신뢰성 판단"""
        return (result.status == ValidationStatus.VALID and 
                result.confidence_score >= self.validation_config['confidence_threshold'])
    
    def get_recommendation(self, result: ValidationResult) -> str:
        """검증 결과에 따른 권장사항"""
        if result.status == ValidationStatus.VALID:
            return "✅ 데이터가 신뢰할 수 있습니다. 정상적으로 사용하세요."
        elif result.status == ValidationStatus.SUSPICIOUS:
            return "⚠️ 데이터에 의심스러운 점이 있습니다. 재확인이 필요합니다."
        elif result.status == ValidationStatus.INVALID:
            return "❌ 데이터가 유효하지 않습니다. 크롤링을 다시 시도하세요."
        else:
            return "🚨 검증 중 오류가 발생했습니다. 시스템을 점검하세요." 