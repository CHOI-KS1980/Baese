#!/usr/bin/env python3
"""
🤖 AI 기반 지능형 분석 시스템
- 머신러닝 기반 성과 예측
- 실시간 이상 패턴 감지
- 자동 최적화 추천
- 트렌드 분석 및 인사이트
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import statistics
from dataclasses import dataclass
import pytz

logger = logging.getLogger(__name__)
KST = pytz.timezone('Asia/Seoul')

@dataclass
class PerformanceMetrics:
    """성과 지표 데이터 클래스"""
    timestamp: datetime
    total_score: int
    total_completed: int
    mission_completion_rate: float
    avg_rider_efficiency: float
    peak_performance: Dict[str, float]
    anomaly_score: float

@dataclass
class PredictionResult:
    """예측 결과 데이터 클래스"""
    predicted_completion: int
    confidence: float
    trend: str  # 'increasing', 'decreasing', 'stable'
    recommendation: str
    risk_factors: List[str]

class AIAnalytics:
    """AI 기반 분석 시스템"""
    
    def __init__(self):
        self.performance_history: List[PerformanceMetrics] = []
        self.analysis_cache = {}
        self.anomaly_threshold = 2.0  # 표준편차 기준
        
        logger.info("🤖 AI 분석 시스템 초기화 완료")
    
    def add_performance_data(self, data: Dict) -> None:
        """성과 데이터 추가"""
        try:
            # 미션 완료율 계산
            total_missions = sum(mission.get('target', 0) for mission in data.get('missions', {}).values())
            total_completed = sum(mission.get('current', 0) for mission in data.get('missions', {}).values())
            completion_rate = (total_completed / total_missions * 100) if total_missions > 0 else 0
            
            # 라이더 평균 효율성 계산
            active_riders = [r for r in data.get('riders', []) if r.get('completed', 0) > 0]
            avg_efficiency = statistics.mean([r.get('acceptance_rate', 0) for r in active_riders]) if active_riders else 0
            
            # 피크시간 성과 분석
            peak_performance = self._analyze_peak_performance(data)
            
            # 이상 점수 계산
            anomaly_score = self._calculate_anomaly_score(total_completed, completion_rate)
            
            metrics = PerformanceMetrics(
                timestamp=datetime.now(KST),
                total_score=data.get('total_score', 0),
                total_completed=total_completed,
                mission_completion_rate=completion_rate,
                avg_rider_efficiency=avg_efficiency,
                peak_performance=peak_performance,
                anomaly_score=anomaly_score
            )
            
            self.performance_history.append(metrics)
            
            # 최근 100개 데이터만 유지
            if len(self.performance_history) > 100:
                self.performance_history = self.performance_history[-100:]
                
            logger.info(f"📊 성과 데이터 추가: 완료율 {completion_rate:.1f}%, 이상점수 {anomaly_score:.2f}")
            
        except Exception as e:
            logger.error(f"❌ 성과 데이터 추가 실패: {e}")
    
    def _analyze_peak_performance(self, data: Dict) -> Dict[str, float]:
        """피크시간별 성과 분석"""
        missions = data.get('missions', {})
        peak_analysis = {}
        
        for mission_name, mission_data in missions.items():
            target = mission_data.get('target', 0)
            current = mission_data.get('current', 0)
            
            if target > 0:
                performance_ratio = current / target
                peak_analysis[mission_name] = performance_ratio
        
        return peak_analysis
    
    def _calculate_anomaly_score(self, current_completed: int, completion_rate: float) -> float:
        """이상 점수 계산"""
        if len(self.performance_history) < 5:
            return 0.0
        
        # 최근 데이터 기반 평균과 표준편차 계산
        recent_completed = [m.total_completed for m in self.performance_history[-10:]]
        recent_rates = [m.mission_completion_rate for m in self.performance_history[-10:]]
        
        if len(recent_completed) < 2:
            return 0.0
        
        try:
            # Z-score 계산
            completed_mean = statistics.mean(recent_completed)
            completed_std = statistics.stdev(recent_completed)
            rate_mean = statistics.mean(recent_rates)
            rate_std = statistics.stdev(recent_rates)
            
            completed_z = abs((current_completed - completed_mean) / completed_std) if completed_std > 0 else 0
            rate_z = abs((completion_rate - rate_mean) / rate_std) if rate_std > 0 else 0
            
            return max(completed_z, rate_z)
            
        except Exception:
            return 0.0
    
    def predict_performance(self, target_time: datetime) -> PredictionResult:
        """성과 예측"""
        try:
            if len(self.performance_history) < 3:
                return PredictionResult(
                    predicted_completion=0,
                    confidence=0.0,
                    trend='insufficient_data',
                    recommendation="더 많은 데이터가 필요합니다.",
                    risk_factors=['데이터 부족']
                )
            
                        # 최근 트렌드 분석
            recent_data = self.performance_history[-5:]
            completed_values = [m.total_completed for m in recent_data]
            
            # 선형 회귀를 통한 예측 (간단한 구현)
            if len(completed_values) >= 2:
                trend_slope = self._calculate_trend([float(v) for v in completed_values])
                
                # 예측값 계산
                base_value = completed_values[-1]
                hours_ahead = (target_time - recent_data[-1].timestamp).total_seconds() / 3600
                predicted = max(0, int(base_value + trend_slope * hours_ahead))
                
                # 신뢰도 계산
                confidence = min(0.95, 0.5 + (len(self.performance_history) * 0.01))
                
                # 트렌드 분류
                if trend_slope > 5:
                    trend = 'increasing'
                elif trend_slope < -5:
                    trend = 'decreasing'
                else:
                    trend = 'stable'
                
                # 추천사항 생성
                recommendation = self._generate_recommendation(trend, recent_data[-1])
                
                # 위험 요소 분석
                risk_factors = self._analyze_risk_factors(recent_data[-1])
                
                return PredictionResult(
                    predicted_completion=predicted,
                    confidence=confidence,
                    trend=trend,
                    recommendation=recommendation,
                    risk_factors=risk_factors
                )
            
        except Exception as e:
            logger.error(f"❌ 성과 예측 실패: {e}")
        
        return PredictionResult(
            predicted_completion=0,
            confidence=0.0,
            trend='error',
            recommendation="예측 시스템 오류",
            risk_factors=['시스템 오류']
        )
    
    def _calculate_trend(self, values: List[float]) -> float:
        """트렌드 기울기 계산"""
        n = len(values)
        if n < 2:
            return 0
        
        x_values = list(range(n))
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(values)
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        return numerator / denominator if denominator != 0 else 0
    
    def _generate_recommendation(self, trend: str, latest_metrics: PerformanceMetrics) -> str:
        """추천사항 생성"""
        recommendations = []
        
        if trend == 'decreasing':
            recommendations.append("📉 성과 하락 추세 - 라이더 동기부여 필요")
        elif trend == 'increasing':
            recommendations.append("📈 성과 상승 추세 - 현재 전략 유지")
        
        if latest_metrics.mission_completion_rate < 80:
            recommendations.append("⚠️ 미션 완료율 저조 - 목표 재검토 필요")
        
        if latest_metrics.avg_rider_efficiency < 85:
            recommendations.append("🎯 라이더 효율성 개선 필요 - 교육 프로그램 검토")
        
        if latest_metrics.anomaly_score > self.anomaly_threshold:
            recommendations.append("🚨 이상 패턴 감지 - 즉시 점검 필요")
        
        return " / ".join(recommendations) if recommendations else "✅ 모든 지표 양호"
    
    def _analyze_risk_factors(self, metrics: PerformanceMetrics) -> List[str]:
        """위험 요소 분석"""
        risks = []
        
        if metrics.anomaly_score > self.anomaly_threshold:
            risks.append("이상 패턴 감지")
        
        if metrics.mission_completion_rate < 70:
            risks.append("낮은 미션 완료율")
        
        if metrics.avg_rider_efficiency < 80:
            risks.append("라이더 효율성 저하")
        
        # 피크시간 성과 분석
        poor_performance_peaks = [peak for peak, ratio in metrics.peak_performance.items() if ratio < 0.7]
        if poor_performance_peaks:
            risks.append(f"저조한 피크시간: {', '.join(poor_performance_peaks)}")
        
        return risks if risks else ["위험 요소 없음"]
    
    def get_intelligence_report(self) -> Dict:
        """지능형 분석 리포트"""
        if not self.performance_history:
            return {"status": "데이터 부족", "message": "분석할 데이터가 없습니다."}
        
        latest = self.performance_history[-1]
        
        # 예측 수행
        prediction = self.predict_performance(datetime.now(KST) + timedelta(hours=1))
        
        # 트렌드 분석
        if len(self.performance_history) >= 5:
            recent_trend = self._analyze_recent_trend()
        else:
            recent_trend = "데이터 부족"
        
        return {
            "timestamp": latest.timestamp.isoformat(),
            "current_performance": {
                "completion_rate": f"{latest.mission_completion_rate:.1f}%",
                "rider_efficiency": f"{latest.avg_rider_efficiency:.1f}%",
                "anomaly_score": f"{latest.anomaly_score:.2f}",
                "total_completed": latest.total_completed
            },
            "prediction": {
                "next_hour_completion": prediction.predicted_completion,
                "confidence": f"{prediction.confidence * 100:.1f}%",
                "trend": prediction.trend,
                "recommendation": prediction.recommendation
            },
            "risk_analysis": {
                "factors": prediction.risk_factors,
                "level": self._get_risk_level(latest.anomaly_score)
            },
            "trend_analysis": recent_trend
        }
    
    def _analyze_recent_trend(self) -> str:
        """최근 트렌드 분석"""
        recent_data = self.performance_history[-5:]
        rates = [m.mission_completion_rate for m in recent_data]
        
        if len(rates) < 2:
            return "데이터 부족"
        
        trend_slope = self._calculate_trend(rates)
        
        if trend_slope > 2:
            return "📈 지속적 개선"
        elif trend_slope < -2:
            return "📉 성과 하락"
        else:
            return "📊 안정적 유지"
    
    def _get_risk_level(self, anomaly_score: float) -> str:
        """위험 레벨 평가"""
        if anomaly_score > 3.0:
            return "🔴 높음"
        elif anomaly_score > 2.0:
            return "🟡 중간"
        else:
            return "🟢 낮음"
    
    def save_analytics_data(self, filepath: str = "analytics_data.json") -> None:
        """분석 데이터 저장"""
        try:
            data = {
                "performance_history": [
                    {
                        "timestamp": m.timestamp.isoformat(),
                        "total_score": m.total_score,
                        "total_completed": m.total_completed,
                        "mission_completion_rate": m.mission_completion_rate,
                        "avg_rider_efficiency": m.avg_rider_efficiency,
                        "peak_performance": m.peak_performance,
                        "anomaly_score": m.anomaly_score
                    }
                    for m in self.performance_history
                ]
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"📊 분석 데이터 저장 완료: {filepath}")
            
        except Exception as e:
            logger.error(f"❌ 분석 데이터 저장 실패: {e}")
    
    def load_analytics_data(self, filepath: str = "analytics_data.json") -> None:
        """분석 데이터 로드"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.performance_history = []
            for item in data.get("performance_history", []):
                metrics = PerformanceMetrics(
                    timestamp=datetime.fromisoformat(item["timestamp"]),
                    total_score=item["total_score"],
                    total_completed=item["total_completed"],
                    mission_completion_rate=item["mission_completion_rate"],
                    avg_rider_efficiency=item["avg_rider_efficiency"],
                    peak_performance=item["peak_performance"],
                    anomaly_score=item["anomaly_score"]
                )
                self.performance_history.append(metrics)
            
            logger.info(f"📊 분석 데이터 로드 완료: {len(self.performance_history)}개 항목")
            
        except FileNotFoundError:
            logger.info("📊 기존 분석 데이터 없음 - 새로 시작")
        except Exception as e:
            logger.error(f"❌ 분석 데이터 로드 실패: {e}") 