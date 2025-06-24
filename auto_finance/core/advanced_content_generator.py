"""
✍️ 고도화된 콘텐츠 생성 시스템
감정 분석 및 시장 데이터를 활용한 전문적인 콘텐츠 생성
"""

import asyncio
import json
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import re
from pathlib import Path

from auto_finance.core.ai_ensemble import ai_ensemble
from auto_finance.core.market_sentiment_analyzer import sentiment_analyzer
from auto_finance.utils.logger import setup_logger
from auto_finance.config.settings import CONTENT_CONFIG

logger = setup_logger(__name__)

@dataclass
class AdvancedContent:
    """고도화된 콘텐츠 데이터 클래스"""
    title: str
    content: str
    summary: str
    keywords: List[str]
    sentiment_score: float
    market_impact: str
    target_audience: str
    content_type: str
    word_count: int
    seo_score: float
    readability_score: float
    generated_at: datetime
    metadata: Dict[str, Any]

@dataclass
class ContentRequest:
    """콘텐츠 생성 요청"""
    articles: List[Dict[str, Any]]
    sentiment_data: Optional[Dict[str, Any]] = None
    market_data: Optional[Dict[str, Any]] = None
    target_audience: str = "general"
    content_type: str = "analysis"
    tone: str = "professional"
    length: str = "medium"
    include_charts: bool = False

class AdvancedContentGenerator:
    """고도화된 콘텐츠 생성 시스템"""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.seo_keywords = CONTENT_CONFIG.get('seo_keywords', [])
        self.tone_options = CONTENT_CONFIG.get('tone_options', [])
        
        self.stats = {
            'total_generations': 0,
            'successful_generations': 0,
            'failed_generations': 0,
            'average_processing_time': 0.0,
            'content_types': {},
            'audience_types': {}
        }
    
    def _load_templates(self) -> Dict[str, str]:
        """템플릿 로드"""
        return {
            'analysis': """
# {{title}}

## 📊 시장 현황
{{market_overview}}

## 🔍 핵심 분석
{{core_analysis}}

## 💡 투자자 관점
{{investment_insights}}

## ⚠️ 리스크 요인
{{risk_factors}}

## 📈 전망
{{outlook}}

**키워드**: {{keywords}}
**생성일시**: {{timestamp}}
**시장 감정**: {{sentiment}}
            """,
            
            'summary': """
## 📰 뉴스 요약

{{summary_content}}

## 🎯 핵심 포인트
{{key_points}}

## 📊 시장 영향도
{{market_impact}}

**생성일시**: {{timestamp}}
            """,
            
            'report': """
# {{title}}

## 📋 개요
{{overview}}

## 📊 데이터 분석
{{data_analysis}}

## 🔍 심층 분석
{{deep_analysis}}

## 💼 투자 전략
{{investment_strategy}}

## 📈 결론
{{conclusion}}

**키워드**: {{keywords}}
**생성일시**: {{timestamp}}
            """
        }
    
    async def generate_advanced_content(self, request: ContentRequest) -> List[AdvancedContent]:
        """고도화된 콘텐츠 생성"""
        logger.info(f"✍️ 고도화된 콘텐츠 생성 시작: {len(request.articles)}개 기사")
        
        start_time = time.time()
        results = []
        
        try:
            # 감정 분석 수행
            if not request.sentiment_data:
                news_sentiments = await sentiment_analyzer.analyze_news_sentiment(request.articles)
                market_sentiment = await sentiment_analyzer.analyze_market_sentiment(news_sentiments)
            else:
                market_sentiment = request.sentiment_data
            
            # 기사별 콘텐츠 생성
            for i, article in enumerate(request.articles):
                try:
                    content = await self._generate_single_content(
                        article, market_sentiment, request, i
                    )
                    results.append(content)
                    self.stats['successful_generations'] += 1
                    
                except Exception as e:
                    logger.error(f"❌ 콘텐츠 생성 실패: {e}")
                    self.stats['failed_generations'] += 1
                    continue
            
            # 통계 업데이트
            processing_time = time.time() - start_time
            self.stats['total_generations'] += len(request.articles)
            self.stats['average_processing_time'] = processing_time / len(request.articles) if request.articles else 0
            
            # 콘텐츠 타입별 통계
            content_type = request.content_type
            self.stats['content_types'][content_type] = self.stats['content_types'].get(content_type, 0) + len(results)
            
            # 대상 독자별 통계
            audience = request.target_audience
            self.stats['audience_types'][audience] = self.stats['audience_types'].get(audience, 0) + len(results)
            
            logger.info(f"✅ 고도화된 콘텐츠 생성 완료: {len(results)}개 성공, {processing_time:.2f}초")
            return results
            
        except Exception as e:
            logger.error(f"❌ 고도화된 콘텐츠 생성 실패: {e}")
            return []
    
    async def _generate_single_content(self, article: Dict[str, Any], 
                                     market_sentiment: Any, 
                                     request: ContentRequest, 
                                     index: int) -> AdvancedContent:
        """단일 콘텐츠 생성"""
        # 기사 정보 추출
        title = article.get('title', '')
        content = article.get('content', '')
        source = article.get('source', '')
        
        # 감정 분석
        article_sentiment = await sentiment_analyzer._analyze_single_article(article)
        
        # AI 앙상블을 사용한 콘텐츠 생성
        ai_prompt = self._create_ai_prompt(article, market_sentiment, request)
        ai_response = await ai_ensemble.generate_content_ensemble(ai_prompt, 'content_generation')
        
        # 콘텐츠 후처리
        processed_content = self._post_process_content(ai_response.final_content, request)
        
        # SEO 최적화
        seo_optimized_content = self._optimize_for_seo(processed_content, article)
        
        # 품질 점수 계산
        seo_score = self._calculate_seo_score(seo_optimized_content)
        readability_score = self._calculate_readability_score(seo_optimized_content)
        
        # 키워드 추출
        keywords = self._extract_keywords(seo_optimized_content, article)
        
        # 시장 영향도 분석
        market_impact = self._analyze_market_impact(article_sentiment, market_sentiment)
        
        return AdvancedContent(
            title=self._generate_title(title, article_sentiment),
            content=seo_optimized_content,
            summary=self._generate_summary(seo_optimized_content),
            keywords=keywords,
            sentiment_score=article_sentiment.overall_sentiment.compound,
            market_impact=market_impact,
            target_audience=request.target_audience,
            content_type=request.content_type,
            word_count=len(seo_optimized_content.split()),
            seo_score=seo_score,
            readability_score=readability_score,
            generated_at=datetime.now(),
            metadata={
                'source': source,
                'ai_confidence': ai_response.confidence_score,
                'processing_time': ai_response.processing_time,
                'model_contributions': ai_response.model_contributions
            }
        )
    
    def _create_ai_prompt(self, article: Dict[str, Any], market_sentiment: Any, request: ContentRequest) -> str:
        """AI 프롬프트 생성"""
        title = article.get('title', '')
        content = article.get('content', '')
        
        prompt = f"""
        다음 뉴스 기사를 바탕으로 전문적인 투자 분석 글을 작성해주세요:
        
        제목: {title}
        내용: {content}
        
        시장 감정: {market_sentiment.overall_sentiment:.3f} ({market_sentiment.sentiment_trend})
        
        요구사항:
        - 대상 독자: {request.target_audience}
        - 콘텐츠 타입: {request.content_type}
        - 톤: {request.tone}
        - 길이: {request.length} ({self._get_length_guide(request.length)})
        
        다음 구조로 작성해주세요:
        1. 시장 현황 분석
        2. 핵심 포인트 분석
        3. 투자자 관점에서의 인사이트
        4. 리스크 요인
        5. 향후 전망
        
        전문적이면서도 이해하기 쉬운 톤으로 작성하고, 구체적인 데이터와 근거를 제시해주세요.
        """
        
        return prompt
    
    def _get_length_guide(self, length: str) -> str:
        """길이 가이드"""
        guides = {
            'short': '500-800자',
            'medium': '800-1200자',
            'long': '1200-1800자'
        }
        return guides.get(length, '800-1200자')
    
    def _post_process_content(self, content: str, request: ContentRequest) -> str:
        """콘텐츠 후처리"""
        # 불필요한 공백 제거
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        # 제목 형식 통일
        content = re.sub(r'^#\s*', '# ', content, flags=re.MULTILINE)
        
        # 리스트 형식 통일
        content = re.sub(r'^\s*[-*]\s*', '- ', content, flags=re.MULTILINE)
        
        # 길이 조정
        target_length = self._get_target_length(request.length)
        current_length = len(content)
        
        if current_length > target_length * 1.2:
            # 너무 길면 요약
            sentences = content.split('.')
            content = '. '.join(sentences[:len(sentences)//2]) + '.'
        elif current_length < target_length * 0.8:
            # 너무 짧으면 확장
            content += "\n\n추가 분석이 필요합니다."
        
        return content.strip()
    
    def _get_target_length(self, length: str) -> int:
        """목표 길이"""
        lengths = {
            'short': 600,
            'medium': 1000,
            'long': 1500
        }
        return lengths.get(length, 1000)
    
    def _optimize_for_seo(self, content: str, article: Dict[str, Any]) -> str:
        """SEO 최적화"""
        # 키워드 밀도 최적화
        title_keywords = self._extract_keywords(article.get('title', ''), [])
        
        for keyword in title_keywords[:5]:  # 상위 5개 키워드만
            if keyword not in content:
                # 키워드가 없으면 적절한 위치에 추가
                content = self._insert_keyword_naturally(content, keyword)
        
        # 헤딩 태그 최적화
        content = self._optimize_headings(content)
        
        # 메타 설명 추가
        meta_description = self._generate_meta_description(content)
        content = f"<!-- Meta Description: {meta_description} -->\n\n{content}"
        
        return content
    
    def _insert_keyword_naturally(self, content: str, keyword: str) -> str:
        """자연스럽게 키워드 삽입"""
        sentences = content.split('.')
        
        # 적절한 문장에 키워드 삽입
        for i, sentence in enumerate(sentences):
            if len(sentence) > 50 and keyword not in sentence:
                # 문장 중간에 키워드 삽입
                words = sentence.split()
                if len(words) > 5:
                    insert_pos = len(words) // 2
                    words.insert(insert_pos, keyword)
                    sentences[i] = ' '.join(words)
                    break
        
        return '. '.join(sentences)
    
    def _optimize_headings(self, content: str) -> str:
        """헤딩 태그 최적화"""
        # H1 태그는 하나만
        h1_count = content.count('# ')
        if h1_count > 1:
            content = re.sub(r'^# ', '## ', content, flags=re.MULTILINE)
        
        # H2, H3 태그 적절히 배치
        lines = content.split('\n')
        optimized_lines = []
        
        for line in lines:
            if line.startswith('## '):
                # H2 태그는 주요 섹션에만
                if any(keyword in line.lower() for keyword in ['분석', '전망', '전략', '리스크']):
                    optimized_lines.append(line)
                else:
                    optimized_lines.append(line.replace('## ', '### '))
            else:
                optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def _generate_meta_description(self, content: str) -> str:
        """메타 설명 생성"""
        # 첫 번째 문단에서 추출
        paragraphs = content.split('\n\n')
        if paragraphs:
            first_para = paragraphs[0]
            # HTML 태그 제거
            clean_para = re.sub(r'<[^>]+>', '', first_para)
            # 150자로 제한
            if len(clean_para) > 150:
                clean_para = clean_para[:147] + '...'
            return clean_para
        return "주식 투자 분석 및 시장 전망"
    
    def _calculate_seo_score(self, content: str) -> float:
        """SEO 점수 계산"""
        score = 0.0
        
        # 키워드 밀도
        keyword_density = self._calculate_keyword_density(content)
        score += min(keyword_density * 10, 30)
        
        # 헤딩 구조
        heading_score = self._calculate_heading_score(content)
        score += heading_score
        
        # 콘텐츠 길이
        length_score = min(len(content) / 100, 20)
        score += length_score
        
        # 가독성
        readability = self._calculate_readability_score(content)
        score += readability * 20
        
        return min(score, 100.0)
    
    def _calculate_keyword_density(self, content: str) -> float:
        """키워드 밀도 계산"""
        total_words = len(content.split())
        if total_words == 0:
            return 0.0
        
        keyword_count = 0
        for keyword in self.seo_keywords:
            keyword_count += content.lower().count(keyword.lower())
        
        return keyword_count / total_words
    
    def _calculate_heading_score(self, content: str) -> float:
        """헤딩 점수 계산"""
        score = 0.0
        
        # H1 태그 (하나만)
        h1_count = content.count('# ')
        if h1_count == 1:
            score += 10
        elif h1_count > 1:
            score -= 5
        
        # H2 태그 (3-5개 권장)
        h2_count = content.count('## ')
        if 3 <= h2_count <= 5:
            score += 15
        elif h2_count > 0:
            score += 10
        
        # H3 태그
        h3_count = content.count('### ')
        if h3_count > 0:
            score += 5
        
        return score
    
    def _calculate_readability_score(self, content: str) -> float:
        """가독성 점수 계산"""
        sentences = content.split('.')
        words = content.split()
        
        if not sentences or not words:
            return 0.0
        
        # 평균 문장 길이
        avg_sentence_length = len(words) / len(sentences)
        
        # 가독성 점수 (문장이 짧을수록 높은 점수)
        if avg_sentence_length <= 15:
            score = 1.0
        elif avg_sentence_length <= 20:
            score = 0.8
        elif avg_sentence_length <= 25:
            score = 0.6
        else:
            score = 0.4
        
        return score
    
    def _extract_keywords(self, content: str, article: Dict[str, Any]) -> List[str]:
        """키워드 추출"""
        keywords = []
        
        # 기사 제목에서 키워드 추출
        title = article.get('title', '')
        title_keywords = self._extract_keywords_from_text(title)
        keywords.extend(title_keywords)
        
        # 콘텐츠에서 키워드 추출
        content_keywords = self._extract_keywords_from_text(content)
        keywords.extend(content_keywords)
        
        # SEO 키워드와 매칭
        matched_keywords = [kw for kw in self.seo_keywords if kw in content.lower()]
        keywords.extend(matched_keywords)
        
        # 중복 제거 및 상위 10개 선택
        unique_keywords = list(set(keywords))
        return unique_keywords[:10]
    
    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """텍스트에서 키워드 추출"""
        # 간단한 키워드 추출 (실제로는 더 정교한 NLP 사용)
        keywords = []
        
        # 금융 관련 키워드
        financial_keywords = [
            '주식', '투자', '경제', '금융', '시장', '분석', '전망', '전략',
            '포트폴리오', '리스크', '수익률', '성장', '가치', '배당',
            '상승', '하락', '급등', '급락', '호재', '악재'
        ]
        
        for keyword in financial_keywords:
            if keyword in text:
                keywords.append(keyword)
        
        return keywords
    
    def _analyze_market_impact(self, article_sentiment: Any, market_sentiment: Any) -> str:
        """시장 영향도 분석"""
        article_compound = article_sentiment.overall_sentiment.compound
        market_compound = market_sentiment.overall_sentiment
        
        if article_compound > 0.3 and market_compound > 0.1:
            return "강한 긍정적 영향"
        elif article_compound > 0.1 and market_compound > -0.1:
            return "긍정적 영향"
        elif article_compound < -0.3 and market_compound < -0.1:
            return "강한 부정적 영향"
        elif article_compound < -0.1 and market_compound < 0.1:
            return "부정적 영향"
        else:
            return "중립적 영향"
    
    def _generate_title(self, original_title: str, sentiment: Any) -> str:
        """제목 생성"""
        # 감정에 따른 제목 수정
        compound = sentiment.overall_sentiment.compound
        
        if compound > 0.2:
            prefix = "📈 긍정적 전망: "
        elif compound < -0.2:
            prefix = "📉 주의 필요: "
        else:
            prefix = "📊 시장 분석: "
        
        return prefix + original_title
    
    def _generate_summary(self, content: str) -> str:
        """요약 생성"""
        # 첫 번째 문단을 요약으로 사용
        paragraphs = content.split('\n\n')
        if paragraphs:
            summary = paragraphs[0]
            # HTML 태그 제거
            summary = re.sub(r'<[^>]+>', '', summary)
            # 200자로 제한
            if len(summary) > 200:
                summary = summary[:197] + '...'
            return summary
        return "상세한 시장 분석 내용을 확인하세요."
    
    def get_statistics(self) -> Dict[str, Any]:
        """시스템 통계 반환"""
        return {
            'total_generations': self.stats['total_generations'],
            'successful_generations': self.stats['successful_generations'],
            'failed_generations': self.stats['failed_generations'],
            'success_rate': (self.stats['successful_generations'] / self.stats['total_generations'] * 100) if self.stats['total_generations'] > 0 else 0,
            'average_processing_time': self.stats['average_processing_time'],
            'content_types': self.stats['content_types'],
            'audience_types': self.stats['audience_types']
        }
    
    def save_statistics(self, file_path: str = "data/content_generation_stats.json"):
        """통계 저장"""
        try:
            stats = self.get_statistics()
            stats['timestamp'] = datetime.now().isoformat()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"💾 콘텐츠 생성 통계 저장: {file_path}")
            
        except Exception as e:
            logger.error(f"❌ 콘텐츠 생성 통계 저장 실패: {e}")

# 전역 인스턴스
advanced_content_generator = AdvancedContentGenerator() 