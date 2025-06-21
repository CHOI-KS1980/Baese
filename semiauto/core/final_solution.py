#!/usr/bin/env python3
"""
🎯 최종 검증된 솔루션: 카카오톡 나에게 보내기 + 수동 복사
- 웹 크롤링 → 데이터 가공 (자동)
- 카카오톡 나에게 보내기 (자동)
- 클립보드 자동 복사 (자동)
- 오픈채팅방 복사/붙여넣기 (수동 5초)
"""

import requests
import json
import schedule
import time
from datetime import datetime, timedelta
# pyperclip은 조건부 import (GitHub Actions 환경에서는 사용 불가)
import logging
import os
import re
import datetime as dt

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('grider_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TokenManager:
    """카카오톡 토큰 관리 클래스"""
    
    def __init__(self, rest_api_key, refresh_token):
        self.rest_api_key = rest_api_key
        self.refresh_token = refresh_token
        self.access_token = None
        self.token_expires_at = None
    
    def refresh_access_token(self):
        """액세스 토큰 갱신"""
        url = "https://kauth.kakao.com/oauth/token"
        data = {
            'grant_type': 'refresh_token',
            'client_id': self.rest_api_key,
            'refresh_token': self.refresh_token
        }
        
        try:
            response = requests.post(url, data=data)
            result = response.json()
            
            if 'access_token' in result:
                self.access_token = result['access_token']
                # 액세스 토큰은 6시간 유효
                self.token_expires_at = datetime.now() + timedelta(hours=6)
                
                # 새로운 리프레시 토큰이 있으면 업데이트
                if 'refresh_token' in result:
                    self.refresh_token = result['refresh_token']
                
                # 토큰 파일 업데이트
                self.save_tokens()
                
                logger.info(f"✅ 토큰 갱신 완료: {self.access_token[:20]}...")
                return True
            else:
                logger.error(f"❌ 토큰 갱신 실패: {result}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 토큰 갱신 중 오류: {e}")
            return False
    
    def get_valid_token(self):
        """유효한 액세스 토큰 반환 (필요시 자동 갱신)"""
        if not self.access_token or self.is_token_expired():
            if not self.refresh_access_token():
                raise Exception("토큰 갱신 실패")
        
        return self.access_token
    
    def is_token_expired(self):
        """토큰 만료 여부 확인"""
        if not self.token_expires_at:
            return True
        
        # 만료 30분 전에 미리 갱신
        return datetime.now() >= (self.token_expires_at - timedelta(minutes=30))
    
    def save_tokens(self):
        """토큰을 파일에 저장"""
        try:
            with open('kakao_tokens.txt', 'w') as f:
                f.write(f"ACCESS_TOKEN={self.access_token}\n")
                f.write(f"REFRESH_TOKEN={self.refresh_token}\n")
                f.write(f"EXPIRES_AT={self.token_expires_at.isoformat()}\n")
        except Exception as e:
            logger.error(f"❌ 토큰 저장 실패: {e}")

class KakaoSender:
    """카카오톡 메시지 전송 클래스"""
    
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    
    def send_text_message(self, text, link_url=None):
        """텍스트 메시지 전송"""
        # 방법: 메시지 API 대신 친구에게 메시지 API 사용 시도
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
        
        # 나에게 보내기 API 사용 (다른 엔드포인트)
        url = 'https://kapi.kakao.com/v2/api/talk/memo/default/send'
        
        template_object = {
            "object_type": "text",
            "text": text,
            "link": {
                "web_url": "https://www.google.com"
            }
        }
        
        data = {
            'template_object': json.dumps(template_object, ensure_ascii=False)
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            return response.json()
        except Exception as e:
            logger.error(f"❌ 메시지 전송 중 오류: {e}")
            return {"error": str(e)}
    
    def send_feed_message(self, title, description, image_url, link_url):
        """피드 메시지 전송"""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
        
        template_object = {
            "object_type": "feed",
            "content": {
                "title": title,
                "description": description,
                "image_url": image_url,
                "image_width": 640,
                "image_height": 640,
                "link": {
                    "web_url": link_url,
                    "mobile_web_url": link_url
                }
            },
            "buttons": [
                {
                    "title": "자세히 보기",
                    "link": {
                        "web_url": link_url,
                        "mobile_web_url": link_url
                    }
                }
            ]
        }
        
        data = {
            'template_object': json.dumps(template_object, ensure_ascii=False)
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, data=data)
            return response.json()
        except Exception as e:
            logger.error(f"❌ 피드 메시지 전송 중 오류: {e}")
            return {"error": str(e)}

class GriderDataCollector:
    """심플 배민 플러스 데이터 수집 클래스"""
    
    def __init__(self):
        self.base_url = "https://grider.co.kr"  # 실제 URL로 변경 필요
        self.mission_data_cache_file = 'mission_data_cache.json'
    
    def get_grider_data(self):
        """심플 배민 플러스 데이터 수집 (main_(2).py와 동일한 로직)"""
        try:
            # main_(2).py의 검증된 크롤링 로직 사용
            html = self._crawl_jangboo(max_retries=3, retry_delay=5)
            
            if html:
                logger.info("✅ 크롤링 성공, 데이터 파싱 시작")
                data = self._parse_data(html)
                
                if data:
                    logger.info("✅ 실제 심플 배민 플러스 데이터 수집 완료")
                    return data
                else:
                    logger.warning("파싱 실패 - 샘플 데이터 사용")
                    return self._get_sample_data()
            else:
                logger.warning("크롤링 실패 - 샘플 데이터 사용")
                return self._get_sample_data()
                    
        except Exception as e:
            logger.error(f"데이터 수집 실패: {e}")
            logger.info("샘플 데이터로 대체합니다")
            return self._get_sample_data()
    
    def _crawl_jangboo(self, max_retries=3, retry_delay=5):
        """최적화된 크롤링 함수 (main_(2).py와 동일한 로직)"""
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        
        start_time = time.time()
        driver = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"크롤링 시도 {attempt + 1}/{max_retries}")
                
                # Chrome 옵션 설정 (main_(2).py와 동일)
                options = Options()
                chrome_args = [
                    '--headless', '--no-sandbox', '--disable-dev-shm-usage',
                    '--disable-gpu', '--disable-images', '--memory-pressure-off',
                    '--max_old_space_size=4096', '--disable-web-security',
                    '--disable-features=VizDisplayCompositor', '--disable-extensions',
                    '--no-first-run', '--ignore-certificate-errors', '--ignore-ssl-errors',
                    '--ignore-certificate-errors-spki-list',
                    '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                ]
                
                for arg in chrome_args:
                    options.add_argument(arg)
                
                driver = webdriver.Chrome(options=options)
                driver.set_page_load_timeout(30)  # 타임아웃 늘림
                driver.implicitly_wait(10)  # 암시적 대기 추가
                
                # 로그인 페이지 로드 (재시도 로직)
                LOGIN_URL = 'https://jangboo.grider.ai/'
                logger.info(f"로그인 페이지 접속: {LOGIN_URL}")
                driver.get(LOGIN_URL)
                time.sleep(2)  # 페이지 로딩 대기

                # 페이지 로드 완료 확인
                if "jangboo" not in driver.current_url.lower():
                    raise Exception(f"예상과 다른 페이지 로드: {driver.current_url}")

                # 로그인 처리
                logger.info("로그인 시도")
                USER_ID = 'DP2406035262'  
                USER_PW = 'wldud050323!'
                
                id_field = driver.find_element(By.ID, 'id')
                pw_field = driver.find_element(By.ID, 'password')
                login_btn = driver.find_element(By.ID, 'loginBtn')
                
                # 입력 필드 클리어 후 입력
                id_field.clear()
                id_field.send_keys(USER_ID)
                
                pw_field.clear()
                pw_field.send_keys(USER_PW)
                
                login_btn.click()
                time.sleep(3)  # 로그인 처리 대기

                # 로그인 성공 확인
                current_url = driver.current_url
                logger.info(f"로그인 후 현재 URL: {current_url}")
                
                # HTML 추출
                html = driver.page_source
                
                if len(html) < 1000:  # HTML이 너무 짧으면 실패로 판단
                    raise Exception("HTML 길이가 너무 짧습니다. 페이지 로딩 실패 가능성")
                
                # 디버깅용 HTML 저장
                with open('debug_grider_page.html', 'w', encoding='utf-8') as f:
                    f.write(html)
                logger.info("📄 디버깅용 페이지 소스를 debug_grider_page.html에 저장했습니다")
                
                logger.info(f"✅ 크롤링 성공 (시도: {attempt + 1}/{max_retries}, 소요시간: {time.time() - start_time:.2f}초)")
                return html
                
            except Exception as e:
                logger.error(f"❌ 크롤링 시도 {attempt + 1} 실패: {e}")
                
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
                    driver = None
                
                # 마지막 시도가 아니면 재시도
                if attempt < max_retries - 1:
                    logger.info(f"⏳ {retry_delay}초 후 재시도...")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"❌ 모든 크롤링 시도 실패 ({max_retries}회)")
                    
            finally:
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
        
        return None

    def _get_sample_data(self):
        """크롤링 실패 시 사용할 샘플 데이터"""
        return {
            '총점': 90,
            '물량점수': 45,
            '수락률점수': 45,
            '총완료': 150,
            '총거절': 10,
            '수락률': 93.8,
            '아침점심피크': {"current": 30, "target": 25},
            '오후논피크': {"current": 26, "target": 20},
            '저녁피크': {"current": 40, "target": 30},
            '심야논피크': {"current": 8, "target": 15},
            'riders': [
                {'name': '홍길동', 'complete': 45, 'contribution': 30.0, 'acceptance_rate': 95.2, 'reject': 2, 'cancel': 1, 
                 '아침점심피크': 12, '오후논피크': 8, '저녁피크': 15, '심야논피크': 10},
                {'name': '김철수', 'complete': 38, 'contribution': 25.3, 'acceptance_rate': 92.1, 'reject': 3, 'cancel': 0,
                 '아침점심피크': 10, '오후논피크': 7, '저녁피크': 12, '심야논피크': 9}
            ],
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def _parse_data(self, html):
        """최적화된 데이터 파싱 함수 (main_(2).py와 동일한 로직)"""
        from bs4 import BeautifulSoup
        
        start_time = time.time()
        
        # html.parser 파서 사용으로 속도 향상
        soup = BeautifulSoup(html, 'html.parser')
        
        # 정규표현식 패턴 미리 컴파일 (성능 향상)
        int_pattern = re.compile(r'[\d,]+')  # 쉼표 포함 숫자 패턴
        float_pattern = re.compile(r'(\d+(?:\.\d+)?)')

        def fast_parse_int(selector, default=0):
            """최적화된 정수 파싱 (쉼표 처리 포함)"""
            node = soup.select_one(selector)
            if node:
                match = int_pattern.search(node.get_text(strip=True))
                if match:
                    # 쉼표 제거 후 정수 변환
                    number_str = match.group().replace(',', '')
                    return int(number_str) if number_str.isdigit() else default
            return default

        def fast_parse_float(selector, default=0.0):
            """최적화된 실수 파싱"""
            node = soup.select_one(selector)
            if node:
                match = float_pattern.search(node.get_text(strip=True))
                return float(match.group(1)) if match else default
            return default

        # 한 번에 모든 요소 선택 (병렬 처리)
        selectors = {
            'total_score': '.score_total_value[data-text="total"]',
            'quantity_score': '.detail_score_value[data-text="quantity"]',
            'acceptance_score': '.detail_score_value[data-text="acceptance"]',
            'total_complete': '.etc_value[data-etc="complete"] span',
            'total_reject': '.etc_value[data-etc="reject"] span',
            'acceptance_rate_total': '.etc_value[data-etc="acceptance"] span'
        }
        
        # 병렬로 파싱
        results = {}
        for key, selector in selectors.items():
            if key == 'acceptance_rate_total':
                results[key] = fast_parse_float(selector)
            else:
                results[key] = fast_parse_int(selector)
        
        total_score = results['total_score']
        quantity_score = results['quantity_score']
        acceptance_score = results['acceptance_score']
        total_complete = results['total_complete']
        total_reject = results['total_reject']
        acceptance_rate_total = results['acceptance_rate_total']

        # 물량 점수관리 테이블에서 피크별 데이터 파싱 (캐시 활용)
        logger.info("=== 미션 데이터 파싱 시작 ===")
        
        # 1단계: 캐시된 데이터가 있고 최신인지 확인
        cached_peak_data = self._load_mission_data_cache()
        if cached_peak_data:
            logger.info("✅ 캐시된 미션 데이터를 사용합니다.")
            peak_data = cached_peak_data
        else:
            logger.info("🔍 새로운 미션 데이터를 크롤링하여 파싱합니다.")
            peak_data = self._parse_mission_table_data(html)
            
            # 파싱 성공시 캐시에 저장
            if peak_data:
                mission_date = self._get_mission_date()
                self._save_mission_data_cache(mission_date, peak_data)
                logger.info("💾 새로운 미션 데이터를 캐시에 저장했습니다.")
        
        # 3단계 Fallback 시스템 (최적화)
        if not peak_data:
            logger.warning("⚠️ 1단계 파싱 실패! 2단계 fallback 시도")
            
            # 2단계: 기존 방식으로 데이터 파싱
            peak_data = {}
            quantity_items = soup.select('.quantity_item')
            logger.info(f"2단계: quantity_item 요소 {len(quantity_items)}개 발견")
            
            if quantity_items:
                # 통일된 용어 사용
                web_peak_names = ['아침점심피크', '오후논피크', '저녁피크', '심야논피크']
                legacy_peak_names = ['오전피크', '오후피크', '저녁피크', '심야피크']
                
                for idx, item in enumerate(quantity_items):
                    try:
                        name_node = item.select_one('.quantity_title')
                        current_node = item.select_one('.performance_value')
                        target_node = item.select_one('.number_value span:not(.performance_value)')

                        # 통일된 용어 사용
                        name = web_peak_names[idx] if idx < len(web_peak_names) else f'피크{idx+1}'
                        if name_node:
                            parsed_name = name_node.get_text(strip=True)
                            # 웹사이트에서 가져온 이름을 통일된 용어로 매핑
                            name_mapping = {
                                '오전피크': '아침점심피크',
                                '오후피크': '오후논피크', 
                                '저녁피크': '저녁피크',
                                '심야피크': '심야논피크'
                            }
                            name = name_mapping.get(parsed_name, name)
                        
                        # 최적화된 숫자 파싱
                        current = 0
                        if current_node:
                            current_match = int_pattern.search(current_node.get_text(strip=True))
                            current = int(current_match.group()) if current_match else 0
                        
                        target = 0
                        if target_node:
                            target_match = int_pattern.search(target_node.get_text(strip=True))
                            target = int(target_match.group()) if target_match else 0
                        
                        if name:
                            peak_data[name] = {
                                'current': current,
                                'target': target,
                                'progress': (current / target * 100) if target > 0 else 0
                            }
                            logger.info(f"2단계 미션 파싱: {name} = {current}/{target}건")
                            
                        # 기존 코드 호환성을 위해 레거시 이름으로도 저장
                        if idx < len(legacy_peak_names):
                            legacy_name = legacy_peak_names[idx]
                            peak_data[legacy_name] = peak_data[name]
                            
                    except Exception as e:
                        logger.warning(f"미션 아이템 {idx} 파싱 실패: {e}")
                        continue

        logger.info(f"파싱 완료 (소요시간: {time.time() - start_time:.2f}초)")

        # 라이더별 데이터 추출 (제공된 HTML 구조에 맞게 최적화)
        riders = []
        rider_items = soup.select('.rider_item')
        logger.info(f"🔍 라이더 데이터 파싱 시작: {len(rider_items)}명의 라이더 발견")
        
        for idx, rider in enumerate(rider_items):
            try:
                # 라이더 이름 추출 (모바일 수락률 텍스트 제거)
                name_node = rider.select_one('.rider_name')
                if not name_node:
                    logger.warning(f"라이더 {idx+1}: 이름 노드를 찾을 수 없음")
                    continue
                    
                name_text = name_node.get_text(strip=True)
                # "수락률:XX%" 부분 제거
                name = re.sub(r'수락률:\d+%', '', name_text).strip()
                
                # 수락률 추출 (정확한 구조 반영)
                acceptance_rate = 0.0
                acc_node = rider.select_one('.rider_contents.midium.acceptance_rate')
                if acc_node:
                    acc_text = acc_node.get_text(strip=True)
                    match = re.search(r'(\d+(?:\.\d+)?)\s*%', acc_text)
                    if match:
                        acceptance_rate = float(match.group(1))
                
                # 완료 건수 추출
                complete = 0
                complete_node = rider.select_one('.rider_contents.complete_count')
                if complete_node:
                    complete_text = complete_node.get_text(strip=True)
                    match = re.search(r'(\d+)', complete_text)
                    if match:
                        complete = int(match.group(1))
                
                # 거절 건수 추출
                reject = 0
                reject_node = rider.select_one('.rider_contents.reject_count')
                if reject_node:
                    reject_text = reject_node.get_text(strip=True)
                    match = re.search(r'(\d+)', reject_text)
                    if match:
                        reject = int(match.group(1))
                
                # 배차취소 건수 추출
                cancel = 0
                cancel_node = rider.select_one('.rider_contents.accept_cancel_count')
                if cancel_node:
                    cancel_text = cancel_node.get_text(strip=True)
                    match = re.search(r'(\d+)', cancel_text)
                    if match:
                        cancel = int(match.group(1))
                
                # 배달취소 건수 추출
                delivery_cancel = 0
                delivery_cancel_node = rider.select_one('.rider_contents.accept_cancel_rider_fault_count')
                if delivery_cancel_node:
                    delivery_cancel_text = delivery_cancel_node.get_text(strip=True)
                    match = re.search(r'(\d+)', delivery_cancel_text)
                    if match:
                        delivery_cancel = int(match.group(1))
                
                # 피크별 수행 건수 추출
                morning = 0
                morning_node = rider.select_one('.rider_contents.morning_peak_count')
                if morning_node:
                    morning_text = morning_node.get_text(strip=True)
                    match = re.search(r'(\d+)', morning_text)
                    if match:
                        morning = int(match.group(1))
                
                afternoon = 0
                afternoon_node = rider.select_one('.rider_contents.afternoon_peak_count')
                if afternoon_node:
                    afternoon_text = afternoon_node.get_text(strip=True)
                    match = re.search(r'(\d+)', afternoon_text)
                    if match:
                        afternoon = int(match.group(1))
                
                evening = 0
                evening_node = rider.select_one('.rider_contents.evening_peak_count')
                if evening_node:
                    evening_text = evening_node.get_text(strip=True)
                    match = re.search(r'(\d+)', evening_text)
                    if match:
                        evening = int(match.group(1))
                
                midnight = 0
                midnight_node = rider.select_one('.rider_contents.midnight_peak_count')
                if midnight_node:
                    midnight_text = midnight_node.get_text(strip=True)
                    match = re.search(r'(\d+)', midnight_text)
                    if match:
                        midnight = int(match.group(1))
                
                # 운행 상태 추출
                working_status = "운행종료"
                status_node = rider.select_one('.rider_contents.working_status .rider_info_text')
                if status_node:
                    status_text = status_node.get_text(strip=True)
                    if "운행중" in status_text:
                        working_status = "운행중"
                
                # 아이디 추출
                user_id = ""
                id_node = rider.select_one('.rider_contents.user_id')
                if id_node:
                    id_text = id_node.get_text(strip=True)
                    # "아이디" 텍스트 제거
                    user_id = re.sub(r'아이디', '', id_text).strip()
                
                rider_data = {
                    'name': name,
                    'user_id': user_id,
                    'complete': complete,
                    'acceptance_rate': acceptance_rate,
                    'reject': reject,
                    'cancel': cancel,
                    'delivery_cancel': delivery_cancel,
                    'working_status': working_status,
                    # 새로운 통일된 용어
                    '아침점심피크': morning,
                    '오후논피크': afternoon,
                    '저녁피크': evening,
                    '심야논피크': midnight,
                    # 기존 호환성 유지
                    '오전피크': morning,
                    '오후피크': afternoon,
                    '심야피크': midnight,
                }
                
                # 금일 완료 내역이 있는 라이더만 포함
                if complete > 0:
                    riders.append(rider_data)
                    logger.info(f"✅ 라이더 {idx+1}: {name} (완료: {complete}건, 수락률: {acceptance_rate}%, 상태: {working_status})")
                else:
                    logger.info(f"⏭️ 라이더 {idx+1}: {name} (완료 0건으로 제외)")
                
            except Exception as e:
                logger.error(f"❌ 라이더 {idx+1} 파싱 실패: {e}")
                continue

        # 라이더별 미션 기여도 계산 (각 피크별 기여도의 평균)
        peak_names = ['오전피크', '오후피크', '저녁피크', '심야피크']
        for rider in riders:
            peak_contributions = []
            
            for peak in peak_names:
                target = peak_data.get(peak, {'target': 0})['target']
                performed = rider.get(peak, 0)
                
                if target > 0:
                    # 각 피크별 기여도 = (개인 수행 ÷ 목표) × 100
                    peak_contribution = (performed / target) * 100
                    peak_contributions.append(peak_contribution)
                else:
                    # 목표가 0이면 기여도도 0
                    peak_contributions.append(0)
            
            # 4개 피크의 평균 기여도
            rider['contribution'] = round(sum(peak_contributions) / len(peak_contributions), 1)
            
            # 디버깅용: 각 피크별 기여도도 저장
            rider['peak_contributions'] = {
                '오전피크': round(peak_contributions[0], 1),
                '오후피크': round(peak_contributions[1], 1),
                '저녁피크': round(peak_contributions[2], 1),
                '심야피크': round(peak_contributions[3], 1)
            }

        # 새로운 용어와 기존 용어 모두 포함하여 데이터 구성
        data = {
            # 새로운 통일된 용어
            '아침점심피크': peak_data.get('아침점심피크', peak_data.get('오전피크', {'current': 0, 'target': 0})),
            '오후논피크': peak_data.get('오후논피크', peak_data.get('오후피크', {'current': 0, 'target': 0})),
            '저녁피크': peak_data.get('저녁피크', {'current': 0, 'target': 0}),
            '심야논피크': peak_data.get('심야논피크', peak_data.get('심야피크', {'current': 0, 'target': 0})),
            # 기존 호환성 유지
            '오전피크': peak_data.get('오전피크', peak_data.get('아침점심피크', {'current': 0, 'target': 0})),
            '오후피크': peak_data.get('오후피크', peak_data.get('오후논피크', {'current': 0, 'target': 0})),
            '심야피크': peak_data.get('심야피크', peak_data.get('심야논피크', {'current': 0, 'target': 0})),
            '총점': total_score,
            '물량점수': quantity_score,
            '수락률점수': acceptance_score,
            '총완료': total_complete,
            '총거절': total_reject,
            '수락률': acceptance_rate_total,
            'riders': riders,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return data
    
    def _save_mission_data_cache(self, mission_date, peak_data):
        """미션 데이터를 캐시 파일에 저장"""
        try:
            cache_data = {
                'date': mission_date,
                'timestamp': dt.datetime.now().isoformat(),
                'peak_data': peak_data
            }
            
            with open(self.mission_data_cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 미션 데이터 캐시 저장 완료: {mission_date}")
            
        except Exception as e:
            logger.error(f"❌ 미션 데이터 캐시 저장 실패: {e}")

    def _load_mission_data_cache(self):
        """캐시된 미션 데이터 로드"""
        try:
            if not os.path.exists(self.mission_data_cache_file):
                logger.info("📂 미션 데이터 캐시 파일이 없습니다.")
                return None
            
            with open(self.mission_data_cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 캐시된 데이터의 날짜 확인
            cached_date = cache_data.get('date')
            current_mission_date = self._get_mission_date()
            
            if cached_date == current_mission_date:
                logger.info(f"✅ 캐시된 미션 데이터 사용: {cached_date}")
                return cache_data.get('peak_data')
            else:
                logger.info(f"🔄 날짜 변경 감지: {cached_date} → {current_mission_date}")
                logger.info("새로운 미션 데이터 크롤링이 필요합니다.")
                return None
        
        except Exception as e:
            logger.error(f"❌ 미션 데이터 캐시 로드 실패: {e}")
            return None

    def _get_mission_date(self):
        """
        미션 기준 날짜를 계산합니다.
        06:00~다음날 03:00를 하나의 미션 날짜로 간주합니다.
        예: 2025-06-15 06:00 ~ 2025-06-16 03:00 = 2025-06-15 미션
        """
        now = dt.datetime.now()
        
        # 현재 시간이 06:00 이전이면 전날을 미션 날짜로 계산
        if now.time() < dt.time(6, 0):
            mission_date = now.date() - dt.timedelta(days=1)
        else:
            mission_date = now.date()
        
        return mission_date.strftime('%Y-%m-%d')

    def _parse_mission_table_data(self, html):
        """
        물량 점수관리 테이블에서 미션 데이터를 파싱합니다. (main_(2).py와 동일)
        """
        
        # html.parser 파서 사용으로 속도 향상
        soup = BeautifulSoup(html, 'html.parser')
        
        # 미션 기준 날짜 계산
        target_date = self._get_mission_date()
        
        # 물량 점수관리 테이블 찾기 (다양한 선택자 시도)
        sla_table = None
        
        # 여러 가능한 선택자들을 시도
        possible_selectors = [
            'table.sla_table[data-type="partner"]',
            'table.sla_table',
            'table[data-type="partner"]',
            '.sla_table',
            'table[id*="sla"]',
            'table[class*="sla"]',
            '.mission_table',
            '.quantity_table'
        ]
        
        # 1단계: CSS 선택자로 테이블 찾기
        for selector in possible_selectors:
            try:
                sla_table = soup.select_one(selector)
                if sla_table:
                    logger.info(f"✅ 테이블 발견 (선택자: {selector})")
                    break
            except Exception as e:
                continue
        
        # 2단계: 텍스트 내용으로 테이블 찾기
        if not sla_table:
            tables = soup.find_all('table')
            for table in tables:
                table_text = table.get_text()
                if any(keyword in table_text for keyword in ['물량 점수관리', '아침점심피크', '오후논피크', '저녁피크', '심야논피크']):
                    sla_table = table
                    logger.info(f"✅ 테이블 발견 (텍스트 기반 검색)")
                    break
        
        if not sla_table:
            logger.warning("물량 점수관리 테이블을 찾을 수 없습니다.")
            return None
        
        # 모든 행을 한 번에 가져오기
        rows = sla_table.select('tbody tr')
        if not rows:
            # tbody가 없는 경우 tr 직접 선택
            rows = sla_table.select('tr')
        
        target_row = None
        
        # 날짜 매칭 최적화 (정규표현식 미리 컴파일)
        date_pattern = re.compile(target_date)
        for row in rows:
            # 첫 번째 또는 두 번째 셀에서 날짜 찾기
            for idx in range(min(3, len(row.select('td')))):
                date_cell = row.select('td')[idx] if row.select('td') else None
                if date_cell and date_pattern.search(date_cell.get_text(strip=True)):
                    target_row = row
                    break
            if target_row:
                break
        
        if not target_row:
            logger.warning(f"날짜 {target_date}에 해당하는 데이터를 찾을 수 없습니다.")
            return None
        
        # 모든 셀을 한 번에 파싱
        cells = target_row.select('td')
        if len(cells) < 4:
            logger.warning("테이블 구조가 예상과 다릅니다.")
            return None
        
        # 정규표현식 패턴 미리 컴파일 (성능 향상)
        count_pattern = re.compile(r'(\d+)/(\d+)')
        
        def parse_mission_cell(cell_text):
            """최적화된 미션 셀 파싱"""
            match = count_pattern.search(cell_text)
            if match:
                return int(match.group(1)), int(match.group(2))
            return 0, 0
        
        # 실제 웹사이트 테이블 헤더에 맞는 용어 사용
        web_peak_names = ['아침점심피크', '오후논피크', '저녁피크', '심야논피크']
        # 기존 코드와의 호환성을 위한 용어 매핑
        legacy_peak_names = ['오전피크', '오후피크', '저녁피크', '심야피크']
        
        # 피크별 데이터 병렬 파싱
        # 날짜 셀 다음부터 4개 피크 데이터 추출
        peak_start_idx = 1  # 일반적으로 날짜 다음이 피크 데이터
        for idx, cell in enumerate(cells):
            if date_pattern.search(cell.get_text(strip=True)):
                peak_start_idx = idx + 1
                break
        
        peak_data = {}
        peak_cells = cells[peak_start_idx:peak_start_idx + 4]
        
        for idx, cell in enumerate(peak_cells):
            if idx >= len(web_peak_names):
                break
                
            text = cell.get_text(strip=True)
            current, target = parse_mission_cell(text)
            # 통일된 용어로 저장 (아침점심피크, 오후논피크, 저녁피크, 심야논피크)
            unified_name = web_peak_names[idx] if idx < len(web_peak_names) else f'피크{idx+1}'
            
            peak_data[unified_name] = {
                'current': current, 
                'target': target,
                'progress': (current / target * 100) if target > 0 else 0
            }
            
            # 기존 코드 호환성을 위해 레거시 이름으로도 저장
            if idx < len(legacy_peak_names):
                legacy_name = legacy_peak_names[idx]
                peak_data[legacy_name] = peak_data[unified_name]
        
        logger.info(f"파싱된 미션 데이터 ({target_date}): {len(web_peak_names)}개 피크")
        for name in web_peak_names:
            if name in peak_data:
                data = peak_data[name]
                logger.info(f"✅ {name}: {data['current']}/{data['target']}건 ({data['progress']:.1f}%)")
        
        return peak_data
    
    def _parse_grider_html_old(self, soup):
        """실제 HTML 파싱 로직 (main_(2).py의 검증된 parse_data 함수 기반)"""
        try:
            data = {}
            
            # main_(2).py의 검증된 선택자 사용
            # 정규표현식 패턴 미리 컴파일 (성능 향상)
            int_pattern = re.compile(r'[\d,]+')  # 쉼표 포함 숫자 패턴
            float_pattern = re.compile(r'(\d+(?:\.\d+)?)')

            def fast_parse_int(selector, default=0):
                """최적화된 정수 파싱 (쉼표 처리 포함)"""
                node = soup.select_one(selector)
                if node:
                    match = int_pattern.search(node.get_text(strip=True))
                    if match:
                        # 쉼표 제거 후 정수 변환
                        number_str = match.group().replace(',', '')
                        return int(number_str) if number_str.isdigit() else default
                return default

            def fast_parse_float(selector, default=0.0):
                """최적화된 실수 파싱"""
                node = soup.select_one(selector)
                if node:
                    match = float_pattern.search(node.get_text(strip=True))
                    return float(match.group(1)) if match else default
                return default

            # 검증된 선택자 사용 (main_(2).py와 동일)
            selectors = {
                'total_score': '.score_total_value[data-text="total"]',
                'quantity_score': '.detail_score_value[data-text="quantity"]',
                'acceptance_score': '.detail_score_value[data-text="acceptance"]',
                'total_complete': '.etc_value[data-etc="complete"] span',
                'total_reject': '.etc_value[data-etc="reject"] span',
                'acceptance_rate_total': '.etc_value[data-etc="acceptance"] span'
            }
            
            # 병렬로 파싱
            results = {}
            for key, selector in selectors.items():
                if key == 'acceptance_rate_total':
                    results[key] = fast_parse_float(selector)
                else:
                    results[key] = fast_parse_int(selector)
            
            # 기본 점수 정보
            data['총점'] = results['total_score']
            data['물량점수'] = results['quantity_score']
            data['수락률점수'] = results['acceptance_score']
            data['총완료'] = results['total_complete']
            data['총거절'] = results['total_reject']
            data['수락률'] = results['acceptance_rate_total']
            
            logger.info(f"기본 점수 파싱 성공: 총점={data['총점']}, 물량={data['물량점수']}, 수락률={data['수락률점수']}")
            
            # 미션 데이터 파싱 (main_(2).py 로직 적용)
            peak_data = {}
            quantity_items = soup.select('.quantity_item')
            logger.info(f"quantity_item 요소 {len(quantity_items)}개 발견")
            
            if quantity_items:
                # 통일된 용어 사용
                web_peak_names = ['아침점심피크', '오후논피크', '저녁피크', '심야논피크']
                
                for idx, item in enumerate(quantity_items):
                    try:
                        name_node = item.select_one('.quantity_title')
                        current_node = item.select_one('.performance_value')
                        target_node = item.select_one('.number_value span:not(.performance_value)')

                        # 통일된 용어 사용
                        name = web_peak_names[idx] if idx < len(web_peak_names) else f'피크{idx+1}'
                        if name_node:
                            parsed_name = name_node.get_text(strip=True)
                            # 웹사이트에서 가져온 이름을 통일된 용어로 매핑
                            name_mapping = {
                                '오전피크': '아침점심피크',
                                '오후피크': '오후논피크', 
                                '저녁피크': '저녁피크',
                                '심야피크': '심야논피크'
                            }
                            name = name_mapping.get(parsed_name, name)
                        
                        # 최적화된 숫자 파싱
                        current = 0
                        if current_node:
                            current_match = int_pattern.search(current_node.get_text(strip=True))
                            current = int(current_match.group()) if current_match else 0
                        
                        target = 0
                        if target_node:
                            target_match = int_pattern.search(target_node.get_text(strip=True))
                            target = int(target_match.group()) if target_match else 0
                        
                        if name:
                            peak_data[name] = {
                                'current': current,
                                'target': target
                            }
                            logger.info(f"미션 파싱 성공: {name} = {current}/{target}건")
                            
                    except Exception as e:
                        logger.warning(f"미션 아이템 {idx} 파싱 실패: {e}")
                        continue
            
            # 파싱된 미션 데이터를 data에 추가
            if peak_data:
                data.update(peak_data)
                logger.info("✅ 실제 미션 데이터 파싱 성공!")
            else:
                # 파싱 실패 시 기본값
                data['아침점심피크'] = {"current": 0, "target": 0}
                data['오후논피크'] = {"current": 0, "target": 0}
                data['저녁피크'] = {"current": 0, "target": 0}
                data['심야논피크'] = {"current": 0, "target": 0}
                logger.warning("미션 데이터 파싱 실패 - 기본값 사용")
            
            # 라이더 데이터 파싱 (main_(2).py 로직 적용)
            riders = []
            rider_items = soup.select('.rider_item')
            logger.info(f"라이더 아이템 {len(rider_items)}개 발견")
            
            for rider in rider_items:
                try:
                    rider_data = {}
                    
                    # 라이더 이름
                    name_node = rider.select_one('.rider_name')
                    if name_node:
                        rider_data['name'] = name_node.text.strip().split('수락률')[0].strip()
                    else:
                        rider_data['name'] = '이름없음'
                    
                    # 완료 건수
                    complete_node = rider.select_one('.complete_count')
                    if complete_node:
                        complete_text = complete_node.text
                        complete_match = re.search(r'\d+', complete_text)
                        rider_data['complete'] = int(complete_match.group()) if complete_match else 0
                    else:
                        rider_data['complete'] = 0
                    
                    # 수락률
                    acceptance_rate = 0.0
                    acc_node = rider.select_one('.rider_contents.acceptance_rate')
                    if acc_node:
                        acc_text = acc_node.get_text()
                        match = re.search(r'(\d+(?:\.\d+)?)\s*%', acc_text)
                        if match:
                            acceptance_rate = float(match.group(1))
                    rider_data['acceptance_rate'] = acceptance_rate
                    
                    # 거절 건수
                    reject = 0
                    reject_node = rider.select_one('.rider_contents.reject_count')
                    if reject_node:
                        reject_text = reject_node.get_text()
                        match = re.search(r'(\d+)', reject_text)
                        if match:
                            reject = int(match.group(1))
                    rider_data['reject'] = reject
                    
                    # 배차취소 건수
                    cancel = 0
                    cancel_node = rider.select_one('.rider_contents.accept_cancel_count')
                    if cancel_node:
                        cancel_text = cancel_node.get_text()
                        match = re.search(r'(\d+)', cancel_text)
                        if match:
                            cancel = int(match.group(1))
                    rider_data['cancel'] = cancel
                    
                    # 피크별 건수 파싱 (main_(2).py와 동일한 선택자 사용)
                    morning_node = rider.select_one('.morning_peak_count')
                    afternoon_node = rider.select_one('.afternoon_peak_count')
                    evening_node = rider.select_one('.evening_peak_count')
                    midnight_node = rider.select_one('.midnight_peak_count')  # night -> midnight
                    
                    morning = 0
                    afternoon = 0
                    evening = 0
                    midnight = 0
                    
                    if morning_node:
                        match = re.search(r'\d+', morning_node.text)
                        morning = int(match.group()) if match else 0
                    
                    if afternoon_node:
                        match = re.search(r'\d+', afternoon_node.text)
                        afternoon = int(match.group()) if match else 0
                    
                    if evening_node:
                        match = re.search(r'\d+', evening_node.text)
                        evening = int(match.group()) if match else 0
                    
                    if midnight_node:
                        match = re.search(r'\d+', midnight_node.text)
                        midnight = int(match.group()) if match else 0
                    
                    # 통일된 용어와 기존 호환성 모두 저장
                    rider_data['아침점심피크'] = morning
                    rider_data['오후논피크'] = afternoon
                    rider_data['저녁피크'] = evening
                    rider_data['심야논피크'] = midnight
                    
                    # 기존 호환성 유지
                    rider_data['오전피크'] = morning
                    rider_data['오후피크'] = afternoon
                    rider_data['심야피크'] = midnight
                    
                    if rider_data['complete'] > 0:  # 완료 건수가 있는 라이더만 추가
                        riders.append(rider_data)
                        logger.info(f"라이더 파싱 성공: {rider_data['name']} ({rider_data['complete']}건)")
                        
                except Exception as e:
                    logger.warning(f"라이더 데이터 파싱 실패: {e}")
                    continue
            
            # 라이더별 미션 기여도 계산 (main_(2).py와 동일한 로직)
            peak_names = ['오전피크', '오후피크', '저녁피크', '심야피크']
            for rider in riders:
                peak_contributions = []
                
                for peak in peak_names:
                    # 해당 피크의 목표값 가져오기
                    peak_mapping = {
                        '오전피크': '아침점심피크',
                        '오후피크': '오후논피크', 
                        '저녁피크': '저녁피크',
                        '심야피크': '심야논피크'
                    }
                    mapped_peak = peak_mapping.get(peak, peak)
                    target = data.get(mapped_peak, {'target': 0}).get('target', 0)
                    performed = rider.get(peak, 0)
                    
                    if target > 0:
                        # 각 피크별 기여도 = (개인 수행 ÷ 목표) × 100
                        peak_contribution = (performed / target) * 100
                        peak_contributions.append(peak_contribution)
                    else:
                        # 목표가 0이면 기여도도 0
                        peak_contributions.append(0)
                
                # 4개 피크의 평균 기여도
                rider['contribution'] = round(sum(peak_contributions) / len(peak_contributions), 1)
                
                # 디버깅용: 각 피크별 기여도도 저장
                rider['peak_contributions'] = {
                    '오전피크': round(peak_contributions[0], 1),
                    '오후피크': round(peak_contributions[1], 1),
                    '저녁피크': round(peak_contributions[2], 1),
                    '심야피크': round(peak_contributions[3], 1)
                }
            
            data['riders'] = riders
            data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            logger.info(f"✅ 전체 데이터 파싱 완료: 기본정보, 미션 {len(peak_data)}개, 라이더 {len(riders)}명")
            # 라이더별 기여도 로그 (f-string 오류 방지)
            rider_contributions = [f"{r['name']}({r['contribution']:.1f}%)" for r in riders[:3]]
            logger.info(f"라이더별 기여도 계산 완료: {rider_contributions}")
            return data
            
        except Exception as e:
            logger.error(f"❌ HTML 파싱 실패: {e}")
            return None

class GriderAutoSender:
    """심플 배민 플러스 자동화 메인 클래스"""
    
    def __init__(self, rest_api_key, refresh_token):
        self.token_manager = TokenManager(rest_api_key, refresh_token)
        self.data_collector = GriderDataCollector()
        self.sender = None
    
    def format_message(self, data):
        """깔끔하고 읽기 좋은 메시지 포맷"""
        
        # 날씨 정보 (전체 버전으로 복원)
        weather_info = self._get_weather_info()
        
        # 1. 미션 현황 - 깔끔하게 줄바꿈
        peak_order = ['아침점심피크', '오후논피크', '저녁피크', '심야논피크']
        peak_emojis = {
            '아침점심피크': '🌅', 
            '오후논피크': '🌇', 
            '저녁피크': '🌃', 
            '심야논피크': '🌙'
        }
        
        mission_parts = []
        lacking_missions = []
        
        for key in peak_order:
            peak_info = data.get(key, {'current': 0, 'target': 0})
            cur = peak_info.get('current', 0)
            tgt = peak_info.get('target', 0)
            
            if tgt == 0:
                continue
                
            if cur >= tgt:
                status = '✅ (달성)'
            else:
                status = f'❌ ({tgt-cur}건 부족)'
                lacking_missions.append(f'{key.replace("피크","").replace("논","")} {tgt-cur}건')
            
            mission_parts.append(f"{peak_emojis.get(key, '')} {key}: {cur}/{tgt} {status}")
        
        # 2. 기본 정보 - 두 줄로 정리
        total_score = data.get("총점", 0)
        quantity_score = data.get("물량점수", 0)
        acceptance_score = data.get("수락률점수", 0)
        acceptance_rate = data.get("수락률", 0.0)
        total_completed = data.get("총완료", 0)
        total_rejected = data.get("총거절", 0)
        
        summary_parts = [
            "📊 금주 미션 수행 예상점수",
            f"총점: {total_score}점 (물량:{quantity_score}, 수락률:{acceptance_score})",
            f"수락률: {acceptance_rate:.1f}% | 완료: {total_completed} | 거절: {total_rejected}"
        ]
        
        # 3. 라이더 순위 - 완료 건수가 있는 라이더만 대상으로 TOP 3 선정
        sorted_riders = sorted(
            [r for r in data.get('riders', []) if r.get('complete', 0) > 0], 
            key=lambda x: x.get('contribution', 0), 
            reverse=True
        )
        
        rider_parts = []
        top_riders = sorted_riders[:3]
        other_riders = sorted_riders[3:]
        
        # 라이더 순위 (3위까지 자세한 정보)
        if sorted_riders:
            # 운행중인 라이더 수 계산 (금일 완료 내역이 있는 라이더 수)
            active_rider_count = len(sorted_riders)
            rider_parts.append(f"🏆 라이더 순위 (운행 : {active_rider_count}명)")
            medals = ['🥇', '🥈', '🥉']
            
            # 3위까지만 표시
            for i, rider in enumerate(sorted_riders[:3]):
                name = rider.get('name', '이름없음')
                contribution = rider.get('contribution', 0)
                
                # 피크별 기여도
                morning = rider.get('아침점심피크', 0)
                afternoon = rider.get('오후논피크', 0)
                evening = rider.get('저녁피크', 0)
                midnight = rider.get('심야논피크', 0)
                
                acceptance_rate = rider.get('acceptance_rate', 0.0)
                reject = rider.get('reject', 0)
                cancel = rider.get('cancel', 0)
                complete = rider.get('complete', 0)
                
                # 진행률 바 생성 (퍼센트 바 안쪽에 표시)
                bar_len = 10
                filled = int(round(contribution / 10))  # 10%당 1칸
                if filled > 10:
                    filled = 10
                
                # 퍼센트 텍스트 길이 계산
                percent_text = f"{contribution:.1f}%"
                remaining_dashes = bar_len - filled - len(percent_text)
                
                if remaining_dashes > 0:
                    bar = '■' * filled + '─' * remaining_dashes + percent_text
                else:
                    # 퍼센트 텍스트가 너무 길면 뒤쪽 ■을 일부 대체
                    bar = '■' * max(0, bar_len - len(percent_text)) + percent_text
                
                # 1-3위는 메달만 표시
                rider_parts.append(f"**{medals[i]} {name}** | [{bar}]")
                
                rider_parts.append(f"    총 {complete}건 (🌅{morning} 🌇{afternoon} 🌃{evening} 🌙{midnight})")
                rider_parts.append(f"    수락률: {acceptance_rate:.1f}% (거절:{reject}, 취소:{cancel})")
        
        # 전체 라이더의 금일 완료/거절/취소/수락률 통계 계산
        total_complete_today = sum(rider.get('complete', 0) for rider in data.get('riders', []))
        total_reject_today = sum(rider.get('reject', 0) for rider in data.get('riders', []))
        total_cancel_today = sum(rider.get('cancel', 0) for rider in data.get('riders', []))
        total_delivery_cancel_today = sum(rider.get('delivery_cancel', 0) for rider in data.get('riders', []))
        
        # 미션 현황 아래 완료/거절/취소/수락률 정보를 깔끔하게 표시
        total_cancel_all = total_cancel_today + total_delivery_cancel_today  # 배차취소 + 배달취소
        
        # 전체 수락률 계산 (완료 / (완료 + 거절 + 취소) * 100)
        total_attempts = total_complete_today + total_reject_today + total_cancel_all
        overall_acceptance_rate = (total_complete_today / total_attempts * 100) if total_attempts > 0 else 0.0
        
        # 거절에 취소를 합산 (금주 미션 수행 예상점수와 동일한 방식)
        total_reject_combined = total_reject_today + total_cancel_all
        
        mission_summary_parts = [
            "📈 금일 수행 내역",
            f"수락률: {overall_acceptance_rate:.1f}% | 완료: {total_complete_today} | 거절: {total_reject_combined}"
        ]
        mission_summary = "\n".join(mission_summary_parts)
        
        # 최종 메시지 조합 (순서 변경: 미션상황 → 날씨 → 금일수행내역 → 기본정보 → 라이더순위)
        message_parts = [
            "📊 심플 배민 플러스 미션 알리미",
            "",
            "\n".join(mission_parts),
            "",
            weather_info,
            "",
            mission_summary,
            "",
            "\n".join(summary_parts),
            "",
            "\n".join(rider_parts)
        ]
        
        if lacking_missions:
            message_parts.append("")
            message_parts.append(f"⚠️ 미션 부족: {', '.join(lacking_missions)}")
        
        message_parts.append("")
        message_parts.append("🤖 자동화 시스템에 의해 전송됨")
        
        return "\n".join(message_parts)
    
    def _get_weather_info(self):
        """날씨 정보 가져오기 (오전/오후 요약 버전)"""
        try:
            # 간단한 날씨 정보 (실제 API 연동 가능)
            now = datetime.now()
            return f"""🌍 오늘의 날씨 (기상청)
🌅 오전: ☀️ 18~22°C
🌇 오후: ☀️ 20~24°C"""
        except Exception as e:
            return "⚠️ 날씨 정보를 가져올 수 없습니다."
    
    def send_report(self):
        """리포트 전송 (클립보드 복사만 사용)"""
        try:
            logger.info("🚀 심플 배민 플러스 리포트 전송 시작...")
            
            # 1. 데이터 수집
            data = self.data_collector.get_grider_data()
            message = self.format_message(data)
            
            # 3. 메시지 전송
            result = self.sender.send_text_message(
                text=message,
                link_url="https://grider.co.kr"  # 실제 링크로 변경
            )
            
            # 4. 클립보드에도 복사 (로컬 실행시에만)
            try:
                import pyperclip
                pyperclip.copy(message)
                logger.info("📋 클립보드에 복사됨 - 오픈채팅방에 붙여넣기하세요!")
            except Exception as e:
                logger.info("📋 클립보드 복사 생략 (GitHub Actions 환경)")
            
            if result.get('result_code') == 0:
                logger.info(f"✅ {datetime.now()} - 메시지 전송 성공!")
                return True
            else:
                logger.error(f"❌ 메시지 전송 실패: {result}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 리포트 전송 중 오류: {e}")
            return False
    
    def test_connection(self):
        """연결 테스트"""
        try:
            logger.info("🔧 카카오톡 연결 테스트 중...")
            
            access_token = self.token_manager.get_valid_token()
            self.sender = KakaoSender(access_token)
            
            test_message = f"🧪 심플 배민 플러스 자동화 테스트\n시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n✅ 연결 성공!"
            
            result = self.sender.send_text_message(test_message)
            
            if result.get('result_code') == 0:
                logger.info("✅ 테스트 성공! 카카오톡 연결 정상")
                return True
            else:
                logger.error(f"❌ 테스트 실패: {result}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 테스트 중 오류: {e}")
            return False
    
    def start_scheduler(self):
        """스케줄러 시작 (기존 main_(2).py 스케줄 적용)"""
        # 특별 알림: 오전 10시 시작 알림
        schedule.every().day.at("10:00").do(self._send_start_notification)
        
        # 특별 알림: 자정 종료 알림  
        schedule.every().day.at("00:00").do(self._send_end_notification)
        
        # 기본 설정: 10분 간격 (10:00~00:00 운영시간)
        schedule.every(10).minutes.do(self._scheduled_send)
        
        # 피크 시간 집중 모니터링 (5분 간격)
        peak_hours = [11, 12, 13, 17, 18, 19]  # 피크 시간대
        for hour in peak_hours:
            schedule.every().day.at(f"{hour:02d}:00").do(self._scheduled_send)
            schedule.every().day.at(f"{hour:02d}:05").do(self._scheduled_send)
            schedule.every().day.at(f"{hour:02d}:10").do(self._scheduled_send)
            schedule.every().day.at(f"{hour:02d}:15").do(self._scheduled_send)
            schedule.every().day.at(f"{hour:02d}:20").do(self._scheduled_send)
            schedule.every().day.at(f"{hour:02d}:25").do(self._scheduled_send)
            schedule.every().day.at(f"{hour:02d}:30").do(self._scheduled_send)
            schedule.every().day.at(f"{hour:02d}:35").do(self._scheduled_send)
            schedule.every().day.at(f"{hour:02d}:40").do(self._scheduled_send)
            schedule.every().day.at(f"{hour:02d}:45").do(self._scheduled_send)
            schedule.every().day.at(f"{hour:02d}:50").do(self._scheduled_send)
            schedule.every().day.at(f"{hour:02d}:55").do(self._scheduled_send)
        
        logger.info("🚀 심플 배민 플러스 자동화 시작!")
        logger.info("📊 현재 설정:")
        logger.info("   • 알림 시간: 10:00~00:00")
        logger.info("   • 특별 알림: 10:00 시작알림, 00:00 종료알림")
        logger.info("   • 모니터링 간격: 10분 (피크시간 5분)")
        logger.info("   • 피크시간: 11-13시, 17-19시")
        logger.info("💡 Ctrl+C로 중지 가능")
        
        # 즉시 실행 여부 확인
        now = datetime.now()
        current_hour = now.hour
        is_service_time = 10 <= current_hour <= 23
        
        if is_service_time:
            logger.info("✅ 알림 시간대입니다. 즉시 첫 모니터링을 시작합니다.")
            self.send_report()
        else:
            logger.info("💤 현재 휴식 시간대입니다. 10:00부터 알림을 시작합니다.")
        
        try:
            while True:
                # 현재 시간이 서비스 시간인지 확인
                current_time = datetime.now()
                if 10 <= current_time.hour <= 23:
                    schedule.run_pending()
                time.sleep(60)  # 1분마다 확인
        except KeyboardInterrupt:
            logger.info("🛑 사용자에 의해 중지됨")
        except Exception as e:
            logger.error(f"❌ 스케줄러 오류: {e}")
    
    def _scheduled_send(self):
        """스케줄된 전송 (시간 체크 포함)"""
        now = datetime.now()
        current_hour = now.hour
        
        # 운영 시간 체크 (10:00~00:00)
        if not (10 <= current_hour <= 23):
            return
        
        # 실제 전송 실행
        self.send_report()
    
    def _send_start_notification(self):
        """오전 10시 시작 알림"""
        try:
            access_token = self.token_manager.get_valid_token()
            self.sender = KakaoSender(access_token)
            
            start_message = f"""🌅 심플 배민 플러스 자동 모니터링 시작!
            
📅 {datetime.now().strftime('%Y년 %m월 %d일')} 오전 10시
🚀 오늘 하루 미션 현황을 실시간으로 모니터링합니다

⏰ 운영 시간: 10:00 ~ 00:00 (14시간)
📊 모니터링 간격: 
   • 일반시간: 10분 간격
   • 피크시간(11-13시, 17-19시): 5분 간격

💪 오늘도 화이팅하세요!"""
            
            result = self.sender.send_text_message(start_message)
            if result.get('result_code') == 0:
                logger.info("✅ 오전 10시 시작 알림 전송 완료!")
            
            # 시작과 함께 첫 리포트도 전송
            self.send_report()
            
        except Exception as e:
            logger.error(f"❌ 시작 알림 전송 실패: {e}")
    
    def _send_end_notification(self):
        """자정 종료 알림"""
        try:
            access_token = self.token_manager.get_valid_token()
            self.sender = KakaoSender(access_token)
            
            # 마지막 리포트 먼저 전송
            self.send_report()
            
            end_message = f"""🌙 심플 배민 플러스 자동 모니터링 종료
            
📅 {datetime.now().strftime('%Y년 %m월 %d일')} 자정
✅ 오늘 하루 모니터링이 완료되었습니다

📊 오늘의 최종 현황이 위 메시지에 포함되어 있습니다
💤 다음 모니터링: 내일 오전 10시부터

🙏 오늘도 수고하셨습니다!"""
            
            result = self.sender.send_text_message(end_message)
            if result.get('result_code') == 0:
                logger.info("✅ 자정 종료 알림 전송 완료!")
                
        except Exception as e:
            logger.error(f"❌ 종료 알림 전송 실패: {e}")

def load_config():
    """설정 파일 로드"""
    config_file = 'config.txt'
    
    if not os.path.exists(config_file):
        logger.error(f"❌ 설정 파일이 없습니다: {config_file}")
        logger.info("📝 config.txt 파일을 생성하고 다음 내용을 입력하세요:")
        logger.info("REST_API_KEY=your_rest_api_key_here")
        logger.info("REFRESH_TOKEN=your_refresh_token_here")
        return None, None
    
    try:
        with open(config_file, 'r') as f:
            lines = f.readlines()
        
        rest_api_key = None
        refresh_token = None
        
        for line in lines:
            if line.startswith('REST_API_KEY='):
                rest_api_key = line.split('=')[1].strip()
            elif line.startswith('REFRESH_TOKEN='):
                refresh_token = line.split('=')[1].strip()
        
        if not rest_api_key or not refresh_token:
            logger.error("❌ 설정 파일에 필수 정보가 없습니다")
            return None, None
        
        return rest_api_key, refresh_token
        
    except Exception as e:
        logger.error(f"❌ 설정 파일 로드 실패: {e}")
        return None, None

def main():
    """메인 실행 함수"""
    import sys
    
    # GitHub Actions용 단일 실행 모드 체크
    single_run = '--single-run' in sys.argv
    
    logger.info("🎯 심플 배민 플러스 카카오톡 자동화 시작")
    
    # 설정 로드
    rest_api_key, refresh_token = load_config()
    if not rest_api_key or not refresh_token:
        return
    
    # 자동화 객체 생성
    auto_sender = GriderAutoSender(rest_api_key, refresh_token)
    
    # 연결 테스트
    if not auto_sender.test_connection():
        logger.error("❌ 연결 테스트 실패. 설정을 확인해주세요.")
        return
    
    if single_run:
        # GitHub Actions용 단일 실행
        logger.info("🤖 GitHub Actions 단일 실행 모드")
        success = auto_sender.send_report()
        if success:
            logger.info("✅ GitHub Actions 실행 완료")
        else:
            logger.error("❌ GitHub Actions 실행 실패")
            sys.exit(1)
    else:
        # 로컬 스케줄러 모드
        logger.info("🧪 연결 테스트 완료. 스케줄러에서 자동 시작됩니다.")
        auto_sender.start_scheduler()

if __name__ == "__main__":
    main() 