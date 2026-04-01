document.getElementById('scan-btn').addEventListener('click', () => {
    const btn = document.getElementById('scan-btn');
    const loading = document.getElementById('loading');
    const resultDiv = document.getElementById('result');
    const errorMsg = document.getElementById('error-msg');
    const findingsDiv = document.getElementById('findings');
    const scoreDiv = document.getElementById('score');
    const riskDiv = document.getElementById('risk');
    const gradeDiv = document.getElementById('grade');

    btn.disabled = true;
    loading.style.display = 'block';
    resultDiv.style.display = 'none';
    errorMsg.style.display = 'none';

    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        if (!tabs || tabs.length === 0) {
            errorMsg.textContent = "No active tab found.";
            errorMsg.style.display = 'block';
            loading.style.display = 'none';
            btn.disabled = false;
            return;
        }

        const activeTab = tabs[0];
        const url = activeTab.url;

        // Ensure we don't scan internal chrome pages
        if (url.startsWith('chrome://') || url.startsWith('about:')) {
            errorMsg.textContent = "Cannot scan internal browser pages.";
            errorMsg.style.display = 'block';
            loading.style.display = 'none';
            btn.disabled = false;
            return;
        }

        chrome.runtime.sendMessage({ type: "SCAN_CURRENT_PAGE", url: url }, response => {
            loading.style.display = 'none';
            btn.disabled = false;

            if (chrome.runtime.lastError || !response) {
                errorMsg.textContent = "Backend server is down or unreachable.";
                errorMsg.style.display = 'block';
                return;
            }

            if (response.status === 'success') {
                const report = response.report;
                const score = report.trust_score;
                
                scoreDiv.textContent = score + '%';
                
                let color = '#d63031'; // Danger
                let riskText = 'High Risk';
                let gradeText = 'Critical UX Issues';

                if (score >= 90) {
                    color = '#00b894'; // Success
                    riskText = 'Secure';
                    gradeText = 'No dark patterns found';
                } else if (score >= 70) {
                    color = '#fdcb6e'; // Warning
                    riskText = 'Fair';
                    gradeText = 'Minor patterns detected';
                }

                scoreDiv.style.color = color;
                riskDiv.textContent = riskText;
                riskDiv.style.background = color + '20';
                riskDiv.style.color = color;
                gradeDiv.textContent = 'GRADE ' + report.grade;
                gradeDiv.style.color = color;

                const patterns = report.findings_list || report.patterns_detected || [];
                if (patterns.length > 0) {
                    findingsDiv.innerHTML = `<strong>Detected:</strong><br>` + 
                                       patterns.map(p => `• ${p.pattern_name || p.category.replace('_',' ')}`).slice(0, 3).join('<br>') + 
                                       (patterns.length > 3 ? `<br>...and ${patterns.length - 3} more` : '');
                } else {
                    findingsDiv.innerHTML = '<span style="color:#00b894">✅ Safe from dark patterns!</span>';
                }

                resultDiv.style.display = 'block';
            } else {
                errorMsg.textContent = "Scan Failed: " + (response.message || "Unknown error");
                errorMsg.style.display = 'block';
            }
        });
    });
});
