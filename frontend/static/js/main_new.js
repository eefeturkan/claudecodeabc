/**
 * BIST100 Akıllı Portföy Danışmanı - Frontend JavaScript
 * Tercih bazlı hisse önerisi ve portföy optimizasyonu
 */

// Global state
let availableSectors = [];

// Sayfa yüklendiğinde
document.addEventListener('DOMContentLoaded', async function() {
    console.log('Uygulama başlatılıyor...');

    // Gelişmiş ayarlar toggle
    setupAdvancedSettings();

    // Bilgi paneli toggle
    setupInfoPanel();

    // Sektörleri yükle
    await loadSectors();

    // Event listeners
    document.getElementById('analyzeBtn').addEventListener('click', analyzePortfolio);
});


/**
 * Gelişmiş ayarlar collapse işlevi
 */
function setupAdvancedSettings() {
    const toggle = document.getElementById('advancedToggle');
    const settings = document.getElementById('advancedSettings');

    toggle.addEventListener('click', () => {
        settings.classList.toggle('hidden');
        toggle.textContent = settings.classList.contains('hidden')
            ? '5. Gelişmiş Ayarlar (Opsiyonel) ▼'
            : '5. Gelişmiş Ayarlar (Opsiyonel) ▲';
    });
}


/**
 * Bilgi paneli toggle işlevi
 */
function setupInfoPanel() {
    const toggle = document.getElementById('infoPanelToggle');
    const content = document.getElementById('infoPanelContent');

    toggle.addEventListener('click', () => {
        content.classList.toggle('hidden');
        toggle.classList.toggle('active');
    });
}


/**
 * Sektör listesini API'den yükle
 */
async function loadSectors() {
    try {
        const response = await fetch('/api/sectors');
        const data = await response.json();

        if (data.success) {
            availableSectors = data.sectors;
            renderSectors(availableSectors);
        } else {
            console.error('Sektörler yüklenemedi:', data.error);
        }
    } catch (error) {
        console.error('Sektörler yüklenirken hata:', error);
    }
}


/**
 * Sektörleri checkbox olarak render et
 */
function renderSectors(sectors) {
    const container = document.getElementById('sectorSelection');
    container.innerHTML = '';

    sectors.forEach(sector => {
        const label = document.createElement('label');
        label.className = 'checkbox-option';

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.name = 'sector';
        checkbox.value = sector;

        const span = document.createElement('span');
        span.textContent = sector;

        label.appendChild(checkbox);
        label.appendChild(span);
        container.appendChild(label);
    });
}


/**
 * Seçili tercihleri al
 */
function getPreferences() {
    // Risk profili
    const riskProfile = document.querySelector('input[name="riskProfile"]:checked')?.value || 'orta';

    // Yatırım süresi
    const investmentPeriod = document.querySelector('input[name="investmentPeriod"]:checked')?.value || 'orta';

    // Seçili sektörler (boş array = tüm sektörler)
    const selectedSectors = Array.from(
        document.querySelectorAll('input[name="sector"]:checked')
    ).map(cb => cb.value);

    // Max hisse sayısı
    const maxStocks = parseInt(document.getElementById('maxStocks').value);

    // Yatırım tutarı
    const investmentAmount = parseInt(document.getElementById('investmentAmount').value);

    // Gelişmiş ayarlar
    const colonySize = parseInt(document.getElementById('colonySize').value);
    const maxIterations = parseInt(document.getElementById('maxIterations').value);
    const minWeight = parseFloat(document.getElementById('minWeight').value) / 100;
    const maxWeight = parseFloat(document.getElementById('maxWeight').value) / 100;
    const riskFreeRate = parseFloat(document.getElementById('riskFreeRate').value) / 100;

    return {
        risk_profile: riskProfile,
        investment_period: investmentPeriod,
        sectors: selectedSectors.length > 0 ? selectedSectors : null,
        max_stocks: maxStocks,
        investment_amount: investmentAmount,
        colony_size: colonySize,
        max_iterations: maxIterations,
        min_weight: minWeight,
        max_weight: maxWeight,
        risk_free_rate: riskFreeRate
    };
}


/**
 * Portföy analizi başlat
 */
async function analyzePortfolio() {
    const preferences = getPreferences();

    console.log('Tercihler:', preferences);

    // UI güncellemeleri
    showProgress();
    hideResults();
    hideInitialMessage();

    try {
        const response = await fetch('/api/optimize-with-preferences', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(preferences)
        });

        const data = await response.json();

        if (data.success) {
            console.log('Sonuçlar:', data);
            displayResults(data);
        } else {
            alert('Hata: ' + data.error);
            showInitialMessage();
        }
    } catch (error) {
        console.error('Optimizasyon hatası:', error);
        alert('Bir hata oluştu. Lütfen tekrar deneyin.');
        showInitialMessage();
    } finally {
        hideProgress();
    }
}


/**
 * Sonuçları göster
 */
function displayResults(data) {
    const { recommendation, optimization } = data;

    // Önerilen hisseleri göster
    displayRecommendedStocks(recommendation.recommended_stocks);

    // Metrikleri göster
    displayMetrics(optimization);

    // Grafikleri çiz
    plotSectorChart(optimization.sector_distribution);
    plotWeightsChart(optimization.weights);
    plotWeightsTable(optimization.weights);
    plotConvergenceChart(optimization.history);

    // Sonuç bölümünü göster
    showResults();
}


/**
 * Önerilen hisseleri göster
 */
function displayRecommendedStocks(stocks) {
    const container = document.getElementById('recommendedStocks');
    container.innerHTML = '';

    const intro = document.createElement('p');
    intro.className = 'stocks-intro';
    intro.textContent = `Tercihlerinize göre ${stocks.length} adet hisse seçildi:`;
    container.appendChild(intro);

    const stocksGrid = document.createElement('div');
    stocksGrid.className = 'stocks-grid';

    stocks.forEach(stock => {
        const stockCard = document.createElement('div');
        stockCard.className = 'stock-card';
        stockCard.innerHTML = `
            <div class="stock-symbol">${stock.symbol}</div>
            <div class="stock-name">${stock.name}</div>
        `;
        stocksGrid.appendChild(stockCard);
    });

    container.appendChild(stocksGrid);
}


/**
 * Metrikleri göster
 */
function displayMetrics(optimization) {
    const { metrics, summary, investment_amount, period_years, expected_total_amount } = optimization;

    // Toplam yatırım - Başlangıç ve beklenen toplam
    document.getElementById('totalInvestment').innerHTML =
        `<div style="font-size: 0.85em; margin-bottom: 4px;">Başlangıç: ${formatCurrency(investment_amount)}</div>` +
        `<div style="font-size: 1.1em; font-weight: 700;">Beklenen: ${formatCurrency(expected_total_amount)}</div>`;

    // Beklenen getiri - Hem yıllık hem de toplam göster
    const periodText = period_years === 0.5 ? '6 Ay' : period_years === 1 ? '1 Yıl' : '5 Yıl';
    document.getElementById('expectedReturn').innerHTML =
        `<div style="font-size: 0.85em; margin-bottom: 4px;">Yıllık: ${formatPercent(summary.expected_annual_return_pct)}</div>` +
        `<div style="font-size: 1.1em; font-weight: 700;">${periodText}: ${formatPercent(summary.expected_total_return_pct)}</div>`;

    // Volatilite
    document.getElementById('volatility').textContent =
        formatPercent(summary.volatility_pct);

    // Sharpe Ratio
    document.getElementById('sharpeRatio').textContent =
        summary.sharpe_ratio.toFixed(3);

    // Sortino Ratio
    document.getElementById('sortinoRatio').textContent =
        metrics.sortino_ratio.toFixed(3);

    // Max Drawdown
    document.getElementById('maxDrawdown').textContent =
        formatPercent(metrics.max_drawdown * 100);

    // Çeşitlendirme
    document.getElementById('diversification').textContent =
        metrics.diversification_ratio.toFixed(2);

    // Hisse sayısı
    document.getElementById('stockCount').textContent =
        summary.stocks_with_weight + ' / ' + summary.total_stocks;
}


/**
 * Sektör dağılımı pasta grafiği
 */
function plotSectorChart(sectorDistribution) {
    if (!sectorDistribution || sectorDistribution.length === 0) return;

    const data = [{
        type: 'pie',
        labels: sectorDistribution.map(s => s.sector),
        values: sectorDistribution.map(s => s.percentage),
        textinfo: 'label+percent',
        textposition: 'auto',
        hovertemplate: '<b>%{label}</b><br>' +
                       'Ağırlık: %{value:.2f}%<br>' +
                       '<extra></extra>',
        marker: {
            colors: ['#58a6ff', '#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#06b6d4']
        }
    }];

    const layout = {
        title: {
            text: 'Sektörel Dağılım (%)',
            font: { size: 16, color: '#c9d1d9', family: '-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif' }
        },
        showlegend: true,
        height: 500,
        margin: { t: 60, b: 50, l: 50, r: 200 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#8b949e', family: '-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif' },
        legend: {
            font: { size: 11 },
            orientation: 'v',
            x: 1.05,
            y: 0.5,
            xanchor: 'left',
            yanchor: 'middle'
        }
    };

    Plotly.newPlot('sectorChart', data, layout, { responsive: true, displayModeBar: false });
}


/**
 * Portföy dağılımı pasta grafiği
 */
function plotWeightsChart(weights) {
    // Sadece ağırlığı > 0 olanları göster
    const filteredWeights = weights.filter(w => w.weight > 0.001);

    const data = [{
        type: 'pie',
        labels: filteredWeights.map(w => `${w.symbol} - ${w.name}`),
        values: filteredWeights.map(w => w.percentage),
        textinfo: 'label+percent',
        textposition: 'auto',
        hovertemplate: '<b>%{label}</b><br>' +
                       'Ağırlık: %{value:.2f}%<br>' +
                       '<extra></extra>',
        marker: {
            colors: generateColors(filteredWeights.length)
        }
    }];

    const layout = {
        title: {
            text: 'Hisse Dağılımı (%)',
            font: { size: 16, color: '#c9d1d9', family: '-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif' }
        },
        showlegend: true,
        height: 550,
        margin: { t: 60, b: 50, l: 50, r: 250 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#8b949e', family: '-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif' },
        legend: {
            font: { size: 11 },
            orientation: 'v',
            x: 1.05,
            y: 0.5,
            xanchor: 'left',
            yanchor: 'middle'
        }
    };

    Plotly.newPlot('weightsChart', data, layout, { responsive: true, displayModeBar: false });
}


/**
 * Ağırlık tablosu
 */
function plotWeightsTable(weights) {
    const container = document.getElementById('weightsTable');

    // Sadece ağırlığı > 0 olanları göster
    const filteredWeights = weights.filter(w => w.weight > 0.001);

    let html = `
        <table class="weights-table">
            <thead>
                <tr>
                    <th>Sıra</th>
                    <th>Hisse</th>
                    <th>Şirket</th>
                    <th>Ağırlık (%)</th>
                    <th>Tutar (₺)</th>
                </tr>
            </thead>
            <tbody>
    `;

    filteredWeights.forEach((w, index) => {
        html += `
            <tr>
                <td>${index + 1}</td>
                <td class="stock-symbol-cell">${w.symbol}</td>
                <td>${w.name}</td>
                <td>${w.percentage.toFixed(2)}%</td>
                <td>${formatCurrency(w.amount_tl)}</td>
            </tr>
        `;
    });

    html += `
            </tbody>
        </table>
    `;

    container.innerHTML = html;
}


/**
 * Yakınsama grafiği
 */
function plotConvergenceChart(history) {
    const iterations = Array.from({ length: history.best_fitness.length }, (_, i) => i + 1);

    const data = [
        {
            x: iterations,
            y: history.best_fitness,
            type: 'scatter',
            mode: 'lines',
            name: 'En İyi Fitness',
            line: {
                color: '#58a6ff',
                width: 2
            }
        },
        {
            x: iterations,
            y: history.mean_fitness,
            type: 'scatter',
            mode: 'lines',
            name: 'Ortalama Fitness',
            line: {
                color: '#8b949e',
                width: 2,
                dash: 'dash'
            }
        }
    ];

    const layout = {
        title: {
            text: 'Algoritma Yakınsama Süreci',
            font: { size: 14, color: '#c9d1d9', family: '-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif' }
        },
        xaxis: {
            title: 'İterasyon',
            gridcolor: '#30363d',
            color: '#8b949e'
        },
        yaxis: {
            title: 'Fitness (Sharpe Ratio)',
            gridcolor: '#30363d',
            color: '#8b949e'
        },
        showlegend: true,
        height: 380,
        margin: { t: 50, b: 60, l: 70, r: 30 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#8b949e', family: '-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif' }
    };

    Plotly.newPlot('convergenceChart', data, layout, { responsive: true, displayModeBar: false });
}


/**
 * Renk paleti üretici
 */
function generateColors(count) {
    const colors = [
        '#58a6ff', '#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b',
        '#10b981', '#06b6d4', '#6366f1', '#a855f7', '#f43f5e',
        '#eab308', '#14b8a6', '#0ea5e9', '#8b5cf6', '#d946ef'
    ];

    // Renkleri tekrarla
    const result = [];
    for (let i = 0; i < count; i++) {
        result.push(colors[i % colors.length]);
    }
    return result;
}


/**
 * Para formatı
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('tr-TR', {
        style: 'currency',
        currency: 'TRY',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}


/**
 * Yüzde formatı
 */
function formatPercent(value) {
    return (value >= 0 ? '+' : '') + value.toFixed(2) + '%';
}


/**
 * UI Helper Functions
 */
function showProgress() {
    document.getElementById('progressSection').classList.remove('hidden');
}

function hideProgress() {
    document.getElementById('progressSection').classList.add('hidden');
}

function showResults() {
    document.getElementById('resultsSection').classList.remove('hidden');
}

function hideResults() {
    document.getElementById('resultsSection').classList.add('hidden');
}

function showInitialMessage() {
    document.getElementById('initialMessage').classList.remove('hidden');
}

function hideInitialMessage() {
    document.getElementById('initialMessage').classList.add('hidden');
}
