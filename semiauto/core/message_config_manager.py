#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 메시지 설정 관리 시스템

웹 대시보드와 GitHub Actions 간의 메시지 설정 동기화
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import pytz

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 한국 시간대
KST = pytz.timezone('Asia/Seoul')

class MessageConfigManager:
    """메시지 설정 관리자"""
    
    def __init__(self):
        """초기화"""
        self.config_file = "dashboard/api/message-settings.json"
        self.template_file = "dashboard/api/message-templates.json"
        self.cache_file = "message_config_cache.json"
        
        # 기본 템플릿 정의
        self.default_templates = {
            "standard": {
                "title": "🚀 G라이더 현황 알림",
                "content": "📊 현재 점수: {score}점\n✅ 완료 미션: {completed_missions}개\n🏍️ 활성 라이더: {active_riders}명\n💰 예상 수익: {estimated_income:,}원",
                "footer": "📅 {timestamp}",
                "description": "기본적인 정보를 포함한 표준 형식"
            },
            "detailed": {
                "title": "📈 G라이더 상세 현황 리포트",
                "content": "🎯 성과 지표\n━━━━━━━━━━━━━━━━━━━━━\n📊 현재 점수: {score}점 ({score_change:+d})\n✅ 완료 미션: {completed_missions}개 ({mission_change:+d})\n🏍️ 활성 라이더: {active_riders}명 ({riders_change:+d})\n💰 예상 수익: {estimated_income:,}원 ({income_change:+,})\n\n📈 시간대별 추이\n━━━━━━━━━━━━━━━━━━━━━\n🕒 피크시간 성과율: {peak_performance}%\n⏰ 평균 응답시간: {avg_response_time}분\n🎯 목표 달성률: {goal_achievement}%",
                "footer": "📅 {timestamp} | 다음 업데이트: {next_update}",
                "description": "변화량과 추이를 포함한 상세 형식"
            },
            "simple": {
                "title": "G라이더",
                "content": "점수 {score}점 | 미션 {completed_missions}개 | 라이더 {active_riders}명",
                "footer": "{timestamp}",
                "description": "핵심 정보만 담은 간단 형식"
            },
            "emoji_rich": {
                "title": "🌟 G라이더 실시간 현황 🌟",
                "content": "🎯 오늘의 성과\n📊 점수: {score}점 ⭐\n✅ 미션: {completed_missions}개 완료 🎉\n🏍️ 라이더: {active_riders}명 활동중 🚀\n💰 수익: {estimated_income:,}원 예상 💎\n\n📈 실시간 트렌드\n{trend_emoji} {trend_description}",
                "footer": "⏰ {timestamp} | 💪 화이팅!",
                "description": "이모지가 풍부한 재미있는 형식"
            },
            "business": {
                "title": "G라이더 운영 현황 보고",
                "content": "■ 당일 성과 요약\n- 현재 점수: {score}점\n- 완료 미션: {completed_missions}건\n- 활성 라이더: {active_riders}명\n- 예상 수익: {estimated_income:,}원\n\n■ 주요 지표\n- 목표 달성률: {goal_achievement}%\n- 평균 응답시간: {avg_response_time}분\n- 시스템 상태: 정상 운영",
                "footer": "보고일시: {timestamp}",
                "description": "공식적인 비즈니스 리포트 형식"
            }
        }
        
        self.ensure_config_files()
        logger.info("📱 메시지 설정 관리자 초기화 완료")
    
    def ensure_config_files(self):
        """설정 파일들이 존재하는지 확인하고 없으면 생성"""
        # 디렉토리 생성
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        # 기본 메시지 설정 파일 생성
        if not os.path.exists(self.config_file):
            default_config = {
                "template": "standard",
                "sendOnChange": True,
                "sendOnSchedule": True,
                "sendOnAlert": False,
                "customMessage": None,
                "lastUpdated": datetime.now(KST).isoformat(),
                "updatedBy": "system"
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            
            logger.info(f"📁 기본 메시지 설정 파일 생성: {self.config_file}")
        
        # 템플릿 파일 생성
        if not os.path.exists(self.template_file):
            with open(self.template_file, 'w', encoding='utf-8') as f:
                json.dump(self.default_templates, f, ensure_ascii=False, indent=2)
            
            logger.info(f"📁 기본 템플릿 파일 생성: {self.template_file}")
    
    def load_config(self) -> Dict[str, Any]:
        """현재 메시지 설정 로드"""
        try:
            # 캐시 파일에서 먼저 시도
            if os.path.exists(self.cache_file):
                cache_age = datetime.now().timestamp() - os.path.getmtime(self.cache_file)
                if cache_age < 300:  # 5분 이내 캐시는 유효
                    with open(self.cache_file, 'r', encoding='utf-8') as f:
                        cached_config = json.load(f)
                        logger.debug("📦 캐시된 설정 사용")
                        return cached_config
            
            # 원본 설정 파일에서 로드
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                    # 캐시 업데이트
                    with open(self.cache_file, 'w', encoding='utf-8') as cache_f:
                        json.dump(config, cache_f, ensure_ascii=False, indent=2)
                    
                    logger.info("✅ 메시지 설정 로드 완료")
                    return config
            
        except Exception as e:
            logger.error(f"❌ 설정 로드 실패: {e}")
        
        # 기본 설정 반환
        logger.warning("⚠️ 기본 설정 사용")
        return {
            "template": "standard",
            "sendOnChange": True,
            "sendOnSchedule": True,
            "sendOnAlert": False,
            "customMessage": None
        }
    
    def load_templates(self) -> Dict[str, Any]:
        """사용 가능한 템플릿 로드"""
        try:
            if os.path.exists(self.template_file):
                with open(self.template_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"❌ 템플릿 로드 실패: {e}")
        
        # 기본 템플릿 반환
        return self.default_templates
    
    def save_config(self, config: Dict[str, Any], updated_by: str = "unknown") -> bool:
        """메시지 설정 저장"""
        try:
            # 메타데이터 추가
            config["lastUpdated"] = datetime.now(KST).isoformat()
            config["updatedBy"] = updated_by
            
            # 설정 파일 저장
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            # 캐시 업데이트
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 메시지 설정 저장 완료 (by: {updated_by})")
            return True
            
        except Exception as e:
            logger.error(f"❌ 설정 저장 실패: {e}")
            return False
    
    def get_template(self, template_name: str) -> Optional[Dict[str, str]]:
        """특정 템플릿 가져오기"""
        templates = self.load_templates()
        
        if template_name == "custom":
            config = self.load_config()
            custom_message = config.get("customMessage")
            
            if custom_message:
                try:
                    return json.loads(custom_message)
                except json.JSONDecodeError:
                    logger.error("❌ 사용자 정의 템플릿 JSON 파싱 실패")
                    return templates.get("standard")
        
        return templates.get(template_name, templates.get("standard"))
    
    def format_message(self, template: Dict[str, str], variables: Dict[str, Any]) -> Dict[str, str]:
        """템플릿에 변수를 적용하여 메시지 생성"""
        try:
            # 기본 변수 추가
            default_vars = {
                "timestamp": datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S'),
                "next_update": (datetime.now(KST) + timedelta(minutes=30)).strftime('%H:%M'),
                "trend_emoji": self._get_trend_emoji(variables),
                "trend_description": self._get_trend_description(variables)
            }
            
            # 변수 병합 (기본값 < 전달받은 값)
            all_vars = {**default_vars, **variables}
            
            # 템플릿 변수 치환
            title = template.get("title", "G라이더 현황").format(**all_vars)
            content = template.get("content", "점수: {score}점").format(**all_vars)
            footer = template.get("footer", "{timestamp}").format(**all_vars)
            
            return {
                "title": title,
                "content": content,
                "footer": footer,
                "full_message": f"{title}\n\n{content}\n\n{footer}"
            }
            
        except Exception as e:
            logger.error(f"❌ 메시지 포맷팅 실패: {e}")
            # 안전한 기본 메시지 반환
            return {
                "title": "🚀 G라이더 현황",
                "content": f"점수: {variables.get('score', 0)}점\n미션: {variables.get('completed_missions', 0)}개",
                "footer": datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S'),
                "full_message": f"🚀 G라이더 현황\n\n점수: {variables.get('score', 0)}점\n미션: {variables.get('completed_missions', 0)}개\n\n{datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')}"
            }
    
    def _get_trend_emoji(self, variables: Dict[str, Any]) -> str:
        """트렌드에 따른 이모지 반환"""
        score_change = variables.get("score_change", 0)
        mission_change = variables.get("mission_change", 0)
        
        if score_change > 0 and mission_change > 0:
            return "📈"  # 상승
        elif score_change < 0 or mission_change < 0:
            return "📉"  # 하락
        else:
            return "📊"  # 보합
    
    def _get_trend_description(self, variables: Dict[str, Any]) -> str:
        """트렌드 설명 반환"""
        score_change = variables.get("score_change", 0)
        mission_change = variables.get("mission_change", 0)
        
        if score_change > 10 and mission_change > 0:
            return "성과가 크게 상승했습니다! 🎉"
        elif score_change > 0 and mission_change >= 0:
            return "꾸준히 상승하고 있습니다 💪"
        elif score_change < -10 or mission_change < -2:
            return "주의가 필요합니다 ⚠️"
        elif score_change < 0:
            return "약간 하락했지만 괜찮습니다"
        else:
            return "안정적으로 유지되고 있습니다 ✨"
    
    def generate_message_for_grider_data(self, grider_data: Dict[str, Any]) -> Dict[str, str]:
        """G라이더 데이터로부터 완전한 메시지 생성"""
        try:
            # 현재 설정 로드
            config = self.load_config()
            template_name = config.get("template", "standard")
            
            # 템플릿 가져오기
            template = self.get_template(template_name)
            if not template:
                logger.error(f"❌ 템플릿을 찾을 수 없음: {template_name}")
                template = self.get_template("standard")
            
            # 변수 준비
            variables = {
                "score": grider_data.get("current_score", 0),
                "completed_missions": grider_data.get("completed_missions", 0),
                "active_riders": grider_data.get("active_riders", 0),
                "estimated_income": grider_data.get("estimated_income", 0),
                "score_change": grider_data.get("score_change", 0),
                "mission_change": grider_data.get("mission_change", 0),
                "riders_change": grider_data.get("riders_change", 0),
                "income_change": grider_data.get("income_change", 0),
                "peak_performance": grider_data.get("peak_performance", 85.0),
                "avg_response_time": grider_data.get("avg_response_time", 3.5),
                "goal_achievement": grider_data.get("goal_achievement", 80.0)
            }
            
            # 메시지 생성
            message = self.format_message(template, variables)
            
            logger.info(f"📱 메시지 생성 완료: {template_name} 템플릿")
            return message
            
        except Exception as e:
            logger.error(f"❌ 메시지 생성 실패: {e}")
            # 안전한 기본 메시지
            return {
                "title": "🚀 G라이더 현황",
                "content": f"점수: {grider_data.get('current_score', 0)}점",
                "footer": datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S'),
                "full_message": f"🚀 G라이더 현황\n\n점수: {grider_data.get('current_score', 0)}점\n\n{datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S')}"
            }
    
    def should_send_message(self, grider_data: Dict[str, Any], context: str = "schedule") -> bool:
        """메시지 전송 여부 판단"""
        config = self.load_config()
        
        # 전송 조건 확인
        if context == "schedule" and not config.get("sendOnSchedule", True):
            logger.info("📅 스케줄 전송이 비활성화됨")
            return False
        
        if context == "change" and not config.get("sendOnChange", True):
            logger.info("🔄 변경시 전송이 비활성화됨")
            return False
        
        if context == "alert" and not config.get("sendOnAlert", False):
            logger.info("🚨 알림 전송이 비활성화됨")
            return False
        
        # 데이터 품질 확인
        score = grider_data.get("current_score", 0)
        missions = grider_data.get("completed_missions", 0)
        
        if score <= 0 and missions <= 0:
            logger.warning("⚠️ 유효하지 않은 데이터로 인해 전송 스킵")
            return False
        
        return True
    
    def get_config_status(self) -> Dict[str, Any]:
        """설정 상태 정보 반환"""
        config = self.load_config()
        templates = self.load_templates()
        
        return {
            "current_template": config.get("template", "standard"),
            "available_templates": list(templates.keys()),
            "send_conditions": {
                "on_schedule": config.get("sendOnSchedule", True),
                "on_change": config.get("sendOnChange", True),
                "on_alert": config.get("sendOnAlert", False)
            },
            "last_updated": config.get("lastUpdated", "알 수 없음"),
            "updated_by": config.get("updatedBy", "알 수 없음"),
            "has_custom_template": bool(config.get("customMessage")),
            "config_file_exists": os.path.exists(self.config_file),
            "template_file_exists": os.path.exists(self.template_file)
        }

def main():
    """테스트 실행"""
    manager = MessageConfigManager()
    
    # 샘플 데이터로 테스트
    sample_data = {
        "current_score": 785,
        "completed_missions": 23,
        "active_riders": 31,
        "estimated_income": 94200,
        "score_change": 25,
        "mission_change": 3,
        "riders_change": 2,
        "peak_performance": 92.5,
        "avg_response_time": 3.2,
        "goal_achievement": 78.5
    }
    
    # 각 템플릿으로 메시지 생성 테스트
    templates = manager.load_templates()
    
    for template_name in templates.keys():
        print(f"\n{'='*50}")
        print(f"📱 템플릿: {template_name}")
        print('='*50)
        
        # 임시로 템플릿 변경
        config = manager.load_config()
        config["template"] = template_name
        manager.save_config(config, "test")
        
        # 메시지 생성
        message = manager.generate_message_for_grider_data(sample_data)
        print(message["full_message"])
    
    print(f"\n{'='*50}")
    print("📊 설정 상태")
    print('='*50)
    status = manager.get_config_status()
    for key, value in status.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main() 