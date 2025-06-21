#!/usr/bin/env python3
"""
🔍 통합 자동화 모니터링 시스템
- 모든 자동화 시스템 상태 모니터링
- 실행 스케줄 통합 관리
- 성능 최적화 자동 실행
- 리포지토리 건강도 실시간 체크
"""

import os
import sys
import time
import json
import schedule
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/unified_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UnifiedMonitor:
    def __init__(self):
        self.base_dir = Path('.')
        self.logs_dir = Path('logs')
        self.logs_dir.mkdir(exist_ok=True)
        
        # 모니터링 대상 시스템들
        self.systems = {
            'semiauto_grider_24h': {
                'name': '심플 배민 플러스 24시간 자동화',
                'workflow': '.github/workflows/semiauto-grider-24h.yml',
                'script': 'semiauto/core/final_solution.py',
                'status': 'unknown'
            },
            'log_cleanup': {
                'name': '로그 정리 시스템',
                'workflow': '.github/workflows/log-cleanup.yml',
                'script': 'log_cleanup_system.py',
                'status': 'unknown'
            }
        }
        
        self.last_health_check = None
        self.health_score = 100
        
    def check_system_status(self) -> Dict[str, Any]:
        """모든 시스템 상태 체크"""
        logger.info("🔍 시스템 상태 체크 시작")
        
        status_report = {
            'timestamp': datetime.now().isoformat(),
            'systems': {},
            'overall_health': 'unknown',
            'issues': [],
            'recommendations': []
        }
        
        for system_id, system_info in self.systems.items():
            try:
                system_status = self._check_individual_system(system_id, system_info)
                status_report['systems'][system_id] = system_status
                
                if system_status['status'] == 'error':
                    status_report['issues'].append(f"⚠️ {system_info['name']}: {system_status.get('error', '알 수 없는 오류')}")
                    
            except Exception as e:
                logger.error(f"❌ {system_info['name']} 상태 체크 실패: {e}")
                status_report['systems'][system_id] = {
                    'status': 'error',
                    'error': str(e),
                    'last_check': datetime.now().isoformat()
                }
        
        # 전체 건강도 계산
        healthy_systems = sum(1 for s in status_report['systems'].values() if s['status'] == 'healthy')
        total_systems = len(status_report['systems'])
        
        if healthy_systems == total_systems:
            status_report['overall_health'] = 'excellent'
        elif healthy_systems >= total_systems * 0.8:
            status_report['overall_health'] = 'good'
        elif healthy_systems >= total_systems * 0.6:
            status_report['overall_health'] = 'warning'
        else:
            status_report['overall_health'] = 'critical'
        
        # 추천사항 생성
        status_report['recommendations'] = self._generate_recommendations(status_report)
        
        logger.info(f"✅ 시스템 상태 체크 완료: {status_report['overall_health']}")
        return status_report
    
    def _check_individual_system(self, system_id: str, system_info: Dict) -> Dict[str, Any]:
        """개별 시스템 상태 체크"""
        status = {
            'name': system_info['name'],
            'status': 'healthy',
            'last_check': datetime.now().isoformat(),
            'details': {}
        }
        
        # 1. 워크플로우 파일 존재 체크
        workflow_path = Path(system_info['workflow'])
        if not workflow_path.exists():
            status['status'] = 'error'
            status['error'] = f"워크플로우 파일 없음: {workflow_path}"
            return status
        
        # 2. 스크립트 파일 존재 체크
        script_path = Path(system_info['script'])
        if not script_path.exists():
            status['status'] = 'warning'
            status['warning'] = f"스크립트 파일 없음: {script_path}"
        
        # 3. 최근 실행 로그 체크
        log_pattern = f"*{system_id}*.log"
        recent_logs = list(self.logs_dir.glob(log_pattern))
        
        if recent_logs:
            latest_log = max(recent_logs, key=lambda x: x.stat().st_mtime)
            log_age = datetime.now() - datetime.fromtimestamp(latest_log.stat().st_mtime)
            
            status['details']['last_log'] = latest_log.name
            status['details']['log_age_hours'] = log_age.total_seconds() / 3600
            
            # 24시간 이상 로그가 없으면 경고
            if log_age > timedelta(hours=24):
                status['status'] = 'warning'
                status['warning'] = f"24시간 이상 로그 없음 (마지막: {log_age.days}일 전)"
        
        # 4. 파일 크기 체크
        if script_path.exists():
            file_size = script_path.stat().st_size
            status['details']['script_size'] = file_size
            
            # 100MB 이상이면 경고
            if file_size > 100 * 1024 * 1024:
                status['status'] = 'warning'
                status['warning'] = f"스크립트 파일이 너무 큼: {file_size / 1024 / 1024:.1f}MB"
        
        return status
    
    def _generate_recommendations(self, status_report: Dict) -> List[str]:
        """시스템 상태 기반 추천사항 생성"""
        recommendations = []
        
        # 오류가 있는 시스템들
        error_systems = [s for s in status_report['systems'].values() if s['status'] == 'error']
        if error_systems:
            recommendations.append(f"🔴 {len(error_systems)}개 시스템에 오류가 있습니다. 즉시 수정이 필요합니다.")
        
        # 경고가 있는 시스템들
        warning_systems = [s for s in status_report['systems'].values() if s['status'] == 'warning']
        if warning_systems:
            recommendations.append(f"🟡 {len(warning_systems)}개 시스템에 경고가 있습니다. 점검을 권장합니다.")
        
        # 로그 정리 필요 여부
        log_files = list(self.logs_dir.glob('*.log'))
        if len(log_files) > 20:
            recommendations.append("🧹 로그 파일이 많습니다. 정리를 권장합니다.")
        
        # 최적화 권장
        if not recommendations:
            recommendations.append("✅ 모든 시스템이 정상 작동 중입니다!")
            recommendations.append("💡 정기적인 최적화를 위해 'python3 optimize_repository.py full' 실행을 권장합니다.")
        
        return recommendations
    
    def auto_optimize(self):
        """자동 최적화 실행"""
        logger.info("🚀 자동 최적화 시작")
        
        try:
            # 1. 로그 정리
            result = subprocess.run([
                'python3', 'log_cleanup_system.py', 'cleanup'
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("✅ 로그 정리 완료")
            else:
                logger.error(f"❌ 로그 정리 실패: {result.stderr}")
            
            # 2. 리포지토리 최적화
            result = subprocess.run([
                'python3', 'optimize_repository.py', 'clean'
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("✅ 리포지토리 최적화 완료")
            else:
                logger.error(f"❌ 리포지토리 최적화 실패: {result.stderr}")
            
            # 3. Git 최적화
            result = subprocess.run([
                'python3', 'log_cleanup_system.py', 'optimize_git'
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("✅ Git 최적화 완료")
            else:
                logger.error(f"❌ Git 최적화 실패: {result.stderr}")
                
        except Exception as e:
            logger.error(f"❌ 자동 최적화 중 오류: {e}")
    
    def generate_daily_report(self):
        """일일 리포트 생성"""
        logger.info("📊 일일 리포트 생성 시작")
        
        status_report = self.check_system_status()
        
        # 리포트 파일 생성
        report_date = datetime.now().strftime('%Y-%m-%d')
        report_file = self.logs_dir / f'daily_report_{report_date}.json'
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(status_report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ 일일 리포트 저장: {report_file}")
            
            # 콘솔에 요약 출력
            self._print_status_summary(status_report)
            
        except Exception as e:
            logger.error(f"❌ 일일 리포트 저장 실패: {e}")
    
    def _print_status_summary(self, status_report: Dict):
        """상태 요약 출력"""
        print("\n" + "="*60)
        print(f"🔍 자동화 시스템 상태 리포트 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # 전체 건강도
        health_emoji = {
            'excellent': '🟢',
            'good': '🟡',
            'warning': '🟠',
            'critical': '🔴'
        }
        
        health = status_report['overall_health']
        print(f"📈 전체 건강도: {health_emoji.get(health, '❓')} {health.upper()}")
        
        # 시스템별 상태
        print("\n📋 시스템별 상태:")
        for system_id, system_status in status_report['systems'].items():
            status_emoji = {
                'healthy': '✅',
                'warning': '⚠️',
                'error': '❌'
            }
            
            emoji = status_emoji.get(system_status['status'], '❓')
            name = system_status['name']
            status = system_status['status'].upper()
            
            print(f"   {emoji} {name}: {status}")
            
            if 'error' in system_status:
                print(f"      🔴 오류: {system_status['error']}")
            elif 'warning' in system_status:
                print(f"      🟡 경고: {system_status['warning']}")
        
        # 문제점
        if status_report['issues']:
            print("\n⚠️ 발견된 문제점:")
            for issue in status_report['issues']:
                print(f"   {issue}")
        
        # 추천사항
        if status_report['recommendations']:
            print("\n💡 추천사항:")
            for rec in status_report['recommendations']:
                print(f"   {rec}")
        
        print("="*60)
    
    def start_monitoring(self):
        """모니터링 시작"""
        logger.info("🚀 통합 모니터링 시스템 시작")
        
        # 스케줄 설정
        schedule.every().hour.do(self.check_system_status)  # 매시간 상태 체크
        schedule.every().day.at("07:00").do(self.auto_optimize)  # 매일 07:00 자동 최적화
        schedule.every().day.at("08:00").do(self.generate_daily_report)  # 매일 08:00 일일 리포트
        
        print("🔍 통합 자동화 모니터링 시스템 시작")
        print("="*50)
        print("📅 스케줄:")
        print("   🔄 매시간: 시스템 상태 체크")
        print("   🚀 07:00: 자동 최적화")
        print("   📊 08:00: 일일 리포트 생성")
        print("="*50)
        
        # 초기 상태 체크
        self.generate_daily_report()
        
        # 무한 루프로 스케줄 실행
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 체크
                
        except KeyboardInterrupt:
            logger.info("🛑 모니터링 시스템 종료")
            print("\n🛑 모니터링 시스템이 종료되었습니다.")

def main():
    """메인 실행 함수"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        monitor = UnifiedMonitor()
        
        if command == 'status':
            # 현재 상태 체크
            status_report = monitor.check_system_status()
            monitor._print_status_summary(status_report)
            
        elif command == 'report':
            # 일일 리포트 생성
            monitor.generate_daily_report()
            
        elif command == 'optimize':
            # 자동 최적화 실행
            monitor.auto_optimize()
            
        elif command == 'monitor':
            # 모니터링 시작
            monitor.start_monitoring()
            
        else:
            print("사용법: python3 unified_monitor.py [status|report|optimize|monitor]")
            print("")
            print("명령어:")
            print("  status   - 현재 시스템 상태 체크")
            print("  report   - 일일 리포트 생성")
            print("  optimize - 자동 최적화 실행")
            print("  monitor  - 실시간 모니터링 시작")
    
    else:
        print("🔍 통합 자동화 모니터링 시스템")
        print("="*50)
        print("사용법: python3 unified_monitor.py [명령어]")
        print("")
        print("명령어:")
        print("  status   - 현재 시스템 상태 체크")
        print("  report   - 일일 리포트 생성")
        print("  optimize - 자동 최적화 실행")
        print("  monitor  - 실시간 모니터링 시작")

if __name__ == "__main__":
    main()
