/**
 * OneBailey - 예측 히스토리 페이지
 */

document.addEventListener('DOMContentLoaded', function () {
    buildMonthFilter();
    loadHistory();

    document.getElementById('monthFilter').addEventListener('change', function () {
        loadHistory(this.value);
    });
});

// ============================================
// 월별 필터 생성
// ============================================
function buildMonthFilter() {
    const select = document.getElementById('monthFilter');
    const now = new Date();

    // 최근 6개월 옵션 생성
    for (let i = 0; i < 6; i++) {
        const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
        const value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
        const label = `${d.getFullYear()}년 ${d.getMonth() + 1}월`;
        const option = document.createElement('option');
        option.value = value;
        option.textContent = label;
        select.appendChild(option);
    }
}

// ============================================
// 히스토리 로드
// ============================================
async function loadHistory(month) {
    const listEl = document.getElementById('historyList');
    listEl.innerHTML = '<div class="loading-text">로딩 중...</div>';

    try {
        let url = '/api/predictions/history/all';
        if (month) url += `?month=${month}`;

        const res = await fetch(url);
        if (!res.ok) throw new Error('데이터를 불러올 수 없습니다');

        const data = await res.json();
        renderStats(data.stats, data.total);
        renderList(data.items);
    } catch (e) {
        console.error(e);
        listEl.innerHTML = '<div class="loading-text">데이터를 불러올 수 없습니다.</div>';
    }
}

// ============================================
// 통계 렌더링
// ============================================
function renderStats(stats, total) {
    document.getElementById('statTotal').textContent = total;
    document.getElementById('statCorrect').textContent = stats.correct;
    document.getElementById('statAccuracy').textContent = stats.accuracy + '%';
}

// ============================================
// 리스트 렌더링
// ============================================
function renderList(items) {
    const listEl = document.getElementById('historyList');

    if (!items || items.length === 0) {
        listEl.innerHTML = '<div class="loading-text">예측 기록이 없습니다.</div>';
        return;
    }

    listEl.innerHTML = items.map(item => {
        const isUp = item.direction === 'UP';
        const dirIcon = isUp ? '📈' : '📉';
        const dirClass = isUp ? 'up' : 'down';

        let resultHtml = '';
        if (item.is_correct === true) {
            resultHtml = `<span class="result-badge correct">✅ 적중</span>`;
        } else if (item.is_correct === false) {
            resultHtml = `<span class="result-badge wrong">❌ 미적중</span>`;
        } else {
            resultHtml = `<span class="result-badge pending">⏳ 대기</span>`;
        }

        let changeHtml = '';
        if (item.actual_change !== null && item.actual_change !== undefined) {
            const sign = item.actual_change >= 0 ? '+' : '';
            const changeClass = item.actual_change >= 0 ? 'positive' : 'negative';
            changeHtml = `<span class="change ${changeClass}">${sign}${item.actual_change.toFixed(2)}%</span>`;
        }

        return `
            <div class="history-item" onclick="window.location.href='/detail.html?date=${item.date_iso}'">
                <div class="item-left">
                    <div class="item-date">${item.date}</div>
                    <div class="item-summary">${item.summary || ''}</div>
                </div>
                <div class="item-right">
                    <div class="item-direction ${dirClass}">
                        <span>${dirIcon}</span>
                        <span>${item.direction_text}</span>
                        <span class="item-confidence">${item.confidence_percent}%</span>
                    </div>
                    <div class="item-result">
                        ${resultHtml}
                        ${changeHtml}
                    </div>
                </div>
            </div>
        `;
    }).join('');
}
