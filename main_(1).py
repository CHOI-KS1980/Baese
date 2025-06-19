import os
import time
import schedule
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import pandas as pd
import re
import matplotlib
import datetime
import numpy as np
import matplotlib
matplotlib.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# 환경변수 로드 (아이디/비밀번호 등)
load_dotenv()
USER_ID = 'DP2406035262'  # 또는 본인 아이디
USER_PW = 'wldud050323!'  # 또는 본인 비밀번호

# 크롬 드라이버 옵션 설정
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

LOGIN_URL = 'https://jangboo.grider.ai/'

# 1. Selenium으로 로그인 및 데이터 크롤링
def crawl_jangboo():
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(LOGIN_URL)
    time.sleep(2)

    # 로그인 폼 채우기 (id, pw 입력)
    driver.find_element(By.ID, 'id').send_keys(USER_ID)
    driver.find_element(By.ID, 'password').send_keys(USER_PW)
    driver.find_element(By.ID, 'loginBtn').click()
    time.sleep(3)

    # 메인 화면 HTML 추출
    html = driver.page_source
    driver.quit()
    return html

# 2. BeautifulSoup으로 데이터 파싱 (예시)
def parse_data(html):
    soup = BeautifulSoup(html, 'html.parser')

    def safe_parse_int(selector, default=0):
        """CSS selector로 노드를 찾아 텍스트를 정수형으로 안전하게 변환합니다."""
        node = soup.select_one(selector)
        if node:
            # text에서 숫자만 추출
            text = re.sub(r'[^0-9]', '', node.text)
            if text.isdigit():
                return int(text)
        return default

    def safe_parse_float(selector, default=0.0):
        """CSS selector로 노드를 찾아 텍스트를 실수형으로 안전하게 변환합니다."""
        node = soup.select_one(selector)
        if node:
            # 정규표현식으로 숫자(소수점 포함)만 추출
            match = re.search(r'(\d+(?:\.\d+)?)', node.text)
            if match:
                return float(match.group(1))
        return default

    # 총점, 물량점수, 수락률점수, 총완료, 총거절, 수락률을 안전하게 파싱
    total_score = safe_parse_int('.score_total_value[data-text="total"]')
    quantity_score = safe_parse_int('.detail_score_value[data-text="quantity"]')
    acceptance_score = safe_parse_int('.detail_score_value[data-text="acceptance"]')
    total_complete = safe_parse_int('.etc_value[data-etc="complete"] span')
    total_reject = safe_parse_int('.etc_value[data-etc="reject"] span')
    acceptance_rate_total = safe_parse_float('.etc_value[data-etc="acceptance"] span')

    # 피크별 데이터 (오전, 오후, 저녁, 심야)
    peak_names = ['오전피크', '오후피크', '저녁피크', '심야피크']
    peak_data = {}
    quantity_items = soup.select('.quantity_item')
    for idx, item in enumerate(quantity_items):
        name_node = item.select_one('.quantity_title')
        current_node = item.select_one('.performance_value')
        target_node = item.select_one('.number_value span:not(.performance_value)')

        name = name_node.text.strip() if name_node else ''
        current = int(current_node.text.strip()) if current_node and current_node.text.strip().isdigit() else 0
        target_text = target_node.text.strip().replace('건','') if target_node else '0'
        target = int(target_text) if target_text.isdigit() else 0
        
        if name:
            peak_data[name] = {'current': current, 'target': target}

    # 라이더별 데이터 추출
    riders = []
    rider_items = soup.select('.rider_item')
    for rider in rider_items:
        name = rider.select_one('.rider_name').text.strip().split('수락률')[0].strip()
        # 라이더별 수락률 추출 (정확한 구조 반영)
        acceptance_rate = None
        acc_node = rider.select_one('.rider_contents.acceptance_rate')
        if acc_node:
            acc_text = acc_node.get_text()
            match = re.search(r'(\d+(?:\.\d+)?)\s*%', acc_text)
            if match:
                acceptance_rate = float(match.group(1))
        if acceptance_rate is None:
            acceptance_rate = 0.0
        # 거절 건수 추출
        reject = 0
        reject_node = rider.select_one('.rider_contents.reject_count')
        if reject_node:
            reject_text = reject_node.get_text()
            match = re.search(r'(\d+)', reject_text)
            if match:
                reject = int(match.group(1))
        # 배차취소 건수 추출
        cancel = 0
        cancel_node = rider.select_one('.rider_contents.accept_cancel_count')
        if cancel_node:
            cancel_text = cancel_node.get_text()
            match = re.search(r'(\d+)', cancel_text)
            if match:
                cancel = int(match.group(1))
        # 숫자만 추출
        complete_text = rider.select_one('.complete_count').text
        complete = int(re.search(r'\d+', complete_text).group()) if re.search(r'\d+', complete_text) else 0
        morning = int(re.search(r'\d+', rider.select_one('.morning_peak_count').text).group()) if re.search(r'\d+', rider.select_one('.morning_peak_count').text) else 0
        afternoon = int(re.search(r'\d+', rider.select_one('.afternoon_peak_count').text).group()) if re.search(r'\d+', rider.select_one('.afternoon_peak_count').text) else 0
        evening = int(re.search(r'\d+', rider.select_one('.evening_peak_count').text).group()) if re.search(r'\d+', rider.select_one('.evening_peak_count').text) else 0
        midnight = int(re.search(r'\d+', rider.select_one('.midnight_peak_count').text).group()) if re.search(r'\d+', rider.select_one('.midnight_peak_count').text) else 0
        riders.append({
            'name': name,
            'complete': complete,
            '오전피크': morning,
            '오후피크': afternoon,
            '저녁피크': evening,
            '심야피크': midnight,
            'acceptance_rate': acceptance_rate,
            'reject': reject,
            'cancel': cancel
        })

    # 라이더별 전체 미션 기여도 계산 (각 피크별 수행건수/전체 목표 합)
    total_peak_target = sum([peak_data.get(k, {'target':0})['target'] for k in peak_names])
    for rider in riders:
        rider_total = rider['오전피크'] + rider['오후피크'] + rider['저녁피크'] + rider['심야피크']
        rider['contribution'] = round((rider_total / total_peak_target) * 100, 1) if total_peak_target else 0

    data = {
        '오전피크': peak_data.get('오전피크', {'current': 0, 'target': 0}),
        '오후피크': peak_data.get('오후피크', {'current': 0, 'target': 0}),
        '저녁피크': peak_data.get('저녁피크', {'current': 0, 'target': 0}),
        '심야피크': peak_data.get('심야피크', {'current': 0, 'target': 0}),
        '총점': total_score,
        '물량점수': quantity_score,
        '수락률점수': acceptance_score,
        '총완료': total_complete,
        '총거절': total_reject,
        '수락률': acceptance_rate_total,
        'riders': riders
    }
    return data

# 3. 미션 달성/부족 계산 및 메시지 포맷팅
def get_active_peaks():
    now = datetime.datetime.now()
    weekday = now.weekday()  # 0=월, 5=토, 6=일
    peaks = [
        {
            'name': '오전피크',
            'start': datetime.time(6, 0),
            'end': datetime.time(14, 0) if weekday in [5, 6] else datetime.time(13, 0)
        },
        {
            'name': '오후피크',
            'start': datetime.time(13, 0),
            'end': datetime.time(17, 0)
        },
        {
            'name': '저녁피크',
            'start': datetime.time(17, 0),
            'end': datetime.time(20, 0)
        },
        {
            'name': '심야피크',
            'start': datetime.time(20, 0),
            'end': datetime.time(3, 0)
        }
    ]
    active = []
    for peak in peaks:
        # 심야피크는 20:00~03:00 (다음날 새벽)
        if peak['name'] == '심야피크':
            if now.time() >= peak['start'] or now.time() < peak['end']:
                active.append(peak['name'])
        else:
            if now.time() >= peak['start']:
                active.append(peak['name'])
    return active

def make_message(data):
    """데이터를 기반으로 카카오톡에 보낼 깔끔한 포맷의 메시지를 생성합니다."""
    
    # 1. 미션 현황 섹션
    mission_status_parts = []
    lacking_missions = []
    
    peak_order = ['오전피크', '오후피크', '저녁피크', '심야피크']
    peak_emojis = {'오전피크': '🌅', '오후피크': '🌇', '저녁피크': '🌃', '심야피크': '🌙'}
    
    # 현재 시간 기준, 시작된 모든 피크를 표시 (기존 로직 유지)
    active_peaks = get_active_peaks()
    
    for key in peak_order:
        if key not in active_peaks:
            continue

        peak_info = data.get(key, {'current': 0, 'target': 0})
        cur = peak_info['current']
        tgt = peak_info['target']
        
        if cur >= tgt:
            status = '✅ (달성)'
        else:
            status = f'❌ ({tgt-cur}건 부족)'
            lacking_missions.append(f'{key.replace("피크","")} {tgt-cur}건')
        
        mission_status_parts.append(f"{peak_emojis.get(key, '')} {key}: {cur}/{tgt} {status}")

    mission_status_str = "\n".join(mission_status_parts)

    # 2. 종합 정보 섹션
    summary_str = (
        f'총점: {data.get("총점", 0)}점 (물량:{data.get("물량점수", 0)}, 수락률:{data.get("수락률점수", 0)})\n'
        f'수락률: {data.get("수락률", 0.0)}% | 완료: {data.get("총완료", 0)} | 거절: {data.get("총거절", 0)}'
    )
    
    # 3. 라이더별 기여도 섹션
    rider_parts = []
    # 'complete' 건수가 1 이상인 라이더만 필터링하고, 'contribution' 기준으로 내림차순 정렬
    sorted_riders = sorted(
        [r for r in data.get('riders', []) if r.get('complete', 0) > 0], 
        key=lambda x: x.get('contribution', 0), 
        reverse=True
    )
    
    top_riders = sorted_riders[:3]
    other_riders = sorted_riders[3:]

    # TOP 3 라이더
    if top_riders:
        rider_parts.append("🏆 <b>TOP 3 라이더</b>")
        medals = ['🥇', '🥈', '🥉']
        for i, rider in enumerate(top_riders):
            bar_len = 12
            filled = int(round(rider.get('contribution', 0) / 100 * bar_len))
            bar = '■' * filled + '─' * (bar_len - filled)
            
            # 모든 정보를 포함한 라인
            details = (
                f"총 {rider.get('complete', 0)}건 (오:{rider.get('오전피크',0)}/후:{rider.get('오후피크',0)}/저:{rider.get('저녁피크',0)}/심:{rider.get('심야피크',0)})\n"
                f"    └ 수락률: {rider.get('acceptance_rate', 0.0)}% (거절:{rider.get('reject', 0)}, 취소:{rider.get('cancel', 0)})"
            )
            rider_parts.append(f"{medals[i]} {rider.get('name', '이름없음')} | [{bar}] {rider.get('contribution', 0.0)}%\n    └ {details}")

    # 기타 라이더
    if other_riders:
        if top_riders:
             rider_parts.append("─" * 15)
        rider_parts.append("🏃 <b>그 외 라이더</b>")
        for i, rider in enumerate(other_riders, 4):
            details = (
                f"총 {rider.get('complete', 0)}건 (오:{rider.get('오전피크',0)}/후:{rider.get('오후피크',0)}/저:{rider.get('저녁피크',0)}/심:{rider.get('심야피크',0)})\n"
                f"   └ 수락률: {rider.get('acceptance_rate', 0.0)}% (거절:{rider.get('reject', 0)}, 취소:{rider.get('cancel', 0)})"
            )
            rider_parts.append(f"{i}. {rider.get('name', '이름없음')} ({rider.get('contribution', 0.0)}%)\n   └ {details}")

    rider_str = "\n".join(rider_parts)

    # 최종 메시지 조합
    separator = "\n" + "─" * 22 + "\n"
    
    msg = (
        f"📊 <b>미션 현황 리포트</b>\n"
        f"{mission_status_str}"
        f"{separator}"
        f"{summary_str}"
        f"{separator}"
        f"{rider_str}"
    )
    
    if lacking_missions:
        msg += f"{separator}⚠️ **미션 부족**: {', '.join(lacking_missions)}"

    msg += '\n\n(그래프 이미지는 첨부파일로 전송됩니다.)'
    
    return msg

# 4. 카카오톡 API로 메시지 전송 (예시 함수, 실제 구현 필요)
def send_kakao_message(message):
    # 카카오톡 비즈니스/챗봇 API 연동 코드 작성 필요
    print('[카카오톡 전송]')
    print(message)
    # 예: requests.post('https://kakaoapi...', data={...})

def draw_peak_graph(data, save_path='mission_graph.png'):
    peaks = ['오전피크', '오후피크', '저녁피크', '심야피크']
    수행량 = [data[p]['current'] for p in peaks]
    할당량 = [data[p]['target'] for p in peaks]
    x = range(len(peaks))

    plt.figure(figsize=(7, 4))
    # 할당량(분홍색)
    plt.plot(x, 할당량, color='#ff8a8a', marker='o', linewidth=2, label='할당량')
    plt.fill_between(x, 할당량, color='#ffb6b6', alpha=0.3)
    # 수행량(파란색)
    plt.plot(x, 수행량, color='#4aa8ff', marker='o', linewidth=2, label='수행량')
    plt.fill_between(x, 수행량, color='#7ecbff', alpha=0.3)
    plt.xticks(x, peaks, fontsize=12)
    plt.yticks(fontsize=11)
    plt.xlabel('피크 구간', fontsize=13)
    plt.ylabel('건수', fontsize=13)
    plt.title('피크별 수행량/할당량', fontsize=15)
    plt.legend(fontsize=11, loc='upper center')
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

def draw_rider_contribution_table(data, save_path='rider_contribution_table.png'):
    import matplotlib
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.offsetbox import OffsetImage, AnnotationBbox

    matplotlib.rcParams['font.family'] = 'AppleGothic'
    plt.rcParams['axes.unicode_minus'] = False

    riders = data.get('riders', [])
    if not riders:
        return
    riders = [r for r in riders if r['complete'] > 0]
    riders = sorted(riders, key=lambda x: x['contribution'], reverse=True)
    names = [r['name'] for r in riders]
    contributions = [r['contribution'] for r in riders]
    x = np.arange(len(names))
    plt.figure(figsize=(12, 0.7 + 0.6*len(names)))
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("mycmap", ["#ffe066", "#7ecbff", "#1e90ff"])
    colors = [cmap(i/len(names)) for i in range(len(names))]
    for lw in [8, 4, 2]:
        plt.plot(x, contributions, linestyle=':', color='#b3e0ff', marker='o', markersize=0, linewidth=lw, alpha=0.2)
    plt.plot(x, contributions, linestyle=':', color='#4aa8ff', marker='o', markersize=14, linewidth=2, alpha=0.9, zorder=2)
    top_colors = ['#ffd700', '#c0c0c0', '#cd7f32']
    for i in range(min(3, len(names))):
        plt.scatter(x[i], contributions[i], s=600, marker='*', color=top_colors[i], edgecolor='#333', zorder=5)
        plt.text(x[i], contributions[i]+5, f'TOP{i+1}\n{names[i]}\n{contributions[i]}%', 
                 ha='center', va='bottom', fontsize=18, fontweight='bold', color=top_colors[i], family='AppleGothic', zorder=6)
    for i in range(3, len(names)):
        plt.scatter(x[i], contributions[i], s=200, marker='o', color=colors[i], edgecolor='#333', zorder=4)
        plt.text(x[i], contributions[i]+3, f'{names[i]}\n{contributions[i]}%', ha='center', va='bottom', 
                 fontsize=14, fontweight='semibold', color='#333', family='AppleGothic', zorder=5)
    plt.gca().set_facecolor('#f7fbff')
    plt.grid(axis='y', linestyle='--', alpha=0.4)
    plt.xticks(x, names, fontsize=15, rotation=20, family='AppleGothic')
    plt.yticks(fontsize=14, family='AppleGothic')
    plt.xlabel('라이더', fontsize=16, family='AppleGothic', fontweight='bold')
    plt.ylabel('미션 기여도(%)', fontsize=16, family='AppleGothic', fontweight='bold')
    plt.title('라이더별 미션 기여도', fontsize=22, fontweight='bold', family='AppleGothic', color='#1e90ff')
    plt.ylim(0, 100)
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight', dpi=180)
    plt.close()

def draw_rider_contribution_bar(data, save_path='rider_contribution_bar.png'):
    riders = [r for r in data.get('riders', []) if r['complete'] > 0]
    if not riders:
        return
    # 기여도 내림차순 정렬
    riders = sorted(riders, key=lambda x: x['contribution'], reverse=True)
    names = [r['name'] for r in riders]
    contributions = [r['contribution'] for r in riders]
    colors = ['#7ecbff'] * len(riders)
    edgecolors = ['#4aa8ff'] * len(riders)
    if len(riders) > 0:
        colors[0] = '#1e90ff'
        edgecolors[0] = '#003366'
    plt.figure(figsize=(10, 0.6 + 0.5*len(names)))
    y = np.arange(len(names))
    # 1. 0~100% 전체 배경 막대 (연한 회색)
    plt.barh(y, [100]*len(names), color='#e6e6e6', edgecolor='#cccccc', height=0.6, zorder=1)
    # 2. 실제 기여도만큼 진한 색상 막대
    bars = plt.barh(y, contributions, color=colors, edgecolor=edgecolors, height=0.6, alpha=0.95, linewidth=2, zorder=2)
    if len(riders) > 0:
        bars[0].set_zorder(3)
        bars[0].set_alpha(1)
        bars[0].set_linewidth(3)
    plt.xlabel('미션 기여도(%)', fontsize=14)
    plt.title('라이더별 미션 기여도', fontsize=17, fontweight='bold')
    plt.xlim(0, 100)
    plt.yticks(y, names, fontsize=13, fontname='AppleGothic')
    # 기여도 수치 표시
    for i, (bar, value) in enumerate(zip(bars, contributions)):
        plt.text(value + 1, bar.get_y() + bar.get_height()/2, f'{value}%', va='center', fontsize=13, fontweight='bold' if i == 0 else 'normal', color='#003366' if i == 0 else '#333', fontname='AppleGothic')
    if len(riders) > 0:
        plt.text(100, bars[0].get_y() + bars[0].get_height()/2, f'🏆 TOP: {names[0]}', va='center', ha='right', fontsize=15, fontweight='bold', color='#1e90ff', bbox=dict(facecolor='#e6f2ff', edgecolor='#1e90ff', boxstyle='round,pad=0.3'), fontname='AppleGothic')
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight', dpi=150)
    plt.close()

def add_icon(ax, x, y, icon_path, zoom=0.15):
    img = plt.imread(icon_path)
    imagebox = OffsetImage(img, zoom=zoom)
    ab = AnnotationBbox(imagebox, (x, y), frameon=False)
    ax.add_artist(ab)

# 5. 전체 플로우 함수
def job():
    html = crawl_jangboo()
    data = parse_data(html)
    # 전체 미션 그래프
    draw_peak_graph(data)
    # 라이더별 기여도 표
    draw_rider_contribution_table(data)
    # 라이더별 기여도 그래프
    draw_rider_contribution_bar(data)
    msg = make_message(data)
    send_kakao_message(msg)

# 6. 30분마다 실행
def main():
    schedule.every(30).minutes.do(job)
    print('자동 미션 체크/알림 서비스 시작!')
    while True:
        schedule.run_pending()
        time.sleep(1)

def send_to_kakao_openbuilder(message):
    url = "http://localhost:5000/webhook"  # Webhook 서버가 VM에서 실행 중이어야 함
    data = {
        "userRequest": {
            "utterance": "자동미션"
        }
    }
    # 실제 오픈빌더 Webhook 포맷에 맞게 수정 필요
    response = requests.post(url, json=data)
    print(response.text)

if __name__ == '__main__':
    job()  # 이 줄을 추가하면 바로 한 번 실행됨
    main() # 기존 자동 스케줄러
    # 미션 현황 메시지 생성
    mission_message = "여기에 자동 미션 현황 메시지"
    send_to_kakao_openbuilder(mission_message)

plt.plot([1,2,3], [1,2,3])
plt.title('한글 테스트')
plt.show() 