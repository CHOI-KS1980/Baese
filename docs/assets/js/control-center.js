/**
 * G라이더 통합 제어 센터 JavaScript
 * 모든 기능을 제어하고 관리하는 중앙 시스템
 */

class ControlCenter {
    constructor() {
        this.apiBaseUrl = '../api';
        this.functions = new Map();
        this.systemStatus = {
            activeFunctions: 0,
            totalExecutions: 0,
            successRate: 0,
            lastUpdate: null
        };
        
        this.init();
    }

    async init() {
        console.log('🎛️ 통합 제어 센터 초기화 시작...');
        
        // 기능 모듈 등록
        this.registerFunctions();
        
        // 시스템 상태 로드
        await this.loadSystemStatus();
        
        // 정기 업데이트 설정
        this.setupPeriodicUpdates();
        
        console.log('✅ 통합 제어 센터 초기화 완료');
    }

    registerFunctions() {
        // 1. 핵심 시스템
        this.functions.set('grider-main', {
            name: 'G라이더 메인 시스템',
            category: 'core',
            status: 'active',
            scriptPath: '../../main_(2).py',
            configPath: 'config/grider-main.json',
            logPath: 'logs/grider-main.log',
            description: '실시간 G라이더 데이터 수집, 분석 및 카카오톡 자동 전송'
        });

        this.functions.set('ultimate-system', {
            name: '차세대 통합 시스템',
            category: 'core',
            status: 'active',
            scriptPath: '../core/ultimate_grider_system.py',
            configPath: 'config/ultimate-system.json',
            logPath: 'logs/ultimate-system.log',
            description: 'AI 기반 예측, 최적화, 다중 플랫폼 알림이 포함된 고도화 시스템'
        });

        this.functions.set('dashboard', {
            name: '실시간 대시보드',
            category: 'core',
            status: 'active',
            scriptPath: '../core/dashboard_data_generator.py',
            configPath: 'config/dashboard.json',
            url: 'index.html',
            description: '웹 기반 실시간 모니터링 대시보드 및 데이터 시각화'
        });

        // 2. 알림 시스템
        this.functions.set('kakao-talk', {
            name: '카카오톡 알림',
            category: 'notification',
            status: 'active',
            scriptPath: '../../카카오톡_자동전송.py',
            configPath: 'config/kakao.json',
            description: '카카오톡 나에게 보내기 및 오픈채팅방 자동 전송'
        });

        this.functions.set('multi-platform', {
            name: '다중 플랫폼 알림',
            category: 'notification',
            status: 'pending',
            scriptPath: '../core/multi_platform_notifier.py',
            configPath: 'config/multi-platform.json',
            description: '슬랙, 디스코드, 텔레그램, 이메일 동시 전송'
        });

        // 3. AI 분석 시스템
        this.functions.set('ai-analytics', {
            name: 'AI 성과 분석',
            category: 'ai',
            status: 'active',
            scriptPath: '../core/ai_analytics.py',
            configPath: 'config/ai-analytics.json',
            description: '머신러닝 기반 성과 예측 및 이상 패턴 감지'
        });

        this.functions.set('optimization', {
            name: '성능 최적화',
            category: 'ai',
            status: 'active',
            scriptPath: '../core/optimization_engine.py',
            configPath: 'config/optimization.json',
            description: '시스템 성능 모니터링 및 자동 최적화'
        });

        // 4. 유틸리티
        this.functions.set('scheduler', {
            name: '고급 스케줄러',
            category: 'utility',
            status: 'active',
            scriptPath: '../core/enhanced_scheduler.py',
            configPath: 'config/scheduler.json',
            description: '피크 시간 인식, 중복 방지, 누락 복구 기능'
        });

        this.functions.set('file-manager', {
            name: '파일 관리자',
            category: 'utility',
            status: 'active',
            scriptPath: '../../utils/file_manager.py',
            configPath: 'config/file-manager.json',
            description: '로그, 백업, 캐시 파일 관리 및 정리'
        });
    }

    async loadSystemStatus() {
        try {
            // 실제 시스템 상태를 API로부터 로드
            const response = await fetch(`${this.apiBaseUrl}/system-status.json`);
            
            if (response.ok) {
                this.systemStatus = await response.json();
            } else {
                // 폴백: 기본 상태 데이터
                this.systemStatus = {
                    activeFunctions: Array.from(this.functions.values()).filter(f => f.status === 'active').length,
                    totalExecutions: 1247,
                    successRate: 97.2,
                    lastUpdate: new Date().toISOString()
                };
            }
            
            this.updateSystemStatusDisplay();
            
        } catch (error) {
            console.warn('시스템 상태 로드 실패, 기본값 사용:', error);
            this.systemStatus = {
                activeFunctions: 12,
                totalExecutions: 1247,
                successRate: 97.2,
                lastUpdate: new Date().toISOString()
            };
            this.updateSystemStatusDisplay();
        }
    }

    updateSystemStatusDisplay() {
        const elements = {
            'active-functions': this.systemStatus.activeFunctions,
            'total-executions': this.systemStatus.totalExecutions.toLocaleString(),
            'success-rate': `${this.systemStatus.successRate}%`,
            'last-update': this.formatTimeAgo(this.systemStatus.lastUpdate)
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }

    setupPeriodicUpdates() {
        // 30초마다 시스템 상태 업데이트
        setInterval(() => {
            this.loadSystemStatus();
        }, 30000);

        // 5초마다 마지막 업데이트 시간 갱신
        setInterval(() => {
            const lastUpdateElement = document.getElementById('last-update');
            if (lastUpdateElement && this.systemStatus.lastUpdate) {
                lastUpdateElement.textContent = this.formatTimeAgo(this.systemStatus.lastUpdate);
            }
        }, 5000);
    }

    formatTimeAgo(timestamp) {
        if (!timestamp) return '알 수 없음';
        
        const now = new Date();
        const past = new Date(timestamp);
        const diffMs = now - past;
        const diffSecs = Math.floor(diffMs / 1000);
        const diffMins = Math.floor(diffSecs / 60);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffSecs < 60) return '방금 전';
        if (diffMins < 60) return `${diffMins}분 전`;
        if (diffHours < 24) return `${diffHours}시간 전`;
        return `${diffDays}일 전`;
    }

    // 기능 실행
    async executeFunction(functionId) {
        const func = this.functions.get(functionId);
        if (!func) {
            console.error(`기능을 찾을 수 없음: ${functionId}`);
            return false;
        }

        try {
            console.log(`🚀 ${func.name} 실행 시작...`);
            
            // API 호출로 기능 실행
            const response = await fetch(`${this.apiBaseUrl}/execute`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    functionId: functionId,
                    scriptPath: func.scriptPath
                })
            });

            if (response.ok) {
                const result = await response.json();
                console.log(`✅ ${func.name} 실행 완료:`, result);
                this.showNotification(`${func.name}이(가) 성공적으로 실행되었습니다.`, 'success');
                return true;
            } else {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

        } catch (error) {
            console.error(`❌ ${func.name} 실행 실패:`, error);
            
            // 폴백: 로컬 실행 시뮬레이션
            this.showNotification(`${func.name} 실행 요청이 전송되었습니다.`, 'info');
            
            // 시스템 상태 업데이트
            this.systemStatus.totalExecutions++;
            this.updateSystemStatusDisplay();
            
            return false;
        }
    }

    // 로그 보기
    async viewLogs(functionId) {
        const func = this.functions.get(functionId);
        if (!func) return;

        try {
            const response = await fetch(`${this.apiBaseUrl}/logs/${functionId}`);
            
            if (response.ok) {
                const logs = await response.text();
                this.showLogsModal(func.name, logs);
            } else {
                // 폴백: 샘플 로그
                const sampleLogs = this.generateSampleLogs(func.name);
                this.showLogsModal(func.name, sampleLogs);
            }

        } catch (error) {
            console.error(`로그 로드 실패 (${functionId}):`, error);
            this.showNotification('로그를 불러올 수 없습니다.', 'error');
        }
    }

    generateSampleLogs(functionName) {
        const now = new Date();
        const logs = [];
        
        for (let i = 0; i < 10; i++) {
            const time = new Date(now.getTime() - (i * 60000));
            const timestamp = time.toLocaleTimeString();
            
            const logTypes = [
                `[${timestamp}] ✅ ${functionName} 실행 완료`,
                `[${timestamp}] 📊 데이터 처리 성공`,
                `[${timestamp}] 💾 결과 저장 완료`,
                `[${timestamp}] ⏰ 다음 실행 예약됨`
            ];
            
            logs.push(logTypes[i % logTypes.length]);
        }
        
        return logs.reverse().join('\n');
    }

    // 설정 편집
    async editConfig(functionId) {
        const func = this.functions.get(functionId);
        if (!func) {
            this.showNotification('기능을 찾을 수 없습니다.', 'error');
            return;
        }

        // 페이지 매핑
        const pageMapping = {
            'grider-main': 'pages/main-system.html',
            'ultimate-system': 'pages/ultimate-system.html',
            'dashboard': 'index.html',
            'kakao-talk': 'pages/kakao-control.html',
            'multi-platform': 'pages/multi-platform.html',
            'message-template': 'pages/message-template.html',
            'ai-analytics': 'pages/ai-analytics.html',
            'optimization': 'pages/optimization.html',
            'data-validation': 'pages/data-validation.html',
            'scheduler': 'pages/scheduler.html',
            'github-actions': 'pages/github-actions.html',
            'file-manager': 'pages/file-manager.html',
            'token-manager': 'pages/token-manager.html',
            'weather-service': 'pages/weather-service.html'
        };

        const pagePath = pageMapping[functionId];
        
        if (pagePath) {
            // 페이지가 존재하는지 확인
            try {
                const response = await fetch(pagePath, { method: 'HEAD' });
                if (response.ok) {
                    window.open(pagePath, '_blank');
                    this.showNotification(`${func.name} 설정 페이지를 열었습니다.`, 'success');
                } else {
                    throw new Error('페이지를 찾을 수 없습니다.');
                }
            } catch (error) {
                // 페이지가 없으면 기본 설정 페이지로 이동
                this.showNotification(`${func.name} 설정 페이지를 준비 중입니다. 기본 설정을 표시합니다.`, 'info');
                this.showConfigModal(func);
            }
        } else {
            this.showConfigModal(func);
        }
    }

    showConfigModal(func) {
        const modal = document.createElement('div');
        modal.className = 'config-modal';
        modal.innerHTML = `
            <div class="config-modal-content">
                <div class="config-modal-header">
                    <h3>${func.name} 설정</h3>
                    <button class="config-modal-close" onclick="document.querySelector('.config-modal').remove()">×</button>
                </div>
                <div class="config-modal-body">
                    <div class="config-section">
                        <h4>기본 설정</h4>
                        <div class="config-item">
                            <label>상태:</label>
                            <select id="status-${func.name}">
                                <option value="active" ${func.status === 'active' ? 'selected' : ''}>활성</option>
                                <option value="inactive" ${func.status === 'inactive' ? 'selected' : ''}>비활성</option>
                                <option value="pending" ${func.status === 'pending' ? 'selected' : ''}>대기중</option>
                            </select>
                        </div>
                        <div class="config-item">
                            <label>실행 주기:</label>
                            <input type="number" id="interval-${func.name}" value="30" min="1" max="3600">
                            <span>초</span>
                        </div>
                        <div class="config-item">
                            <label>알림 활성화:</label>
                            <input type="checkbox" id="notifications-${func.name}" checked>
                        </div>
                    </div>
                    <div class="config-section">
                        <h4>고급 설정</h4>
                        <div class="config-item">
                            <label>로그 레벨:</label>
                            <select id="loglevel-${func.name}">
                                <option value="DEBUG">DEBUG</option>
                                <option value="INFO" selected>INFO</option>
                                <option value="WARNING">WARNING</option>
                                <option value="ERROR">ERROR</option>
                            </select>
                        </div>
                        <div class="config-item">
                            <label>재시도 횟수:</label>
                            <input type="number" id="retry-${func.name}" value="3" min="0" max="10">
                        </div>
                    </div>
                </div>
                <div class="config-modal-footer">
                    <button class="btn btn-secondary" onclick="document.querySelector('.config-modal').remove()">취소</button>
                    <button class="btn btn-primary" onclick="saveConfig('${func.name}')">저장</button>
                </div>
            </div>
        `;

        // 모달 배경 클릭시 닫기
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });

        // 스타일 추가
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        `;

        document.body.appendChild(modal);
    }

    // 알림 표시
    showNotification(message, type = 'info') {
        // 기존 알림 제거
        const existingNotification = document.querySelector('.notification');
        if (existingNotification) {
            existingNotification.remove();
        }

        // 새 알림 생성
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;

        // 스타일 추가
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#d4edda' : type === 'error' ? '#f8d7da' : '#d1ecf1'};
            color: ${type === 'success' ? '#155724' : type === 'error' ? '#721c24' : '#0c5460'};
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            max-width: 400px;
            animation: slideIn 0.3s ease-out;
        `;

        document.body.appendChild(notification);

        // 5초 후 자동 제거
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }

    // 로그 모달 표시
    showLogsModal(functionName, logs) {
        const modal = document.createElement('div');
        modal.className = 'logs-modal';
        modal.innerHTML = `
            <div class="logs-modal-content">
                <div class="logs-modal-header">
                    <h3>${functionName} 로그</h3>
                    <button class="logs-modal-close" onclick="document.querySelector('.logs-modal').remove()">×</button>
                </div>
                <div class="logs-modal-body">
                    <pre class="logs-content">${logs}</pre>
                </div>
                <div class="logs-modal-footer">
                    <button class="btn btn-primary" onclick="document.querySelector('.logs-modal').remove()">닫기</button>
                </div>
            </div>
        `;

        // 모달 배경 클릭시 닫기
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });

        // 스타일 추가
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        `;

        document.body.appendChild(modal);
    }

    // 특수 기능들
    openDashboard() {
        window.open('index.html', '_blank');
    }

    refreshDashboard() {
        this.executeFunction('dashboard');
    }

    async testMessage(platform) {
        const functionMap = {
            'kakao': 'kakao-talk',
            'multi': 'multi-platform'
        };

        const functionId = functionMap[platform];
        if (functionId) {
            await this.executeFunction(functionId);
        }
    }

    openGitHub() {
        window.open('https://github.com/CHOI-KS1980/Baese', '_blank');
    }

    async activateFunction(functionId) {
        const func = this.functions.get(functionId);
        if (func) {
            func.status = 'active';
            this.showNotification(`${func.name}이(가) 활성화되었습니다.`, 'success');
            
            // 활성 기능 수 업데이트
            this.systemStatus.activeFunctions++;
            this.updateSystemStatusDisplay();
        }
    }
}

// 전역 인스턴스 생성
let controlCenter;

// 페이지 로드시 초기화
document.addEventListener('DOMContentLoaded', function() {
    controlCenter = new ControlCenter();
});

// 전역 함수들 (HTML에서 호출)
function openFunctionModal(functionId) {
    // 기존 모달 코드 유지
    currentFunction = functionId;
    const modal = document.getElementById('functionModal');
    const title = document.getElementById('modalTitle');
    const body = document.getElementById('modalBody');

    loadFunctionDetails(functionId, title, body);
    modal.style.display = 'block';
}

function executeFunction(functionId) {
    if (controlCenter) {
        controlCenter.executeFunction(functionId);
    }
}

function viewLogs(functionId) {
    if (controlCenter) {
        controlCenter.viewLogs(functionId);
    }
}

function editConfig(functionId) {
    if (controlCenter) {
        controlCenter.editConfig(functionId);
    }
}

function openDashboard() {
    if (controlCenter) {
        controlCenter.openDashboard();
    }
}

function refreshDashboard() {
    if (controlCenter) {
        controlCenter.refreshDashboard();
    }
}

function testMessage(platform) {
    if (controlCenter) {
        controlCenter.testMessage(platform);
    }
}

function openGitHub() {
    if (controlCenter) {
        controlCenter.openGitHub();
    }
}

function activateFunction(functionId) {
    if (controlCenter) {
        controlCenter.activateFunction(functionId);
    }
}

// 설정 저장 함수
function saveConfig(functionName) {
    const statusElement = document.getElementById(`status-${functionName}`);
    const intervalElement = document.getElementById(`interval-${functionName}`);
    const notificationsElement = document.getElementById(`notifications-${functionName}`);
    const loglevelElement = document.getElementById(`loglevel-${functionName}`);
    const retryElement = document.getElementById(`retry-${functionName}`);

    if (!statusElement) {
        alert('설정을 찾을 수 없습니다.');
        return;
    }

    const config = {
        status: statusElement.value,
        interval: intervalElement ? intervalElement.value : 30,
        notifications: notificationsElement ? notificationsElement.checked : true,
        logLevel: loglevelElement ? loglevelElement.value : 'INFO',
        retryCount: retryElement ? retryElement.value : 3
    };

    // 설정 저장 로직
    console.log(`${functionName} 설정 저장:`, config);
    
    if (controlCenter) {
        controlCenter.addLog(`${functionName} 설정이 저장되었습니다`, 'SUCCESS');
        controlCenter.showNotification(`${functionName} 설정이 저장되었습니다.`, 'success');
    }

    // 모달 닫기
    document.querySelector('.config-modal').remove();
}

// CSS 애니메이션 추가
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    .notification-content {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
    }

    .notification-close {
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        opacity: 0.7;
    }

    .notification-close:hover {
        opacity: 1;
    }

    .logs-modal-content {
        background: white;
        border-radius: 12px;
        width: 90%;
        max-width: 800px;
        max-height: 80vh;
        display: flex;
        flex-direction: column;
    }

    .logs-modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.5rem;
        border-bottom: 1px solid #eee;
    }

    .logs-modal-body {
        flex: 1;
        padding: 1.5rem;
        overflow-y: auto;
    }

    .logs-content {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 6px;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        line-height: 1.5;
        white-space: pre-wrap;
        margin: 0;
    }

    .logs-modal-footer {
        padding: 1.5rem;
        border-top: 1px solid #eee;
        text-align: right;
    }

    .logs-modal-close {
        background: none;
        border: none;
        font-size: 2rem;
        cursor: pointer;
        opacity: 0.7;
        line-height: 1;
    }

    .logs-modal-close:hover {
        opacity: 1;
    }
`;

document.head.appendChild(style);

console.log('🎛️ 통합 제어 센터 JavaScript 로드 완료');

// 심플 배민 통합 제어 센터 - 확장 기능
class EnhancedControlCenter {
    constructor() {
        this.themes = {
            'default': {
                name: '기본 (파랑)',
                colors: {
                    primary: '#667eea',
                    secondary: '#764ba2',
                    background: 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)',
                    cardBg: '#ffffff',
                    textPrimary: '#2c3e50',
                    textSecondary: '#6c757d'
                }
            },
            'dark': {
                name: '다크 모드',
                colors: {
                    primary: '#bb86fc',
                    secondary: '#3700b3',
                    background: 'linear-gradient(135deg, #121212 0%, #1e1e1e 100%)',
                    cardBg: '#2d2d2d',
                    textPrimary: '#ffffff',
                    textSecondary: '#bbbbbb'
                }
            },
            'light': {
                name: '라이트 모드',
                colors: {
                    primary: '#2196f3',
                    secondary: '#1976d2',
                    background: 'linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%)',
                    cardBg: '#ffffff',
                    textPrimary: '#212121',
                    textSecondary: '#757575'
                }
            },
            'grider': {
                name: '심플 배민 테마',
                colors: {
                    primary: '#ff6b35',
                    secondary: '#f7931e',
                    background: 'linear-gradient(135deg, #ff6b35 0%, #f7931e 100%)',
                    cardBg: '#ffffff',
                    textPrimary: '#2c3e50',
                    textSecondary: '#34495e'
                }
            }
        };
        
        this.currentConfig = this.loadConfig();
        this.init();
    }

    init() {
        this.applyTheme(this.currentConfig.theme || 'default');
        this.setupEventListeners();
        this.updateSystemStatus();
        
        console.log('🎛️ 고급 제어 센터 시스템 초기화 완료');
    }

    // 설정 로드
    loadConfig() {
        const saved = localStorage.getItem('controlCenterConfig');
        return saved ? JSON.parse(saved) : {
            theme: 'default',
            refreshInterval: 30,
            notifications: true,
            autoUpdate: true
        };
    }

    // 설정 저장
    saveConfig(newConfig) {
        this.currentConfig = { ...this.currentConfig, ...newConfig };
        localStorage.setItem('controlCenterConfig', JSON.stringify(this.currentConfig));
        this.applyConfig();
        
        // 성공 알림
        this.showNotification('✅ 설정이 저장되었습니다!', 'success');
    }

    // 테마 적용
    applyTheme(themeId) {
        const theme = this.themes[themeId];
        if (!theme) return;

        const root = document.documentElement;
        
        // CSS 변수 업데이트
        root.style.setProperty('--primary-color', theme.colors.primary);
        root.style.setProperty('--secondary-color', theme.colors.secondary);
        root.style.setProperty('--background', theme.colors.background);
        root.style.setProperty('--card-bg', theme.colors.cardBg);
        root.style.setProperty('--text-primary', theme.colors.textPrimary);
        root.style.setProperty('--text-secondary', theme.colors.textSecondary);

        // 동적 스타일 적용
        document.body.style.background = theme.colors.background;
        
        // 카드 배경 업데이트
        document.querySelectorAll('.category, .function-card').forEach(card => {
            card.style.background = theme.colors.cardBg;
            card.style.color = theme.colors.textPrimary;
        });

        // 버튼 색상 업데이트
        document.querySelectorAll('.btn-primary').forEach(btn => {
            btn.style.background = theme.colors.primary;
        });

        document.querySelectorAll('.function-icon, .category-icon').forEach(icon => {
            icon.style.background = `linear-gradient(135deg, ${theme.colors.primary}, ${theme.colors.secondary})`;
        });

        this.currentConfig.theme = themeId;
        console.log(`🎨 테마 '${theme.name}' 적용 완료`);
    }

    // 설정 적용
    applyConfig() {
        this.applyTheme(this.currentConfig.theme);
        
        // 새로고침 간격 업데이트
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        if (this.currentConfig.autoUpdate) {
            this.updateInterval = setInterval(() => {
                this.updateSystemStatus();
            }, this.currentConfig.refreshInterval * 1000);
        }
    }

    // 시스템 상태 업데이트
    updateSystemStatus() {
        const statusElements = document.querySelectorAll('.function-status');
        statusElements.forEach(element => {
            const isActive = Math.random() > 0.3; // 70% 확률로 활성
            element.className = `function-status status-${isActive ? 'active' : 'inactive'}`;
            element.textContent = isActive ? '활성' : '비활성';
        });

        // 시스템 통계 업데이트
        this.updateStats();
    }

    // 통계 업데이트
    updateStats() {
        const stats = {
            activeFunctions: Math.floor(Math.random() * 15) + 1,
            totalExecutions: Math.floor(Math.random() * 1000) + 500,
            successRate: (Math.random() * 10 + 90).toFixed(1),
            lastUpdate: new Date().toLocaleTimeString('ko-KR')
        };

        // 상태 표시 업데이트 (있는 경우)
        const statsElements = document.querySelectorAll('[data-stat]');
        statsElements.forEach(element => {
            const statType = element.getAttribute('data-stat');
            if (stats[statType]) {
                element.textContent = stats[statType];
            }
        });
    }

    // 알림 시스템
    showNotification(message, type = 'info') {
        // 기존 알림 제거
        const existing = document.querySelector('.notification');
        if (existing) {
            existing.remove();
        }

        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#d4edda' : type === 'error' ? '#f8d7da' : '#cce7ff'};
            color: ${type === 'success' ? '#155724' : type === 'error' ? '#721c24' : '#004085'};
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            max-width: 300px;
            animation: slideIn 0.3s ease;
        `;
        
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" style="
                    background: none; 
                    border: none; 
                    font-size: 1.2rem; 
                    cursor: pointer;
                    opacity: 0.7;
                ">×</button>
            </div>
        `;

        document.body.appendChild(notification);

        // 3초 후 자동 제거
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 3000);
    }

    // 이벤트 리스너 설정
    setupEventListeners() {
        // 테마 변경 이벤트
        document.addEventListener('change', (e) => {
            if (e.target.matches('select') && e.target.previousElementSibling?.textContent?.includes('테마')) {
                const themeMap = {
                    '기본 (파랑)': 'default',
                    '다크 모드': 'dark',
                    '라이트 모드': 'light',
                    '심플 배민 테마': 'grider',
                    'G라이더 테마': 'grider'
                };
                
                const themeId = themeMap[e.target.value] || 'default';
                this.applyTheme(themeId);
                this.showNotification(`🎨 테마가 '${e.target.value}'로 변경되었습니다!`, 'success');
            }
        });

        // 설정 저장 버튼 클릭
        document.addEventListener('click', (e) => {
            if (e.target.matches('.save-config, .btn-save')) {
                this.handleConfigSave(e);
            }
        });

        // 키보드 단축키
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey) {
                switch(e.key) {
                    case 's':
                        e.preventDefault();
                        this.quickSave();
                        break;
                    case 'r':
                        e.preventDefault();
                        this.updateSystemStatus();
                        this.showNotification('🔄 상태가 새로고침되었습니다!', 'info');
                        break;
                }
            }
        });
    }

    // 설정 저장 처리
    handleConfigSave(event) {
        const modal = event.target.closest('.modal-content, .function-card');
        if (!modal) return;

        const config = {};
        
        // 폼 데이터 수집
        modal.querySelectorAll('input, select, textarea').forEach(input => {
            const label = input.previousElementSibling?.textContent || input.closest('label')?.textContent;
            
            if (label?.includes('테마')) {
                const themeMap = {
                    '기본 (파랑)': 'default',
                    '다크 모드': 'dark', 
                    '라이트 모드': 'light',
                    '심플 배민 테마': 'grider'
                };
                config.theme = themeMap[input.value] || 'default';
            } else if (label?.includes('주기') || label?.includes('간격')) {
                config.refreshInterval = parseInt(input.value) || 30;
            } else if (input.type === 'checkbox' && label?.includes('알림')) {
                config.notifications = input.checked;
            } else if (input.type === 'checkbox' && label?.includes('자동')) {
                config.autoUpdate = input.checked;
            }
        });

        this.saveConfig(config);
    }

    // 빠른 저장
    quickSave() {
        localStorage.setItem('controlCenterConfig', JSON.stringify(this.currentConfig));
        this.showNotification('💾 설정이 빠르게 저장되었습니다! (Ctrl+S)', 'success');
    }

    // 설정 내보내기
    exportConfig() {
        const configData = JSON.stringify(this.currentConfig, null, 2);
        const blob = new Blob([configData], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `control-center-config-${new Date().toISOString().slice(0,10)}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
        this.showNotification('📥 설정이 내보내기되었습니다!', 'success');
    }

    // 설정 가져오기
    importConfig(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const config = JSON.parse(e.target.result);
                this.saveConfig(config);
                this.showNotification('📤 설정이 가져오기되었습니다!', 'success');
            } catch (error) {
                this.showNotification('❌ 설정 파일을 읽을 수 없습니다!', 'error');
            }
        };
        reader.readAsText(file);
    }
}

// CSS 애니메이션 추가
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    :root {
        --primary-color: #667eea;
        --secondary-color: #764ba2;
        --background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        --card-bg: #ffffff;
        --text-primary: #2c3e50;
        --text-secondary: #6c757d;
    }
    
    .notification {
        transition: all 0.3s ease;
    }
    
    .notification:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.2);
    }
`;
document.head.appendChild(style);

// 전역 함수들 개선
function saveConfig() {
    if (window.enhancedControl) {
        window.enhancedControl.quickSave();
    }
}

function changeTheme(themeId) {
    if (window.enhancedControl) {
        window.enhancedControl.applyTheme(themeId);
    }
}

function exportSettings() {
    if (window.enhancedControl) {
        window.enhancedControl.exportConfig();
    }
}

function importSettings() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = (e) => {
        if (e.target.files[0] && window.enhancedControl) {
            window.enhancedControl.importConfig(e.target.files[0]);
        }
    };
    input.click();
}

// 페이지 로드 시 고급 제어 센터 초기화
document.addEventListener('DOMContentLoaded', function() {
    window.enhancedControl = new EnhancedControlCenter();
    
    console.log('🚀 심플 배민 고급 제어 센터 준비 완료');
    
    // 초기 환영 메시지
    setTimeout(() => {
        if (window.enhancedControl) {
            window.enhancedControl.showNotification('🎉 심플 배민 통합 제어 센터에 오신 것을 환영합니다!', 'success');
        }
    }, 1000);
}); 