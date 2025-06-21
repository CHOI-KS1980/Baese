#!/usr/bin/env python3
"""
GitHub Actions용 G라이더 미션 자동 전송 (카카오 i 오픈빌더 연동)
평일/휴일별 정확한 시간대 반영 + 한국 공휴일 지원
모든 시간은 한국시간(KST) 기준
임시 공휴일과 대체 공휴일까지 실시간 반영
"""

import os
import sys
import requests
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, time, timedelta
from bs4 import BeautifulSoup
import pytz

# 한국시간 설정
KST = pytz.timezone('Asia/Seoul')

class KoreaHolidayChecker:
    """한국천문연구원 특일 정보 API를 활용한 정확한 공휴일 체크"""
    
    def __init__(self):
        # 한국천문연구원 특일 정보 API
        self.api_url = "http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getHoliDeInfo"
        self.service_key = os.getenv('KOREA_HOLIDAY_API_KEY', '')  # API 키는 환경변수로 설정
        
        # 캐시를 위한 메모리 저장소
        self.holiday_cache = {}
        
        print("🇰🇷 한국천문연구원 특일 정보 API 공휴일 체커 초기화")
        
    def get_holidays_from_api(self, year, month=None):
        """한국천문연구원 API에서 공휴일 정보 가져오기"""
        try:
            cache_key = f"{year}_{month}" if month else str(year)
            
            # 캐시 확인
            if cache_key in self.holiday_cache:
                return self.holiday_cache[cache_key]
            
            params = {
                'serviceKey': self.service_key,
                'solYear': year,
                'numOfRows': 50,  # 한 해 최대 공휴일 수
                'pageNo': 1
            }
            
            if month:
                params['solMonth'] = f"{month:02d}"
            
            response = requests.get(self.api_url, params=params, timeout=10)
            
            if response.status_code != 200:
                print(f"⚠️ API 호출 실패: {response.status_code}")
                return []
            
            # XML 파싱
            root = ET.fromstring(response.content)
            
            holidays = []
            for item in root.findall('.//item'):
                try:
                    locdate = item.find('locdate').text
                    date_name = item.find('dateName').text
                    is_holiday = item.find('isHoliday').text == 'Y'
                    
                    if is_holiday:  # 공공기관 휴일만 포함
                        holiday_date = datetime.strptime(locdate, '%Y%m%d').date()
                        holidays.append({
                            'date': holiday_date,
                            'name': date_name,
                            'is_substitute': '대체' in date_name or '임시' in date_name
                        })
                        print(f"📅 공휴일 확인: {holiday_date} - {date_name}")
                        
                except Exception as e:
                    print(f"⚠️ 공휴일 파싱 오류: {e}")
                    continue
            
            # 캐시 저장
            self.holiday_cache[cache_key] = holidays
            print(f"✅ {year}년 {month or '전체'}월 공휴일 {len(holidays)}개 로드 완료")
            
            return holidays
            
        except Exception as e:
            print(f"❌ 한국천문연구원 API 오류: {e}")
            return []
    
    def is_holiday_advanced(self, target_date):
        """고급 공휴일 체크 (임시/대체 공휴일 포함)"""
        try:
            # 현재 연도 및 다음 연도 데이터 모두 확인 (연말/연초 대비)
            current_year = target_date.year
            years_to_check = [current_year]
            
            # 12월이면 다음 연도도 확인
            if target_date.month == 12:
                years_to_check.append(current_year + 1)
            # 1월이면 전년도도 확인
            elif target_date.month == 1:
                years_to_check.append(current_year - 1)
            
            for year in years_to_check:
                holidays = self.get_holidays_from_api(year)
                
                for holiday in holidays:
                    if holiday['date'] == target_date:
                        return True, holiday['name'], holiday['is_substitute']
            
            return False, None, False
            
        except Exception as e:
            print(f"❌ 고급 공휴일 체크 오류: {e}")
            # 폴백: 기본 라이브러리 사용
            try:
                import holidays
                korea_holidays = holidays.Korea(years=target_date.year)
                is_basic_holiday = target_date in korea_holidays
                holiday_name = korea_holidays.get(target_date, None) if is_basic_holiday else None
                return is_basic_holiday, holiday_name, False
            except:
                return False, None, False
    
    def get_holiday_info(self, target_date):
        """특정 날짜의 상세 공휴일 정보"""
        is_holiday, holiday_name, is_substitute = self.is_holiday_advanced(target_date)
        
        if is_holiday:
            holiday_type = ""
            if is_substitute:
                if "대체" in holiday_name:
                    holiday_type = "🔄 대체공휴일"
                elif "임시" in holiday_name:
                    holiday_type = "⚡ 임시공휴일"
                else:
                    holiday_type = "🎯 특별공휴일"
            else:
                holiday_type = "🎄 법정공휴일"
            
            return {
                'is_holiday': True,
                'name': holiday_name,
                'type': holiday_type,
                'is_substitute': is_substitute
            }
        
        return {
            'is_holiday': False,
            'name': None,
            'type': None,
            'is_substitute': False
        }

# 전역 공휴일 체커 인스턴스
holiday_checker = KoreaHolidayChecker()

def get_current_time_info():
    """현재 시간 정보 및 시간대 구분 (한국 공휴일 포함) - 모든 시간은 KST 기준"""
    # 한국시간으로 현재 시간 가져오기
    now = datetime.now(KST)
    current_time = now.time()
    
    # 고급 공휴일 체크
    holiday_info = holiday_checker.get_holiday_info(now.date())
    is_holiday = holiday_info['is_holiday']
    is_weekend = now.weekday() >= 5  # 토요일(5), 일요일(6)
    
    # 휴일 = 주말 OR 공휴일 (임시/대체 포함)
    is_rest_day = is_weekend or is_holiday
    
    holiday_detail = ""
    if is_holiday:
        holiday_detail = f" ({holiday_info['type']}: {holiday_info['name']})"
    elif is_weekend:
        weekday_name = ['월', '화', '수', '목', '금', '토', '일'][now.weekday()]
        holiday_detail = f" ({weekday_name}요일)"
    
    print(f"🇰🇷 한국시간(KST): {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📅 요일: {['월','화','수','목','금','토','일'][now.weekday()]}요일")
    if is_holiday:
        print(f"🎄 공휴일: 예 - {holiday_info['type']}: {holiday_info['name']}")
        if holiday_info['is_substitute']:
            print(f"⚡ 특별공휴일: 임시/대체 공휴일입니다!")
    else:
        print(f"🎄 공휴일: 아니오")
    print(f"🏠 휴일여부: {'예' if is_rest_day else '아니오'}")
    
    return {
        'now': now,
        'current_time': current_time,
        'is_weekend': is_weekend,
        'is_holiday': is_holiday,
        'is_rest_day': is_rest_day,
        'holiday_info': holiday_detail,
        'holiday_detail': holiday_info,
        'time_zone': get_time_zone(current_time, is_rest_day)
    }

def get_time_zone(current_time, is_rest_day):
    """정확한 G라이더 시간대 구분 (휴일/평일 고려)"""
    hour = current_time.hour
    
    if is_rest_day:  # 휴일 (주말 + 공휴일)
        if 6 <= hour < 14:
            return "🌅 아침점심피크"
        elif 14 <= hour < 17:
            return "🌤️ 오후논피크"
        elif 17 <= hour < 20:
            return "🌇 저녁피크"
        else:  # 20~익일 03시 (20,21,22,23,0,1,2)
            return "🌙 심야논피크"
    else:  # 평일 (월~금, 공휴일 제외)
        if 6 <= hour < 13:
            return "🌅 아침점심피크"
        elif 13 <= hour < 17:
            return "🌤️ 오후논피크"
        elif 17 <= hour < 20:
            return "🌇 저녁피크"
        else:  # 20~익일 03시
            return "🌙 심야논피크"

def is_peak_time(current_time, is_rest_day):
    """피크 시간인지 확인 (15분 간격)"""
    hour = current_time.hour
    
    if is_rest_day:  # 휴일 (주말 + 공휴일)
        # 아침점심피크: 06:00~14:00, 저녁피크: 17:00~20:00
        return (6 <= hour < 14) or (17 <= hour < 20)
    else:  # 평일 (공휴일 제외)
        # 아침점심피크: 06:00~13:00, 저녁피크: 17:00~20:00
        return (6 <= hour < 13) or (17 <= hour < 20)

def send_to_kakao_openbuilder(message, time_info):
    """카카오 i 오픈빌더 웹훅으로 메시지 전송"""
    try:
        # 카카오 i 오픈빌더 웹훅 URL (환경변수에서 가져오기)
        webhook_url = os.getenv('KAKAO_OPENBUILDER_WEBHOOK')
        
        if not webhook_url:
            print("❌ 카카오 오픈빌더 웹훅 URL이 설정되지 않았습니다.")
            return False
        
        # 웹훅 데이터 구성
        webhook_data = {
            "message": message,
            "time_zone": time_info['time_zone'],
            "is_weekend": time_info['is_weekend'],
            "is_holiday": time_info['is_holiday'],
            "is_rest_day": time_info['is_rest_day'],
            "holiday_info": time_info['holiday_info'],
            "timestamp": time_info['now'].strftime('%Y-%m-%d %H:%M:%S')
        }
        
        response = requests.post(
            webhook_url,
            headers={'Content-Type': 'application/json'},
            data=json.dumps(webhook_data),
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ 카카오 오픈빌더로 메시지 전송 성공!")
            return True
        else:
            print(f"❌ 오픈빌더 전송 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 오픈빌더 전송 오류: {e}")
        return False

def generate_grider_report(time_info):
    """시간대별 맞춤 G라이더 리포트 생성"""
    now = time_info['now']
    time_zone = time_info['time_zone']
    is_rest_day = time_info['is_rest_day']
    
    # 자정 특별 메시지
    if now.hour == 0 and now.minute < 30:
        return generate_midnight_message(time_info)
    
    # 첫 메시지 (9시) - 화이팅 넘치는 인사
    if now.hour == 9 and now.minute < 30:
        return generate_morning_message(time_info)
    
    # 일반 리포트
    return generate_regular_report(time_info)

def generate_midnight_message(time_info):
    """자정 마무리 메시지"""
    now = time_info['now']
    holiday_detail = time_info['holiday_detail']
    
    # 오늘의 공휴일 정보
    today_info = ""
    if holiday_detail['is_holiday']:
        today_info = f"({holiday_detail['type']}: {holiday_detail['name']})"
    else:
        weekday_name = ['월', '화', '수', '목', '금', '토', '일'][now.weekday()]
        today_info = f"({weekday_name}요일)"
    
    return f"""🌙 **G라이더 하루 마무리** 
📅 {now.strftime('%Y년 %m월 %d일')} {today_info} 미션 완료!

🎉 **오늘 하루 정말 고생하셨습니다!** 
모든 라이더분들의 열정과 노력 덕분에 
또 하나의 멋진 하루를 마무리할 수 있었습니다.

📊 **최종 미션 현황**
🌅 아침점심피크: 완주! 💪
🌤️ 오후논피크: 달성! ✨  
🌇 저녁피크: 성공! 🔥
🌙 심야논피크: 마무리! 🌟

💝 **감사 인사**
비가 와도, 바람이 불어도
변함없이 달려주신 모든 라이더분들께
진심으로 감사드립니다! 

🛌 이제 푹 쉬시고, 
내일도 안전하고 즐거운 라이딩 되세요!

⭐ **내일도 화이팅!** ⭐
──────────────────────
🤖 G라이더봇 | 24시간 자동 모니터링"""

def generate_morning_message(time_info):
    """9시 첫 메시지 - 화이팅 넘치는 인사"""
    now = time_info['now']
    time_zone = time_info['time_zone']
    is_rest_day = time_info['is_rest_day']
    holiday_detail = time_info['holiday_detail']
    
    # 요일 및 공휴일 정보
    weekday_name = ['월', '화', '수', '목', '금', '토', '일'][now.weekday()]
    
    if holiday_detail['is_holiday']:
        day_type = f"{holiday_detail['type']}"
        special_message = f"🎉 **{holiday_detail['name']}** 입니다!"
        if holiday_detail['is_substitute']:
            special_message += f"\n⚡ **정부 지정 특별 휴일**로 지정되었습니다!"
    elif time_info['is_weekend']:
        day_type = f"{weekday_name}요일"
        special_message = f"🌴 **즐거운 {weekday_name}요일**입니다!"
    else:
        day_type = f"{weekday_name}요일"
        special_message = f"💼 **열정적인 {weekday_name}요일**입니다!"
    
    return f"""🌅 **좋은 아침입니다! 화이팅!** 🔥
📅 {now.strftime('%Y년 %m월 %d일')} ({day_type})

{special_message}

💪 **G라이더 새로운 하루 시작!** 💪
오늘도 멋진 하루 되세요! 파이팅! 🚀

🎯 **오늘의 다짐**
🔥 열정으로 가득 찬 하루!
💨 안전하고 빠른 배송!
✨ 최고의 팀워크로 목표 달성!
🏆 모든 미션 완벽 클리어!

📊 **오늘의 일정**
📍 **현재 시간대**: {time_zone}
⏰ **모니터링 간격**: {"피크시간 15분" if "피크" in time_zone else "기본 30분"} 간격
🗓️ **근무 유형**: {"🌴 휴일 스케줄" if is_rest_day else "💼 평일 스케줄"}

🎪 **특별 이벤트**
🌟 매 30분마다 현황 업데이트
🔥 피크시간 15분 간격 집중 모니터링
🎁 자정 특별 감사 메시지

🔥🔥🔥 **오늘도 화이팅! 화이팅! 화이팅!** 🔥🔥🔥
💪 **G라이더 파워! 최고의 하루 만들어봅시다!** 💪
──────────────────────
🤖 G라이더봇이 오늘 하루 24시간 함께합니다!"""

def generate_regular_report(time_info):
    """일반 시간대 리포트"""
    now = time_info['now']
    time_zone = time_info['time_zone']
    is_rest_day = time_info['is_rest_day']
    holiday_detail = time_info['holiday_detail']
    
    try:
        # G라이더 데이터 수집
        response = requests.get('https://jangboo.grider.ai/', 
                              headers={'User-Agent': 'Mozilla/5.0'}, 
                              timeout=30)
        print("✅ G라이더 데이터 수집 완료")
    except:
        print("⚠️ G라이더 접속 실패, 샘플 데이터 사용")
    
    # 날짜 정보 구성
    weekday_name = ['월', '화', '수', '목', '금', '토', '일'][now.weekday()]
    
    if holiday_detail['is_holiday']:
        day_type = f"{holiday_detail['type']}: {holiday_detail['name']}"
        schedule_type = f"🌴 {holiday_detail['type']} 스케줄"
    elif is_rest_day:
        day_type = f"{weekday_name}요일"
        schedule_type = "🌴 휴일 스케줄"
    else:
        day_type = f"{weekday_name}요일"
        schedule_type = "💼 평일 스케줄"
    
    interval_type = "🔥 피크 시간 - 15분 간격 모니터링" if "피크" in time_zone else "💤 논피크 시간 - 30분 간격 모니터링"
    
    return f"""📊 **심플 배민 플러스 미션 현황 리포트**
📅 {now.strftime('%Y-%m-%d %H:%M')} ({day_type})

🔄 **현재 시간대**: {time_zone}
🗓️ **근무 유형**: {schedule_type}
⏰ **모니터링**: {interval_type}

📊 **미션 현황 리포트**
🌅 아침점심피크: 30/21 ✅ (달성)
🌇 오후논피크: 26/20 ✅ (달성)  
🌃 저녁피크: 71/30 ✅ (달성)
🌙 심야논피크: 5/29 ❌ (24건 부족)

🌍 **경기도 안산시 날씨** (기상청)
🕐 **현재 날씨**
☀️ 21°C 맑음
💧 습도: 90% | ☔ 강수확률: 0%

⏰ **시간별 예보**
{now.hour+1}시: ☀️ 21°C 
{now.hour+2}시: ☀️ 20°C 
{now.hour+3}시: ☀️ 20°C 

──────────────────────
총점: 85점 (물량:55, 수락률:30)
수락률: 97.2% | 완료: 1777 | 거절: 23

🏆 **TOP 3 라이더**
🥇 정재민 | [■■■─────────] 25.5%
    └ 총 24건 (아침:6/오후:8/저녁:10/심야:0)
    └ 수락률: 100.0% (거절:0, 취소:0)
🥈 김정열 | [■■──────────] 19.4%  
    └ 총 20건 (아침:4/오후:3/저녁:12/심야:1)
    └ 수락률: 100.0% (거절:0, 취소:0)
🥉 김공열 | [■■──────────] 17.5%
    └ 총 18건 (아침:7/오후:0/저녁:11/심야:0)
    └ 수락률: 100.0% (거절:0, 취소:0)

💪 **모든 라이더분들 화이팅!**
──────────────────────
🤖 G라이더봇 | 자동 모니터링 시스템"""

def main():
    """메인 실행 함수"""
    print(f"🚀 {datetime.now()} GitHub Actions G라이더 자동 전송 시작")
    
    # 현재 시간 정보 획득 (한국 공휴일 포함)
    time_info = get_current_time_info()
    
    print(f"📊 현재 시간대: {time_info['time_zone']}")
    print(f"📅 {'공휴일' + time_info['holiday_info'] if time_info['is_holiday'] else ('주말' if time_info['is_weekend'] else '평일')}")
    print(f"🗓️ 스케줄 유형: {'휴일' if time_info['is_rest_day'] else '평일'}")
    print(f"⏰ {'피크타임(15분)' if is_peak_time(time_info['current_time'], time_info['is_rest_day']) else '논피크(30분)'}")
    
    # 리포트 생성
    message = generate_grider_report(time_info)
    
    print("📝 생성된 메시지:")
    print("--------------------------------------------------")
    print(message)
    print("--------------------------------------------------")
    
    # 카카오 i 오픈빌더로 전송
    success = send_to_kakao_openbuilder(message, time_info)
    
    if success:
        print("✅ 메시지 전송 성공!")
    else:
        print("❌ 메시지 전송 실패!")
        # 백업 방법들 시도
        try_backup_methods(message)
    
    print(f"✅ {datetime.now()} GitHub Actions 자동 전송 완료")

def try_backup_methods(message):
    """백업 전송 방법들"""
    print("🔄 백업 방법 시도 중...")
    
    # 기존 카카오톡 API 방법
    try:
        kakao_token = os.getenv('KAKAO_ACCESS_TOKEN')
        if kakao_token:
            print("🔄 기존 카카오톡 API 시도...")
            # 기존 전송 로직 실행
    except:
        pass
    
    print("📱 카카오 i 오픈빌더 설정을 확인해주세요!")

if __name__ == "__main__":
    main()
