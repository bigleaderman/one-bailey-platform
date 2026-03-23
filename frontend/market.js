/**
 * OneBailey - 시장 현황 페이지
 */

document.addEventListener('DOMContentLoaded', function () {
    loadSummary();
    loadTrend();
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
            <div class="ind-card ${statusClass}">
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
                <div class="econ-item">
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
