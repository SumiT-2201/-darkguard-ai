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
const apiKeyInput = document.getElementById('api-key-input');
const thresholdSlider = document.getElementById('threshold-slider');
const thresholdVal = document.getElementById('threshold-val');
const resetBtn = document.getElementById('reset-settings');

let currentThreshold = 0.8;
let currentApiKey = "";

// --- INITIALIZE SETTINGS ---
chrome.storage.sync.get(['confidence_threshold', 'darkguard_api_key'], (data) => {
    if (data.confidence_threshold) {
        currentThreshold = data.confidence_threshold;
        thresholdSlider.value = currentThreshold;
        thresholdVal.textContent = parseFloat(currentThreshold).toFixed(2);
    }
    if (data.darkguard_api_key) {
        currentApiKey = data.darkguard_api_key;
        apiKeyInput.value = currentApiKey;
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

apiKeyInput.addEventListener('change', (e) => {
    currentApiKey = e.target.value.trim();
    chrome.storage.sync.set({ darkguard_api_key: currentApiKey });
});

resetBtn.addEventListener('click', () => {
    currentThreshold = 0.8;
    currentApiKey = "";
    thresholdSlider.value = 0.8;
    apiKeyInput.value = "";
    thresholdVal.textContent = '0.80';
    chrome.storage.sync.set({ confidence_threshold: 0.8, darkguard_api_key: "" });
});

// --- SCAN LOGIC ---
btn.addEventListener('click', () => {
    // Basic validation
    if (!currentApiKey) {
        settingsPanel.style.display = 'block';
        settingsToggle.textContent = '❌';
        apiKeyInput.focus();
        showError("Please set your API Key in settings first.");
        return;
    }

    btn.disabled = true;
    loading.style.display = 'block';
    resultDiv.style.display = 'none';
    errorMsg.style.display = 'none';
    settingsPanel.style.display = 'none';
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

        chrome.runtime.sendMessage({ 
            type: "SCAN_CURRENT_PAGE", 
            url: url,
            threshold: currentThreshold,
            apiKey: currentApiKey
        }, response => {
            loading.style.display = 'none';
            btn.disabled = false;

            if (chrome.runtime.lastError || !response) {
                showError("Backend server is unreachable.");
                return;
            }

            if (response.status === 'success') {
                renderResult(response.report);
            } else {
                showError("Scan Failed: " + (response.message || response.error || "Unknown error"));
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
        findingsDiv.innerHTML = '<span style="color:#00b894">✅ Safe! No patterns found.</span>';
    }

    resultDiv.style.display = 'block';
}
