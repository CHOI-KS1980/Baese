"""
📁 파일 관리 유틸리티
파일 생성, 삭제, 백업, 압축, 검색 등
"""

import os
import shutil
import zipfile
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from auto_finance.utils.logger import setup_logger

logger = setup_logger(__name__)

class FileManager:
    """파일 관리 클래스"""
    
    def __init__(self, base_dir: str = "data"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # 하위 디렉토리 생성
        self.dirs = {
            'cache': self.base_dir / 'cache',
            'logs': self.base_dir / 'logs',
            'reports': self.base_dir / 'reports',
            'backups': self.base_dir / 'backups',
            'temp': self.base_dir / 'temp',
            'uploads': self.base_dir / 'uploads',
            'generated': self.base_dir / 'generated'
        }
        
        # 디렉토리 생성
        for dir_path in self.dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📁 파일 매니저 초기화: {self.base_dir}")
    
    def create_file(self, file_path: str, content: str = "", overwrite: bool = False) -> bool:
        """파일 생성"""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            if path.exists() and not overwrite:
                logger.warning(f"⚠️ 파일이 이미 존재합니다: {file_path}")
                return False
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"📄 파일 생성 완료: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 파일 생성 실패 ({file_path}): {e}")
            return False
    
    def read_file(self, file_path: str) -> Optional[str]:
        """파일 읽기"""
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"❌ 파일이 존재하지 않습니다: {file_path}")
                return None
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return content
            
        except Exception as e:
            logger.error(f"❌ 파일 읽기 실패 ({file_path}): {e}")
            return None
    
    def delete_file(self, file_path: str) -> bool:
        """파일 삭제"""
        try:
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"⚠️ 파일이 존재하지 않습니다: {file_path}")
                return False
            
            path.unlink()
            logger.info(f"🗑️ 파일 삭제 완료: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 파일 삭제 실패 ({file_path}): {e}")
            return False
    
    def copy_file(self, src_path: str, dst_path: str, overwrite: bool = False) -> bool:
        """파일 복사"""
        try:
            src = Path(src_path)
            dst = Path(dst_path)
            
            if not src.exists():
                logger.error(f"❌ 원본 파일이 존재하지 않습니다: {src_path}")
                return False
            
            if dst.exists() and not overwrite:
                logger.warning(f"⚠️ 대상 파일이 이미 존재합니다: {dst_path}")
                return False
            
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            
            logger.info(f"📋 파일 복사 완료: {src_path} → {dst_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 파일 복사 실패 ({src_path} → {dst_path}): {e}")
            return False
    
    def move_file(self, src_path: str, dst_path: str, overwrite: bool = False) -> bool:
        """파일 이동"""
        try:
            src = Path(src_path)
            dst = Path(dst_path)
            
            if not src.exists():
                logger.error(f"❌ 원본 파일이 존재하지 않습니다: {src_path}")
                return False
            
            if dst.exists() and not overwrite:
                logger.warning(f"⚠️ 대상 파일이 이미 존재합니다: {dst_path}")
                return False
            
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            
            logger.info(f"📦 파일 이동 완료: {src_path} → {dst_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 파일 이동 실패 ({src_path} → {dst_path}): {e}")
            return False
    
    def list_files(self, directory: str, pattern: str = "*", recursive: bool = False) -> List[str]:
        """파일 목록 조회"""
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                logger.error(f"❌ 디렉토리가 존재하지 않습니다: {directory}")
                return []
            
            if recursive:
                files = list(dir_path.rglob(pattern))
            else:
                files = list(dir_path.glob(pattern))
            
            file_paths = [str(f) for f in files if f.is_file()]
            logger.debug(f"📋 파일 목록 조회: {len(file_paths)}개 파일")
            
            return file_paths
            
        except Exception as e:
            logger.error(f"❌ 파일 목록 조회 실패 ({directory}): {e}")
            return []
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """파일 정보 조회"""
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"❌ 파일이 존재하지 않습니다: {file_path}")
                return None
            
            stat = path.stat()
            
            info = {
                'name': path.name,
                'path': str(path),
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'extension': path.suffix,
                'is_file': path.is_file(),
                'is_directory': path.is_dir()
            }
            
            return info
            
        except Exception as e:
            logger.error(f"❌ 파일 정보 조회 실패 ({file_path}): {e}")
            return None
    
    def create_backup(self, file_path: str, backup_dir: Optional[str] = None) -> Optional[str]:
        """파일 백업 생성"""
        try:
            src_path = Path(file_path)
            if not src_path.exists():
                logger.error(f"❌ 백업할 파일이 존재하지 않습니다: {file_path}")
                return None
            
            # 백업 디렉토리 설정
            if backup_dir:
                backup_path = Path(backup_dir)
            else:
                backup_path = self.dirs['backups']
            
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # 백업 파일명 생성 (타임스탬프 포함)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{src_path.stem}_{timestamp}{src_path.suffix}"
            backup_file_path = backup_path / backup_filename
            
            # 파일 복사
            shutil.copy2(src_path, backup_file_path)
            
            logger.info(f"💾 백업 생성 완료: {file_path} → {backup_file_path}")
            return str(backup_file_path)
            
        except Exception as e:
            logger.error(f"❌ 백업 생성 실패 ({file_path}): {e}")
            return None
    
    def cleanup_old_files(self, directory: str, days: int = 30, pattern: str = "*") -> int:
        """오래된 파일 정리"""
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                logger.error(f"❌ 디렉토리가 존재하지 않습니다: {directory}")
                return 0
            
            cutoff_date = datetime.now() - timedelta(days=days)
            deleted_count = 0
            
            for file_path in dir_path.glob(pattern):
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_date:
                        file_path.unlink()
                        deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"🧹 오래된 파일 정리: {deleted_count}개 파일 삭제")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ 파일 정리 실패 ({directory}): {e}")
            return 0
    
    def create_zip_archive(self, source_dir: str, output_path: str, 
                          include_pattern: str = "*") -> bool:
        """ZIP 아카이브 생성"""
        try:
            source_path = Path(source_dir)
            if not source_path.exists():
                logger.error(f"❌ 소스 디렉토리가 존재하지 않습니다: {source_dir}")
                return False
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in source_path.rglob(include_pattern):
                    if file_path.is_file():
                        arcname = file_path.relative_to(source_path)
                        zipf.write(file_path, arcname)
            
            logger.info(f"📦 ZIP 아카이브 생성 완료: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ ZIP 아카이브 생성 실패: {e}")
            return False
    
    def extract_zip_archive(self, zip_path: str, extract_dir: str) -> bool:
        """ZIP 아카이브 압축 해제"""
        try:
            zip_path = Path(zip_path)
            if not zip_path.exists():
                logger.error(f"❌ ZIP 파일이 존재하지 않습니다: {zip_path}")
                return False
            
            extract_path = Path(extract_dir)
            extract_path.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(extract_path)
            
            logger.info(f"📦 ZIP 아카이브 압축 해제 완료: {zip_path} → {extract_dir}")
            return True
            
        except Exception as e:
            logger.error(f"❌ ZIP 아카이브 압축 해제 실패: {e}")
            return False
    
    def get_directory_size(self, directory: str) -> int:
        """디렉토리 크기 계산 (바이트)"""
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                return 0
            
            total_size = 0
            for file_path in dir_path.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            
            return total_size
            
        except Exception as e:
            logger.error(f"❌ 디렉토리 크기 계산 실패 ({directory}): {e}")
            return 0

# 전역 파일 매니저 인스턴스
file_manager = FileManager() 