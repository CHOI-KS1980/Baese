// 🌟 G라이더 대시보드 JavaScript

// 전역 변수
let performanceChart = null;
let missionChart = null;
let lastDataUpdate = null;
let messageSettings = {
    template: 'standard',
    sendOnChange: true,
    sendOnSchedule: true,
    sendOnAlert: false,
    customMessage: null
};

// 메시지 템플릿
const messageTemplates = {
    standard: {
        title: "🚀 G라이더 현황 알림",
        content: "📊 현재 점수: {score}점\n✅ 완료 미션: {completed_missions}개\n🏍️ 활성 라이더: {active_riders}명\n💰 예상 수익: {estimated_income}원",
        footer: "📅 {timestamp}"
    },
    detailed: {
        title: "📈 G라이더 상세 현황 리포트",
        content: "🎯 성과 지표\n━━━━━━━━━━━━━━━━━━━━━\n📊 현재 점수: {score}점 ({score_change})\n✅ 완료 미션: {completed_missions}개 ({mission_change})\n🏍️ 활성 라이더: {active_riders}명 ({riders_change})\n💰 예상 수익: {estimated_income}원 ({income_change})\n\n📈 시간대별 추이\n━━━━━━━━━━━━━━━━━━━━━\n🕒 피크시간 성과율: {peak_performance}%\n⏰ 평균 응답시간: {avg_response_time}분\n🎯 목표 달성률: {goal_achievement}%",
        footer: "📅 {timestamp} | 다음 업데이트: {next_update}"
    },
    simple: {
        title: "G라이더",
        content: "점수 {score}점 | 미션 {completed_missions}개 | 라이더 {active_riders}명",
        footer: "{timestamp}"
    }
};

// 대시보드 초기화
function initializeDashboard() {
    console.log('🌟 G라이더 대시보드 초기화 시작');
    
    // 빌드 시간 설정
    document.getElementById('build-time').textContent = new Date().toLocaleString('ko-KR');
    
    // 차트 초기화
    initializeCharts();
    
    // 초기 데이터 로드
    refreshData();
    
    // 메시지 설정 로드
    loadMessageSettings();
    
    console.log('✅ 대시보드 초기화 완료');
}

// 차트 초기화
function initializeCharts() {
    // 성과 추이 차트
    const performanceCtx = document.getElementById('performance-chart').getContext('2d');
    performanceChart = new Chart(performanceCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '점수',
                data: [],
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                tension: 0.4,
                fill: true
            }, {
                label: '완료 미션',
                data: [],
                borderColor: '#27ae60',
                backgroundColor: 'rgba(39, 174, 96, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    }
                }
            }
        }
    });

    // 미션 분포 차트
    const missionCtx = document.getElementById('mission-chart').getContext('2d');
    missionChart = new Chart(missionCtx, {
        type: 'doughnut',
        data: {
            labels: ['완료', '진행중', '대기중'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: [
                    '#27ae60',
                    '#f39c12',
                    '#e74c3c'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                }
            }
        }
    });
}

// 데이터 새로고침
async function refreshData() {
    console.log('🔄 데이터 새로고침 시작');
    try {
        const data = await fetchLatestData();
        if (data && !data.error) {
            updateDashboard(data);
            updateSystemStatus('online', data.last_updated);
        } else {
            const errorMessage = data ? data.error_reason : '데이터 파일을 찾을 수 없습니다.';
            updateSystemStatus('error', null, errorMessage);
            showNotification(errorMessage, 'error');
        }
    } catch (error) {
        console.error('❌ 데이터 새로고침 실패:', error);
        updateSystemStatus('error', null, error.message);
    }
}

// 최신 데이터 가져오기
async function fetchLatestData() {
    try {
        const response = await fetch('api/latest-data.json?t=' + Date.now());
        if (!response.ok) {
            throw new Error(`데이터 파일 로드 실패 (${response.status})`);
        }
        return await response.json();
    } catch (error) {
        console.error('fetchLatestData 에러:', error);
        // 샘플 데이터 대신 null을 반환하여 오류 처리를 유도
        return null; 
    }
}

// 대시보드 업데이트
function updateDashboard(data) {
    // latest-data.json의 실제 구조에 맞게 키를 직접 사용
    const riders = data.riders || [];

    // 운행 기록이 있는 라이더만 필터링 (키 이름: '완료')
    const activeRiders = riders.filter(rider => (rider.완료 || 0) > 0);

    // 1. 통계 카드 업데이트
    const totalScoreEl = document.getElementById('total-score');
    const totalCompletedEl = document.getElementById('total-completed');
    const acceptanceRateEl = document.getElementById('acceptance-rate');
    const activeRidersEl = document.getElementById('active-riders');

    if (totalScoreEl) totalScoreEl.textContent = data.총점 || 0;
    if (totalCompletedEl) totalCompletedEl.textContent = data.총완료 || 0;
    if (acceptanceRateEl) acceptanceRateEl.textContent = `${data.수락률 || 0}%`;
    if (activeRidersEl) activeRidersEl.textContent = activeRiders.length;

    // 2. 라이더 현황 업데이트
    const riderListContainer = document.getElementById('rider-list-container');
    if (!riderListContainer) return; // 요소가 없으면 중단

    riderListContainer.innerHTML = ''; // 기존 목록 초기화

    if (activeRiders.length === 0) {
        riderListContainer.innerHTML = '<div class="rider-item-placeholder">운행 기록이 있는 라이더가 없습니다.</div>';
    } else {
        activeRiders.forEach(rider => {
            const riderElement = document.createElement('div');
            riderElement.className = 'rider-item';
            // 실제 키 이름('name', '완료', '수락률')을 사용
            riderElement.innerHTML = `
                <div class="rider-name">${rider.name}</div>
                <div class="rider-stats">
                    <span>완료: ${rider.완료}</span>
                    <span>수락률: ${rider.수락률}%</span>
                </div>
            `;
            riderListContainer.appendChild(riderElement);
        });
    }

    showNotification('대시보드 데이터가 업데이트되었습니다.', 'success');
}

// 시스템 상태 업데이트
function updateSystemStatus(status, lastUpdated, errorMessage = '데이터 수신 중단') {
    const statusIndicator = document.getElementById('system-status-indicator');
    const statusText = document.getElementById('system-status-text');
    
    statusIndicator.className = `status-indicator ${status}`;
    
    switch (status) {
        case 'online':
            statusText.textContent = `실시간 연결 (${new Date(lastUpdated).toLocaleString('ko-KR')} 기준)`;
            break;
        case 'offline':
            statusText.textContent = '연결 끊김';
            break;
        case 'error':
            statusText.textContent = `오류: ${errorMessage}`;
            break;
    }
}

// 메시지 설정 토글
function toggleMessageSettings() {
    const configElement = document.getElementById('message-config');
    const isVisible = configElement.style.display !== 'none';
    configElement.style.display = isVisible ? 'none' : 'block';
}

// 메시지 미리보기 업데이트
function updateMessagePreview(data = null) {
    const template = document.getElementById('message-template').value;
    const customMessage = document.getElementById('custom-message').value;
    const previewElement = document.getElementById('message-preview');
    
    let messageTemplate;
    
    if (template === 'custom') {
        try {
            messageTemplate = JSON.parse(customMessage);
        } catch (error) {
            previewElement.textContent = 'JSON 형식 오류: ' + error.message;
            return;
        }
    } else {
        messageTemplate = messageTemplates[template];
    }
    
    // 샘플 데이터 사용 (실제 데이터가 없을 경우)
    const sampleData = data || {
        score: 750,
        completed_missions: 23,
        active_riders: 31,
        estimated_income: 90000,
        score_change: '+25',
        mission_change: '+3',
        riders_change: '+2',
        income_change: '+15000',
        timestamp: new Date().toLocaleString('ko-KR'),
        next_update: new Date(Date.now() + 1800000).toLocaleString('ko-KR'),
        peak_performance: 92,
        avg_response_time: 3.5,
        goal_achievement: 87
    };
    
    // 템플릿 변수 치환
    let content = messageTemplate.content;
    Object.keys(sampleData).forEach(key => {
        const regex = new RegExp(`{${key}}`, 'g');
        content = content.replace(regex, sampleData[key]);
    });
    
    let footer = messageTemplate.footer;
    Object.keys(sampleData).forEach(key => {
        const regex = new RegExp(`{${key}}`, 'g');
        footer = footer.replace(regex, sampleData[key]);
    });
    
    previewElement.innerHTML = `
        <strong>${messageTemplate.title}</strong><br><br>
        ${content.replace(/\n/g, '<br>')}<br><br>
        <em>${footer}</em>
    `;
}

// 메시지 설정 저장
function saveMessageSettings() {
    messageSettings = {
        template: document.getElementById('message-template').value,
        sendOnChange: document.getElementById('send-on-change').checked,
        sendOnSchedule: document.getElementById('send-on-schedule').checked,
        sendOnAlert: document.getElementById('send-on-alert').checked,
        customMessage: document.getElementById('custom-message').value
    };
    
    // 로컬 스토리지에 저장
    localStorage.setItem('grider-message-settings', JSON.stringify(messageSettings));
    
    showNotification('메시지 설정이 저장되었습니다.', 'success');
    
    // GitHub에 설정 파일 업데이트 (실제 구현에서는 API 호출)
    updateMessageConfig();
}

// 메시지 설정 로드
function loadMessageSettings() {
    const saved = localStorage.getItem('grider-message-settings');
    if (saved) {
        messageSettings = JSON.parse(saved);
        
        document.getElementById('message-template').value = messageSettings.template;
        document.getElementById('send-on-change').checked = messageSettings.sendOnChange;
        document.getElementById('send-on-schedule').checked = messageSettings.sendOnSchedule;
        document.getElementById('send-on-alert').checked = messageSettings.sendOnAlert;
        document.getElementById('custom-message').value = messageSettings.customMessage || '';
    }
}

// 테스트 메시지 전송
async function testMessage() {
    showNotification('테스트 메시지를 전송 중입니다...', 'info');
    
    try {
        // 실제로는 GitHub Actions를 트리거하거나 API 호출
        await simulateMessageSend();
        showNotification('테스트 메시지가 성공적으로 전송되었습니다!', 'success');
    } catch (error) {
        showNotification('테스트 메시지 전송에 실패했습니다.', 'error');
    }
}

// 메시지 전송 시뮬레이션
function simulateMessageSend() {
    return new Promise((resolve) => {
        setTimeout(resolve, 2000); // 2초 후 성공
    });
}

// 알림 표시
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;

    document.body.appendChild(notification);

    // Fade in
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateY(0)';
    }, 10);

    // Fade out and remove
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateY(-20px)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// 활동 새로고침
function refreshActivity() {
    const button = event.target.closest('button');
    const icon = button.querySelector('i');
    
    icon.style.animation = 'spin 1s ease-in-out';
    setTimeout(() => {
        icon.style.animation = '';
        refreshData();
    }, 1000);
}

// 차트 시간 범위 변경
function changeTimeRange(range) {
    // 버튼 활성화 상태 변경
    document.querySelectorAll('.chart-controls .btn-small').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // 차트 데이터 업데이트 (실제로는 다른 데이터 로드)
    console.log(`차트 시간 범위 변경: ${range}`);
    refreshData();
}

// 숫자 포맷팅
function formatNumber(num) {
    if (typeof num !== 'number') return num;
    return num.toLocaleString('ko-KR');
}

// 메시지 설정 업데이트 (GitHub Actions용)
async function updateMessageConfig() {
    // 실제 구현에서는 GitHub API를 통해 설정 파일 업데이트
    const config = {
        message_settings: messageSettings,
        updated_at: new Date().toISOString()
    };
    
    console.log('메시지 설정 업데이트:', config);
    
    // 로컬에서는 파일로 저장 시뮬레이션
    try {
        // GitHub Actions에서 읽을 수 있도록 JSON 파일 생성
        const blob = new Blob([JSON.stringify(config, null, 2)], 
                             {type: 'application/json'});
        console.log('설정 파일 생성됨');
    } catch (error) {
        console.error('설정 파일 생성 실패:', error);
    }
}

// 페이지 언로드 시 설정 저장
window.addEventListener('beforeunload', () => {
    if (messageSettings) {
        localStorage.setItem('grider-message-settings', JSON.stringify(messageSettings));
    }
});

// 키보드 단축키
document.addEventListener('keydown', (e) => {
    // Ctrl + R: 데이터 새로고침
    if (e.ctrlKey && e.key === 'r') {
        e.preventDefault();
        refreshData();
    }
    
    // Ctrl + S: 설정 저장
    if (e.ctrlKey && e.key === 's') {
        e.preventDefault();
        saveMessageSettings();
    }
});

// 차트 반응형 처리
window.addEventListener('resize', () => {
    if (performanceChart) performanceChart.resize();
    if (missionChart) missionChart.resize();
});

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', refreshData);

console.log('🌟 G라이더 대시보드 JavaScript 로드 완료'); 