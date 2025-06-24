"""
🤖 AI 앙상블 시스템
다중 AI 모델을 활용한 고도화된 콘텐츠 생성 및 팩트 체크
"""

import asyncio
import json
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import google.generativeai as genai
import openai
from anthropic import Anthropic

from auto_finance.utils.logger import setup_logger
from auto_finance.config.settings import AI_CONFIG

logger = setup_logger(__name__)

@dataclass
class AIResponse:
    """AI 응답 데이터 클래스"""
    model_name: str
    content: str
    confidence: float
    processing_time: float
    tokens_used: int
    cost: float
    metadata: Dict[str, Any]

@dataclass
class EnsembleResult:
    """앙상블 결과 데이터 클래스"""
    final_content: str
    confidence_score: float
    model_contributions: Dict[str, float]
    processing_time: float
    total_cost: float
    individual_responses: List[AIResponse]

class AIEnsembleSystem:
    """다중 AI 모델 앙상블 시스템"""
    
    def __init__(self):
        self.models = {
            'gemini': self._init_gemini(),
            'gpt4': self._init_openai(),
            'claude': self._init_anthropic()
        }
        
        # 모델 가중치 (성능 기반)
        self.model_weights = {
            'gemini': 0.4,    # 빠르고 안정적
            'gpt4': 0.35,     # 고품질
            'claude': 0.25    # 분석적
        }
        
        # 모델별 특화 기능
        self.model_specialties = {
            'gemini': ['fact_checking', 'summarization'],
            'gpt4': ['creative_writing', 'analysis'],
            'claude': ['detailed_analysis', 'reasoning']
        }
        
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_processing_time': 0.0,
            'total_cost': 0.0,
            'model_performance': {}
        }
    
    def _init_gemini(self):
        """Gemini 모델 초기화"""
        try:
            if AI_CONFIG.get('api_key'):
                genai.configure(api_key=AI_CONFIG['api_key'])
                return genai.GenerativeModel(AI_CONFIG.get('model_name', 'gemini-2.0-flash-exp'))
            return None
        except Exception as e:
            logger.warning(f"Gemini 초기화 실패: {e}")
            return None
    
    def _init_openai(self):
        """OpenAI 모델 초기화"""
        try:
            api_key = AI_CONFIG.get('openai_api_key')
            if api_key:
                return openai.OpenAI(api_key=api_key)
            return None
        except Exception as e:
            logger.warning(f"OpenAI 초기화 실패: {e}")
            return None
    
    def _init_anthropic(self):
        """Anthropic 모델 초기화"""
        try:
            api_key = AI_CONFIG.get('anthropic_api_key')
            if api_key:
                return Anthropic(api_key=api_key)
            return None
        except Exception as e:
            logger.warning(f"Anthropic 초기화 실패: {e}")
            return None
    
    async def generate_content_ensemble(self, prompt: str, task_type: str = 'content_generation') -> EnsembleResult:
        """앙상블 기반 콘텐츠 생성"""
        start_time = time.time()
        self.stats['total_requests'] += 1
        
        logger.info(f"🎯 앙상블 콘텐츠 생성 시작: {task_type}")
        
        try:
            # 각 모델별 응답 수집
            responses = []
            tasks = []
            
            for model_name, model in self.models.items():
                if model is not None:
                    task = self._generate_with_model(model_name, model, prompt, task_type)
                    tasks.append(task)
            
            # 병렬 실행
            if tasks:
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                responses = [r for r in responses if isinstance(r, AIResponse)]
            
            if not responses:
                raise Exception("모든 AI 모델이 실패했습니다")
            
            # 앙상블 결과 생성
            ensemble_result = self._create_ensemble_result(responses, task_type)
            
            # 통계 업데이트
            processing_time = time.time() - start_time
            self.stats['successful_requests'] += 1
            self.stats['total_processing_time'] += processing_time
            self.stats['total_cost'] += ensemble_result.total_cost
            
            logger.info(f"✅ 앙상블 생성 완료: {processing_time:.2f}초, 비용: ${ensemble_result.total_cost:.4f}")
            return ensemble_result
            
        except Exception as e:
            self.stats['failed_requests'] += 1
            logger.error(f"❌ 앙상블 생성 실패: {e}")
            raise
    
    async def _generate_with_model(self, model_name: str, model, prompt: str, task_type: str) -> AIResponse:
        """개별 모델로 콘텐츠 생성"""
        start_time = time.time()
        
        try:
            if model_name == 'gemini':
                return await self._generate_with_gemini(model, prompt, task_type)
            elif model_name == 'gpt4':
                return await self._generate_with_openai(model, prompt, task_type)
            elif model_name == 'claude':
                return await self._generate_with_anthropic(model, prompt, task_type)
            else:
                raise ValueError(f"지원하지 않는 모델: {model_name}")
                
        except Exception as e:
            logger.error(f"❌ {model_name} 모델 생성 실패: {e}")
            raise
    
    async def _generate_with_gemini(self, model, prompt: str, task_type: str) -> AIResponse:
        """Gemini 모델로 생성"""
        try:
            # 태스크별 프롬프트 최적화
            optimized_prompt = self._optimize_prompt_for_gemini(prompt, task_type)
            
            response = await asyncio.to_thread(
                model.generate_content,
                optimized_prompt,
                generation_config={
                    'temperature': AI_CONFIG.get('temperature', 0.7),
                    'max_output_tokens': AI_CONFIG.get('max_tokens', 1000)
                }
            )
            
            processing_time = time.time()
            content = response.text
            
            return AIResponse(
                model_name='gemini',
                content=content,
                confidence=self._calculate_confidence(content, task_type),
                processing_time=processing_time,
                tokens_used=len(content.split()),
                cost=0.0,  # Gemini는 현재 무료
                metadata={'task_type': task_type}
            )
            
        except Exception as e:
            logger.error(f"❌ Gemini 생성 실패: {e}")
            raise
    
    async def _generate_with_openai(self, model, prompt: str, task_type: str) -> AIResponse:
        """OpenAI 모델로 생성"""
        try:
            # 태스크별 프롬프트 최적화
            optimized_prompt = self._optimize_prompt_for_openai(prompt, task_type)
            
            response = await asyncio.to_thread(
                model.chat.completions.create,
                model="gpt-4",
                messages=[{"role": "user", "content": optimized_prompt}],
                max_tokens=AI_CONFIG.get('max_tokens', 1000),
                temperature=AI_CONFIG.get('temperature', 0.7)
            )
            
            processing_time = time.time()
            content = response.choices[0].message.content
            
            return AIResponse(
                model_name='gpt4',
                content=content,
                confidence=self._calculate_confidence(content, task_type),
                processing_time=processing_time,
                tokens_used=response.usage.total_tokens,
                cost=self._calculate_openai_cost(response.usage),
                metadata={'task_type': task_type}
            )
            
        except Exception as e:
            logger.error(f"❌ OpenAI 생성 실패: {e}")
            raise
    
    async def _generate_with_anthropic(self, model, prompt: str, task_type: str) -> AIResponse:
        """Anthropic 모델로 생성"""
        try:
            # 태스크별 프롬프트 최적화
            optimized_prompt = self._optimize_prompt_for_anthropic(prompt, task_type)
            
            response = await asyncio.to_thread(
                model.messages.create,
                model="claude-3-sonnet-20240229",
                max_tokens=AI_CONFIG.get('max_tokens', 1000),
                temperature=AI_CONFIG.get('temperature', 0.7),
                messages=[{"role": "user", "content": optimized_prompt}]
            )
            
            processing_time = time.time()
            content = response.content[0].text
            
            return AIResponse(
                model_name='claude',
                content=content,
                confidence=self._calculate_confidence(content, task_type),
                processing_time=processing_time,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                cost=self._calculate_anthropic_cost(response.usage),
                metadata={'task_type': task_type}
            )
            
        except Exception as e:
            logger.error(f"❌ Anthropic 생성 실패: {e}")
            raise
    
    def _optimize_prompt_for_gemini(self, prompt: str, task_type: str) -> str:
        """Gemini용 프롬프트 최적화"""
        if task_type == 'fact_checking':
            return f"""
            다음 뉴스 기사의 사실 여부를 검증해주세요:
            
            {prompt}
            
            다음 형식으로 답변해주세요:
            - 사실 여부: [확인됨/확인 불가/오류]
            - 신뢰도 점수: 0-100
            - 근거: 구체적인 근거
            - 결론: 요약
            """
        elif task_type == 'content_generation':
            return f"""
            다음 뉴스 기사를 바탕으로 전문적인 투자 분석 글을 작성해주세요:
            
            {prompt}
            
            다음 요구사항을 만족해주세요:
            - 전문적이면서도 이해하기 쉬운 톤
            - 구체적인 데이터와 근거 제시
            - 투자자 관점에서의 인사이트 제공
            - 800-1200자 내외
            """
        else:
            return prompt
    
    def _optimize_prompt_for_openai(self, prompt: str, task_type: str) -> str:
        """OpenAI용 프롬프트 최적화"""
        if task_type == 'fact_checking':
            return f"""
            You are a professional fact-checker. Please verify the following news article:
            
            {prompt}
            
            Please respond in the following format:
            - Fact Status: [Verified/Unverified/False]
            - Confidence Score: 0-100
            - Evidence: Specific evidence
            - Conclusion: Summary
            """
        elif task_type == 'content_generation':
            return f"""
            You are a professional financial analyst. Please create an investment analysis article based on the following news:
            
            {prompt}
            
            Requirements:
            - Professional yet accessible tone
            - Specific data and evidence
            - Investment insights from investor perspective
            - 800-1200 words
            """
        else:
            return prompt
    
    def _optimize_prompt_for_anthropic(self, prompt: str, task_type: str) -> str:
        """Anthropic용 프롬프트 최적화"""
        if task_type == 'fact_checking':
            return f"""
            <fact_checking_task>
            Please verify the factual accuracy of the following news article:
            
            {prompt}
            
            Provide your analysis in this format:
            - Fact Status: [Verified/Unverified/False]
            - Confidence Score: 0-100
            - Evidence: Specific evidence
            - Conclusion: Summary
            </fact_checking_task>
            """
        elif task_type == 'content_generation':
            return f"""
            <content_generation_task>
            Create a professional investment analysis article based on this news:
            
            {prompt}
            
            Requirements:
            - Professional yet accessible tone
            - Specific data and evidence
            - Investment insights from investor perspective
            - 800-1200 words
            </content_generation_task>
            """
        else:
            return prompt
    
    def _calculate_confidence(self, content: str, task_type: str) -> float:
        """콘텐츠 신뢰도 계산"""
        # 기본 신뢰도
        base_confidence = 0.7
        
        # 콘텐츠 길이 기반 조정
        if len(content) > 100:
            base_confidence += 0.1
        
        # 특정 키워드 기반 조정
        confidence_keywords = ['확인됨', 'verified', '근거', 'evidence', '데이터', 'data']
        if any(keyword in content.lower() for keyword in confidence_keywords):
            base_confidence += 0.1
        
        # 태스크별 조정
        if task_type == 'fact_checking':
            if '확인됨' in content or 'verified' in content.lower():
                base_confidence += 0.2
        
        return min(base_confidence, 1.0)
    
    def _calculate_openai_cost(self, usage) -> float:
        """OpenAI 비용 계산"""
        # GPT-4 가격 (2024년 기준)
        input_cost_per_1k = 0.03
        output_cost_per_1k = 0.06
        
        input_cost = (usage.prompt_tokens / 1000) * input_cost_per_1k
        output_cost = (usage.completion_tokens / 1000) * output_cost_per_1k
        
        return input_cost + output_cost
    
    def _calculate_anthropic_cost(self, usage) -> float:
        """Anthropic 비용 계산"""
        # Claude-3-Sonnet 가격 (2024년 기준)
        input_cost_per_1k = 0.003
        output_cost_per_1k = 0.015
        
        input_cost = (usage.input_tokens / 1000) * input_cost_per_1k
        output_cost = (usage.output_tokens / 1000) * output_cost_per_1k
        
        return input_cost + output_cost
    
    def _create_ensemble_result(self, responses: List[AIResponse], task_type: str) -> EnsembleResult:
        """앙상블 결과 생성"""
        if not responses:
            raise ValueError("응답이 없습니다")
        
        # 가중 평균 계산
        weighted_content = ""
        total_weight = 0
        total_confidence = 0
        total_cost = 0
        total_processing_time = 0
        
        for response in responses:
            weight = self.model_weights.get(response.model_name, 0.1)
            total_weight += weight
            total_confidence += response.confidence * weight
            total_cost += response.cost
            total_processing_time += response.processing_time
        
        # 최고 신뢰도 모델의 콘텐츠 선택
        best_response = max(responses, key=lambda x: x.confidence)
        final_content = best_response.content
        
        # 모델 기여도 계산
        model_contributions = {}
        for response in responses:
            weight = self.model_weights.get(response.model_name, 0.1)
            model_contributions[response.model_name] = weight / total_weight
        
        return EnsembleResult(
            final_content=final_content,
            confidence_score=total_confidence / total_weight if total_weight > 0 else 0,
            model_contributions=model_contributions,
            processing_time=total_processing_time,
            total_cost=total_cost,
            individual_responses=responses
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """시스템 통계 반환"""
        return {
            'total_requests': self.stats['total_requests'],
            'successful_requests': self.stats['successful_requests'],
            'failed_requests': self.stats['failed_requests'],
            'success_rate': (self.stats['successful_requests'] / self.stats['total_requests'] * 100) if self.stats['total_requests'] > 0 else 0,
            'total_processing_time': self.stats['total_processing_time'],
            'total_cost': self.stats['total_cost'],
            'average_processing_time': (self.stats['total_processing_time'] / self.stats['successful_requests']) if self.stats['successful_requests'] > 0 else 0,
            'model_performance': self.stats['model_performance']
        }
    
    def save_statistics(self, file_path: str = "data/ai_ensemble_stats.json"):
        """통계 저장"""
        try:
            stats = self.get_statistics()
            stats['timestamp'] = datetime.now().isoformat()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"💾 AI 앙상블 통계 저장: {file_path}")
            
        except Exception as e:
            logger.error(f"❌ AI 앙상블 통계 저장 실패: {e}")

# 전역 인스턴스
ai_ensemble = AIEnsembleSystem() 