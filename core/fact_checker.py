"""
🤖 고도화된 AI 팩트 체커
다중 AI 모델 지원, 신뢰도 점수, 근거 추출, 자동 검증
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
from auto_finance.config.settings import AI_CONFIG, FACT_CHECK_CONFIG

logger = setup_logger(__name__)

@dataclass
class FactCheckResult:
    """팩트 체크 결과"""
    article_id: str
    title: str
    content: str
    fact_check_score: float
    confidence: float
    verification_status: str  # verified, disputed, uncertain
    evidence: List[str]
    reasoning: str
    ai_model: str
    checked_at: str
    processing_time: float

class FactChecker:
    """고도화된 AI 팩트 체커"""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.ai_client = None
        self.model_name = AI_CONFIG.get('model_name', 'gemini-2.0-flash-exp')
        self.api_key = AI_CONFIG.get('api_key')
        
        # 팩트 체크 통계
        self.stats = {
            'total_checks': 0,
            'successful_checks': 0,
            'failed_checks': 0,
            'average_score': 0.0,
            'processing_time': 0.0
        }
        
        # 신뢰도 임계값
        self.confidence_threshold = FACT_CHECK_CONFIG.get('confidence_threshold', 0.7)
        self.score_threshold = FACT_CHECK_CONFIG.get('score_threshold', 0.6)
        
        logger.info(f"🤖 AI 팩트 체커 초기화: {self.model_name}")
    
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
            
            logger.info("🧹 AI 팩트 체커 정리 완료")
            
        except Exception as e:
            logger.error(f"❌ AI 팩트 체커 정리 실패: {e}")
    
    @retry_on_error(max_retries=3, delay=2.0)
    async def check_fact(self, article: Dict[str, Any]) -> Optional[FactCheckResult]:
        """단일 기사 팩트 체크"""
        if not self.ai_client:
            logger.warning("⚠️ AI 클라이언트가 초기화되지 않았습니다")
            return None
        
        start_time = datetime.now()
        article_id = article.get('id', f"article_{hash(article['title'])}")
        
        try:
            # 캐시 확인
            cache_key = f"factcheck_{article_id}"
            cached_result = cache_manager.get(cache_key)
            
            if cached_result:
                logger.info(f"💾 캐시된 팩트 체크 결과 사용: {article_id}")
                return FactCheckResult(**cached_result)
            
            # 팩트 체크 프롬프트 생성
            prompt = self._create_fact_check_prompt(article)
            
            # AI 호출
            response = await self._call_ai_api(prompt)
            
            # 응답 파싱
            result = self._parse_fact_check_response(response, article_id, article)
            
            if result:
                # 처리 시간 계산
                processing_time = (datetime.now() - start_time).total_seconds()
                result.processing_time = processing_time
                
                # 캐시 저장
                cache_manager.set(cache_key, result.__dict__, ttl=3600)  # 1시간
                
                # 통계 업데이트
                self._update_statistics(result)
                
                logger.info(f"✅ 팩트 체크 완료: {article_id} (점수: {result.fact_check_score:.2f})")
            
            return result
            
        except Exception as e:
            self.stats['failed_checks'] += 1
            self.error_handler.handle_error(e, f"팩트 체크 실패 ({article_id})")
            logger.error(f"❌ 팩트 체크 실패 ({article_id}): {e}")
            return None
    
    def _create_fact_check_prompt(self, article: Dict[str, Any]) -> str:
        """팩트 체크 프롬프트 생성"""
        title = article.get('title', '')
        content = article.get('content', '')
        
        prompt = f"""
다음 뉴스 기사의 사실 여부를 검증해주세요.

제목: {title}
내용: {content}

다음 형식으로 JSON 응답을 제공해주세요:

{{
    "fact_check_score": 0.0-1.0,  // 사실 여부 점수 (1.0이 가장 사실에 가까움)
    "confidence": 0.0-1.0,        // 검증 신뢰도 (1.0이 가장 확실함)
    "verification_status": "verified|disputed|uncertain",  // 검증 상태
    "evidence": [                 // 근거 목록
        "근거 1",
        "근거 2"
    ],
    "reasoning": "검증 과정에 대한 상세한 설명"
}}

주의사항:
1. 객관적이고 중립적인 관점에서 검증하세요
2. 구체적인 근거를 제시하세요
3. 불확실한 경우 신뢰도를 낮게 설정하세요
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
    
    def _parse_fact_check_response(self, response: str, article_id: str, 
                                  article: Dict[str, Any]) -> Optional[FactCheckResult]:
        """AI 응답 파싱"""
        try:
            # JSON 추출
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                logger.error(f"❌ JSON 응답을 찾을 수 없습니다: {response}")
                return None
            
            json_str = json_match.group()
            data = json.loads(json_str)
            
            # 결과 객체 생성
            result = FactCheckResult(
                article_id=article_id,
                title=article.get('title', ''),
                content=article.get('content', ''),
                fact_check_score=float(data.get('fact_check_score', 0.0)),
                confidence=float(data.get('confidence', 0.0)),
                verification_status=data.get('verification_status', 'uncertain'),
                evidence=data.get('evidence', []),
                reasoning=data.get('reasoning', ''),
                ai_model=self.model_name,
                checked_at=datetime.now().isoformat(),
                processing_time=0.0
            )
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON 파싱 실패: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ 응답 파싱 실패: {e}")
            return None
    
    def _update_statistics(self, result: FactCheckResult):
        """통계 업데이트"""
        self.stats['total_checks'] += 1
        self.stats['successful_checks'] += 1
        
        # 평균 점수 계산
        current_avg = self.stats['average_score']
        total_checks = self.stats['total_checks']
        self.stats['average_score'] = (current_avg * (total_checks - 1) + result.fact_check_score) / total_checks
    
    async def check_multiple_articles(self, articles: List[Dict[str, Any]], 
                                    max_concurrent: int = 5) -> List[FactCheckResult]:
        """다중 기사 팩트 체크"""
        if not articles:
            return []
        
        logger.info(f"🔍 다중 기사 팩트 체크 시작: {len(articles)}개 기사")
        
        # 세마포어로 동시 실행 제한
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def check_with_semaphore(article):
            async with semaphore:
                return await self.check_fact(article)
        
        # 병렬 실행
        tasks = [check_with_semaphore(article) for article in articles]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 필터링
        valid_results = []
        for result in results:
            if isinstance(result, FactCheckResult):
                valid_results.append(result)
            elif isinstance(result, Exception):
                logger.error(f"❌ 팩트 체크 작업 실패: {result}")
        
        # 신뢰도 순으로 정렬
        valid_results.sort(key=lambda x: x.confidence, reverse=True)
        
        logger.info(f"✅ 다중 팩트 체크 완료: {len(valid_results)}개 성공")
        return valid_results
    
    def filter_high_confidence_results(self, results: List[FactCheckResult]) -> List[FactCheckResult]:
        """높은 신뢰도 결과 필터링"""
        return [r for r in results if r.confidence >= self.confidence_threshold]
    
    def filter_verified_results(self, results: List[FactCheckResult]) -> List[FactCheckResult]:
        """검증된 결과 필터링"""
        return [r for r in results if r.verification_status == 'verified']
    
    def get_verification_summary(self, results: List[FactCheckResult]) -> Dict[str, Any]:
        """검증 결과 요약"""
        if not results:
            return {}
        
        summary = {
            'total_articles': len(results),
            'verified_count': len([r for r in results if r.verification_status == 'verified']),
            'disputed_count': len([r for r in results if r.verification_status == 'disputed']),
            'uncertain_count': len([r for r in results if r.verification_status == 'uncertain']),
            'average_score': sum(r.fact_check_score for r in results) / len(results),
            'average_confidence': sum(r.confidence for r in results) / len(results),
            'high_confidence_count': len([r for r in results if r.confidence >= self.confidence_threshold]),
            'timestamp': datetime.now().isoformat()
        }
        
        return summary
    
    def save_results(self, results: List[FactCheckResult], file_path: str = "data/fact_check_results.json"):
        """결과 저장"""
        try:
            # FactCheckResult 객체를 딕셔너리로 변환
            data = [result.__dict__ for result in results]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"💾 팩트 체크 결과 저장: {file_path}")
            
        except Exception as e:
            logger.error(f"❌ 결과 저장 실패: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """팩트 체크 통계 반환"""
        return {
            **self.stats,
            'error_statistics': self.error_handler.get_statistics(),
            'model_name': self.model_name,
            'confidence_threshold': self.confidence_threshold,
            'score_threshold': self.score_threshold,
            'timestamp': datetime.now().isoformat()
        }

# 사용 예시
async def main():
    """팩트 체커 테스트"""
    test_articles = [
        {
            'id': 'test_1',
            'title': '삼성전자 1분기 실적 예상치 상회',
            'content': '삼성전자가 1분기 실적에서 시장 예상치를 상회했다는 소식이 전해졌습니다.'
        },
        {
            'id': 'test_2', 
            'title': '코로나19 백신 개발 완료',
            'content': '새로운 코로나19 백신이 개발되어 임상시험을 완료했다고 발표했습니다.'
        }
    ]
    
    async with FactChecker() as fact_checker:
        results = await fact_checker.check_multiple_articles(test_articles)
        
        print(f"🔍 팩트 체크 결과: {len(results)}개 기사")
        for result in results:
            print(f"- {result.title}")
            print(f"  점수: {result.fact_check_score:.2f}, 신뢰도: {result.confidence:.2f}")
            print(f"  상태: {result.verification_status}")
            print()
        
        summary = fact_checker.get_verification_summary(results)
        print(f"📊 요약: {summary}")

if __name__ == "__main__":
    asyncio.run(main()) 