// Global state
let availableStocks = [];
let selectedStocks = new Set();

// DOM Elements
const stockList = document.getElementById('stockList');
const selectedCount = document.getElementById('selectedCount');
const selectAllBtn = document.getElementById('selectAll');
const clearAllBtn = document.getElementById('clearAll');
const optimizeBtn = document.getElementById('optimizeBtn');
const progressSection = document.getElementById('progressSection');
const resultsSection = document.getElementById('resultsSection');
const initialMessage = document.getElementById('initialMessage');

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadStocks();
    setupEventListeners();
});

// Load available stocks
async function loadStocks() {
    try {
        const response = await fetch('/api/stocks');
        const data = await response.json();

        if (data.success) {
            availableStocks = data.stocks;
            renderStockList();
        } else {
            showError('Hisse listesi yüklenemedi: ' + data.error);
        }
    } catch (error) {
        showError('Hisse listesi yüklenirken hata: ' + error.message);
    }
}

// Render stock list
function renderStockList() {
    stockList.innerHTML = '';

    availableStocks.forEach(stock => {
        const div = document.createElement('div');
        div.className = 'stock-item';

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `stock_${stock.symbol}`;
        checkbox.value = stock.symbol;
        checkbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                selectedStocks.add(stock.symbol);
            } else {
                selectedStocks.delete(stock.symbol);
            }
            updateSelectedCount();
        });

        const label = document.createElement('label');
        label.htmlFor = `stock_${stock.symbol}`;
        label.innerHTML = `<span class="stock-symbol">${stock.symbol}</span> ${stock.name}`;

        div.appendChild(checkbox);
        div.appendChild(label);
        stockList.appendChild(div);
    });
}

// Update selected count
function updateSelectedCount() {
    selectedCount.textContent = selectedStocks.size;
    optimizeBtn.disabled = selectedStocks.size < 2;
}

// Setup event listeners
function setupEventListeners() {
    selectAllBtn.addEventListener('click', () => {
        const checkboxes = stockList.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(cb => {
            cb.checked = true;
            selectedStocks.add(cb.value);
        });
        updateSelectedCount();
    });

    clearAllBtn.addEventListener('click', () => {
        const checkboxes = stockList.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(cb => {
            cb.checked = false;
        });
        selectedStocks.clear();
        updateSelectedCount();
    });

    optimizeBtn.addEventListener('click', runOptimization);
}

// Run optimization
async function runOptimization() {
    if (selectedStocks.size < 2) {
        alert('En az 2 hisse seçmelisiniz!');
        return;
    }

    // Get parameters
    const params = {
        symbols: Array.from(selectedStocks),
        objective: document.getElementById('objective').value,
        period: document.getElementById('period').value,
        colony_size: parseInt(document.getElementById('colonySize').value),
        max_iterations: parseInt(document.getElementById('maxIterations').value),
        min_weight: parseFloat(document.getElementById('minWeight').value) / 100,
        max_weight: parseFloat(document.getElementById('maxWeight').value) / 100,
        risk_free_rate: parseFloat(document.getElementById('riskFreeRate').value) / 100
    };

    // Show progress
    initialMessage.classList.add('hidden');
    resultsSection.classList.add('hidden');
    progressSection.classList.remove('hidden');
    optimizeBtn.disabled = true;

    try {
        const response = await fetch('/api/optimize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        });

        const data = await response.json();

        if (data.success) {
            displayResults(data);
        } else {
            showError('Optimizasyon hatası: ' + data.error);
        }
    } catch (error) {
        showError('İstek hatası: ' + error.message);
    } finally {
        progressSection.classList.add('hidden');
        optimizeBtn.disabled = false;
    }
}

// Display results
function displayResults(data) {
    // Show results section
    resultsSection.classList.remove('hidden');

    // Update metrics
    document.getElementById('expectedReturn').textContent =
        (data.metrics.expected_return * 100).toFixed(2) + '%';
    document.getElementById('volatility').textContent =
        (data.metrics.volatility * 100).toFixed(2) + '%';
    document.getElementById('sharpeRatio').textContent =
        data.metrics.sharpe_ratio.toFixed(4);
    document.getElementById('sortinoRatio').textContent =
        data.metrics.sortino_ratio.toFixed(4);
    document.getElementById('maxDrawdown').textContent =
        (data.metrics.max_drawdown * 100).toFixed(2) + '%';
    document.getElementById('diversification').textContent =
        data.metrics.diversification_ratio.toFixed(4);

    // Display weights chart (pie chart)
    displayWeightsChart(data.weights);

    // Display weights table
    displayWeightsTable(data.weights);

    // Display convergence chart
    displayConvergenceChart(data.history);

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Display weights as pie chart
function displayWeightsChart(weights) {
    // Filter significant weights (> 0.1%)
    const significantWeights = weights.filter(w => w.percentage > 0.1);

    const data = [{
        values: significantWeights.map(w => w.percentage),
        labels: significantWeights.map(w => `${w.symbol} (${w.percentage.toFixed(1)}%)`),
        type: 'pie',
        textinfo: 'label+percent',
        textposition: 'outside',
        automargin: true,
        marker: {
            colors: generateColors(significantWeights.length)
        }
    }];

    const layout = {
        title: 'Portföy Dağılımı',
        height: 500,
        showlegend: true,
        legend: {
            orientation: 'v',
            x: 1.1,
            y: 0.5
        }
    };

    Plotly.newPlot('weightsChart', data, layout, { responsive: true });
}

// Display weights table
function displayWeightsTable(weights) {
    // Filter significant weights
    const significantWeights = weights.filter(w => w.percentage > 0.1);

    let html = `
        <table class="weights-table">
            <thead>
                <tr>
                    <th>Sembol</th>
                    <th>Şirket</th>
                    <th>Ağırlık</th>
                    <th>Görsel</th>
                </tr>
            </thead>
            <tbody>
    `;

    significantWeights.forEach(w => {
        html += `
            <tr>
                <td><strong>${w.symbol}</strong></td>
                <td>${w.name}</td>
                <td><strong>${w.percentage.toFixed(2)}%</strong></td>
                <td>
                    <div style="width: 100%; background: #e9ecef; border-radius: 10px;">
                        <div class="weight-bar" style="width: ${w.percentage}%"></div>
                    </div>
                </td>
            </tr>
        `;
    });

    html += `
            </tbody>
        </table>
    `;

    document.getElementById('weightsTable').innerHTML = html;
}

// Display convergence chart
function displayConvergenceChart(history) {
    const iterations = Array.from({ length: history.best_fitness.length }, (_, i) => i + 1);

    const trace1 = {
        x: iterations,
        y: history.best_fitness,
        mode: 'lines',
        name: 'En İyi Fitness',
        line: {
            color: '#667eea',
            width: 3
        }
    };

    const trace2 = {
        x: iterations,
        y: history.mean_fitness,
        mode: 'lines',
        name: 'Ortalama Fitness',
        line: {
            color: '#764ba2',
            width: 2,
            dash: 'dash'
        }
    };

    const data = [trace1, trace2];

    const layout = {
        title: 'ABC Algoritması Yakınsama Grafiği',
        xaxis: {
            title: 'İterasyon',
            showgrid: true
        },
        yaxis: {
            title: 'Fitness Değeri',
            showgrid: true
        },
        height: 400,
        showlegend: true,
        legend: {
            x: 0.7,
            y: 1
        }
    };

    Plotly.newPlot('convergenceChart', data, layout, { responsive: true });
}

// Generate colors for pie chart
function generateColors(n) {
    const colors = [
        '#667eea', '#764ba2', '#f093fb', '#4facfe',
        '#43e97b', '#fa709a', '#fee140', '#30cfd0',
        '#a8edea', '#fed6e3', '#c471f5', '#fa71cd'
    ];

    const result = [];
    for (let i = 0; i < n; i++) {
        result.push(colors[i % colors.length]);
    }
    return result;
}

// Show error message
function showError(message) {
    alert('HATA: ' + message);
    progressSection.classList.add('hidden');
    optimizeBtn.disabled = false;
}

// Format number
function formatNumber(num, decimals = 2) {
    return num.toFixed(decimals);
}

// Format percentage
function formatPercent(num, decimals = 2) {
    return (num * 100).toFixed(decimals) + '%';
}
