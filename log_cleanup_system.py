#!/usr/bin/env python3
"""
🧹 로그 파일 자동 관리 및 최적화 시스템

주요 기능:
1. 로그 파일 크기 모니터링
2. 자동 로그 로테이션 (크기/날짜 기준)
3. 오래된 로그 파일 자동 삭제
4. GitHub 리포지토리 최적화
5. 시스템 리소스 모니터링
"""

import os
import sys
import shutil
import gzip
import logging
import schedule
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import json
import subprocess
import threading

# 로깅 설정 (자체 로그는 최소화)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('log_cleanup.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LogCleanupManager:
    """로그 파일 자동 관리자"""
    
    def __init__(self, config_file='log_cleanup_config.json'):
        self.config_file = config_file
        self.config = self.load_config()
        self.setup_logging()
        
    def load_config(self) -> Dict[str, Any]:
        """설정 파일 로드 또는 기본값 생성"""
        default_config = {
            "log_directories": [
                ".",
                "logs/",
                "semiauto/",
                "autoinfo/core/",
                "autoinfo/webhook/",
                "kakao/"
            ],
            "log_patterns": [
                "*.log",
                "debug_*.html",
                "*.debug",
                "*.tmp"
            ],
            "max_file_size_mb": 10,  # 10MB 이상 파일 압축
            "max_age_days": 7,       # 7일 이상 파일 삭제
            "keep_compressed_days": 30,  # 압축 파일 30일 보관
            "exclude_files": [
                "log_cleanup.log",
                "requirements.txt",
                "README.md"
            ],
            "github_cleanup": {
                "enabled": True,
                "auto_commit": True,
                "commit_threshold_mb": 5  # 5MB 이상 정리시 자동 커밋
            },
            "monitoring": {
                "check_interval_minutes": 60,  # 1시간마다 체크
                "alert_threshold_mb": 50,      # 50MB 이상시 알림
                "max_total_log_size_mb": 100   # 전체 로그 100MB 제한
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 기본값과 병합
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                logger.error(f"❌ 설정 파일 로드 실패: {e}, 기본값 사용")
        
        # 기본 설정 파일 생성
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config: Dict[str, Any]):
        """설정 파일 저장"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ 설정 파일 저장 실패: {e}")
    
    def setup_logging(self):
        """로깅 설정 최적화"""
        # 기존 핸들러들의 로그 레벨 조정
        for handler in logging.root.handlers:
            if isinstance(handler, logging.FileHandler):
                # 로그 파일 크기 제한
                handler.setLevel(logging.WARNING)  # WARNING 이상만 파일에 기록
    
    def find_log_files(self) -> List[Path]:
        """로그 파일 찾기"""
        log_files = []
        
        for directory in self.config['log_directories']:
            dir_path = Path(directory)
            if not dir_path.exists():
                continue
                
            for pattern in self.config['log_patterns']:
                for file_path in dir_path.glob(pattern):
                    if file_path.is_file() and file_path.name not in self.config['exclude_files']:
                        log_files.append(file_path)
        
        return log_files
    
    def get_file_size_mb(self, file_path: Path) -> float:
        """파일 크기 MB 단위로 반환"""
        try:
            return file_path.stat().st_size / (1024 * 1024)
        except:
            return 0
    
    def get_file_age_days(self, file_path: Path) -> int:
        """파일 생성일로부터 경과 일수"""
        try:
            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            return (datetime.now() - file_time).days
        except:
            return 0
    
    def compress_log_file(self, file_path: Path) -> bool:
        """로그 파일 압축"""
        try:
            compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
            
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # 원본 파일 삭제
            file_path.unlink()
            
            logger.info(f"🗜️ 압축 완료: {file_path.name} → {compressed_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 압축 실패 {file_path}: {e}")
            return False
    
    def delete_old_file(self, file_path: Path) -> bool:
        """오래된 파일 삭제"""
        try:
            file_path.unlink()
            logger.info(f"🗑️ 삭제 완료: {file_path.name}")
            return True
        except Exception as e:
            logger.error(f"❌ 삭제 실패 {file_path}: {e}")
            return False
    
    def cleanup_logs(self) -> Dict[str, Any]:
        """로그 파일 정리 실행"""
        logger.info("🧹 로그 파일 정리 시작...")
        
        log_files = self.find_log_files()
        stats = {
            'total_files': len(log_files),
            'compressed_files': 0,
            'deleted_files': 0,
            'freed_space_mb': 0,
            'errors': 0
        }
        
        for file_path in log_files:
            try:
                file_size_mb = self.get_file_size_mb(file_path)
                file_age_days = self.get_file_age_days(file_path)
                
                # 압축된 파일은 더 오래 보관 후 삭제
                if file_path.suffix == '.gz':
                    if file_age_days > self.config['keep_compressed_days']:
                        if self.delete_old_file(file_path):
                            stats['deleted_files'] += 1
                            stats['freed_space_mb'] += file_size_mb
                    continue
                
                # 오래된 파일 삭제
                if file_age_days > self.config['max_age_days']:
                    if self.delete_old_file(file_path):
                        stats['deleted_files'] += 1
                        stats['freed_space_mb'] += file_size_mb
                
                # 큰 파일 압축
                elif file_size_mb > self.config['max_file_size_mb']:
                    if self.compress_log_file(file_path):
                        stats['compressed_files'] += 1
                        # 압축으로 절약된 공간 추정 (약 70% 압축률)
                        stats['freed_space_mb'] += file_size_mb * 0.7
                        
            except Exception as e:
                logger.error(f"❌ 파일 처리 실패 {file_path}: {e}")
                stats['errors'] += 1
        
        logger.info(f"✅ 로그 정리 완료: 압축 {stats['compressed_files']}개, 삭제 {stats['deleted_files']}개, 절약 {stats['freed_space_mb']:.1f}MB")
        return stats
    
    def monitor_disk_usage(self) -> Dict[str, Any]:
        """디스크 사용량 모니터링"""
        try:
            total_log_size = 0
            log_files = self.find_log_files()
            
            for file_path in log_files:
                total_log_size += self.get_file_size_mb(file_path)
            
            # 전체 디스크 사용량
            disk_usage = shutil.disk_usage('.')
            free_space_gb = disk_usage.free / (1024**3)
            
            return {
                'total_log_size_mb': total_log_size,
                'free_space_gb': free_space_gb,
                'log_files_count': len(log_files),
                'alert_needed': total_log_size > self.config['monitoring']['alert_threshold_mb']
            }
            
        except Exception as e:
            logger.error(f"❌ 디스크 모니터링 실패: {e}")
            return {'error': str(e)}
    
    def github_cleanup(self) -> bool:
        """GitHub 리포지토리 정리"""
        if not self.config['github_cleanup']['enabled']:
            return False
        
        try:
            # Git 상태 확인
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.warning("⚠️ Git 리포지토리가 아니거나 Git이 설치되지 않음")
                return False
            
            # 변경된 파일이 있는지 확인
            if result.stdout.strip():
                logger.info("📝 Git에 변경사항 감지됨")
                
                # 자동 커밋이 활성화된 경우
                if self.config['github_cleanup']['auto_commit']:
                    try:
                        # .gitignore 확인 및 추가
                        subprocess.run(['git', 'add', '.gitignore'], check=True)
                        
                        # 로그 파일들이 실수로 추가되지 않도록 제거
                        log_patterns = ['*.log', '*.debug', 'debug_*.html']
                        for pattern in log_patterns:
                            subprocess.run(['git', 'rm', '--cached', pattern], 
                                         capture_output=True)
                        
                        # 커밋
                        commit_message = f"🧹 자동 로그 정리 - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                        subprocess.run(['git', 'commit', '-m', commit_message], 
                                     check=True)
                        
                        logger.info("✅ 자동 커밋 완료")
                        return True
                        
                    except subprocess.CalledProcessError as e:
                        logger.error(f"❌ 자동 커밋 실패: {e}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ GitHub 정리 실패: {e}")
            return False
    
    def generate_report(self) -> str:
        """시스템 상태 리포트 생성"""
        try:
            disk_info = self.monitor_disk_usage()
            log_files = self.find_log_files()
            
            report = f"""📊 로그 관리 시스템 상태 리포트
            
🕐 생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📁 로그 파일 현황:
• 총 파일 수: {len(log_files)}개
• 총 크기: {disk_info.get('total_log_size_mb', 0):.1f}MB
• 여유 공간: {disk_info.get('free_space_gb', 0):.1f}GB

⚙️ 설정:
• 최대 파일 크기: {self.config['max_file_size_mb']}MB
• 보관 기간: {self.config['max_age_days']}일
• 압축 파일 보관: {self.config['keep_compressed_days']}일

🎯 다음 정리 예정: {datetime.now() + timedelta(minutes=self.config['monitoring']['check_interval_minutes'])}
"""
            
            if disk_info.get('alert_needed'):
                report += f"\n⚠️ 경고: 로그 파일 크기가 {self.config['monitoring']['alert_threshold_mb']}MB를 초과했습니다!"
            
            return report
            
        except Exception as e:
            return f"❌ 리포트 생성 실패: {e}"
    
    def start_monitoring(self):
        """자동 모니터링 시작"""
        logger.info("🚀 로그 자동 관리 시스템 시작")
        
        # 스케줄 설정
        interval = self.config['monitoring']['check_interval_minutes']
        schedule.every(interval).minutes.do(self.cleanup_logs)
        
        # 매일 자정에 GitHub 정리
        schedule.every().day.at("00:30").do(self.github_cleanup)
        
        # 매주 일요일에 전체 리포트 생성
        schedule.every().sunday.at("23:00").do(self.generate_weekly_report)
        
        logger.info(f"⏰ 스케줄 설정 완료: {interval}분마다 정리, 매일 00:30 GitHub 정리")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 체크
        except KeyboardInterrupt:
            logger.info("⏹️ 로그 관리 시스템 종료")
    
    def generate_weekly_report(self):
        """주간 리포트 생성"""
        report = self.generate_report()
        
        # 리포트를 파일로 저장
        report_file = f"log_report_{datetime.now().strftime('%Y%m%d')}.txt"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"📋 주간 리포트 생성: {report_file}")
        except Exception as e:
            logger.error(f"❌ 리포트 저장 실패: {e}")

def main():
    """메인 실행 함수"""
    print("🧹 로그 파일 자동 관리 시스템")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        manager = LogCleanupManager()
        
        if command == 'cleanup':
            # 즉시 정리 실행
            stats = manager.cleanup_logs()
            print(f"✅ 정리 완료: {stats}")
            
        elif command == 'report':
            # 상태 리포트 출력
            report = manager.generate_report()
            print(report)
            
        elif command == 'monitor':
            # 모니터링 시작
            manager.start_monitoring()
            
        elif command == 'github':
            # GitHub 정리
            success = manager.github_cleanup()
            print(f"GitHub 정리: {'성공' if success else '실패'}")
            
        else:
            print("사용법: python log_cleanup_system.py [cleanup|report|monitor|github]")
    
    else:
        # 기본: 즉시 정리 후 모니터링 시작
        manager = LogCleanupManager()
        manager.cleanup_logs()
        manager.start_monitoring()

if __name__ == "__main__":
    main() 