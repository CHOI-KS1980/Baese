"""
✍️ 고도화된 AI 콘텐츠 생성기
다중 AI 모델, SEO 최적화, 다양한 형식, 품질 검증
"""

import asyncio
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from auto_finance.utils.logger import setup_logger
from auto_finance.utils.error_handler import retry_on_error, ErrorHandler
from auto_finance.utils.cache_manager import cache_manager
from auto_finance.config.settings import AI_CONFIG, CONTENT_CONFIG

logger = setup_logger(__name__)

@dataclass
class ContentRequest:
    """콘텐츠 생성 요청"""
    title: str
    content: str
    keywords: List[str]
    content_type: str  # article, summary, analysis, report
    target_length: int
    tone: str  # professional, casual, technical
    seo_optimized: bool = True

@dataclass
class GeneratedContent:
    """생성된 콘텐츠"""
    title: str
    content: str
    summary: str
    keywords: List[str]
    seo_score: float
    readability_score: float
    word_count: int
    content_type: str
    ai_model: str
    generated_at: str
    processing_time: float

class ContentGenerator:
    """고도화된 AI 콘텐츠 생성기"""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.ai_client = None
        self.model_name = AI_CONFIG.get('model_name', 'gemini-2.0-flash-exp')
        self.api_key = AI_CONFIG.get('api_key')
        
        # 콘텐츠 생성 통계
        self.stats = {
            'total_generations': 0,
            'successful_generations': 0,
            'failed_generations': 0,
            'average_processing_time': 0.0,
            'total_words_generated': 0
        }
        
        # SEO 키워드 가중치
        self.seo_keywords = CONTENT_CONFIG.get('seo_keywords', [])
        self.content_templates = CONTENT_CONFIG.get('templates', {})
        
        logger.info(f"✍️ AI 콘텐츠 생성기 초기화: {self.model_name}")
    
    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        await self.cleanup()
    
    async def initialize(self):
        """AI 클라이언트 초기화"""
        try:
            if not self.api_key:
                logger.warning("⚠️ AI API 키가 설정되지 않았습니다")
                return
            
            # Google Gemini API 클라이언트 설정
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            
            # 모델 설정
            self.ai_client = genai.GenerativeModel(self.model_name)
            
            logger.info(f"✅ AI 클라이언트 초기화 완료: {self.model_name}")
            
        except Exception as e:
            logger.error(f"❌ AI 클라이언트 초기화 실패: {e}")
            raise
    
    async def cleanup(self):
        """리소스 정리"""
        try:
            if self.ai_client:
                del self.ai_client
            
            logger.info("🧹 AI 콘텐츠 생성기 정리 완료")
            
        except Exception as e:
            logger.error(f"❌ AI 콘텐츠 생성기 정리 실패: {e}")
    
    @retry_on_error(max_retries=3, delay=2.0)
    async def generate_content(self, request: ContentRequest) -> Optional[GeneratedContent]:
        """콘텐츠 생성"""
        if not self.ai_client:
            logger.warning("⚠️ AI 클라이언트가 초기화되지 않았습니다")
            return None
        
        start_time = datetime.now()
        
        try:
            # 캐시 확인
            cache_key = f"content_{hash(request.title)}_{request.content_type}_{request.target_length}"
            cached_data = cache_manager.get(cache_key)
            
            if cached_data:
                logger.info(f"💾 캐시된 콘텐츠 사용: {request.title}")
                return GeneratedContent(**cached_data)
            
            # 프롬프트 생성
            prompt = self._create_content_prompt(request)
            
            # AI 호출
            response = await self._call_ai_api(prompt)
            
            # 응답 파싱
            content = self._parse_content_response(response, request)
            
            if content:
                # 품질 검증
                content = await self._validate_and_improve_content(content, request)
                
                # 처리 시간 계산
                processing_time = (datetime.now() - start_time).total_seconds()
                content.processing_time = processing_time
                
                # 캐시 저장
                cache_manager.set(cache_key, content.__dict__, ttl=7200)  # 2시간
                
                # 통계 업데이트
                self._update_statistics(content)
                
                logger.info(f"✅ 콘텐츠 생성 완료: {request.title} ({content.word_count}단어)")
            
            return content
            
        except Exception as e:
            self.stats['failed_generations'] += 1
            self.error_handler.handle_error(e, f"콘텐츠 생성 실패 ({request.title})")
            logger.error(f"❌ 콘텐츠 생성 실패 ({request.title}): {e}")
            return None
    
    def _create_content_prompt(self, request: ContentRequest) -> str:
        """콘텐츠 생성 프롬프트 생성"""
        template = self.content_templates.get(request.content_type, "")
        
        prompt = f"""
다음 뉴스 기사를 바탕으로 {request.content_type} 형식의 콘텐츠를 생성해주세요.

제목: {request.title}
내용: {request.content}
키워드: {', '.join(request.keywords)}
목표 길이: {request.target_length}단어
톤: {request.tone}

{template}

다음 형식으로 JSON 응답을 제공해주세요:

{{
    "title": "SEO 최적화된 제목",
    "content": "생성된 콘텐츠 본문",
    "summary": "요약 (100자 이내)",
    "keywords": ["키워드1", "키워드2"],
    "seo_score": 0.0-1.0,
    "readability_score": 0.0-1.0
}}

주의사항:
1. SEO 최적화를 위해 키워드를 자연스럽게 포함하세요
2. 가독성을 높이기 위해 단락을 적절히 나누세요
3. 전문적이면서도 이해하기 쉽게 작성하세요
4. JSON 형식을 정확히 지켜주세요
"""
        
        return prompt
    
    async def _call_ai_api(self, prompt: str) -> str:
        """AI API 호출"""
        try:
            response = self.ai_client.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"❌ AI API 호출 실패: {e}")
            raise
    
    def _parse_content_response(self, response: str, request: ContentRequest) -> Optional[GeneratedContent]:
        """AI 응답 파싱"""
        try:
            # JSON 추출
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                logger.error(f"❌ JSON 응답을 찾을 수 없습니다: {response}")
                return None
            
            json_str = json_match.group()
            data = json.loads(json_str)
            
            # 콘텐츠 객체 생성
            content = GeneratedContent(
                title=data.get('title', request.title),
                content=data.get('content', ''),
                summary=data.get('summary', ''),
                keywords=data.get('keywords', request.keywords),
                seo_score=float(data.get('seo_score', 0.0)),
                readability_score=float(data.get('readability_score', 0.0)),
                word_count=len(data.get('content', '').split()),
                content_type=request.content_type,
                ai_model=self.model_name,
                generated_at=datetime.now().isoformat(),
                processing_time=0.0
            )
            
            return content
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON 파싱 실패: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ 응답 파싱 실패: {e}")
            return None
    
    async def _validate_and_improve_content(self, content: GeneratedContent, 
                                          request: ContentRequest) -> GeneratedContent:
        """콘텐츠 품질 검증 및 개선"""
        try:
            # SEO 점수 재계산
            content.seo_score = self._calculate_seo_score(content, request.keywords)
            
            # 가독성 점수 계산
            content.readability_score = self._calculate_readability_score(content.content)
            
            # 단어 수 재계산
            content.word_count = len(content.content.split())
            
            # 목표 길이와 차이가 크면 조정
            if abs(content.word_count - request.target_length) > request.target_length * 0.2:
                content = await self._adjust_content_length(content, request.target_length)
            
            return content
            
        except Exception as e:
            logger.error(f"❌ 콘텐츠 검증 실패: {e}")
            return content
    
    def _calculate_seo_score(self, content: GeneratedContent, target_keywords: List[str]) -> float:
        """SEO 점수 계산"""
        try:
            score = 0.0
            text = f"{content.title} {content.content}".lower()
            
            # 키워드 밀도 체크
            for keyword in target_keywords:
                keyword_lower = keyword.lower()
                count = text.count(keyword_lower)
                if count > 0:
                    score += min(count * 0.1, 0.3)  # 최대 0.3점
            
            # 제목 길이 체크
            title_length = len(content.title)
            if 30 <= title_length <= 60:
                score += 0.2
            
            # 콘텐츠 길이 체크
            if content.word_count >= 300:
                score += 0.2
            
            # 키워드 포함 여부
            if any(keyword.lower() in content.title.lower() for keyword in target_keywords):
                score += 0.3
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"❌ SEO 점수 계산 실패: {e}")
            return 0.0
    
    def _calculate_readability_score(self, content: str) -> float:
        """가독성 점수 계산"""
        try:
            sentences = re.split(r'[.!?]+', content)
            words = content.split()
            
            if not sentences or not words:
                return 0.0
            
            # 평균 문장 길이
            avg_sentence_length = len(words) / len(sentences)
            
            # 평균 단어 길이
            avg_word_length = sum(len(word) for word in words) / len(words)
            
            # 점수 계산 (간단한 Flesch Reading Ease 기반)
            score = 0.0
            
            if avg_sentence_length <= 20:
                score += 0.4
            elif avg_sentence_length <= 25:
                score += 0.3
            elif avg_sentence_length <= 30:
                score += 0.2
            
            if avg_word_length <= 5:
                score += 0.3
            elif avg_word_length <= 6:
                score += 0.2
            elif avg_word_length <= 7:
                score += 0.1
            
            # 단락 수 체크
            paragraphs = content.split('\n\n')
            if 3 <= len(paragraphs) <= 8:
                score += 0.3
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"❌ 가독성 점수 계산 실패: {e}")
            return 0.0
    
    async def _adjust_content_length(self, content: GeneratedContent, 
                                   target_length: int) -> GeneratedContent:
        """콘텐츠 길이 조정"""
        try:
            if content.word_count > target_length * 1.2:
                # 길이가 너무 길면 요약
                prompt = f"""
다음 콘텐츠를 {target_length}단어로 요약해주세요:

{content.content}

원래 제목과 키워드는 유지하면서 핵심 내용만 남겨주세요.
"""
                
                response = await self._call_ai_api(prompt)
                if response:
                    content.content = response.strip()
                    content.word_count = len(content.content.split())
            
            elif content.word_count < target_length * 0.8:
                # 길이가 너무 짧으면 확장
                prompt = f"""
다음 콘텐츠를 {target_length}단어로 확장해주세요:

{content.content}

키워드: {', '.join(content.keywords)}

자연스럽게 내용을 보강해주세요.
"""
                
                response = await self._call_ai_api(prompt)
                if response:
                    content.content = response.strip()
                    content.word_count = len(content.content.split())
            
            return content
            
        except Exception as e:
            logger.error(f"❌ 콘텐츠 길이 조정 실패: {e}")
            return content
    
    async def generate_multiple_contents(self, requests: List[ContentRequest], 
                                       max_concurrent: int = 3) -> List[GeneratedContent]:
        """다중 콘텐츠 생성"""
        if not requests:
            return []
        
        logger.info(f"✍️ 다중 콘텐츠 생성 시작: {len(requests)}개 요청")
        
        # 세마포어로 동시 실행 제한
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def generate_with_semaphore(request):
            async with semaphore:
                return await self.generate_content(request)
        
        # 병렬 실행
        tasks = [generate_with_semaphore(request) for request in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 필터링
        valid_results = []
        for result in results:
            if isinstance(result, GeneratedContent):
                valid_results.append(result)
            elif isinstance(result, Exception):
                logger.error(f"❌ 콘텐츠 생성 작업 실패: {result}")
        
        # 품질 순으로 정렬
        valid_results.sort(key=lambda x: x.seo_score + x.readability_score, reverse=True)
        
        logger.info(f"✅ 다중 콘텐츠 생성 완료: {len(valid_results)}개 성공")
        return valid_results
    
    def save_content(self, content: GeneratedContent, file_path: str = None) -> str:
        """콘텐츠 저장"""
        try:
            if not file_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_title = re.sub(r'[^\w\s-]', '', content.title)[:50]
                file_path = f"data/generated/{timestamp}_{safe_title}.md"
            
            # 마크다운 형식으로 저장
            markdown_content = f"""# {content.title}

**생성일시**: {content.generated_at}  
**AI 모델**: {content.ai_model}  
**콘텐츠 타입**: {content.content_type}  
**단어 수**: {content.word_count}  
**SEO 점수**: {content.seo_score:.2f}  
**가독성 점수**: {content.readability_score:.2f}  

**키워드**: {', '.join(content.keywords)}

---

## 요약

{content.summary}

---

## 본문

{content.content}

---

**처리 시간**: {content.processing_time:.2f}초
"""
            
            import os
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"💾 콘텐츠 저장: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"❌ 콘텐츠 저장 실패: {e}")
            return ""
    
    def _update_statistics(self, content: GeneratedContent):
        """통계 업데이트"""
        self.stats['total_generations'] += 1
        self.stats['successful_generations'] += 1
        self.stats['total_words_generated'] += content.word_count
        
        # 평균 처리 시간 계산
        current_avg = self.stats['average_processing_time']
        total_generations = self.stats['total_generations']
        self.stats['average_processing_time'] = (
            (current_avg * (total_generations - 1) + content.processing_time) / total_generations
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """생성 통계 반환"""
        return {
            **self.stats,
            'error_statistics': self.error_handler.get_statistics(),
            'model_name': self.model_name,
            'timestamp': datetime.now().isoformat()
        }

# 사용 예시
async def main():
    """콘텐츠 생성기 테스트"""
    test_requests = [
        ContentRequest(
            title="삼성전자 1분기 실적 예상치 상회",
            content="삼성전자가 1분기 실적에서 시장 예상치를 상회했다는 소식이 전해졌습니다.",
            keywords=["삼성전자", "실적", "1분기", "주식"],
            content_type="article",
            target_length=500,
            tone="professional"
        ),
        ContentRequest(
            title="AI 기술 발전으로 인한 주식시장 변화",
            content="인공지능 기술의 급속한 발전이 주식시장에 미치는 영향에 대해 분석합니다.",
            keywords=["AI", "주식시장", "기술", "투자"],
            content_type="analysis",
            target_length=800,
            tone="technical"
        )
    ]
    
    async with ContentGenerator() as generator:
        contents = await generator.generate_multiple_contents(test_requests)
        
        print(f"✍️ 콘텐츠 생성 결과: {len(contents)}개")
        for content in contents:
            print(f"- {content.title}")
            print(f"  단어 수: {content.word_count}, SEO: {content.seo_score:.2f}, 가독성: {content.readability_score:.2f}")
            print()
            
            # 파일로 저장
            file_path = generator.save_content(content)
            print(f"  저장됨: {file_path}")
        
        stats = generator.get_statistics()
        print(f"📊 통계: {stats}")

if __name__ == "__main__":
    asyncio.run(main()) 