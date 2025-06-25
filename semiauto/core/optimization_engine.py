#!/usr/bin/env python3
"""
🔧 고급 자동화 최적화 엔진
- 동적 스케줄 최적화
- 성능 기반 자동 조정
- 리소스 사용량 최적화
- 예측 기반 사전 대응
"""

import json
import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import pytz

logger = logging.getLogger(__name__)
KST = pytz.timezone('Asia/Seoul')

@dataclass
class OptimizationMetrics:
    """최적화 지표"""
    timestamp: datetime
    execution_time: float  # 실행 시간 (초)
    success_rate: float   # 성공률 (%)
    data_quality: float   # 데이터 품질 점수
    system_load: float    # 시스템 부하
    memory_usage: float   # 메모리 사용량 (MB)
    network_latency: float # 네트워크 지연시간 (ms)

@dataclass
class OptimizationRecommendation:
    """최적화 권장사항"""
    category: str         # 'schedule', 'performance', 'resource'
    priority: str         # 'high', 'medium', 'low'
    description: str      # 권장사항 설명
    expected_improvement: float  # 예상 개선율 (%)
    implementation_effort: str   # 'easy', 'medium', 'hard'

class PerformanceMonitor:
    """성능 모니터링"""
    
    def __init__(self):
        self.metrics_history: List[OptimizationMetrics] = []
        self.baseline_metrics: Optional[OptimizationMetrics] = None
        
    def record_metrics(self, execution_time: float, success_rate: float, 
                      data_quality: float, system_load: float = 0.0,
                      memory_usage: float = 0.0, network_latency: float = 0.0):
        """성능 지표 기록"""
        metrics = OptimizationMetrics(
            timestamp=datetime.now(KST),
            execution_time=execution_time,
            success_rate=success_rate,
            data_quality=data_quality,
            system_load=system_load,
            memory_usage=memory_usage,
            network_latency=network_latency
        )
        
        self.metrics_history.append(metrics)
        
        # 최근 100개 데이터만 유지
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]
        
        # 베이스라인 설정 (첫 번째 데이터)
        if self.baseline_metrics is None:
            self.baseline_metrics = metrics
            
        logger.info(f"📊 성능 지표 기록: 실행시간 {execution_time:.2f}s, 성공률 {success_rate:.1f}%")
    
    def get_performance_trend(self, metric_name: str, days: int = 7) -> Dict:
        """성능 트렌드 분석"""
        cutoff_time = datetime.now(KST) - timedelta(days=days)
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        
        if len(recent_metrics) < 2:
            return {"trend": "insufficient_data", "change": 0.0}
        
        values = [getattr(m, metric_name) for m in recent_metrics]
        
        # 선형 회귀를 통한 트렌드 계산
        n = len(values)
        x_values = list(range(n))
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(values)
        
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator
        
        # 변화율 계산
        if len(values) >= 2:
            change_rate = ((values[-1] - values[0]) / values[0] * 100) if values[0] != 0 else 0
        else:
            change_rate = 0
        
        trend = "improving" if slope > 0 else "declining" if slope < 0 else "stable"
        
        return {
            "trend": trend,
            "change": change_rate,
            "slope": slope,
            "current_value": values[-1],
            "average": statistics.mean(values)
        }

class ScheduleOptimizer:
    """스케줄 최적화기"""
    
    def __init__(self):
        self.schedule_performance: Dict[str, List[float]] = {}
        self.optimal_intervals: Dict[str, int] = {
            "peak_hours": 15,      # 피크시간 기본 간격 (분)
            "normal_hours": 30,    # 일반시간 기본 간격 (분)
            "low_hours": 60        # 저부하시간 기본 간격 (분)
        }
    
    def analyze_optimal_timing(self, performance_history: List[OptimizationMetrics]) -> Dict:
        """최적 타이밍 분석"""
        if len(performance_history) < 10:
            return {"status": "insufficient_data"}
        
        # 시간대별 성능 분석
        hourly_performance = {}
        for metrics in performance_history:
            hour = metrics.timestamp.hour
            if hour not in hourly_performance:
                hourly_performance[hour] = []
            
            # 성공률과 실행시간을 결합한 성능 점수
            performance_score = metrics.success_rate - (metrics.execution_time * 10)
            hourly_performance[hour].append(performance_score)
        
        # 시간대별 평균 성능 계산
        hourly_averages = {
            hour: statistics.mean(scores) 
            for hour, scores in hourly_performance.items()
        }
        
        # 최적/최악 시간대 찾기
        best_hours = sorted(hourly_averages.items(), key=lambda x: x[1], reverse=True)[:3]
        worst_hours = sorted(hourly_averages.items(), key=lambda x: x[1])[:3]
        
        return {
            "best_hours": [hour for hour, _ in best_hours],
            "worst_hours": [hour for hour, _ in worst_hours],
            "hourly_performance": hourly_averages,
            "recommendation": self._generate_schedule_recommendation(hourly_averages)
        }
    
    def _generate_schedule_recommendation(self, hourly_performance: Dict[int, float]) -> str:
        """스케줄 권장사항 생성"""
        if not hourly_performance:
            return "데이터 부족으로 권장사항을 생성할 수 없습니다."
        
        best_hour = max(hourly_performance.items(), key=lambda x: x[1])[0]
        worst_hour = min(hourly_performance.items(), key=lambda x: x[1])[0]
        
        recommendations = []
        
        # 피크시간 조정
        peak_hours = [11, 12, 17, 18, 19, 20, 21]
        peak_performance = [hourly_performance.get(h, 0) for h in peak_hours]
        avg_peak_performance = statistics.mean(peak_performance) if peak_performance else 0
        
        if avg_peak_performance < 50:
            recommendations.append("피크시간 모니터링 간격을 30분으로 늘려 시스템 부하 감소")
        elif avg_peak_performance > 80:
            recommendations.append("피크시간 모니터링 간격을 10분으로 줄여 실시간성 향상")
        
        # 저성능 시간대 조정
        if hourly_performance[worst_hour] < 30:
            recommendations.append(f"{worst_hour}시 성능이 저조하므로 해당 시간대 모니터링 강화 필요")
        
        return " / ".join(recommendations) if recommendations else "현재 스케줄이 최적화되어 있습니다."
    
    def optimize_intervals(self, current_performance: float, time_category: str) -> int:
        """간격 최적화"""
        current_interval = self.optimal_intervals.get(time_category, 30)
        
        # 성능 기반 동적 조정
        if current_performance < 50:  # 성능 저조
            new_interval = min(current_interval + 5, 60)  # 간격 늘리기
        elif current_performance > 90:  # 성능 우수
            new_interval = max(current_interval - 5, 10)  # 간격 줄이기
        else:
            new_interval = current_interval  # 유지
        
        self.optimal_intervals[time_category] = new_interval
        return new_interval

class ResourceOptimizer:
    """리소스 최적화기"""
    
    def __init__(self):
        self.resource_thresholds = {
            "memory_warning": 500,    # MB
            "memory_critical": 1000,  # MB
            "latency_warning": 5000,  # ms
            "latency_critical": 10000 # ms
        }
    
    def analyze_resource_usage(self, metrics_history: List[OptimizationMetrics]) -> Dict:
        """리소스 사용량 분석"""
        if not metrics_history:
            return {"status": "no_data"}
        
        recent_metrics = metrics_history[-20:]  # 최근 20개 데이터
        
        # 평균 리소스 사용량 계산
        avg_memory = statistics.mean([m.memory_usage for m in recent_metrics])
        avg_latency = statistics.mean([m.network_latency for m in recent_metrics])
        avg_load = statistics.mean([m.system_load for m in recent_metrics])
        
        # 피크 사용량
        peak_memory = max([m.memory_usage for m in recent_metrics])
        peak_latency = max([m.network_latency for m in recent_metrics])
        
        # 리소스 상태 평가
        memory_status = self._evaluate_resource_status(avg_memory, "memory")
        latency_status = self._evaluate_resource_status(avg_latency, "latency")
        
        return {
            "memory": {
                "average": avg_memory,
                "peak": peak_memory,
                "status": memory_status,
                "threshold": self.resource_thresholds["memory_warning"]
            },
            "network": {
                "average_latency": avg_latency,
                "peak_latency": peak_latency,
                "status": latency_status,
                "threshold": self.resource_thresholds["latency_warning"]
            },
            "system_load": {
                "average": avg_load,
                "status": "normal" if avg_load < 0.8 else "high"
            }
        }
    
    def _evaluate_resource_status(self, value: float, resource_type: str) -> str:
        """리소스 상태 평가"""
        if resource_type == "memory":
            if value > self.resource_thresholds["memory_critical"]:
                return "critical"
            elif value > self.resource_thresholds["memory_warning"]:
                return "warning"
            else:
                return "normal"
        elif resource_type == "latency":
            if value > self.resource_thresholds["latency_critical"]:
                return "critical"
            elif value > self.resource_thresholds["latency_warning"]:
                return "warning"
            else:
                return "normal"
        
        return "unknown"
    
    def generate_optimization_recommendations(self, resource_analysis: Dict) -> List[OptimizationRecommendation]:
        """최적화 권장사항 생성"""
        recommendations = []
        
        # 메모리 최적화
        memory_status = resource_analysis.get("memory", {}).get("status", "normal")
        if memory_status == "critical":
            recommendations.append(OptimizationRecommendation(
                category="resource",
                priority="high",
                description="메모리 사용량이 임계치를 초과했습니다. 캐시 크기 축소 및 가비지 컬렉션 최적화 필요",
                expected_improvement=30.0,
                implementation_effort="medium"
            ))
        elif memory_status == "warning":
            recommendations.append(OptimizationRecommendation(
                category="resource",
                priority="medium",
                description="메모리 사용량 모니터링 강화 및 불필요한 데이터 정리",
                expected_improvement=15.0,
                implementation_effort="easy"
            ))
        
        # 네트워크 최적화
        latency_status = resource_analysis.get("network", {}).get("status", "normal")
        if latency_status == "critical":
            recommendations.append(OptimizationRecommendation(
                category="performance",
                priority="high",
                description="네트워크 지연시간이 과도합니다. 타임아웃 설정 조정 및 재시도 로직 최적화",
                expected_improvement=25.0,
                implementation_effort="medium"
            ))
        
        # 시스템 부하 최적화
        load_status = resource_analysis.get("system_load", {}).get("status", "normal")
        if load_status == "high":
            recommendations.append(OptimizationRecommendation(
                category="schedule",
                priority="medium",
                description="시스템 부하가 높습니다. 실행 간격 조정 및 동시 실행 제한 고려",
                expected_improvement=20.0,
                implementation_effort="easy"
            ))
        
        return recommendations

class OptimizationEngine:
    """통합 최적화 엔진"""
    
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        self.schedule_optimizer = ScheduleOptimizer()
        self.resource_optimizer = ResourceOptimizer()
        
        self.optimization_history: List[Dict] = []
        
        logger.info("🔧 최적화 엔진 초기화 완료")
    
    def analyze_and_optimize(self) -> Dict:
        """종합 분석 및 최적화"""
        try:
            if len(self.performance_monitor.metrics_history) < 5:
                return {
                    "status": "insufficient_data",
                    "message": "최적화를 위한 충분한 데이터가 없습니다.",
                    "recommendations": []
                }
            
            # 성능 트렌드 분석
            trends = {}
            for metric in ['execution_time', 'success_rate', 'data_quality']:
                trends[metric] = self.performance_monitor.get_performance_trend(metric)
            
            # 스케줄 최적화 분석
            schedule_analysis = self.schedule_optimizer.analyze_optimal_timing(
                self.performance_monitor.metrics_history
            )
            
            # 리소스 사용량 분석
            resource_analysis = self.resource_optimizer.analyze_resource_usage(
                self.performance_monitor.metrics_history
            )
            
            # 최적화 권장사항 생성
            recommendations = self.resource_optimizer.generate_optimization_recommendations(
                resource_analysis
            )
            
            # 스케줄 권장사항 추가
            if schedule_analysis.get("recommendation"):
                recommendations.append(OptimizationRecommendation(
                    category="schedule",
                    priority="medium",
                    description=schedule_analysis["recommendation"],
                    expected_improvement=10.0,
                    implementation_effort="easy"
                ))
            
            # 성능 저하 감지 및 권장사항
            success_trend = trends.get('success_rate', {})
            if success_trend.get('trend') == 'declining' and success_trend.get('change', 0) < -10:
                recommendations.append(OptimizationRecommendation(
                    category="performance",
                    priority="high",
                    description="성공률이 지속적으로 하락하고 있습니다. 오류 로그 점검 및 시스템 안정성 강화 필요",
                    expected_improvement=15.0,
                    implementation_effort="medium"
                ))
            
            optimization_result = {
                "timestamp": datetime.now(KST).isoformat(),
                "status": "complete",
                "performance_trends": trends,
                "schedule_analysis": schedule_analysis,
                "resource_analysis": resource_analysis,
                "recommendations": [asdict(rec) for rec in recommendations],
                "total_recommendations": len(recommendations),
                "high_priority_count": len([r for r in recommendations if r.priority == "high"])
            }
            
            # 최적화 히스토리에 추가
            self.optimization_history.append(optimization_result)
            
            # 최근 50개 분석만 유지
            if len(self.optimization_history) > 50:
                self.optimization_history = self.optimization_history[-50:]
            
            logger.info(f"🔧 최적화 분석 완료: {len(recommendations)}개 권장사항 생성")
            
            return optimization_result
            
        except Exception as e:
            logger.error(f"❌ 최적화 분석 실패: {e}")
            return {
                "status": "error",
                "message": f"최적화 분석 중 오류 발생: {e}",
                "recommendations": []
            }
    
    def get_optimization_summary(self) -> Dict:
        """최적화 요약 정보"""
        if not self.optimization_history:
            return {"status": "no_data"}
        
        latest = self.optimization_history[-1]
        
        # 최근 권장사항 통계
        recent_recommendations = []
        for analysis in self.optimization_history[-5:]:  # 최근 5개 분석
            recent_recommendations.extend(analysis.get("recommendations", []))
        
        category_counts = {}
        priority_counts = {}
        
        for rec in recent_recommendations:
            category = rec.get("category", "unknown")
            priority = rec.get("priority", "unknown")
            
            category_counts[category] = category_counts.get(category, 0) + 1
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        return {
            "last_analysis": latest.get("timestamp"),
            "total_analyses": len(self.optimization_history),
            "latest_recommendations": len(latest.get("recommendations", [])),
            "category_distribution": category_counts,
            "priority_distribution": priority_counts,
            "performance_trends": latest.get("performance_trends", {}),
            "system_health": self._assess_system_health(latest)
        }
    
    def _assess_system_health(self, latest_analysis: Dict) -> str:
        """시스템 상태 평가"""
        high_priority_count = latest_analysis.get("high_priority_count", 0)
        
        # 성능 트렌드 확인
        trends = latest_analysis.get("performance_trends", {})
        success_trend = trends.get("success_rate", {}).get("trend", "stable")
        
        if high_priority_count > 3:
            return "🔴 주의 필요"
        elif high_priority_count > 0 or success_trend == "declining":
            return "🟡 모니터링 강화"
        else:
            return "🟢 양호"
    
    def save_optimization_data(self, filepath: str = "optimization_data.json"):
        """최적화 데이터 저장"""
        try:
            data = {
                "optimization_history": self.optimization_history,
                "performance_metrics": [
                    {
                        "timestamp": m.timestamp.isoformat(),
                        "execution_time": m.execution_time,
                        "success_rate": m.success_rate,
                        "data_quality": m.data_quality,
                        "system_load": m.system_load,
                        "memory_usage": m.memory_usage,
                        "network_latency": m.network_latency
                    }
                    for m in self.performance_monitor.metrics_history
                ]
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"🔧 최적화 데이터 저장 완료: {filepath}")
            
        except Exception as e:
            logger.error(f"❌ 최적화 데이터 저장 실패: {e}")
    
    def load_optimization_data(self, filepath: str = "optimization_data.json"):
        """최적화 데이터 로드"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 최적화 히스토리 로드
            self.optimization_history = data.get("optimization_history", [])
            
            # 성능 지표 히스토리 로드
            metrics_data = data.get("performance_metrics", [])
            self.performance_monitor.metrics_history = []
            
            for item in metrics_data:
                metrics = OptimizationMetrics(
                    timestamp=datetime.fromisoformat(item["timestamp"]),
                    execution_time=item["execution_time"],
                    success_rate=item["success_rate"],
                    data_quality=item["data_quality"],
                    system_load=item["system_load"],
                    memory_usage=item["memory_usage"],
                    network_latency=item["network_latency"]
                )
                self.performance_monitor.metrics_history.append(metrics)
            
            logger.info(f"🔧 최적화 데이터 로드 완료: {len(self.optimization_history)}개 분석, {len(metrics_data)}개 지표")
            
        except FileNotFoundError:
            logger.info("🔧 기존 최적화 데이터 없음 - 새로 시작")
        except Exception as e:
            logger.error(f"❌ 최적화 데이터 로드 실패: {e}") 