function renderReport(report) {
    const container = document.getElementById('report-content');
    const color = getGradeColor(report.grade);
    
    // Check if findings_list exists (SQLite stores as findings_list, previous Mongo as patterns_detected)
    const patterns = report.findings_list || report.patterns_detected || [];
    const categories = report.categories || [];
    const recommendations = report.recommendations || [];

    let html = `
        <div class="report-header">
            <div class="site-info">
                <span class="scan-date">${new Date(report.timestamp || report.scan_date).toLocaleString()}</span>
                <h1>${report.domain || 'Scan Result'}</h1>
                <p class="url-link-row">🔗 <a href="${report.url}" target="_blank">${report.url}</a></p>
                <div class="summary-pill">${report.summary_text || 'Website analyzed for deceptive practices.'}</div>
            </div>
            <div class="score-circle-container">
                <div class="score-circle" style="--score-color: ${color}">
                    <span class="score-val">${report.trust_score}</span>
                    <span class="score-label">TRUST SCORE</span>
                </div>
                <div class="grade-pill" style="background: ${color}20; color: ${color}">Grade ${report.grade}</div>
            </div>
        </div>

        <div class="analysis-grid">
            <div class="analysis-card chart-section">
                <h3>Pattern Distribution</h3>
                <div class="canvas-container">
                    <canvas id="categoryChart"></canvas>
                </div>
            </div>
            <div class="analysis-card recommendations-section">
                <h3>Recommendations</h3>
                <div class="rec-list">
                    ${recommendations.length > 0 ? recommendations.map(rec => `
                        <div class="rec-item">
                            <div class="rec-icon">🛡️</div>
                            <div>
                                <div class="rec-title">${rec.title}</div>
                                <div class="rec-desc">${rec.description}</div>
                            </div>
                        </div>
                    `).join('') : '<p>No specific recommendations.</p>'}
                </div>
            </div>
        </div>

        <div class="findings-section">
            <h3>Detailed Findings (${patterns.length})</h3>
            ${patterns.length > 0 ? `
                <div class="pattern-list">
                    ${patterns.map(p => `
                        <div class="pattern-item ${p.severity?.toLowerCase() || 'low'}">
                            <div class="pattern-top">
                                <span class="pattern-cat">${p.pattern_name || p.category}</span>
                                <span class="pattern-sev-badge">${p.severity || 'Medium'} Risk</span>
                            </div>
                            <div class="pattern-text">"${p.matched_text}"</div>
                            <div class="pattern-expl">${p.explanation || 'Deceptive pattern detected via ' + (p.detection_method || 'AI analysis') + '.'}</div>
                        </div>
                    `).join('')}
                </div>
            ` : `
                <div class="empty-state">
                    <div class="empty-icon">✅</div>
                    <h4>No Dark Patterns Detected</h4>
                    <p>Our hybrid engine couldn't find any deceptive patterns on this page.</p>
                </div>
            `}
        </div>
    `;

    container.innerHTML = html;

    // Initialize Chart
    if (categories.length > 0) {
        initChart(categories);
    }
}

// Global variable for chart instance to allow cleanup/reuse
let activeChart = null;

function initChart(categories) {
    const canvas = document.getElementById('categoryChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Destroy previous chart to avoid overlapping/memory leaks
    if (activeChart) {
        activeChart.destroy();
    }
    
    // Sort categories by count
    const sorted = [...categories].sort((a, b) => b.count - a.count);
    
    activeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: sorted.map(c => c.name),
            datasets: [{
                data: sorted.map(c => c.count),
                backgroundColor: [
                    '#6c5ce7', '#00b894', '#0984e3', '#fdcb6e', '#d63031', '#e84393'
                ],
                borderWidth: 0,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#9494aa',
                        usePointStyle: true,
                        padding: 20
                    }
                }
            },
            cutout: '70%'
        }
    });
}
