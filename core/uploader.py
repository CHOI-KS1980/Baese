"""
📤 업로드 시스템
티스토리 블로그 자동 업로드 및 파일 저장
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from config.settings import settings

class Uploader:
    def __init__(self):
        self.tistory_token = os.getenv('TISTORY_ACCESS_TOKEN')
        self.blog_name = os.getenv('TISTORY_BLOG_NAME', 'your-blog-name')
        self.api_available = bool(self.tistory_token)
        
        if self.api_available:
            print(f"✅ 티스토리 API 활성화: {self.blog_name}")
        else:
            print("⚠️ 티스토리 API 키 미설정: 파일 저장 모드")
    
    async def upload_articles(self, contents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        기사들을 티스토리에 업로드하거나 파일로 저장
        """
        results = []
        
        for content in contents:
            try:
                if self.api_available:
                    # 티스토리 API 업로드
                    result = await self._upload_to_tistory(content)
                else:
                    # 파일 저장
                    result = await self._save_to_file(content)
                
                results.append(result)
                
            except Exception as e:
                print(f"❌ 업로드 실패: {e}")
                results.append({
                    "success": False,
                    "error": str(e),
                    "title": content.get('title', 'Unknown')
                })
        
        return results
    
    async def _upload_to_tistory(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """티스토리 API를 통한 업로드"""
        try:
            title = content.get('title', '')
            body = content.get('body', '')
            
            # 티스토리 API 요청
            url = f"https://www.tistory.com/apis/post/write"
            params = {
                'access_token': self.tistory_token,
                'blogName': self.blog_name,
                'title': title,
                'content': body,
                'visibility': '3',  # 발행
                'category': '주식뉴스',  # 카테고리
                'tag': '주식,뉴스,자동화'
            }
            
            response = requests.post(url, data=params)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('tistory', {}).get('status') == '200':
                return {
                    "success": True,
                    "platform": "tistory",
                    "post_id": result['tistory'].get('postId'),
                    "url": result['tistory'].get('url'),
                    "title": title
                }
            else:
                return {
                    "success": False,
                    "error": result.get('tistory', {}).get('error_msg', 'Unknown error'),
                    "title": title
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "title": content.get('title', 'Unknown')
            }
    
    async def _save_to_file(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """파일로 저장"""
        try:
            title = content.get('title', 'Untitled')
            body = content.get('body', '')
            
            # 파일명 생성 (특수문자 제거)
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_title}.md"
            
            # 저장 경로
            save_dir = Path("data/generated")
            save_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = save_dir / filename
            
            # 마크다운 파일 생성
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# {title}\n\n")
                f.write(f"**생성일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**원본 출처**: {content.get('source', 'Unknown')}\n\n")
                f.write(f"**원본 URL**: {content.get('url', 'N/A')}\n\n")
                f.write("---\n\n")
                f.write(body)
            
            return {
                "success": True,
                "platform": "file",
                "file_path": str(file_path),
                "title": title
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "title": content.get('title', 'Unknown')
            }
    
    def get_upload_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """업로드 통계 계산"""
        total = len(results)
        successful = sum(1 for r in results if r.get('success', False))
        failed = total - successful
        
        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total * 100) if total > 0 else 0
        } 