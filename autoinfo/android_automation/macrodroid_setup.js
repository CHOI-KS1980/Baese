// MacroDroid 카카오톡 자동화 매크로
// 이 코드를 MacroDroid의 JavaScript 액션에 복사하여 사용하세요

// 설정값
const CONFIG = {
    CHAT_ROOM_NAME: "G라이더 미션방",  // 실제 채팅방 이름으로 변경
    RETRY_COUNT: 3,
    WAIT_TIME: 2000
};

// 메인 실행 함수
function executeMacro() {
    try {
        log("🚀 카카오톡 자동 전송 시작");
        
        // 웹훅 변수에서 메시지 가져오기
        const message = getWebhookVariable("message");
        const chatId = getWebhookVariable("chat_id");
        
        if (!message) {
            log("❌ 메시지가 없습니다");
            return false;
        }
        
        log("📝 전송할 메시지: " + message);
        
        // 카카오톡 실행 및 메시지 전송
        return sendKakaoMessage(message);
        
    } catch (error) {
        log("❌ 매크로 실행 오류: " + error.message);
        return false;
    }
}

// 카카오톡 메시지 전송
function sendKakaoMessage(message) {
    try {
        // 1. 카카오톡 앱 실행
        log("📱 카카오톡 실행 중...");
        launchApp("com.kakao.talk");
        sleep(CONFIG.WAIT_TIME);
        
        // 2. 메인 화면으로 이동 (뒤로가기)
        performGlobalAction(GLOBAL_ACTION_BACK);
        sleep(1000);
        
        // 3. 채팅 탭 클릭
        log("💬 채팅 탭 클릭");
        if (!clickText("채팅")) {
            throw new Error("채팅 탭을 찾을 수 없습니다");
        }
        sleep(1500);
        
        // 4. 검색 버튼 클릭
        log("🔍 검색 시작");
        if (!clickDescription("검색")) {
            // 대안: 검색 텍스트 클릭 시도
            if (!clickText("검색")) {
                throw new Error("검색 버튼을 찾을 수 없습니다");
            }
        }
        sleep(1000);
        
        // 5. 채팅방 이름 입력
        log("📝 채팅방 검색: " + CONFIG.CHAT_ROOM_NAME);
        if (!inputText(CONFIG.CHAT_ROOM_NAME)) {
            throw new Error("채팅방 이름 입력 실패");
        }
        sleep(2000);
        
        // 6. 채팅방 클릭
        log("🎯 채팅방 진입");
        if (!clickTextContains(CONFIG.CHAT_ROOM_NAME)) {
            throw new Error("채팅방을 찾을 수 없습니다: " + CONFIG.CHAT_ROOM_NAME);
        }
        sleep(2000);
        
        // 7. 메시지 입력
        log("✍️ 메시지 입력");
        if (!inputText(message)) {
            throw new Error("메시지 입력 실패");
        }
        sleep(1000);
        
        // 8. 전송 버튼 클릭
        log("📤 메시지 전송");
        if (!clickDescription("전송")) {
            // 대안: 전송 텍스트 클릭 시도
            if (!clickText("전송")) {
                throw new Error("전송 버튼을 찾을 수 없습니다");
            }
        }
        
        sleep(1000);
        log("✅ 메시지 전송 완료!");
        
        // 9. 홈으로 돌아가기
        performGlobalAction(GLOBAL_ACTION_HOME);
        
        return true;
        
    } catch (error) {
        log("❌ 메시지 전송 실패: " + error.message);
        
        // 에러 발생시 홈으로 돌아가기
        performGlobalAction(GLOBAL_ACTION_HOME);
        return false;
    }
}

// 유틸리티 함수들
function getWebhookVariable(key) {
    try {
        return getVariable("wv_" + key) || getVariable(key);
    } catch (error) {
        log("⚠️ 변수 가져오기 실패: " + key);
        return null;
    }
}

function log(message) {
    // MacroDroid 로그에 기록
    addToLog(message);
    
    // 디버깅용 토스트 메시지 (옵션)
    // showToast(message, false);
}

function sleep(ms) {
    // MacroDroid wait 함수 사용
    wait(ms);
}

function launchApp(packageName) {
    // MacroDroid 앱 실행
    return launchApplication(packageName);
}

function clickText(text) {
    try {
        return clickOnText(text);
    } catch (error) {
        log("⚠️ 텍스트 클릭 실패: " + text);
        return false;
    }
}

function clickTextContains(text) {
    try {
        return clickOnTextContains(text);
    } catch (error) {
        log("⚠️ 텍스트 포함 클릭 실패: " + text);
        return false;
    }
}

function clickDescription(desc) {
    try {
        return clickOnContentDescription(desc);
    } catch (error) {
        log("⚠️ 설명 클릭 실패: " + desc);
        return false;
    }
}

function inputText(text) {
    try {
        return enterText(text);
    } catch (error) {
        log("⚠️ 텍스트 입력 실패: " + text);
        return false;
    }
}

// 매크로 실행
executeMacro(); 