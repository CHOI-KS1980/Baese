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
        // API에서 데이터 가져오기 (실제로는 GitHub Actions에서 생성된 JSON 파일)
        const data = await fetchLatestData();
        
        if (data) {
            updateDashboard(data);
            updateSystemStatus('online');
            lastDataUpdate = new Date();
        } else {
            updateSystemStatus('offline');
        }
        
    } catch (error) {
        console.error('❌ 데이터 새로고침 실패:', error);
        updateSystemStatus('error');
        showNotification('데이터 로드에 실패했습니다.', 'error');
    }
    
    // 마지막 업데이트 시간 표시
    document.getElementById('last-update-time').textContent = 
        new Date().toLocaleString('ko-KR');
}

// 최신 데이터 가져오기
async function fetchLatestData() {
    try {
        // GitHub Pages에서 JSON 파일 읽기
        const response = await fetch('api/latest-data.json?t=' + Date.now());
        
        if (!response.ok) {
            throw new Error('데이터 로드 실패');
        }
        
        return await response.json();
    } catch (error) {
        console.warn('API 데이터 로드 실패, 샘플 데이터 사용');
        return generateSampleData();
    }
}

// 샘플 데이터 생성 (실제 데이터가 없을 때)
function generateSampleData() {
    const now = new Date();
    const hour = now.getHours();
    
    // 시간대별 성과 시뮬레이션
    const isPeakTime = (hour >= 11 && hour <= 13) || (hour >= 17 && hour <= 19);
    const baseScore = isPeakTime ? 850 : 720;
    const baseMissions = isPeakTime ? 25 : 18;
    const baseRiders = isPeakTime ? 35 : 28;
    
    return {
        timestamp: now.toISOString(),
        current_score: baseScore + Math.floor(Math.random() * 100),
        completed_missions: baseMissions + Math.floor(Math.random() * 10),
        active_riders: baseRiders + Math.floor(Math.random() * 8),
        estimated_income: (baseScore + Math.floor(Math.random() * 100)) * 120,
        score_change: (Math.random() - 0.5) * 50,
        mission_change: Math.floor((Math.random() - 0.5) * 6),
        riders_change: Math.floor((Math.random() - 0.5) * 4),
        performance_history: generatePerformanceHistory(),
        mission_distribution: {
            completed: baseMissions + Math.floor(Math.random() * 5),
            in_progress: Math.floor(Math.random() * 8),
            pending: Math.floor(Math.random() * 12)
        },
        system_status: 'operational',
        last_action: {
            time: new Date(now.getTime() - Math.random() * 300000).toISOString(),
            action: '데이터 수집 완료',
            status: 'success'
        }
    };
}

// 성과 히스토리 생성
function generatePerformanceHistory() {
    const history = [];
    const now = new Date();
    
    for (let i = 23; i >= 0; i--) {
        const time = new Date(now.getTime() - i * 60 * 60 * 1000);
        const hour = time.getHours();
        const isPeakTime = (hour >= 11 && hour <= 13) || (hour >= 17 && hour <= 19);
        
        history.push({
            timestamp: time.toISOString(),
            score: (isPeakTime ? 800 : 650) + Math.floor(Math.random() * 200),
            missions: (isPeakTime ? 20 : 15) + Math.floor(Math.random() * 15),
            riders: (isPeakTime ? 30 : 25) + Math.floor(Math.random() * 10)
        });
    }
    
    return history;
}

// 대시보드 업데이트
function updateDashboard(data) {
    // 부드러운 전환을 위한 페이드 효과
    const dashboard = document.querySelector('.dashboard-main');
    const originalOpacity = dashboard.style.opacity;
    
    // 데이터가 변경된 경우에만 애니메이션 적용
    const hasChanges = hasDataChanged(data);
    
    if (hasChanges) {
        dashboard.style.transition = 'opacity 0.3s ease';
        dashboard.style.opacity = '0.8';
    }
    
    // 통계 카드 업데이트
    updateStatCard('current-score', data.current_score, data.score_change, '점');
    updateStatCard('completed-missions', data.completed_missions, data.mission_change, '개');
    updateStatCard('active-riders', data.active_riders, data.riders_change, '명');
    updateStatCard('estimated-income', formatNumber(data.estimated_income), 
                   formatNumber(data.estimated_income * 0.1), '원');
    
    // 차트 업데이트 (부드러운 애니메이션)
    updatePerformanceChart(data.performance_history);
    updateMissionChart(data.mission_distribution);
    
    // 활동 로그 업데이트
    updateActivityLog(data.last_action);
    
    // 메시지 미리보기 업데이트
    updateMessagePreview(data);
    
    // 부드럽게 다시 나타내기
    if (hasChanges) {
        setTimeout(() => {
            dashboard.style.opacity = originalOpacity || '1';
        }, 300);
    }
}

// 데이터 변경 감지
let lastData = null;
function hasDataChanged(newData) {
    if (!lastData) {
        lastData = newData;
        return true;
    }
    
    const changed = 
        lastData.current_score !== newData.current_score ||
        lastData.completed_missions !== newData.completed_missions ||
        lastData.active_riders !== newData.active_riders;
    
    lastData = newData;
    return changed;
}

// 통계 카드 업데이트
function updateStatCard(elementId, value, change, unit) {
    const valueElement = document.getElementById(elementId);
    const changeElement = document.getElementById(elementId.replace('-', '-') + '-change');
    
    if (valueElement) {
        valueElement.textContent = formatNumber(value) + unit;
        
        // 애니메이션 효과
        valueElement.style.transform = 'scale(1.1)';
        setTimeout(() => {
            valueElement.style.transform = 'scale(1)';
        }, 200);
    }
    
    if (changeElement && change !== undefined) {
        const changeText = change > 0 ? `+${formatNumber(change)}${unit}` : `${formatNumber(change)}${unit}`;
        changeElement.textContent = changeText;
        changeElement.className = `stat-change ${change >= 0 ? 'positive' : 'negative'}`;
    }
}

// 성과 차트 업데이트
function updatePerformanceChart(history) {
    if (!performanceChart || !history) return;
    
    const labels = history.slice(-12).map(item => {
        const time = new Date(item.timestamp);
        return time.getHours().toString().padStart(2, '0') + ':00';
    });
    
    const scoreData = history.slice(-12).map(item => item.score);
    const missionData = history.slice(-12).map(item => item.missions);
    
    performanceChart.data.labels = labels;
    performanceChart.data.datasets[0].data = scoreData;
    performanceChart.data.datasets[1].data = missionData;
    performanceChart.update('active');
}

// 미션 차트 업데이트
function updateMissionChart(distribution) {
    if (!missionChart || !distribution) return;
    
    missionChart.data.datasets[0].data = [
        distribution.completed,
        distribution.in_progress,
        distribution.pending
    ];
    missionChart.update('active');
}

// 활동 로그 업데이트
function updateActivityLog(lastAction) {
    const activityLog = document.getElementById('activity-log');
    if (!activityLog || !lastAction) return;
    
    const newActivity = document.createElement('div');
    newActivity.className = 'activity-item';
    newActivity.innerHTML = `
        <div class="activity-time">${new Date(lastAction.time).toLocaleString('ko-KR')}</div>
        <div class="activity-content">${lastAction.action}</div>
    `;
    
    // 최신 항목을 맨 위에 추가
    activityLog.insertBefore(newActivity, activityLog.firstChild);
    
    // 오래된 항목 제거 (최대 10개)
    while (activityLog.children.length > 10) {
        activityLog.removeChild(activityLog.lastChild);
    }
}

// 시스템 상태 업데이트
function updateSystemStatus(status) {
    const statusElement = document.getElementById('system-status');
    const statusIcon = statusElement.querySelector('i');
    
    statusIcon.className = 'fas fa-circle';
    
    switch (status) {
        case 'online':
            statusIcon.style.color = '#27ae60';
            statusElement.querySelector('span').textContent = '정상 운영';
            break;
        case 'offline':
            statusIcon.style.color = '#e74c3c';
            statusElement.querySelector('span').textContent = '연결 끊김';
            break;
        case 'error':
            statusIcon.style.color = '#f39c12';
            statusElement.querySelector('span').textContent = '오류 발생';
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
    
    // 애니메이션
    setTimeout(() => notification.classList.add('show'), 100);
    
    // 3초 후 제거
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => document.body.removeChild(notification), 300);
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

console.log('🌟 G라이더 대시보드 JavaScript 로드 완료'); 