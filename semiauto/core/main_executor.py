import os
import re
import json
import time
import logging
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from weather_service import WeatherService

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_korea_time():
    """현재 한국 시간을 반환합니다."""
    return datetime.utcnow() + timedelta(hours=9)

class HolidayChecker:
    """한국천문연구원 API를 사용하여 공휴일을 확인하는 클래스."""
    def __init__(self, api_key):
        self.api_key = api_key
        self.holidays = {}
        self.load_holidays_for_year(get_korea_time().year)
        logging.info("한국천문연구원 특일 정보 API 공휴일 체커 초기화")

    def load_holidays_for_year(self, year):
        """지정된 연도의 모든 월에 대한 공휴일 정보를 로드합니다."""
        for month in range(1, 13):
            self.get_holidays(year, month)
        logging.info(f"{year}년 전체월 공휴일 {len(self.holidays)}개 로드 완료")

    def get_holidays(self, year, month):
        """API를 호출하여 특정 연도와 월의 공휴일 정보를 가져옵니다."""
        url = 'http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo'
        params = {
            'serviceKey': self.api_key,
            'solYear': year,
            'solMonth': f"{month:02d}",
            '_type': 'json'
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            items = response.json().get('response', {}).get('body', {}).get('items', {}).get('item', [])
            if items:
                if not isinstance(items, list):
                    items = [items]
                for item in items:
                    event_date = str(item.get('locdate'))
                    self.holidays[event_date] = item.get('dateName')
                    logging.info(f"공휴일 확인: {event_date[:4]}-{event_date[4:6]}-{event_date[6:]} - {item.get('dateName')}")
        except requests.exceptions.RequestException as e:
            logging.error(f"{year}년 {month}월 공휴일 정보 조회 실패: {e}")
        except json.JSONDecodeError:
            logging.error(f"API 응답 JSON 파싱 실패: {response.text}")

    def is_holiday(self, date_str):
        """주어진 날짜 문자열(YYYYMMDD)이 공휴일인지 확인합니다."""
        return date_str in self.holidays

class TokenManager:
    """카카오톡 API 토큰을 관리(갱신, 저장, 로드)하는 클래스."""
    def __init__(self, rest_api_key, refresh_token):
        self.rest_api_key = rest_api_key
        self.refresh_token = refresh_token
        self.access_token = None
        logging.info("TokenManager 초기화 - 토큰 갱신 시도")
        self.refresh_access_token()

    def refresh_access_token(self):
        """Refresh Token을 사용하여 새로운 Access Token을 발급받습니다."""
        url = "https://kauth.kakao.com/oauth/token"
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.rest_api_key,
            "refresh_token": self.refresh_token,
        }
        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            if self.access_token:
                 logging.info(f"토큰 갱신 완료: {self.access_token[:20]}...")
            else:
                 logging.error("토큰 갱신 실패: 응답에 access_token이 없습니다.")
        except requests.exceptions.RequestException as e:
            logging.error(f"토큰 갱신 요청 실패: {e}")
            self.access_token = None

    def get_valid_token(self):
        """유효한 Access Token을 반환합니다."""
        if not self.access_token:
            logging.warning("Access Token이 없습니다. 갱신을 다시 시도합니다.")
            self.refresh_access_token()
        logging.info(f"유효한 토큰 반환: {self.access_token[:20]}..." if self.access_token else "토큰 없음")
        return self.access_token

class KakaoMessageManager:
    """카카오톡 메시지 전송을 담당하는 클래스."""
    def __init__(self):
        load_dotenv()
        self.rest_api_key = os.getenv("KAKAO_REST_API_KEY")
        self.refresh_token = os.getenv("KAKAO_REFRESH_TOKEN")
        self.token_manager = TokenManager(self.rest_api_key, self.refresh_token)

    def send_message(self, message_text):
        """'나에게 보내기' API를 사용하여 텍스트 메시지를 전송합니다."""
        access_token = self.token_manager.get_valid_token()
        if not access_token:
            logging.error("유효한 Access Token이 없어 메시지를 전송할 수 없습니다.")
            return

        url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
        headers = {"Authorization": f"Bearer {access_token}"}
        template_object = {
            "object_type": "text",
            "text": message_text,
            "link": {"web_url": "https://developers.kakao.com"},
        }
        payload = {"template_object": json.dumps(template_object)}

        try:
            response = requests.post(url, headers=headers, data=payload, timeout=10)
            if response.json().get("result_code") == 0:
                logging.info("✅ 카카오톡 메시지 전송 성공")
            else:
                logging.error(f"❌ 카카오톡 메시지 전송 실패: {response.text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"메시지 전송 요청 중 예외 발생: {e}")

class GriderDataCollector:
    """셀레니움을 사용하여 G-Rider 웹사이트에서 데이터를 수집하는 클래스."""
    def __init__(self):
        load_dotenv()
        self.selectors = self._load_selectors()
        self.temp_daily_riders = []

    def _load_selectors(self):
        """`selectors` 디렉토리에서 모든 JSON 선택자 파일을 로드합니다."""
        selectors_dir = os.path.join(os.path.dirname(__file__), '..', 'selectors')
        all_selectors = {}
        try:
            for filename in os.listdir(selectors_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(selectors_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        key_name = filename.replace('.json', '')
                        all_selectors[key_name] = json.load(f)
                        logging.info(f"선택자 파일 로드 완료: {filename}")
        except FileNotFoundError:
            logging.error(f"선택자 디렉토리 '{selectors_dir}'를 찾을 수 없습니다.")
        except json.JSONDecodeError as e:
            logging.error(f"선택자 파일 파싱 오류: {e}")
        return all_selectors

    def _get_driver(self):
        """셀레니움 WebDriver를 설정하고 반환합니다."""
        options = webdriver.ChromeOptions()
        if 'GITHUB_ACTIONS' in os.environ:
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        logging.info("✅ Chrome WebDriver 초기화 성공 (webdriver-manager)")
        return driver

    def _login(self, driver):
        """G-Rider 웹사이트에 로그인합니다."""
        s_login = self.selectors.get('login', {})
        login_url = os.getenv('G_RIDER_LOGIN_URL')
        user_id = os.getenv('G_RIDER_ID')
        user_pw = os.getenv('G_RIDER_PW')

        if not all([login_url, user_id, user_pw]):
            logging.error("로그인 정보(URL, ID, PW)가 .env 파일에 설정되지 않았습니다.")
            return False

        try:
            driver.get(login_url)
            driver.find_element(By.CSS_SELECTOR, s_login['id_input']).send_keys(user_id)
            driver.find_element(By.CSS_SELECTOR, s_login['pw_input']).send_keys(user_pw)
            driver.find_element(By.CSS_SELECTOR, s_login['login_button']).click()
            
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['daily_data']['container']))
            )
            logging.info("✅ G라이더 로그인 성공")
            return True
        except (TimeoutException, NoSuchElementException) as e:
            logging.error(f"로그인 실패: {e}", exc_info=True)
            return False

    def _get_safe_number(self, text):
        """문자열에서 숫자만 추출하여 정수로 변환합니다. 변환 실패 시 0을 반환합니다."""
        if not isinstance(text, str):
            return 0
        text = text.strip()
        if text in ['N/A', '-', '']:
            return 0
        text = text.replace('점', '').replace('건', '').replace('회', '')
        numbers = re.findall(r'[-+]?\d*\.\d+|\d+', text)
        if numbers:
            try:
                return int(float(numbers[0]))
            except (ValueError, IndexError):
                return 0
        return 0

    def _parse_daily_rider_data(self, driver):
        """대시보드에서 일간 라이더 데이터를 파싱합니다."""
        s_daily = self.selectors['daily_data']
        wait = WebDriverWait(driver, 20)
        daily_data = {'riders': [], 'total_completed': 0, 'total_rejected': 0, 'total_canceled': 0}

        try:
            total_container_selector = s_daily.get('daily_total_container')
            if total_container_selector:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, total_container_selector)))
                daily_data['total_completed'] = self._get_safe_number(driver.find_element(By.CSS_SELECTOR, s_daily.get('daily_total_complete')).text)
                daily_data['total_rejected'] = self._get_safe_number(driver.find_element(By.CSS_SELECTOR, s_daily.get('daily_total_reject')).text)
                cancel_dispatch = self._get_safe_number(driver.find_element(By.CSS_SELECTOR, s_daily.get('daily_total_accept_cancel')).text)
                cancel_delivery = self._get_safe_number(driver.find_element(By.CSS_SELECTOR, s_daily.get('daily_total_accept_cancel_rider_fault')).text)
                daily_data['total_canceled'] = cancel_dispatch + cancel_delivery
                logging.info(f"✅ 일일 총계 파싱 완료: {daily_data}")

            rider_items = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, s_daily.get('item'))))
            logging.info(f"✅ 일간 라이더 목록 아이템 {len(rider_items)}개 로드 완료. 파싱을 시작합니다.")

            for rider_element in rider_items:
                name = rider_element.find_element(By.CSS_SELECTOR, s_daily.get('name')).text.strip()
                if not name: continue
                
                rider_data = {
                    'name': name,
                    '완료': self._get_safe_number(rider_element.find_element(By.CSS_SELECTOR, s_daily.get('complete_count')).text),
                    '거절': self._get_safe_number(rider_element.find_element(By.CSS_SELECTOR, s_daily.get('reject_count')).text),
                    '배차취소': self._get_safe_number(rider_element.find_element(By.CSS_SELECTOR, s_daily.get('accept_cancel_count')).text),
                    '배달취소': self._get_safe_number(rider_element.find_element(By.CSS_SELECTOR, s_daily.get('accept_cancel_rider_fault_count')).text),
                    '오전': self._get_safe_number(rider_element.find_element(By.CSS_SELECTOR, s_daily.get('morning_count')).text),
                    '오후': self._get_safe_number(rider_element.find_element(By.CSS_SELECTOR, s_daily.get('afternoon_count')).text),
                    '저녁': self._get_safe_number(rider_element.find_element(By.CSS_SELECTOR, s_daily.get('evening_count')).text),
                    '심야': self._get_safe_number(rider_element.find_element(By.CSS_SELECTOR, s_daily.get('midnight_count')).text)
                }
                
                if rider_data['완료'] > 0:
                    daily_data['riders'].append(rider_data)
                else:
                    logging.info(f"라이더 '{name}'는 실적이 없어 데이터 수집에서 제외합니다.")

            logging.info(f"✅ {len(daily_data['riders'])}명의 활동 라이더 데이터 파싱 완료.")

        except (TimeoutException, NoSuchElementException) as e:
            logging.error(f"일간 데이터 파싱 실패: {e}", exc_info=True)

        return daily_data
        
    def _parse_weekly_summary_data(self, driver):
        """대시보드에서 주간 요약 데이터를 파싱합니다."""
        s_weekly = self.selectors.get('weekly_summary', {})
        weekly_data = {}
        try:
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, s_weekly['score_card'])))

            weekly_data['총점'] = self._get_safe_number(driver.find_element(By.CSS_SELECTOR, s_weekly['total_score']).text)
            weekly_data['물량점수'] = self._get_safe_number(driver.find_element(By.CSS_SELECTOR, s_weekly['delivery_score']).text)
            weekly_data['수락률점수'] = self._get_safe_number(driver.find_element(By.CSS_SELECTOR, s_weekly['acceptance_score']).text)
            
            total_completed = sum(r.get('완료', 0) for r in self.temp_daily_riders)
            total_rejected = sum(r.get('거절', 0) for r in self.temp_daily_riders)
            total_canceled = sum(r.get('배차취소', 0) + r.get('배달취소', 0) for r in self.temp_daily_riders)
            
            weekly_data['총완료'] = total_completed
            weekly_data['총거절'] = total_rejected + total_canceled
            
            total_decisions = total_completed + total_rejected + total_canceled
            weekly_data['수락률'] = (total_completed / total_decisions * 100) if total_decisions > 0 else 0.0

            logging.info(f"✅ 주간 통계 파싱 완료: {weekly_data}")
        except (TimeoutException, NoSuchElementException) as e:
            logging.error(f"주간 요약 데이터 파싱 실패: {e}", exc_info=True)
        return weekly_data

    def _parse_mission_data(self, driver):
        """대시보드에서 미션 데이터를 파싱합니다."""
        s_mission = self.selectors.get('mission_table', {})
        missions = {}
        try:
            wait = WebDriverWait(driver, 10)
            mission_rows = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, s_mission['row'])))
            
            for row in mission_rows:
                mission_name = row.find_element(By.CSS_SELECTOR, s_mission['name']).text.strip()
                current_str = row.find_element(By.CSS_SELECTOR, s_mission['current']).text
                goal_str = row.find_element(By.CSS_SELECTOR, s_mission['goal']).text
                
                current = self._get_safe_number(current_str)
                goal = self._get_safe_number(goal_str)
                
                is_achieved = current >= goal
                shortage = max(0, goal - current)
                
                icon = "🌅"
                short_name = mission_name
                if "오후" in mission_name: icon = "🌇"; short_name = "오후논"
                elif "저녁" in mission_name: icon = "🌃"; short_name = "저녁"
                elif "심야" in mission_name: icon = "🌙"; short_name = "심야"
                
                missions[mission_name] = {
                    'current': current, 'goal': goal, 'is_achieved': is_achieved,
                    'shortage': shortage, 'icon': icon, 'short_name': short_name
                }
            logging.info(f"✅ 미션 데이터 파싱 완료: {missions}")
        except (TimeoutException, NoSuchElementException) as e:
            logging.error(f"미션 데이터 파싱 실패: {e}", exc_info=True)
        return missions

    def collect_all_data(self):
        """모든 데이터를 수집하고 종합하여 반환합니다."""
        final_data = {'metadata': {'report_date': get_korea_time().strftime('%Y-%m-%d')}}
        driver = None
        try:
            driver = self._get_driver()
            if not self._login(driver):
                raise Exception("G라이더 로그인 실패")

            daily_data = self._parse_daily_rider_data(driver)
            self.temp_daily_riders = daily_data.get('riders', [])
            
            weekly_summary_data = self._parse_weekly_summary_data(driver)
            mission_data = self._parse_mission_data(driver)

            total_completed = daily_data.get('total_completed', 0)
            total_rejected_canceled = daily_data.get('total_rejected', 0) + daily_data.get('total_canceled', 0)
            total_decisions = total_completed + total_rejected_canceled
            acceptance_rate = (total_completed / total_decisions * 100) if total_decisions > 0 else 0.0
            
            final_data['daily_summary'] = {
                'total_completed': total_completed,
                'total_rejected': daily_data.get('total_rejected', 0),
                'total_canceled': daily_data.get('total_canceled', 0),
                'acceptance_rate': acceptance_rate
            }
            final_data['daily_riders'] = daily_data.get('riders', [])
            final_data['weekly_summary'] = weekly_summary_data
            final_data['mission_status'] = mission_data
            final_data['metadata']['error'] = None
        except Exception as e:
            logging.error(f"전체 데이터 수집 프로세스 실패: {e}", exc_info=True)
            final_data['metadata']['error'] = str(e)
        finally:
            if driver:
                driver.quit()
                logging.info("WebDriver를 종료했습니다.")
            self.save_dashboard_data(final_data)
        return final_data

    def save_dashboard_data(self, data):
        """수집된 데이터를 JSON 파일로 저장합니다."""
        try:
            base_dir = os.path.dirname(__file__)
            latest_path = os.path.join(base_dir, '..', 'dashboard', 'api', 'latest-data.json')
            os.makedirs(os.path.dirname(latest_path), exist_ok=True)
            with open(latest_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logging.info(f"대시보드 데이터 저장 완료: {latest_path}")

            history_dir = os.path.join(os.path.dirname(latest_path), 'history')
            os.makedirs(history_dir, exist_ok=True)
            history_filename = f"history-{get_korea_time().strftime('%Y-%m-%d')}.json"
            history_path = os.path.join(history_dir, history_filename)
            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logging.info(f"히스토리 데이터 저장 완료: {history_path}")
        except Exception as e:
            logging.error(f"데이터 파일 저장 실패: {e}")

class G_Rider_Executor:
    def __init__(self):
        self.collector = GriderDataCollector()
        self.kakao_manager = KakaoMessageManager()

    def send_report(self):
        """데이터 수집부터 메시지 전송까지 전체 프로세스를 실행합니다."""
        data = self.collector.collect_all_data()
        if not data:
            logging.error("데이터 수집에 실패하여 리포트를 전송할 수 없습니다.")
            return
        if data.get('metadata', {}).get('error'):
            logging.error(f"데이터 수집 중 오류가 발생하여 리포트를 전송하지 않습니다: {data['metadata']['error']}")
            return
        message = self.format_message(data)
        self.kakao_manager.send_message(message)

    def format_message(self, data):
        """템플릿 파일을 기반으로 최종 메시지를 생성합니다."""
        try:
            template_path = os.path.join(os.path.dirname(__file__), '..', 'message_template.md')
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
        except FileNotFoundError:
            logger.error(f"{template_path} 파일을 찾을 수 없습니다.")
            return "오류: 메시지 템플릿 파일을 찾을 수 없습니다."

        daily_summary_data = data.get('daily_summary', {})
        weekly_summary_data = data.get('weekly_summary', {})
        mission_data = data.get('mission_status', {})
        riders_data = data.get('daily_riders', [])

        daily_completed = daily_summary_data.get('total_completed', 0)
        daily_rejected_and_canceled = daily_summary_data.get('total_rejected', 0) + daily_summary_data.get('total_canceled', 0)
        
        mission_summary = self._format_mission_summary(mission_data)
        daily_acceptance_bar = self._format_progress_bar(daily_summary_data.get('acceptance_rate', 0.0))
        weather_summary = self._format_weather_summary()
        weekly_acceptance_bar = self._format_progress_bar(weekly_summary_data.get('수락률', 0.0))
        rider_rankings, active_rider_count = self._format_rider_rankings(riders_data)
        mission_shortage_summary = self._format_mission_shortage_summary(mission_data)

        return template.format(
            mission_summary=mission_summary,
            daily_completed=daily_completed,
            daily_rejected_and_canceled=daily_rejected_and_canceled,
            daily_acceptance_rate=f"{daily_summary_data.get('acceptance_rate', 0.0):.1f}",
            daily_acceptance_bar=daily_acceptance_bar,
            weather_summary=weather_summary,
            weekly_total_score=weekly_summary_data.get('총점', 0),
            weekly_delivery_score=weekly_summary_data.get('물량점수', 0),
            weekly_acceptance_score=weekly_summary_data.get('수락률점수', 0),
            weekly_completed=weekly_summary_data.get('총완료', 0),
            weekly_rejected_and_canceled=weekly_summary_data.get('총거절', 0),
            weekly_acceptance_rate=f"{weekly_summary_data.get('수락률', 0.0):.1f}",
            weekly_acceptance_bar=weekly_acceptance_bar,
            active_rider_count=active_rider_count,
            rider_rankings=rider_rankings,
            mission_shortage_summary=mission_shortage_summary
        )

    def _format_progress_bar(self, percentage, length=10):
        if not isinstance(percentage, (int, float)): percentage = 0
        fill_count = int(round(percentage / (100 / length)))
        return '🟩' * fill_count + '⬜' * (length - fill_count)

    def _format_mission_summary(self, missions):
        lines = []
        if not missions: return ""
        for mission_name, details in missions.items():
            current, goal = details.get('current',0), details.get('goal',0)
            status_icon = "✅" if details.get('is_achieved') else "⚠️"
            status_text = "(달성)" if details.get('is_achieved') else f"({details.get('shortage',0)}건 부족)"
            lines.append(f"{details.get('icon','')} {status_icon} {mission_name}: {current}/{goal} {status_text}")
        return "\n".join(lines)
        
    def _format_weather_summary(self):
        try:
            weather_service = WeatherService()
            weather_info = weather_service.get_weather()
            if weather_info and 'error' not in weather_info:
                return (f"🌍 오늘의 날씨 ({weather_info['source']})\n"
                        f" 🌅 오전: {weather_info['am_temp_min']}~{weather_info['am_temp_max']}°C, 강수확률 {weather_info['am_rain_prob']}%\n"
                        f" 🌇 오후: {weather_info['pm_temp_min']}~{weather_info['pm_temp_max']}°C, 강수확률 {weather_info['pm_rain_prob']}%")
        except Exception as e:
            logger.warning(f"날씨 정보 조회 실패: {e}")
        return "🌍 날씨 정보 (조회 실패)"

    def _format_rider_rankings(self, riders):
        if not riders:
            return "운행 중인 라이더 정보가 없습니다.", 0

        riders.sort(key=lambda x: x.get('완료', 0), reverse=True)
        active_rider_count = len(riders)
        top_riders = riders[:5]
        top_rider_completed = top_riders[0].get('완료', 0) if top_riders else 0

        rank_icons = ["🥇", "🥈", "🥉"]
        lines = []
        for i, rider in enumerate(top_riders):
            name = rider.get('name', 'N/A')
            completed = rider.get('완료', 0)
            rank_str = f"**{rank_icons[i]} {name}**" if i < len(rank_icons) else f"  **{i+1}. {name}**"
            progress_percent = (completed / top_rider_completed * 100) if top_rider_completed > 0 else 0
            progress_bar = self._format_progress_bar(progress_percent, 5)
            rejected = rider.get('거절', 0)
            canceled = rider.get('배차취소', 0) + rider.get('배달취소', 0)
            total_decisions = completed + rejected + canceled
            acceptance_rate = (completed / total_decisions * 100) if total_decisions > 0 else 100

            lines.append(
                f"{rank_str} | {progress_bar} {progress_percent:.1f}%\n"
                f"    총 {completed}건 (🌅{rider.get('오전', 0)} 🌇{rider.get('오후', 0)} 🌃{rider.get('저녁', 0)} 🌙{rider.get('심야', 0)})\n"
                f"    수락률: {acceptance_rate:.1f}% (거절:{rejected}, 취소:{canceled})"
            )
        return "\n\n".join(lines), active_rider_count

    def _format_mission_shortage_summary(self, missions):
        if not missions: return "미션 정보 없음"
        shortages = [f"{details.get('short_name','')} {details.get('shortage',0)}건" 
                     for details in missions.values() if not details.get('is_achieved')]
        if not shortages:
            return "🎉 모든 미션 달성! 🎉"
        return "⚠️ 미션 부족: " + ", ".join(shortages)

def main():
    """스크립트의 메인 실행 함수입니다."""
    load_dotenv()
    holiday_api_key = os.getenv("HOLIDAY_API_KEY")
    if holiday_api_key:
        HolidayChecker(holiday_api_key)
    else:
        logging.warning("HOLIDAY_API_KEY가 설정되지 않아 공휴일 정보를 로드할 수 없습니다.")

    logging.info("==================================================")
    logging.info(" G-Rider 자동화 스크립트 시작")
    logging.info("==================================================")
    
    executor = G_Rider_Executor()
    executor.send_report()
    
    logging.info("==================================================")
    logging.info(" G-Rider 자동화 스크립트 종료")
    logging.info("==================================================")

if __name__ == "__main__":
    main()
