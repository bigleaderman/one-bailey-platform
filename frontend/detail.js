/**
 * OneBailey - 예측 상세 페이지
 */

document.addEventListener('DOMContentLoaded', function () {
    const params = new URLSearchParams(window.location.search);
    const dateParam = params.get('date');

    if (!dateParam) {
        showError('날짜 파라미터가 없습니다.');
        return;
    }

    loadDetail(dateParam);
    loadMarket(dateParam);
    loadDateNews(dateParam);
});

// ============================================
// 예측 상세 로드
// ============================================
async function loadDetail(dateStr) {
    try {
        const res = await fetch(`/api/predictions/date/${dateStr}`);
        if (!res.ok) throw new Error('예측 데이터를 불러올 수 없습니다');
        const data = await res.json();
        renderDetail(data);
    } catch (e) {
        console.error(e);
        showError(e.message);
    }
}

function renderDetail(data) {
    const isUp = data.direction === 'UP';
    const isDown = data.direction === 'DOWN';

    // 헤더 날짜
    document.getElementById('headerDate').textContent = data.date;

    // 요약 카드
    const card = document.getElementById('summaryCard');
    if (isDown) card.classList.add('down');
    else if (!isUp) card.classList.add('hold');

    document.getElementById('summaryIcon').textContent = isUp ? '📈' : isDown ? '📉' : '📊';
    document.getElementById('summaryLabel').textContent = data.direction_text;
    document.getElementById('summaryConfidence').textContent = data.confidence_percent + '%';
    document.getElementById('summaryText').textContent = data.summary;

    // 별점
    const starsEl = document.getElementById('summaryStars');
    let starsHtml = '';
    for (let i = 0; i < 5; i++) {
        starsHtml += i < data.confidence_stars
            ? '<span class="star">⭐</span>'
            : '<span class="star empty">⭐</span>';
    }
    starsEl.innerHTML = starsHtml;

    // 실제 결과
    if (data.actual_direction) {
        const resultEl = document.getElementById('actualResult');
        resultEl.style.display = 'block';
        const badge = document.getElementById('actualBadge');
        const correct = data.is_correct;
        const changeStr = data.actual_change !== null ? `${data.actual_change >= 0 ? '+' : ''}${data.actual_change.toFixed(2)}%` : '';
        const actualText = data.actual_direction === 'UP' ? '상승' : '하락';

        if (correct) {
            badge.className = 'actual-badge correct';
            badge.textContent = `✅ 적중 — 실제 ${actualText} (${changeStr})`;
        } else {
            badge.className = 'actual-badge wrong';
            badge.textContent = `❌ 미적중 — 실제 ${actualText} (${changeStr})`;
        }
    }

    // 복기 분석
    if (data.review) {
        const reviewEl = document.getElementById('reviewSection');
        reviewEl.style.display = 'block';
        document.getElementById('reviewText').innerHTML = formatReview(data.review, data.is_correct);
    }

    // 상승 요인
    const keyFactors = data.key_factors || [];
    document.getElementById('keyCount').textContent = `(${keyFactors.length})`;
    const keyList = document.getElementById('keyFactorsList');
    if (keyFactors.length > 0) {
        keyList.innerHTML = keyFactors.map(f => `<li>${f}</li>`).join('');
    } else {
        keyList.innerHTML = '<li>정보 없음</li>';
    }

    // 리스크 요인
    const riskFactors = data.risk_factors || [];
    document.getElementById('riskCount').textContent = `(${riskFactors.length})`;
    const riskList = document.getElementById('riskFactorsList');
    if (riskFactors.length > 0) {
        riskList.innerHTML = riskFactors.map(f => `<li>${f}</li>`).join('');
    } else {
        riskList.innerHTML = '<li>정보 없음</li>';
    }
}

// ============================================
// 시장 지표 로드
// ============================================
async function loadMarket(dateStr) {
    try {
        const res = await fetch(`/api/market/date/${dateStr}`);
        if (!res.ok) return; // 시장 데이터 없으면 무시
        const data = await res.json();
        renderMarket(data);
    } catch (e) {
        console.error('Market data error:', e);
    }
}

function renderMarket(data) {
    setIndicator('indVix', data.vix_level, '', 0);
    setIndicator('indNq', data.nq_change, '%', 2, true);
    setIndicator('indRate', data.treasury_10y, '%', 3);
    setIndicator('indQqq', data.qqq_price, '', 2, false, '$');
    setIndicator('indDxy', data.dxy_change, '%', 2, true);
    setIndicator('indGold', data.gold_price, '', 0, false, '$');
}

function setIndicator(id, value, suffix, decimals, colorize, prefix) {
    const el = document.getElementById(id);
    if (value === null || value === undefined) {
        el.textContent = '-';
        return;
    }
    const formatted = (prefix || '') + Number(value).toFixed(decimals) + suffix;
    el.textContent = formatted;

    if (colorize) {
        el.classList.remove('positive', 'negative');
        if (value > 0) el.classList.add('positive');
        else if (value < 0) el.classList.add('negative');
    }
}

// ============================================
// 당일 뉴스
// ============================================
async function loadDateNews(dateStr) {
    try {
        const res = await fetch(`/api/market/news?date=${dateStr}`);
        if (!res.ok) return;
        const data = await res.json();

        // 해당 날짜 뉴스만 필터 (또는 최신 뉴스 표시)
        if (!data.items || data.items.length === 0) return;

        const section = document.getElementById('newsSection');
        section.style.display = 'block';

        const container = document.getElementById('detailNewsList');
        container.innerHTML = data.items.map(item => {
            const headline = item.headline_ko || item.headline;
            const summary = item.summary_ko ? `<p class="detail-news-summary">${item.summary_ko}</p>` : '';
            return `
                <div class="detail-news-item">
                    <p class="detail-news-headline">${headline}</p>
                    ${summary}
                    <span class="detail-news-source">${item.source}</span>
                </div>
            `;
        }).join('');
    } catch (e) {
        console.error('News error:', e);
    }
}

// ============================================
// 복기 포맷팅
// ============================================
function formatReview(text, isCorrect) {
    const icon = isCorrect ? '✅' : '❌';
    const labels = isCorrect
        ? ['적중 핵심 이유', '예측대로 작용한 요인', '참고할 교훈']
        : ['미적중 핵심 이유', '과소/과대평가한 요인', '참고할 교훈'];

    // 1. 2. 3. 패턴 파싱 시도
    const numbered = text.match(/\d+\.\s+[^\n]+/g);

    if (numbered && numbered.length >= 2) {
        let html = '<div class="review-items">';
        numbered.forEach((item, i) => {
            const content = item.replace(/^\d+\.\s*/, '');
            const label = labels[i] || '';
            const itemIcon = i === 0 ? '🔍' : i === 1 ? '📊' : '💡';
            html += `
                <div class="review-item">
                    <div class="review-item-header">
                        <span class="review-item-icon">${itemIcon}</span>
                        <span class="review-item-label">${label}</span>
                    </div>
                    <p class="review-item-text">${content}</p>
                </div>
            `;
        });
        html += '</div>';
        return html;
    }

    // 번호 패턴 없으면 문장 단위로 분리
    const sentences = text.split(/(?<=\.\s)/).filter(s => s.trim());
    if (sentences.length >= 2) {
        let html = '<div class="review-items">';
        sentences.forEach((s, i) => {
            const itemIcon = i === 0 ? '🔍' : i === 1 ? '📊' : '💡';
            const label = labels[Math.min(i, labels.length - 1)] || '';
            html += `
                <div class="review-item">
                    <div class="review-item-header">
                        <span class="review-item-icon">${itemIcon}</span>
                        <span class="review-item-label">${label}</span>
                    </div>
                    <p class="review-item-text">${s.trim()}</p>
                </div>
            `;
        });
        html += '</div>';
        return html;
    }

    return `<p class="review-plain">${text}</p>`;
}

// ============================================
// 에러 표시
// ============================================
function showError(msg) {
    document.getElementById('headerDate').textContent = '오류';
    document.getElementById('summaryText').textContent = msg || '데이터를 불러올 수 없습니다.';
}
