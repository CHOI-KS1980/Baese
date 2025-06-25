"""
📤 업로드 관리자 모듈
티스토리 및 기타 플랫폼에 콘텐츠를 업로드하는 시스템
"""

import asyncio
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

# 유틸리티 임포트
from auto_finance.utils.logger import setup_logger
from auto_finance.utils.error_handler import ErrorHandler
from auto_finance.utils.file_manager import file_manager

logger = setup_logger(__name__)

@dataclass
class UploadRequest:
    """업로드 요청 데이터 클래스"""
    title: str
    content: str
    category: str
    tags: List[str]
    platform: str = "tistory"
    publish_status: str = "publish"  # draft, publish
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None

class UploadManager:
    """업로드 관리자 클래스"""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.stats = {
            'total_uploads': 0,
            'successful_uploads': 0,
            'failed_uploads': 0,
            'processing_time': 0.0,
            'last_upload': None
        }
        
        # 업로드 결과 저장소
        self.upload_results = []
        
        logger.info("📤 업로드 관리자 초기화 완료")
    
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        await self.cleanup()
    
    async def upload_content(self, request: UploadRequest) -> Dict[str, Any]:
        """단일 콘텐츠 업로드"""
        start_time = time.time()
        
        try:
            logger.info(f"📤 콘텐츠 업로드 시작: {request.title}")
            
            # 플랫폼별 업로드 처리
            if request.platform == "tistory":
                result = await self._upload_to_tistory(request)
            else:
                raise ValueError(f"지원하지 않는 플랫폼: {request.platform}")
            
            # 통계 업데이트
            processing_time = time.time() - start_time
            self._update_stats(True, processing_time)
            
            # 결과 저장
            result['processing_time'] = processing_time
            result['timestamp'] = datetime.now().isoformat()
            self.upload_results.append(result)
            
            logger.info(f"✅ 업로드 완료: {request.title}")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._update_stats(False, processing_time)
            self.error_handler.handle_error(e, f"업로드 실패: {request.title}")
            logger.error(f"❌ 업로드 실패: {request.title} - {e}")
            
            return {
                'success': False,
                'error': str(e),
                'title': request.title,
                'processing_time': processing_time,
                'timestamp': datetime.now().isoformat()
            }
    
    async def upload_multiple_contents(self, requests: List[UploadRequest]) -> List[Dict[str, Any]]:
        """다중 콘텐츠 업로드"""
        logger.info(f"📤 다중 콘텐츠 업로드 시작: {len(requests)}개")
        
        results = []
        for request in requests:
            result = await self.upload_content(request)
            results.append(result)
            
            # API 제한을 위한 대기
            await asyncio.sleep(1)
        
        logger.info(f"✅ 다중 업로드 완료: {len(results)}개")
        return results
    
    async def _upload_to_tistory(self, request: UploadRequest) -> Dict[str, Any]:
        """티스토리에 업로드"""
        # 실제 구현에서는 티스토리 API를 사용
        # 현재는 시뮬레이션으로 처리
        
        logger.info(f"📝 티스토리 업로드 시뮬레이션: {request.title}")
        
        # 업로드 성공 시뮬레이션
        await asyncio.sleep(0.5)
        
        return {
            'success': True,
            'platform': 'tistory',
            'title': request.title,
            'url': f"https://example.tistory.com/entry/{int(time.time())}",
            'post_id': f"post_{int(time.time())}",
            'category': request.category,
            'tags': request.tags,
            'publish_status': request.publish_status
        }
    
    def _update_stats(self, success: bool, processing_time: float):
        """통계 업데이트"""
        self.stats['total_uploads'] += 1
        self.stats['processing_time'] += processing_time
        self.stats['last_upload'] = datetime.now().isoformat()
        
        if success:
            self.stats['successful_uploads'] += 1
        else:
            self.stats['failed_uploads'] += 1
    
    def save_results(self, results: List[Dict[str, Any]], 
                    file_path: str = "data/upload_results.json"):
        """업로드 결과 저장"""
        try:
            file_manager.ensure_directory_exists(file_path)
            
            # 기존 결과 로드
            existing_results = []
            if Path(file_path).exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_results = json.load(f)
            
            # 새 결과 추가
            existing_results.extend(results)
            
            # 파일 저장
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 업로드 결과 저장 완료: {file_path}")
            
        except Exception as e:
            logger.error(f"❌ 업로드 결과 저장 실패: {e}")
    
    async def cleanup(self):
        """정리 작업"""
        logger.info("🧹 업로드 관리자 정리 작업 완료")
    
    def get_statistics(self) -> Dict[str, Any]:
        """통계 정보 반환"""
        return {
            'stats': self.stats,
            'success_rate': (self.stats['successful_uploads'] / self.stats['total_uploads'] * 100) 
                           if self.stats['total_uploads'] > 0 else 0,
            'average_processing_time': (self.stats['processing_time'] / self.stats['total_uploads'])
                                      if self.stats['total_uploads'] > 0 else 0
        } 