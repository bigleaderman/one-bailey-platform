/**
 * OneBailey Frontend - API 연동
 */

document.addEventListener('DOMContentLoaded', function() {
    loadHero();
    loadPrediction();
    loadPerformance();
    loadMonthlyTrend();
});

// 요소 참조
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
    
    // QQQ 카드
    const badge = document.getElementById('predictionBadge');
    const summaryEl = document.getElementById('predictionSummary');
    const resultArea = document.getElementById('predictionResult');

    if (!data.is_today) {
        badge.textContent = '어제 예측';
        badge.style.background = '#f3f4f6';
        badge.style.color = '#6b7280';
        directionText.textContent = data.direction_text;
        summaryEl.textContent = data.summary || '';

        // 실제 결과 영역
        if (resultArea && data.actual_direction) {
            resultArea.style.display = 'block';
            const actualText = data.actual_direction === 'UP' ? '상승' : '하락';
            const sign = data.actual_change >= 0 ? '+' : '';
            const changeStr = data.actual_change !== null ? `${sign}${data.actual_change.toFixed(2)}%` : '';
            const correctIcon = data.is_correct ? '✅' : '❌';
            const correctText = data.is_correct ? '적중' : '미적중';
            const correctClass = data.is_correct ? 'correct' : 'wrong';
            resultArea.innerHTML = `
                <div class="result-row ${correctClass}">
                    <span class="result-label">실제</span>
                    <span class="result-value">${actualText} ${changeStr}</span>
                    <span class="result-badge ${correctClass}">${correctIcon} ${correctText}</span>
                </div>
            `;
        }
    } else {
        badge.textContent = '오늘 예측';
        badge.style.background = '';
        badge.style.color = '';
        directionText.textContent = data.direction_text;
        summaryEl.textContent = data.summary || '';
        if (resultArea) resultArea.style.display = 'none';
    }

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
        element.innerHTML = factors.map(f => `<li>${f}</li>`).join('');
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

function toggleDetails() {
    if (currentPredictionDate) {
        window.location.href = `/detail.html?date=${currentPredictionDate}`;
    }
}

// 알림 버튼
document.getElementById('notificationBtn').addEventListener('click', function() {
    alert('알림 기능은 준비 중입니다.');
});

/**
 * Hero 시장 현황 로드
 */
async function loadHero() {
    try {
        const res = await fetch('/api/market/hero');
        if (!res.ok) return;
        const data = await res.json();

        document.getElementById('heroEmoji').textContent = data.emoji;
        document.getElementById('heroTitle').textContent = data.status_text;
        document.getElementById('heroDesc').textContent = data.description;
        document.getElementById('heroActionText').textContent = data.action_guide;

        if (data.data_date) {
            document.getElementById('heroDate').textContent = data.data_date;
        }

        // 상태별 카드 색상
        const card = document.getElementById('heroSection');
        card.classList.remove('fear', 'anxiety', 'stable', 'greed');
        if (data.score < 25) card.classList.add('fear');
        else if (data.score < 40) card.classList.add('anxiety');
        else if (data.score >= 60 && data.score < 75) card.classList.add('stable');
        else if (data.score >= 75) card.classList.add('greed');

        // 행동 가이드가 없으면 숨김
        const actionEl = document.getElementById('heroAction');
        if (!data.action_guide) actionEl.style.display = 'none';
    } catch (e) {
        console.error('Hero error:', e);
    }
}

/**
 * 예측 성과 로드
 */
async function loadPerformance() {
    try {
        const res = await fetch('/api/predictions/history?days=7');
        if (!res.ok) return;
        const data = await res.json();

        // 7일 적중률
        const stats = data.stats;
        document.getElementById('perf7d').textContent =
            stats.total > 0 ? `${stats.accuracy}%` : '-';
        document.getElementById('perf30d').textContent =
            stats.total_30d > 0 ? `${stats.accuracy_30d}%` : '-';

        // 최근 기록 미니 그리드
        const grid = document.getElementById('perfRecent');
        const items = [...data.history].reverse(); // 날짜순
        grid.innerHTML = items.map(item => {
            const icon = item.is_correct === true ? '✅' : item.is_correct === false ? '❌' : '⏳';
            const dir = item.direction === 'UP' ? '↑' : '↓';
            return `
                <div class="perf-item" onclick="window.location.href='/detail.html?date=${item.date}'">
                    <div class="perf-date">${item.date_short}</div>
                    <div class="perf-icon">${icon}</div>
                    <div class="perf-dir">${dir}</div>
                </div>
            `;
        }).join('');
    } catch (e) {
        console.error('Performance error:', e);
    }
}

/**
 * 월간 시장 흐름 로드
 */
async function loadMonthlyTrend() {
    const weeklyList = document.getElementById('weeklyList');
    
    try {
        const response = await fetch('/api/market/monthly-trend');
        
        if (!response.ok) {
            throw new Error('데이터를 불러올 수 없습니다');
        }
        
        const data = await response.json();
        renderMonthlyTrend(data);
    } catch (error) {
        console.error('Error loading monthly trend:', error);
        weeklyList.innerHTML = '<div class="weekly-item"><span class="week-label">데이터 로딩 실패</span></div>';
    }
}

/**
 * 월간 시장 흐름 렌더링
 */
function renderMonthlyTrend(data) {
    const weeklyList = document.getElementById('weeklyList');
    
    // 섹션 타이틀 업데이트
    const sectionTitle = document.querySelector('.monthly-trend-card .section-title');
    if (sectionTitle) {
        sectionTitle.textContent = `📈 ${data.month} 시장 흐름`;
    }
    
    // 주간 아이템 생성
    let html = '';
    
    data.weeks.forEach(week => {
        const directionClass = week.direction.toLowerCase();
        const currentClass = week.is_current_week ? 'current' : '';
        const holdClass = week.direction === 'HOLD' ? 'hold' : '';
        const downClass = week.direction === 'DOWN' ? 'down' : '';
        
        // 방향 아이콘
        let directionIcon = '';
        if (week.direction === 'UP') {
            directionIcon = '📈';
        } else if (week.direction === 'DOWN') {
            directionIcon = '📉';
        } else {
            directionIcon = '➡️';
        }
        
        // 변동률 표시
        let changeText = '';
        if (!week.is_current_week && week.total_change !== 0) {
            const sign = week.total_change > 0 ? '+' : '';
            changeText = `<span class="week-change ${directionClass}">${sign}${week.total_change}%</span>`;
        }
        
        html += `
            <div class="weekly-item ${currentClass} ${downClass} ${holdClass}">
                <span class="week-label">${week.week_label}</span>
                <div class="week-content">
                    <div class="week-direction">
                        <span class="week-direction-icon">${directionIcon}</span>
                        <span class="week-direction-text ${directionClass}">${week.direction_text}</span>
                    </div>
                    <p class="week-summary">${week.summary}</p>
                </div>
                ${changeText}
            </div>
        `;
    });
    
    weeklyList.innerHTML = html;
}