#!/usr/bin/env python3
"""
🎯 최종 통합 고도화 시스템
- AI 분석 + 다중 플랫폼 + 최적화 엔진 통합
- 차세대 자동화 시스템
- 실시간 지능형 모니터링
- 예측 기반 사전 대응
"""

import sys
import os
import logging
import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pytz

# 현재 디렉토리를 파이썬 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# 기존 모듈들 import
from core.enhanced_final_solution import EnhancedGriderAutoSender
from core.ai_analytics import AIAnalytics
from core.final_solution import KakaoSender
# from core.multi_platform_notifier import MultiPlatformNotifier
# from core.optimization_engine import OptimizationEngine

logger = logging.getLogger(__name__)
KST = pytz.timezone('Asia/Seoul')

class UltimateGriderSystem(EnhancedGriderAutoSender):
    """차세대 G라이더 자동화 시스템"""
    
    def __init__(self, rest_api_key, refresh_token):
        super().__init__(rest_api_key, refresh_token)
        
        # 고도화 컴포넌트 초기화
        self.ai_analytics = AIAnalytics()
        # self.multi_notifier = MultiPlatformNotifier()
        # self.optimization_engine = OptimizationEngine()
        
        # 시스템 상태
        self.system_start_time = datetime.now(KST)
        self.total_executions = 0
        self.successful_executions = 0
        self.ai_predictions_made = 0
        self.optimizations_applied = 0
        
        # 성능 모니터링
        self.execution_times = []
        self.last_optimization = None
        
        logger.info("🚀 차세대 G라이더 자동화 시스템 초기화 완료!")
        self._log_system_capabilities()
    
    def _log_system_capabilities(self):
        """시스템 기능 로깅"""
        capabilities = [
            "✅ AI 기반 성과 예측 및 이상 패턴 감지",
            "✅ 실시간 데이터 검증 및 자동 수정",
            "✅ 정확한 시간 기반 스케줄링",
            "✅ 중복 방지 및 누락 메시지 복구",
            "✅ 지능형 분석 리포트",
            # "✅ 다중 플랫폼 알림 (슬랙, 디스코드, 텔레그램, 이메일)",
            # "✅ 동적 성능 최적화",
            "✅ 종합 상태 모니터링"
        ]
        
        logger.info("🎯 시스템 기능:")
        for capability in capabilities:
            logger.info(f"   {capability}")
    
    def execute_intelligent_automation(self) -> Dict:
        """지능형 자동화 실행"""
        start_time = time.time()
        execution_result = {
            "timestamp": datetime.now(KST).isoformat(),
            "success": False,
            "execution_time": 0.0,
            "ai_analysis": {},
            "data_quality": 0.0,
            "notifications_sent": {},
            "optimizations": [],
            "errors": []
        }
        
        try:
            logger.info("🚀 지능형 자동화 시작...")
            
            # 1. 시스템 리소스 체크
            system_resources = self._check_system_resources()
            logger.info(f"💻 시스템 리소스: CPU {system_resources['cpu']}%, 메모리 {system_resources['memory']}%")
            
            # 2. 스케줄 검증 및 데이터 수집
            should_send, reason = self.scheduler.should_send_now()
            if not should_send:
                logger.info(f"⏸️ 전송 스킵: {reason}")
                if "운영시간 외" in reason:
                    execution_result["success"] = True
                    execution_result["reason"] = reason
                return execution_result
            
            # 3. 데이터 수집 및 검증
            logger.info("📊 데이터 수집 시작...")
            data = self.data_collector.get_grider_data()
            
            if not data:
                execution_result["errors"].append("데이터 수집 실패")
                return execution_result
            
            # 4. AI 분석 추가
            logger.info("🤖 AI 분석 시작...")
            self.ai_analytics.add_performance_data(data)
            ai_report = self.ai_analytics.get_intelligence_report()
            execution_result["ai_analysis"] = ai_report
            self.ai_predictions_made += 1
            
            # 5. 데이터 검증
            logger.info("🔍 데이터 검증 중...")
            is_valid, validation_result = self.data_validator.validate_data(data, "crawler")
            execution_result["data_quality"] = validation_result.get("quality_score", 0.0)
            
            if not is_valid:
                logger.warning("⚠️ 데이터 검증 실패, 자동 수정 시도...")
                data = self.data_validator.fix_data_issues(data, validation_result)
                
                # 재검증
                is_valid, _ = self.data_validator.validate_data(data, "auto_fixed")
                if not is_valid:
                    execution_result["errors"].append("데이터 자동 수정 실패")
                    return execution_result
            
            # 6. 기본 카카오톡 메시지 전송
            access_token = self.token_manager.get_valid_token()
            self.sender = KakaoSender(access_token)
            
            message = self.format_message(data)
            result = self.sender.send_text_message(message)
            
            if result.get('result_code') == 0:
                # 전송 성공 기록
                target_time = datetime.now(KST).replace(second=0, microsecond=0)
                message_id = str(result.get('result_id', f"msg_{int(datetime.now().timestamp())}"))
                data_hash = self.data_validator.freshness_checker.get_data_hash(data)
                
                self.scheduler.history.record_sent(target_time, message_id, data_hash)
                
                logger.info("✅ 카카오톡 메시지 전송 성공!")
                execution_result["success"] = True
            else:
                execution_result["errors"].append(f"카카오톡 전송 실패: {result}")
                
            # 7. 다중 플랫폼 알림 (주석 처리)
            # if self.multi_notifier.platforms:
            #     logger.info("📤 다중 플랫폼 알림 전송...")
            #     notification_results = self.multi_notifier.send_grider_report(data)
            #     execution_result["notifications_sent"] = notification_results
            
            # 8. AI 예측 기반 알림
            if ai_report.get("risk_analysis", {}).get("level") == "🔴 높음":
                logger.warning("🚨 AI가 높은 위험도를 감지했습니다!")
                # self.multi_notifier.send_alert(
                #     f"⚠️ AI 위험 감지: {ai_report['prediction']['recommendation']}",
                #     "🚨 G라이더 시스템 주의 알림",
                #     "high"
                # )
            
        except Exception as e:
            logger.error(f"❌ 지능형 자동화 실행 실패: {e}")
            execution_result["errors"].append(str(e))
        
        finally:
            # 실행 시간 기록
            execution_time = time.time() - start_time
            execution_result["execution_time"] = execution_time
            self.execution_times.append(execution_time)
            
            # 최근 50개 실행시간만 유지
            if len(self.execution_times) > 50:
                self.execution_times = self.execution_times[-50:]
            
            # 통계 업데이트
            self.total_executions += 1
            if execution_result["success"]:
                self.successful_executions += 1
            
            # 성능 최적화 엔진에 데이터 제공 (주석 처리)
            # success_rate = (self.successful_executions / self.total_executions * 100) if self.total_executions > 0 else 0
            # self.optimization_engine.performance_monitor.record_metrics(
            #     execution_time=execution_time,
            #     success_rate=success_rate,
            #     data_quality=execution_result["data_quality"],
            #     system_load=system_resources["cpu"] / 100,
            #     memory_usage=system_resources["memory_mb"],
            #     network_latency=0.0  # 추후 구현
            # )
            
            logger.info(f"⏱️ 실행 완료: {execution_time:.2f}초")
        
        return execution_result
    
    def _check_system_resources(self) -> Dict:
        """시스템 리소스 체크"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_mb = memory.used / 1024 / 1024
            
            return {
                "cpu": cpu_percent,
                "memory": memory_percent,
                "memory_mb": memory_mb,
                "available_gb": memory.available / 1024 / 1024 / 1024
            }
        except Exception as e:
            logger.warning(f"⚠️ 시스템 리소스 체크 실패: {e}")
            return {"cpu": 0, "memory": 0, "memory_mb": 0, "available_gb": 0}
    
    def run_optimization_cycle(self) -> Dict:
        """최적화 사이클 실행"""
        logger.info("🔧 최적화 사이클 시작...")
        
        optimization_result = {
            "timestamp": datetime.now(KST).isoformat(),
            "performed": False,
            "recommendations": [],
            "improvements_applied": []
        }
        
        # 주석 처리: 최적화 엔진 사용
        # try:
        #     # 최적화 분석 실행
        #     analysis = self.optimization_engine.analyze_and_optimize()
        #     
        #     if analysis.get("status") == "complete":
        #         recommendations = analysis.get("recommendations", [])
        #         optimization_result["recommendations"] = recommendations
        #         
        #         # 자동 적용 가능한 최적화 실행
        #         for rec in recommendations:
        #             if rec.get("implementation_effort") == "easy" and rec.get("priority") in ["high", "medium"]:
        #                 # 여기서 실제 최적화 적용
        #                 optimization_result["improvements_applied"].append(rec["description"])
        #                 self.optimizations_applied += 1
        #         
        #         self.last_optimization = datetime.now(KST)
        #         optimization_result["performed"] = True
        #         
        #         logger.info(f"🔧 최적화 완료: {len(recommendations)}개 권장사항, {len(optimization_result['improvements_applied'])}개 적용")
        #     
        # except Exception as e:
        #     logger.error(f"❌ 최적화 사이클 실패: {e}")
        #     optimization_result["error"] = str(e)
        
        return optimization_result
    
    def get_comprehensive_status(self) -> Dict:
        """종합 상태 리포트"""
        uptime = datetime.now(KST) - self.system_start_time
        success_rate = (self.successful_executions / self.total_executions * 100) if self.total_executions > 0 else 0
        avg_execution_time = sum(self.execution_times) / len(self.execution_times) if self.execution_times else 0
        
        # AI 분석 통계
        ai_report = self.ai_analytics.get_intelligence_report() if self.ai_analytics.performance_history else {}
        
        # 스케줄러 상태
        scheduler_status = self.scheduler.get_status_report()
        
        # 검증 통계
        validation_stats = self.data_validator.get_validation_stats()
        
        # 최적화 요약 (주석 처리)
        # optimization_summary = self.optimization_engine.get_optimization_summary()
        
        return {
            "🎯 시스템 정보": {
                "시작 시간": self.system_start_time.strftime('%Y-%m-%d %H:%M:%S'),
                "운영 시간": f"{uptime.days}일 {uptime.seconds//3600}시간 {(uptime.seconds%3600)//60}분",
                "버전": "Ultimate v2.0"
            },
            "📊 실행 통계": {
                "총 실행": self.total_executions,
                "성공 실행": self.successful_executions,
                "성공률": f"{success_rate:.1f}%",
                "평균 실행시간": f"{avg_execution_time:.2f}초"
            },
            "🤖 AI 분석": {
                "예측 수행": self.ai_predictions_made,
                "최근 분석": ai_report.get("timestamp", "없음"),
                "현재 트렌드": ai_report.get("trend_analysis", "데이터 부족"),
                "위험 수준": ai_report.get("risk_analysis", {}).get("level", "🟢 낮음")
            },
            "📅 스케줄링": scheduler_status,
            "🔍 데이터 검증": {
                "총 검증": validation_stats.get('total', 0),
                "성공": validation_stats.get('valid', 0),
                "실패": validation_stats.get('invalid', 0),
                "성공률": f"{validation_stats.get('success_rate', 0):.1f}%"
            },
            # "🔧 최적화": {
            #     "적용된 최적화": self.optimizations_applied,
            #     "마지막 최적화": self.last_optimization.strftime('%Y-%m-%d %H:%M:%S') if self.last_optimization else "없음",
            #     "시스템 상태": optimization_summary.get("system_health", "🟢 양호")
            # },
            "💻 시스템 리소스": self._check_system_resources()
        }
    
    def run_single_ultimate_execution(self) -> bool:
        """단일 최고급 실행 (GitHub Actions용)"""
        logger.info("🌟 차세대 G라이더 시스템 실행 시작!")
        
        try:
            # 1. 누락된 메시지 복구
            logger.info("🔄 누락 메시지 복구 중...")
            recovered_count = self.scheduler.recover_missing_messages()
            if recovered_count and recovered_count > 0:
                logger.info(f"✅ {recovered_count}개 메시지 복구 완료")
            
            # 2. 지능형 자동화 실행
            execution_result = self.execute_intelligent_automation()
            
            # 3. 최적화 사이클 (주기적으로)
            # if self.total_executions % 10 == 0:  # 10번 실행마다
            #     optimization_result = self.run_optimization_cycle()
            #     logger.info(f"🔧 최적화 결과: {optimization_result}")
            
            # 4. 종합 상태 리포트
            status = self.get_comprehensive_status()
            logger.info("📊 시스템 상태 리포트:")
            for category, details in status.items():
                logger.info(f"  {category}:")
                if isinstance(details, dict):
                    for key, value in details.items():
                        logger.info(f"    • {key}: {value}")
                else:
                    logger.info(f"    {details}")
            
            # 5. AI 인사이트 출력
            if execution_result.get("ai_analysis"):
                ai_analysis = execution_result["ai_analysis"]
                if ai_analysis.get("prediction"):
                    pred = ai_analysis["prediction"]
                    logger.info(f"🤖 AI 예측: {pred.get('trend', 'N/A')} 트렌드, 신뢰도 {pred.get('confidence', 'N/A')}")
                    logger.info(f"🎯 AI 권장사항: {pred.get('recommendation', 'N/A')}")
            
            # 6. 성공/실패 판정
            success = execution_result.get("success", False)
            
            if success:
                logger.info("🎉 차세대 G라이더 시스템 실행 성공!")
            else:
                errors = execution_result.get("errors", [])
                logger.error(f"❌ 실행 실패: {', '.join(errors)}")
            
            return success
            
        except Exception as e:
            logger.error(f"💥 차세대 시스템 실행 중 치명적 오류: {e}")
            return False
    
    def start_ultimate_scheduler(self):
        """차세대 스케줄러 시작"""
        logger.info("🌟 차세대 G라이더 스케줄러 시작!")
        logger.info("🚀 AI 분석, 지능형 최적화, 다중 플랫폼 알림이 활성화되었습니다.")
        
        # 시작 상태 출력
        status = self.get_comprehensive_status()
        logger.info("📊 시스템 초기 상태:")
        for category, details in status.items():
            logger.info(f"  {category}: {details}")
        
        try:
            while True:
                now = datetime.now(KST)
                
                # 운영시간 체크 (10:00~23:59)
                if 10 <= now.hour <= 23:
                    # 정확한 분에 실행
                    expected_minutes = self.scheduler.validator.get_expected_minutes(now)
                    
                    if now.minute in expected_minutes and now.second < 30:
                        # 지능형 자동화 실행
                        execution_result = self.execute_intelligent_automation()
                        
                        if execution_result.get("success"):
                            logger.info(f"🌟 지능형 전송 완료: {now.strftime('%H:%M')}")
                        
                        # 전송 후 60초 대기 (중복 방지)
                        time.sleep(60)
                    
                    # 10분마다 누락 메시지 체크
                    elif now.minute % 10 == 0 and now.second < 30:
                        self.scheduler.recover_missing_messages()
                        time.sleep(60)
                    
                    # 1시간마다 최적화 수행 (주석 처리)
                    # elif now.minute == 0 and now.second < 30:
                    #     self.run_optimization_cycle()
                    #     time.sleep(60)
                
                # 30초마다 체크
                time.sleep(30)
                
        except KeyboardInterrupt:
            logger.info("🛑 사용자에 의해 중지됨")
            self._save_system_data()
        except Exception as e:
            logger.error(f"💥 차세대 스케줄러 오류: {e}")
            self._save_system_data()
    
    def _save_system_data(self):
        """시스템 데이터 저장"""
        try:
            # AI 분석 데이터 저장
            self.ai_analytics.save_analytics_data("ai_analytics_data.json")
            
            # 최적화 데이터 저장 (주석 처리)
            # self.optimization_engine.save_optimization_data("optimization_data.json")
            
            logger.info("💾 시스템 데이터 저장 완료")
            
        except Exception as e:
            logger.error(f"❌ 시스템 데이터 저장 실패: {e}")

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='차세대 G라이더 자동화 시스템')
    parser.add_argument('--mode', choices=['normal', 'single', 'status'], 
                       default='single', help='실행 모드')
    parser.add_argument('--config', default='../config.txt', help='설정 파일 경로')
    
    args = parser.parse_args()
    
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('ultimate_grider.log', encoding='utf-8')
        ]
    )
    
    try:
        # 환경변수 우선 체크
        import os
        rest_api_key = os.getenv('REST_API_KEY')
        refresh_token = os.getenv('REFRESH_TOKEN')
        
        # 디버그: 환경변수 상태 로깅
        logger.info(f"🔍 REST_API_KEY 환경변수 존재: {'있음' if rest_api_key else '없음'}")
        logger.info(f"🔍 REFRESH_TOKEN 환경변수 존재: {'있음' if refresh_token else '없음'}")
        
        if rest_api_key and refresh_token:
            logger.info("✅ 환경변수에서 REST_API_KEY, REFRESH_TOKEN 로드 완료")
        else:
            logger.error("❌ REST_API_KEY 또는 REFRESH_TOKEN 환경변수가 설정되지 않았습니다")
            logger.error("💡 GitHub Actions에서는 환경변수로 설정해야 합니다")
            
            # 추가 디버그: 모든 환경변수 출력
            env_vars = dict(os.environ)
            logger.error(f"🔍 현재 환경변수 개수: {len(env_vars)}")
            rest_keys = [k for k in env_vars.keys() if 'REST' in k.upper()]
            refresh_keys = [k for k in env_vars.keys() if 'REFRESH' in k.upper() or 'TOKEN' in k.upper()]
            logger.error(f"🔍 REST 관련 환경변수: {rest_keys}")
            logger.error(f"🔍 TOKEN 관련 환경변수: {refresh_keys}")
            
            sys.exit(1)
        
        # 시스템 초기화
        system = UltimateGriderSystem(
            rest_api_key=rest_api_key,
            refresh_token=refresh_token
        )
        
        # 기존 데이터 로드
        system.ai_analytics.load_analytics_data("ai_analytics_data.json")
        # system.optimization_engine.load_optimization_data("optimization_data.json")
        
        if args.mode == 'single':
            # 단일 실행
            success = system.run_single_ultimate_execution()
            sys.exit(0 if success else 1)
            
        elif args.mode == 'normal':
            # 지속적 실행
            system.start_ultimate_scheduler()
            
        elif args.mode == 'status':
            # 상태 확인만
            status = system.get_comprehensive_status()
            print("🌟 차세대 G라이더 시스템 상태:")
            for category, details in status.items():
                print(f"\n{category}:")
                if isinstance(details, dict):
                    for key, value in details.items():
                        print(f"  • {key}: {value}")
                else:
                    print(f"  {details}")
    
    except Exception as e:
        logger.error(f"💥 시스템 시작 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 