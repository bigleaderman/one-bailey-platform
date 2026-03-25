/**
 * OneBailey - 시장 현황 페이지
 */

document.addEventListener('DOMContentLoaded', function () {
    loadSummary();
    loadTrend();
    loadNews();
});

// ============================================
// 시장 종합 상태
// ============================================
async function loadSummary() {
    try {
        const res = await fetch('/api/market/summary');
        if (!res.ok) throw new Error('데이터를 불러올 수 없습니다');
        const data = await res.json();
        renderTemperature(data.temperature);
        renderIndicators(data.indicators);
        renderEconomic(data.economic);
        if (data.updated_at) {
            document.getElementById('updatedAt').textContent = `데이터 기준: ${data.updated_at}`;
        }
    } catch (e) {
        console.error('Summary error:', e);
    }
}

// ============================================
// 시장 온도계
// ============================================
function renderTemperature(temp) {
    // 게이지 바
    const fill = document.getElementById('tempFill');
    const pointer = document.getElementById('tempPointer');
    fill.style.width = temp.score + '%';

    // 색상
    if (temp.score >= 60) {
        fill.className = 'temp-fill green';
    } else if (temp.score >= 40) {
        fill.className = 'temp-fill yellow';
    } else {
        fill.className = 'temp-fill red';
    }

    pointer.style.left = temp.score + '%';

    // 텍스트
    document.getElementById('tempEmoji').textContent = temp.emoji;
    document.getElementById('tempLabel').textContent = temp.label;
    document.getElementById('tempDesc').textContent = temp.description;

    // 카드 색상
    const card = document.getElementById('tempCard');
    card.classList.remove('fear', 'greed');
    if (temp.score < 40) card.classList.add('fear');
    else if (temp.score >= 60) card.classList.add('greed');
}

// ============================================
// 주요 지표 카드
// ============================================
function renderIndicators(indicators) {
    const container = document.getElementById('indicatorCards');

    container.innerHTML = indicators.map(ind => {
        const statusClass = ind.status; // good, neutral, bad
        const valueStr = ind.value !== null ? formatValue(ind.value, ind.name) : '-';
        const changeStr = ind.change !== null ? formatChange(ind.change, ind.name) : '';

        return `
            <div class="ind-card ${statusClass} clickable" onclick="openIndicatorDetail('${ind.name}')">
                <div class="ind-header">
                    <span class="ind-label">${ind.label}</span>
                    <span class="ind-trend ${ind.trend}">${ind.trend_text}</span>
                </div>
                <div class="ind-value">${valueStr}</div>
                ${changeStr ? `<div class="ind-change">${changeStr}</div>` : ''}
                <p class="ind-desc">${ind.description}</p>
            </div>
        `;
    }).join('');
}

function formatValue(value, name) {
    if (name === 'gold') return '$' + value.toLocaleString('en-US', {maximumFractionDigits: 0});
    if (name === 'treasury_10y') return value.toFixed(3) + '%';
    if (name === 'dxy') return value.toFixed(2);
    return value.toFixed(2);
}

function formatChange(change, name) {
    const sign = change >= 0 ? '+' : '';
    if (name === 'treasury_10y') return `전일 대비 ${sign}${change.toFixed(3)}%p`;
    if (name === 'vix') return `전일 대비 ${sign}${change.toFixed(2)}`;
    return `전일 대비 ${sign}${change.toFixed(2)}%`;
}

// ============================================
// 시장 지표 상세 모달
// ============================================
let indDetailChart = null;

async function openIndicatorDetail(name) {
    try {
        const res = await fetch(`/api/market/indicator/${name}`);
        if (!res.ok) throw new Error('데이터 없음');
        const data = await res.json();
        showIndicatorModal(data);
    } catch (e) {
        console.error('Indicator detail error:', e);
    }
}

function showIndicatorModal(data) {
    const existing = document.getElementById('econModal');
    if (existing) existing.remove();

    const statusColors = { good: '#16a34a', neutral: '#f59e0b', bad: '#dc2626' };
    const statusColor = statusColors[data.status] || '#6b7280';
    const valueStr = data.current_value !== null ? formatValue(data.current_value, data.name) : '-';
    const changeStr = data.change !== null ? formatChange(data.change, data.name) : '';

    const modal = document.createElement('div');
    modal.id = 'econModal';
    modal.className = 'modal-overlay';
    modal.onclick = function(e) { if (e.target === modal) closeIndicatorModal(); };

    // 차트에 사용할 필드 매핑
    const fieldMap = {
        'vix': 'vix_level', 'treasury_10y': 'treasury_10y',
        'hy_spread': null, 'real_rate': null,
        'dxy': 'dxy_level', 'gold': 'gold_price'
    };

    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>${data.label}</h3>
                <button class="modal-close" onclick="closeIndicatorModal()">✕</button>
            </div>
            <div class="modal-status" style="border-left: 4px solid ${statusColor}">
                <div class="modal-status-row">
                    <span class="modal-value">${valueStr}</span>
                    <span class="modal-badge" style="background: ${statusColor}20; color: ${statusColor}">${data.status_text}</span>
                </div>
                ${changeStr ? `<div style="font-size:0.85rem;color:#6b7280;margin-bottom:8px">${changeStr}</div>` : ''}
                <p class="modal-meaning">${data.current_meaning}</p>
            </div>
            <div class="modal-section">
                <h4>📖 이 지표는?</h4>
                <p>${data.what_is}</p>
            </div>
            <div class="modal-section">
                <h4>💡 왜 중요한가요?</h4>
                <p>${data.why_matters}</p>
            </div>
            <div class="modal-section">
                <h4>📈 30일 추세</h4>
                <div class="modal-chart-container">
                    <canvas id="indDetailChart"></canvas>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    document.body.style.overflow = 'hidden';

    renderIndicatorDetailChart(data, fieldMap[data.name]);
}

function closeIndicatorModal() {
    const modal = document.getElementById('econModal');
    if (modal) modal.remove();
    document.body.style.overflow = '';
    if (indDetailChart) { indDetailChart.destroy(); indDetailChart = null; }
}

function renderIndicatorDetailChart(data, field) {
    const ctx = document.getElementById('indDetailChart').getContext('2d');
    const history = data.history;
    const labels = history.map(h => h.date ? h.date.slice(5) : '');

    // 필드에서 값 추출
    let values;
    if (field) {
        values = history.map(h => h[field]);
    } else {
        // hy_spread, real_rate는 history에 직접 없으므로 current_value만 표시
        // history의 모든 TrendDataPoint에는 해당 필드가 없으니 빈 차트
        values = history.map(() => null);
    }

    const color = data.name === 'vix' || data.name === 'hy_spread' ? '#ef4444' : '#3b82f6';

    indDetailChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: data.label,
                data: values,
                borderColor: color,
                backgroundColor: color + '1A',
                fill: true,
                tension: 0.3,
                pointRadius: 2,
                pointHoverRadius: 5,
                borderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { display: false }, ticks: { maxTicksLimit: 6, font: { size: 10 } } },
                y: { grid: { color: 'rgba(0,0,0,0.05)' }, ticks: { font: { size: 10 } } }
            }
        }
    });
}

// ============================================
// 경제 지표
// ============================================
function renderEconomic(economic) {
    const container = document.getElementById('economicCards');

    if (!economic || economic.length === 0) {
        container.innerHTML = '<p class="no-data">경제 지표 데이터가 없습니다.</p>';
        return;
    }

    // 카테고리별 그룹
    const groups = {};
    economic.forEach(item => {
        if (!groups[item.category]) groups[item.category] = [];
        groups[item.category].push(item);
    });

    const categoryIcons = { '물가': '💰', '고용': '👷', '성장': '📈' };

    let html = '';
    for (const [category, items] of Object.entries(groups)) {
        const icon = categoryIcons[category] || '📊';
        html += `<div class="econ-group">`;
        html += `<div class="econ-group-title">${icon} ${category}</div>`;

        items.forEach(item => {
            const valueStr = item.value !== null ? `${item.value.toFixed(1)}${item.unit}` : '-';
            html += `
                <div class="econ-item clickable" onclick="openEconomicDetail('${item.name}')">
                    <div class="econ-item-header">
                        <span class="econ-name">${item.label}</span>
                        <span class="econ-value">${valueStr}</span>
                    </div>
                    <p class="econ-desc">${item.description}</p>
                </div>
            `;
        });

        html += `</div>`;
    }

    container.innerHTML = html;
}

// ============================================
// 추세 차트
// ============================================
async function loadTrend() {
    try {
        const res = await fetch('/api/market/trend?days=30');
        if (!res.ok) return;
        const data = await res.json();
        renderQQQChart(data.data);
        renderVIXChart(data.data);
    } catch (e) {
        console.error('Trend error:', e);
    }
}

function renderQQQChart(data) {
    const ctx = document.getElementById('qqqChart').getContext('2d');
    const labels = data.map(d => d.date ? d.date.slice(5) : '');
    const prices = data.map(d => d.qqq_price);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'QQQ',
                data: prices,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                fill: true,
                tension: 0.3,
                pointRadius: 2,
                pointHoverRadius: 5,
                borderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(ctx) { return '$' + ctx.parsed.y.toFixed(2); }
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { maxTicksLimit: 6, font: { size: 11 } }
                },
                y: {
                    grid: { color: 'rgba(0,0,0,0.05)' },
                    ticks: {
                        callback: function(v) { return '$' + v; },
                        font: { size: 11 }
                    }
                }
            }
        }
    });
}

// ============================================
// 경제 지표 상세 모달
// ============================================
let econDetailChart = null;

async function openEconomicDetail(name) {
    try {
        const res = await fetch(`/api/market/economic/${name}`);
        if (!res.ok) throw new Error('데이터 없음');
        const data = await res.json();
        showEconModal(data);
    } catch (e) {
        console.error('Economic detail error:', e);
    }
}

function showEconModal(data) {
    // 기존 모달 제거
    const existing = document.getElementById('econModal');
    if (existing) existing.remove();

    const statusColors = { good: '#16a34a', neutral: '#f59e0b', bad: '#dc2626' };
    const statusColor = statusColors[data.status] || '#6b7280';

    const valueStr = data.current_value !== null ? `${data.current_value.toFixed(1)}${data.unit}` : '-';

    const modal = document.createElement('div');
    modal.id = 'econModal';
    modal.className = 'modal-overlay';
    modal.onclick = function(e) { if (e.target === modal) closeEconModal(); };

    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>${data.label}</h3>
                <button class="modal-close" onclick="closeEconModal()">✕</button>
            </div>

            <div class="modal-status" style="border-left: 4px solid ${statusColor}">
                <div class="modal-status-row">
                    <span class="modal-value">${valueStr}</span>
                    <span class="modal-badge" style="background: ${statusColor}20; color: ${statusColor}">${data.status_text}</span>
                </div>
                <p class="modal-meaning">${data.current_meaning}</p>
            </div>

            <div class="modal-section">
                <h4>📖 이 지표는?</h4>
                <p>${data.what_is}</p>
            </div>

            <div class="modal-section">
                <h4>💡 왜 중요한가요?</h4>
                <p>${data.why_matters}</p>
            </div>

            <div class="modal-section">
                <h4>📈 추세</h4>
                <div class="modal-chart-container">
                    <canvas id="econDetailChart"></canvas>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
    document.body.style.overflow = 'hidden';

    // 차트 렌더링
    renderEconDetailChart(data);
}

function closeEconModal() {
    const modal = document.getElementById('econModal');
    if (modal) modal.remove();
    document.body.style.overflow = '';
    if (econDetailChart) {
        econDetailChart.destroy();
        econDetailChart = null;
    }
}

function renderEconDetailChart(data) {
    const ctx = document.getElementById('econDetailChart').getContext('2d');
    const history = data.history;

    const labels = history.map(h => h.date.slice(0, 7)); // YYYY-MM
    const isYoyType = ['CPI', 'Core_CPI', 'PCE', 'Core_PCE', 'GDP', 'Real_GDP'].includes(data.name);
    const values = history.map(h => isYoyType ? h.yoy_change : h.value);
    const label = isYoyType ? 'YoY 변화율 (%)' : data.label;

    econDetailChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: values,
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                fill: true,
                tension: 0.3,
                pointRadius: 3,
                pointHoverRadius: 6,
                borderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(ctx) {
                            const v = ctx.parsed.y;
                            return isYoyType ? `${v.toFixed(1)}%` : v.toFixed(1);
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { font: { size: 10 }, maxTicksLimit: 8 }
                },
                y: {
                    grid: { color: 'rgba(0,0,0,0.05)' },
                    ticks: {
                        font: { size: 10 },
                        callback: function(v) { return isYoyType ? v + '%' : v; }
                    }
                }
            }
        }
    });
}

// ============================================
// 시장 뉴스
// ============================================
async function loadNews() {
    try {
        const res = await fetch('/api/market/news');
        if (!res.ok) return;
        const data = await res.json();
        renderNews(data);
    } catch (e) {
        console.error('News error:', e);
    }
}

function renderNews(data) {
    const container = document.getElementById('newsList');

    if (!data.items || data.items.length === 0) {
        container.innerHTML = '<p class="no-data">최신 뉴스가 없습니다.</p>';
        return;
    }

    // 심볼별 아이콘
    const symbolIcons = {
        'AAPL': '🍎', 'MSFT': '🪟', 'GOOGL': '🔍', 'NVDA': '🟢',
        'META': '📘', 'AMZN': '📦', 'TSLA': '🚗', 'MARKET': '📰'
    };

    container.innerHTML = data.items.map(item => {
        const icon = symbolIcons[item.symbol] || '📰';
        const timeStr = item.datetime ? `<span class="news-time">${item.datetime}</span>` : '';
        return `
            <div class="news-item">
                <span class="news-icon">${icon}</span>
                <div class="news-content">
                    <p class="news-headline">${item.headline}</p>
                    <span class="news-source">${item.source} ${timeStr}</span>
                </div>
            </div>
        `;
    }).join('');
}

function renderVIXChart(data) {
    const ctx = document.getElementById('vixChart').getContext('2d');
    const labels = data.map(d => d.date ? d.date.slice(5) : '');
    const values = data.map(d => d.vix_level);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'VIX',
                data: values,
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                fill: true,
                tension: 0.3,
                pointRadius: 2,
                pointHoverRadius: 5,
                borderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { maxTicksLimit: 6, font: { size: 11 } }
                },
                y: {
                    grid: { color: 'rgba(0,0,0,0.05)' },
                    ticks: { font: { size: 11 } }
                }
            }
        }
    });
}
