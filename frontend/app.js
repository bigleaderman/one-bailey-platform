/**
 * OneBailey Frontend - API 연동
 */

document.addEventListener('DOMContentLoaded', function() {
    loadPrediction();
});

// 요소 참조
const heroSection = document.getElementById('heroSection');
const predictionDate = document.getElementById('predictionDate');
const heroTitle = document.getElementById('heroTitle');
const heroSubtitle = document.getElementById('heroSubtitle');
const directionText = document.getElementById('directionText');
const directionIcon = document.getElementById('directionIcon');
const confidenceStars = document.getElementById('confidenceStars');
const confidencePercent = document.getElementById('confidencePercent');
const expandBtn = document.getElementById('expandBtn');
const expandContent = document.getElementById('expandContent');
const keyFactorsList = document.getElementById('keyFactorsList');
const riskFactorsList = document.getElementById('riskFactorsList');
const predictionDirection = document.getElementById('predictionDirection');

/**
 * 예측 데이터 로드
 */
async function loadPrediction() {
    try {
        const response = await fetch('/api/predictions/today');
        
        if (!response.ok) {
            throw new Error('데이터를 불러올 수 없습니다');
        }
        
        const data = await response.json();
        updateUI(data);
    } catch (error) {
        console.error('Error loading prediction:', error);
        showError(error.message);
    }
}

/**
 * UI 업데이트
 */
function updateUI(data) {
    // 날짜
    currentPredictionDate = data.date_iso;
    predictionDate.textContent = data.date;
    
    // 방향 판단
    const isUp = data.direction === 'UP';
    const isDown = data.direction === 'DOWN';
    
    // Hero 섹션 스타일
    heroSection.classList.remove('down', 'hold');
    if (isDown) {
        heroSection.classList.add('down');
    } else if (!isUp) {
        heroSection.classList.add('hold');
    }
    
    // Hero 텍스트
    if (isUp) {
        heroTitle.textContent = '오늘 미국 증시는 상승할 것으로 예상돼요 📈';
    } else if (isDown) {
        heroTitle.textContent = '오늘 미국 증시는 하락할 것으로 예상돼요 📉';
    } else {
        heroTitle.textContent = '오늘 미국 증시는 보합세가 예상돼요 📊';
    }
    
    heroSubtitle.textContent = data.summary || '예측 요약 정보가 없습니다.';
    
    // 방향 텍스트 및 아이콘
    directionText.textContent = data.direction_text;
    
    if (isDown) {
        predictionDirection.classList.add('down');
        directionIcon.classList.add('down');
    } else {
        predictionDirection.classList.remove('down');
        directionIcon.classList.remove('down');
    }
    
    // 신뢰도 별점
    const stars = data.confidence_stars || 4;
    let starsHtml = '';
    for (let i = 0; i < 5; i++) {
        if (i < stars) {
            starsHtml += '<span class="star">⭐</span>';
        } else {
            starsHtml += '<span class="star empty">⭐</span>';
        }
    }
    confidenceStars.innerHTML = starsHtml;
    confidencePercent.textContent = `(${data.confidence_percent || Math.round(data.confidence * 100)}%)`;
    
    // 요인 목록
    updateFactorsList(keyFactorsList, data.key_factors, '상승 요인 정보가 없습니다.');
    updateFactorsList(riskFactorsList, data.risk_factors, '리스크 요인 정보가 없습니다.');
}

/**
 * 요인 목록 업데이트
 */
function updateFactorsList(element, factors, emptyMessage) {
    if (factors && factors.length > 0) {
        element.innerHTML = factors.map(f => `<li>${truncateText(f, 100)}</li>`).join('');
    } else {
        element.innerHTML = `<li>${emptyMessage}</li>`;
    }
}

/**
 * 텍스트 자르기
 */
function truncateText(text, maxLength) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

/**
 * 에러 표시
 */
function showError(message) {
    heroTitle.textContent = '데이터를 불러올 수 없습니다';
    heroSubtitle.textContent = message || '잠시 후 다시 시도해주세요.';
    predictionDate.textContent = new Date().toLocaleDateString('ko-KR', {
        year: 'numeric', month: 'long', day: 'numeric'
    });
}

/**
 * 확장/축소 토글
 */
function toggleExpand() {
    expandBtn.classList.toggle('expanded');
    expandContent.classList.toggle('show');
}

/**
 * 상세 페이지로 이동
 */
let currentPredictionDate = null;

function goToDetail() {
    if (currentPredictionDate) {
        window.location.href = `/detail.html?date=${currentPredictionDate}`;
    }
}

// 알림 버튼
document.getElementById('notificationBtn').addEventListener('click', function() {
    alert('알림 기능은 준비 중입니다.');
});
