// --- DOM ELEMENTS ---
const btn = document.getElementById('scan-btn');
const loading = document.getElementById('loading');
const resultDiv = document.getElementById('result');
const errorMsg = document.getElementById('error-msg');
const findingsDiv = document.getElementById('findings');
const scoreDiv = document.getElementById('score');
const riskDiv = document.getElementById('risk');
const gradeDiv = document.getElementById('grade');

// Settings Elements
const settingsToggle = document.getElementById('settings-toggle');
const settingsPanel = document.getElementById('settings-panel');
const thresholdSlider = document.getElementById('threshold-slider');
const thresholdVal = document.getElementById('threshold-val');
const resetBtn = document.getElementById('reset-threshold');

let currentThreshold = 0.8;

// --- INITIALIZE SETTINGS ---
chrome.storage.sync.get(['confidence_threshold'], (data) => {
    if (data.confidence_threshold) {
        currentThreshold = data.confidence_threshold;
        thresholdSlider.value = currentThreshold;
        thresholdVal.textContent = parseFloat(currentThreshold).toFixed(2);
    }
});

// --- SETTINGS EVENT HANDLERS ---
settingsToggle.addEventListener('click', () => {
    const isVisible = settingsPanel.style.display === 'block';
    settingsPanel.style.display = isVisible ? 'none' : 'block';
    settingsToggle.textContent = isVisible ? '⚙️' : '❌';
});

thresholdSlider.addEventListener('input', (e) => {
    currentThreshold = e.target.value;
    thresholdVal.textContent = parseFloat(currentThreshold).toFixed(2);
    chrome.storage.sync.set({ confidence_threshold: currentThreshold });
});

resetBtn.addEventListener('click', () => {
    currentThreshold = 0.8;
    thresholdSlider.value = 0.8;
    thresholdVal.textContent = '0.80';
    chrome.storage.sync.set({ confidence_threshold: 0.8 });
});

// --- SCAN LOGIC ---
btn.addEventListener('click', () => {
    btn.disabled = true;
    loading.style.display = 'block';
    resultDiv.style.display = 'none';
    errorMsg.style.display = 'none';
    settingsPanel.style.display = 'none'; // Auto-hide settings on scan
    settingsToggle.textContent = '⚙️';

    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        if (!tabs || tabs.length === 0) {
            showError("No active tab found.");
            return;
        }

        const activeTab = tabs[0];
        const url = activeTab.url;

        if (url.startsWith('chrome://') || url.startsWith('about:')) {
            showError("Cannot scan internal browser pages.");
            return;
        }

        // Pass threshold to background script
        chrome.runtime.sendMessage({ 
            type: "SCAN_CURRENT_PAGE", 
            url: url,
            threshold: currentThreshold 
        }, response => {
            loading.style.display = 'none';
            btn.disabled = false;

            if (chrome.runtime.lastError || !response) {
                showError("Backend server is down or unreachable.");
                return;
            }

            if (response.status === 'success') {
                renderResult(response.report);
            } else {
                showError("Scan Failed: " + (response.message || "Unknown error"));
            }
        });
    });
});

function showError(msg) {
    loading.style.display = 'none';
    btn.disabled = false;
    errorMsg.textContent = msg;
    errorMsg.style.display = 'block';
}

function renderResult(report) {
    const score = report.trust_score;
    scoreDiv.textContent = score + '%';
    
    let color = '#d63031'; 
    let riskText = 'High Risk';

    if (score >= 90) {
        color = '#00b894'; 
        riskText = 'Secure';
    } else if (score >= 70) {
        color = '#fdcb6e'; 
        riskText = 'Fair';
    }

    scoreDiv.style.color = color;
    riskDiv.textContent = riskText;
    riskDiv.style.background = color + '20';
    riskDiv.style.color = color;
    gradeDiv.textContent = 'GRADE ' + report.grade;
    gradeDiv.style.color = color;

    const patterns = report.findings_list || [];
    if (patterns.length > 0) {
        findingsDiv.innerHTML = `<strong>Detected:</strong><br>` + 
                           patterns.map(p => `• ${p.pattern_name}`).slice(0, 3).join('<br>') + 
                           (patterns.length > 3 ? `<br>...and ${patterns.length - 3} more` : '');
    } else {
        findingsDiv.innerHTML = '<span style="color:#00b894">✅ Safe from dark patterns!</span>';
    }

    resultDiv.style.display = 'block';
}
