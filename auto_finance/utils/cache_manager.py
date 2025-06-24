"""
💾 캐시 관리 유틸리티
메모리/파일/Redis 캐싱, TTL 관리, 캐시 무효화 등
"""

import json
import pickle
import hashlib
import time
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
from pathlib import Path
from auto_finance.utils.logger import setup_logger

logger = setup_logger(__name__)

class CacheManager:
    """캐시 관리 클래스"""
    
    def __init__(self, cache_dir: str = "data/cache", default_ttl: int = 3600):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"💾 캐시 매니저 초기화: {self.cache_dir}")
    
    def _generate_key(self, data: Any) -> str:
        """캐시 키 생성"""
        if isinstance(data, str):
            content = data
        else:
            content = json.dumps(data, sort_keys=True, default=str)
        
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> Path:
        """캐시 파일 경로 반환"""
        return self.cache_dir / f"{key}.cache"
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """캐시 저장"""
        try:
            ttl = ttl or self.default_ttl
            expiry = datetime.now() + timedelta(seconds=ttl)
            
            cache_data = {
                'data': data,
                'expiry': expiry.isoformat(),
                'created': datetime.now().isoformat()
            }
            
            # 메모리 캐시
            self.memory_cache[key] = cache_data
            
            # 파일 캐시
            cache_path = self._get_cache_path(key)
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
            
            logger.debug(f"💾 캐시 저장: {key} (TTL: {ttl}초)")
            return True
            
        except Exception as e:
            logger.error(f"❌ 캐시 저장 실패 ({key}): {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """캐시 조회"""
        try:
            # 메모리 캐시 먼저 확인
            if key in self.memory_cache:
                cache_data = self.memory_cache[key]
                expiry = datetime.fromisoformat(cache_data['expiry'])
                
                if datetime.now() < expiry:
                    logger.debug(f"💾 메모리 캐시 히트: {key}")
                    return cache_data['data']
                else:
                    del self.memory_cache[key]
            
            # 파일 캐시 확인
            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                with open(cache_path, 'rb') as f:
                    cache_data = pickle.load(f)
                
                expiry = datetime.fromisoformat(cache_data['expiry'])
                
                if datetime.now() < expiry:
                    # 메모리 캐시에 복원
                    self.memory_cache[key] = cache_data
                    logger.debug(f"💾 파일 캐시 히트: {key}")
                    return cache_data['data']
                else:
                    # 만료된 캐시 삭제
                    cache_path.unlink()
                    logger.debug(f"🗑️ 만료된 캐시 삭제: {key}")
            
            logger.debug(f"💾 캐시 미스: {key}")
            return None
            
        except Exception as e:
            logger.error(f"❌ 캐시 조회 실패 ({key}): {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """캐시 삭제"""
        try:
            # 메모리 캐시 삭제
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            # 파일 캐시 삭제
            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                cache_path.unlink()
            
            logger.debug(f"🗑️ 캐시 삭제: {key}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 캐시 삭제 실패 ({key}): {e}")
            return False
    
    def clear(self, pattern: Optional[str] = None) -> int:
        """캐시 전체 삭제"""
        try:
            deleted_count = 0
            
            # 메모리 캐시 삭제
            if pattern:
                keys_to_delete = [k for k in self.memory_cache.keys() if pattern in k]
            else:
                keys_to_delete = list(self.memory_cache.keys())
            
            for key in keys_to_delete:
                del self.memory_cache[key]
                deleted_count += 1
            
            # 파일 캐시 삭제
            if pattern:
                cache_files = [f for f in self.cache_dir.glob("*.cache") if pattern in f.stem]
            else:
                cache_files = list(self.cache_dir.glob("*.cache"))
            
            for cache_file in cache_files:
                cache_file.unlink()
                deleted_count += 1
            
            logger.info(f"🗑️ 캐시 전체 삭제: {deleted_count}개")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ 캐시 전체 삭제 실패: {e}")
            return 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """캐시 통계 반환"""
        try:
            memory_cache_size = len(self.memory_cache)
            file_cache_count = len(list(self.cache_dir.glob("*.cache")))
            
            # 메모리 캐시 크기 계산
            memory_size = 0
            for cache_data in self.memory_cache.values():
                memory_size += len(str(cache_data))
            
            # 파일 캐시 크기 계산
            file_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.cache"))
            
            return {
                'memory_cache_size': memory_cache_size,
                'file_cache_count': file_cache_count,
                'memory_size_bytes': memory_size,
                'file_size_bytes': file_size,
                'cache_dir': str(self.cache_dir),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 캐시 통계 조회 실패: {e}")
            return {}
    
    def cleanup_expired(self) -> int:
        """만료된 캐시 정리"""
        try:
            cleaned_count = 0
            
            # 메모리 캐시 정리
            keys_to_delete = []
            for key, cache_data in self.memory_cache.items():
                expiry = datetime.fromisoformat(cache_data['expiry'])
                if datetime.now() >= expiry:
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                del self.memory_cache[key]
                cleaned_count += 1
            
            # 파일 캐시 정리
            for cache_file in self.cache_dir.glob("*.cache"):
                try:
                    with open(cache_file, 'rb') as f:
                        cache_data = pickle.load(f)
                    
                    expiry = datetime.fromisoformat(cache_data['expiry'])
                    if datetime.now() >= expiry:
                        cache_file.unlink()
                        cleaned_count += 1
                        
                except Exception as e:
                    logger.warning(f"⚠️ 캐시 파일 읽기 실패 ({cache_file}): {e}")
                    cache_file.unlink()  # 손상된 파일 삭제
                    cleaned_count += 1
            
            if cleaned_count > 0:
                logger.info(f"🧹 만료된 캐시 정리: {cleaned_count}개")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"❌ 캐시 정리 실패: {e}")
            return 0

# 전역 캐시 매니저 인스턴스
cache_manager = CacheManager() 