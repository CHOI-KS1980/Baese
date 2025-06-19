#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
카카오톡 오픈채팅방 자동 미션 전송 시스템 (GitHub Actions용)
Korean Astronomical Observatory KASI API 연동 버전

한국천문연구원의 공식 특일정보 API를 활용하여
정확한 공휴일, 임시공휴일, 대체공휴일을 감지하고
상황에 맞는 메시지를 전송합니다.

Author: AI Assistant
Version: 3.0 (KASI API 통합)
"""

import os
import json
import requests
import random
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pytz

class KoreaHolidayChecker:
    """한국천문연구원 API를 활용한 한국 공휴일 체크 시스템"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('KOREA_HOLIDAY_API_KEY')
        self.base_url = "http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService"
        self.cache = {}
        
    def _make_api_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """KASI API 요청 실행"""
        if not self.api_key:
            return None
            
        try:
            params.update({
                'ServiceKey': self.api_key,
                'pageNo': 1,
                'numOfRows': 100,
                '_type': 'json'
            })
            
            response = requests.get(f"{self.base_url}/{endpoint}", params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('response', {}).get('header', {}).get('resultCode') == '00':
                return data.get('response', {}).get('body', {})
            return None
            
        except Exception as e:
            print(f"⚠️  KASI API 요청 실패 ({endpoint}): {e}")
            return None
    
    def get_holidays_for_month(self, year: int, month: int) -> List[Dict]:
        """특정 년월의 모든 특일정보 조회"""
        cache_key = f"{year}-{month:02d}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        holidays = []
        
        # 공휴일 정보 조회
        holiday_data = self._make_api_request('getHoliDeInfo', {
            'solYear': year,
            'solMonth': f"{month:02d}"
        })
        
        if holiday_data and holiday_data.get('items'):
            items = holiday_data['items'].get('item', [])
            if isinstance(items, dict):
                items = [items]
            holidays.extend(items)
        
        # 국경일 정보 조회
        national_data = self._make_api_request('getRestDeInfo', {
            'solYear': year,
            'solMonth': f"{month:02d}"
        })
        
        if national_data and national_data.get('items'):
            items = national_data['items'].get('item', [])
            if isinstance(items, dict):
                items = [items]
            holidays.extend(items)
        
        # 기념일 정보 조회 (임시공휴일 포함)
        anniversary_data = self._make_api_request('getAnniversaryInfo', {
            'solYear': year,
            'solMonth': f"{month:02d}"
        })
        
        if anniversary_data and anniversary_data.get('items'):
            items = anniversary_data['items'].get('item', [])
            if isinstance(items, dict):
                items = [items]
            holidays.extend(items)
        
        self.cache[cache_key] = holidays
        return holidays
    
    def is_holiday(self, date: datetime) -> Tuple[bool, Optional[str], Optional[str]]:
        """특정 날짜가 공휴일인지 확인
        
        Returns:
            (is_holiday, holiday_name, holiday_type)
            holiday_type: 'national' (국경일), 'public' (공휴일), 'substitute' (대체공휴일), 
                         'temporary' (임시공휴일), 'anniversary' (기념일)
        """
        holidays = self.get_holidays_for_month(date.year, date.month)
        date_str = date.strftime('%Y%m%d')
        
        for holiday in holidays:
            if holiday.get('locdate') == date_str:
                is_holiday_flag = holiday.get('isHoliday', 'N') == 'Y'
                name = holiday.get('dateName', '')
                
                # 공휴일 유형 판단
                date_kind = holiday.get('dateKind', '')
                if date_kind == '01':  # 국경일
                    holiday_type = 'national'
                elif date_kind == '02':  # 기념일
                    holiday_type = 'anniversary'
                elif is_holiday_flag:
                    if '대체' in name or '임시' in name:
                        holiday_type = 'substitute' if '대체' in name else 'temporary'
                    else:
                        holiday_type = 'public'
                else:
                    holiday_type = 'anniversary'
                
                return is_holiday_flag, name, holiday_type
        
        return False, None, None
    
    def get_upcoming_holidays(self, days_ahead: int = 7) -> List[Dict]:
        """앞으로 며칠간의 공휴일 정보 조회"""
        korea_tz = pytz.timezone('Asia/Seoul')
        now = datetime.now(korea_tz)
        upcoming = []
        
        for i in range(1, days_ahead + 1):
            future_date = now + timedelta(days=i)
            is_hol, name, h_type = self.is_holiday(future_date)
            
            if is_hol:
                upcoming.append({
                    'date': future_date,
                    'name': name,
                    'type': h_type,
                    'days_until': i
                })
        
        return upcoming

class KakaoMessageSender:
    """카카오톡 i 오픈빌더 메시지 전송 클래스"""
    
    def __init__(self):
        self.webhook_url = os.getenv('WEBHOOK_URL')
        self.korea_tz = pytz.timezone('Asia/Seoul')
        self.holiday_checker = KoreaHolidayChecker()
        
        # 날씨 API 설정
        self.weather_api_key = os.getenv('OPENWEATHER_API_KEY')
        self.city = "Seoul"
        
        self.debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        
    def get_current_time_info(self) -> Dict:
        """현재 한국 시간 정보 조회"""
        now = datetime.now(self.korea_tz)
        
        # 공휴일 체크
        is_holiday, holiday_name, holiday_type = self.holiday_checker.is_holiday(now)
        
        return {
            'now': now,
            'hour': now.hour,
            'minute': now.minute,
            'weekday': now.weekday(),  # 0=월요일, 6=일요일
            'is_weekend': now.weekday() >= 5,
            'is_holiday': is_holiday,
            'holiday_name': holiday_name,
            'holiday_type': holiday_type,
            'date_str': now.strftime('%Y년 %m월 %d일'),
            'time_str': now.strftime('%H:%M'),
            'weekday_name': ['월', '화', '수', '목', '금', '토', '일'][now.weekday()]
        }
    
    def get_weather_info(self) -> Dict:
        """OpenWeather API로 날씨 정보 조회"""
        if not self.weather_api_key:
            return {'description': '날씨 좋은', 'temp': '', 'emoji': '☀️'}
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': self.city,
                'appid': self.weather_api_key,
                'units': 'metric',
                'lang': 'kr'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            weather_desc = data['weather'][0]['description']
            temp = int(data['main']['temp'])
            
            # 날씨 이모지 매핑
            weather_emojis = {
                '맑': '☀️', '구름': '☁️', '비': '🌧️', '눈': '❄️',
                '천둥': '⛈️', '안개': '🌫️', '바람': '💨'
            }
            
            emoji = '🌤️'
            for key, em in weather_emojis.items():
                if key in weather_desc:
                    emoji = em
                    break
            
            return {
                'description': weather_desc,
                'temp': f"{temp}°C",
                'emoji': emoji
            }
            
        except Exception as e:
            print(f"⚠️  날씨 정보 조회 실패: {e}")
            return {'description': '좋은', 'temp': '', 'emoji': '🌤️'}
    
    def get_message_templates(self) -> Dict:
        """시간대별 메시지 템플릿"""
        return {
            'morning_greetings': [
                "🌅 좋은 아침이에요! 오늘도 화이팅! ✨",
                "☀️ 새로운 하루가 시작됐어요! 오늘도 힘내세요! 💪",
                "🌤️ 상쾌한 아침! 오늘 하루도 즐겁게 보내세요! 😊",
                "🌟 활기찬 아침! 오늘도 좋은 일들만 가득하길! 🎉",
                "🌸 따뜻한 아침 인사드려요! 오늘도 행복한 하루! 💖"
            ],
            'regular_missions': [
                "🎯 오늘의 미션: 작은 성취라도 자신을 칭찬해주세요! 👏",
                "💡 창의적인 아이디어로 문제를 해결해보세요! 🧠",
                "🤝 동료와 함께 협력하여 더 큰 성과를 만들어보세요! 🌟",
                "📚 새로운 것을 하나 배워보는 시간을 가져보세요! 🎓",
                "🎨 일에 재미를 더해보는 창의적인 방법을 찾아보세요! ✨",
                "💪 도전적인 업무에 적극적으로 임해보세요! 🚀",
                "🌱 성장을 위한 피드백을 주고받아보세요! 📈",
                "🎵 긍정적인 에너지로 하루를 채워보세요! 🌈"
            ],
            'evening_missions': [
                "🌅 내일을 위한 준비를 체크해보세요! 📋",
                "💭 오늘 있었던 좋은 일들을 되돌아보세요! ✨",
                "📝 내일의 목표를 간단히 정리해보세요! 🎯",
                "🧘‍♀️ 잠시 휴식을 취하며 마음을 정리해보세요! 💆‍♀️",
                "🍵 따뜻한 차 한 잔과 함께 여유를 즐겨보세요! ☕"
            ],
            'night_closing': [
                "🌙 오늘 하루도 수고 많으셨어요! 좋은 꿈 꾸세요! 💤",
                "⭐ 내일도 좋은 일들만 가득하길 바라요! 안녕히 주무세요! 🛌",
                "🌌 평안한 밤 되시고, 내일 또 만나요! 💫",
                "🛌 푹 쉬시고 내일 더욱 활기찬 모습으로 만나요! 😴",
                "🌸 오늘도 감사했습니다! 달콤한 꿈 꾸세요! 💝"
            ],
            'holiday_messages': [
                "🎉 즐거운 {holiday_name}이에요! 소중한 사람들과 행복한 시간 보내세요! 💖",
                "🌟 {holiday_name} 잘 보내고 계신가요? 충분한 휴식 취하세요! 😊",
                "🏖️ 특별한 {holiday_name}! 일상의 피로를 날려버리는 시간 되세요! ✨",
                "🎊 의미 있는 {holiday_name}이네요! 감사한 마음으로 보내시길! 🙏"
            ],
            'weekend_messages': [
                "🎮 신나는 주말! 좋아하는 일을 마음껏 해보세요! 🎨",
                "🛋️ 편안한 주말 휴식 시간이에요! 재충전하세요! 🔋",
                "🌳 야외 활동하기 좋은 주말이에요! 신선한 공기 마셔보세요! 🌿",
                "👨‍👩‍👧‍👦 가족, 친구들과 소중한 시간 보내세요! 💕"
            ]
        }
    
    def generate_contextual_message(self, time_info: Dict) -> str:
        """상황에 맞는 메시지 생성"""
        templates = self.get_message_templates()
        weather = self.get_weather_info()
        
        # 공휴일 메시지
        if time_info['is_holiday']:
            holiday_msg = random.choice(templates['holiday_messages']).format(
                holiday_name=time_info['holiday_name']
            )
            
            # 공휴일 유형별 추가 메시지
            if time_info['holiday_type'] == 'national':
                holiday_msg += f"\n\n🇰🇷 뜻깊은 국경일이네요!"
            elif time_info['holiday_type'] == 'substitute':
                holiday_msg += f"\n\n📅 대체공휴일로 추가 휴식!"
            elif time_info['holiday_type'] == 'temporary':
                holiday_msg += f"\n\n🎁 특별한 임시공휴일이에요!"
            
            return holiday_msg
        
        # 시간대별 메시지
        if time_info['hour'] == 9 and time_info['minute'] == 0:
            # 아침 인사
            message = random.choice(templates['morning_greetings'])
            message += f"\n\n{weather['emoji']} 현재 날씨: {weather['description']} {weather['temp']}"
            
            # 다가오는 공휴일 정보
            upcoming = self.holiday_checker.get_upcoming_holidays(7)
            if upcoming:
                holiday = upcoming[0]
                if holiday['days_until'] <= 3:
                    message += f"\n\n📅 {holiday['days_until']}일 후 {holiday['name']}이 있어요!"
                    
        elif time_info['hour'] == 0 and time_info['minute'] == 0:
            # 자정 마무리
            message = random.choice(templates['night_closing'])
            
        elif time_info['is_weekend']:
            # 주말 메시지
            if 18 <= time_info['hour'] <= 21:
                message = random.choice(templates['evening_missions'])
            else:
                message = random.choice(templates['weekend_messages'])
                
        else:
            # 평일 일반 메시지
            if 18 <= time_info['hour'] <= 21:
                message = random.choice(templates['evening_missions'])
            else:
                message = random.choice(templates['regular_missions'])
        
        # 시간 정보 추가
        message += f"\n\n⏰ {time_info['date_str']} ({time_info['weekday_name']}) {time_info['time_str']}"
        
        return message
    
    def send_message(self, message: str) -> bool:
        """카카오톡 i 오픈빌더로 메시지 전송"""
        if not self.webhook_url:
            print("❌ WEBHOOK_URL이 설정되지 않았습니다!")
            return False
        
        payload = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": message
                        }
                    }
                ]
            }
        }
        
        try:
            if self.debug_mode:
                print(f"🔧 DEBUG MODE - 전송할 메시지:\n{message}")
                return True
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            
            print(f"✅ 메시지 전송 성공!")
            print(f"📝 전송된 메시지: {message[:50]}...")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 메시지 전송 실패: {e}")
            return False
    
    def run(self):
        """메인 실행 함수"""
        try:
            print("🚀 카카오톡 자동 전송 시스템 시작")
            print(f"🕐 현재 시간: {datetime.now(self.korea_tz).strftime('%Y-%m-%d %H:%M:%S KST')}")
            
            # 시간 정보 확인
            time_info = self.get_current_time_info()
            print(f"📅 날짜 정보: {time_info['date_str']} ({time_info['weekday_name']}요일)")
            
            if time_info['is_holiday']:
                print(f"🎉 오늘은 {time_info['holiday_name']} ({time_info['holiday_type']})입니다!")
            elif time_info['is_weekend']:
                print("🎮 주말입니다!")
            else:
                print("💼 평일입니다!")
            
            # 메시지 생성 및 전송
            message = self.generate_contextual_message(time_info)
            success = self.send_message(message)
            
            if success:
                print("🎉 전송 완료!")
            else:
                print("⚠️ 전송 실패!")
                
        except Exception as e:
            print(f"💥 오류 발생: {e}")
            print(f"📋 상세 정보:\n{traceback.format_exc()}")

def main():
    """메인 함수"""
    sender = KakaoMessageSender()
    sender.run()

if __name__ == "__main__":
    main() 